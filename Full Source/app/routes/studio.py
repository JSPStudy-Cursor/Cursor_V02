"""
스튜디오 라우트
비디오 업로드 및 관리 기능을 처리합니다.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Video, Tag, Comment
from config import Config
from app.utils.security import (
    validate_video_title, validate_comment_content,
    sanitize_text
)
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import os

studio_bp = Blueprint('studio', __name__)


def allowed_file(filename, allowed_extensions):
    """
    파일 확장자 확인
    
    Args:
        filename: 파일명
        allowed_extensions: 허용된 확장자 집합
    
    Returns:
        bool: 허용된 확장자면 True
    """
    if not filename or '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_file_size(file, max_size):
    """
    파일 크기 검증
    
    Args:
        file: 업로드된 파일 객체
        max_size: 최대 크기 (바이트)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file:
        return True, None
    
    # 파일 크기 확인
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # 파일 포인터를 처음으로 되돌림
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f'파일 크기가 너무 큽니다. 최대 {max_size_mb:.0f}MB까지 업로드 가능합니다.'
    
    return True, None


def validate_video_file(file):
    """
    비디오 파일 검증 (확장자, 크기)
    
    Args:
        file: 업로드된 파일 객체
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file or not file.filename:
        return False, '비디오 파일이 필요합니다.'
    
    # 확장자 검증
    if not allowed_file(file.filename, Config.ALLOWED_VIDEO_EXTENSIONS):
        return False, '지원하지 않는 비디오 형식입니다. (mp4, avi, mov, mkv, webm만 가능)'
    
    # 파일 크기 검증
    is_valid, error = validate_file_size(file, Config.MAX_VIDEO_SIZE)
    if not is_valid:
        return False, error
    
    return True, None


def validate_image_file(file):
    """
    이미지 파일 검증 (확장자, 크기, 실제 이미지 여부)
    
    Args:
        file: 업로드된 파일 객체
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file or not file.filename:
        return True, None  # 선택사항이므로 None 반환
    
    # 확장자 검증
    if not allowed_file(file.filename, Config.ALLOWED_IMAGE_EXTENSIONS):
        return False, '지원하지 않는 이미지 형식입니다. (jpg, jpeg, png, gif, webp만 가능)'
    
    # 파일 크기 검증
    is_valid, error = validate_file_size(file, Config.MAX_IMAGE_SIZE)
    if not is_valid:
        return False, error
    
    # 실제 이미지 파일인지 확인 (Pillow 사용)
    try:
        from PIL import Image
        file.seek(0)
        img = Image.open(file)
        img.verify()  # 이미지 파일 검증
        file.seek(0)  # 파일 포인터를 처음으로 되돌림
    except Exception:
        return False, '유효하지 않은 이미지 파일입니다.'
    
    return True, None


def process_tags(tag_string):
    """
    태그 문자열을 처리하여 Tag 객체 리스트 반환
    
    Args:
        tag_string: 쉼표로 구분된 태그 문자열 (예: "태그1, 태그2, 태그3")
    
    Returns:
        Tag 객체 리스트
    """
    if not tag_string or not tag_string.strip():
        return []
    
    # 쉼표로 분리하고 공백 제거, 중복 제거
    tag_names = [tag.strip() for tag in tag_string.split(',') if tag.strip()]
    tag_names = list(set(tag_names))  # 중복 제거
    
    tags = []
    for tag_name in tag_names:
        # 태그 이름 길이 제한 (50자)
        if len(tag_name) > 50:
            continue
        
        # 기존 태그가 있으면 가져오고, 없으면 생성
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        tags.append(tag)
    
    return tags


def delete_file_safely(file_path):
    """
    파일을 안전하게 삭제하는 헬퍼 함수
    
    Args:
        file_path: 삭제할 파일의 전체 경로
    
    Returns:
        bool: 삭제 성공 시 True, 실패 시 False
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f'파일 삭제 오류: {str(e)}')
    return False


def get_studio_stats(user_id):
    """
    스튜디오 통계 데이터 수집
    
    Args:
        user_id: 사용자 ID
    
    Returns:
        dict: 통계 데이터 딕셔너리
    """
    # 전체 통계
    total_videos = Video.query.filter_by(user_id=user_id).count()
    total_views = db.session.query(func.sum(Video.views))\
        .filter_by(user_id=user_id).scalar() or 0
    total_likes = db.session.query(func.sum(Video.likes))\
        .filter_by(user_id=user_id).scalar() or 0
    
    # 댓글 수 (사용자의 비디오에 달린 댓글)
    total_comments = db.session.query(func.count(Comment.id))\
        .join(Video)\
        .filter(Video.user_id == user_id).scalar() or 0
    
    # 최근 7일 통계
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_videos_7d = Video.query.filter(
        and_(
            Video.user_id == user_id,
            Video.created_at >= seven_days_ago
        )
    ).count()
    
    recent_views_7d = db.session.query(func.sum(Video.views))\
        .filter(
            and_(
                Video.user_id == user_id,
                Video.created_at >= seven_days_ago
            )
        ).scalar() or 0
    
    recent_likes_7d = db.session.query(func.sum(Video.likes))\
        .filter(
            and_(
                Video.user_id == user_id,
                Video.created_at >= seven_days_ago
            )
        ).scalar() or 0
    
    # 최근 30일 통계
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_videos_30d = Video.query.filter(
        and_(
            Video.user_id == user_id,
            Video.created_at >= thirty_days_ago
        )
    ).count()
    
    recent_views_30d = db.session.query(func.sum(Video.views))\
        .filter(
            and_(
                Video.user_id == user_id,
                Video.created_at >= thirty_days_ago
            )
        ).scalar() or 0
    
    recent_likes_30d = db.session.query(func.sum(Video.likes))\
        .filter(
            and_(
                Video.user_id == user_id,
                Video.created_at >= thirty_days_ago
            )
        ).scalar() or 0
    
    # 평균 조회수 (비디오당)
    avg_views = total_views / total_videos if total_videos > 0 else 0
    
    # 평균 좋아요 (비디오당)
    avg_likes = total_likes / total_videos if total_videos > 0 else 0
    
    return {
        'total': {
            'videos': total_videos,
            'views': total_views,
            'likes': total_likes,
            'comments': total_comments,
            'avg_views': round(avg_views, 1),
            'avg_likes': round(avg_likes, 1)
        },
        'recent_7d': {
            'videos': recent_videos_7d,
            'views': recent_views_7d,
            'likes': recent_likes_7d
        },
        'recent_30d': {
            'videos': recent_videos_30d,
            'views': recent_views_30d,
            'likes': recent_likes_30d
        }
    }


@studio_bp.route('/')
@login_required
def index():
    """
    스튜디오 메인 페이지
    사용자가 업로드한 비디오 목록과 통계를 표시합니다.
    
    Returns:
        HTML 템플릿 렌더링
    """
    # 스튜디오에서는 태그는 필요할 때만 로드 (dynamic relationship)
    videos = Video.query.filter_by(user_id=current_user.id)\
        .order_by(Video.created_at.desc()).all()
    
    # 통계 데이터 수집
    stats = get_studio_stats(current_user.id)
    
    # 인기 비디오 TOP 5 (조회수 기준)
    popular_videos = Video.query.filter_by(user_id=current_user.id)\
        .order_by(Video.views.desc())\
        .limit(5).all()
    
    return render_template(
        'studio/index.html', 
        videos=videos,
        stats=stats,
        popular_videos=popular_videos
    )


@studio_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    비디오 업로드 페이지
    
    Returns:
        GET: 업로드 폼 렌더링
        POST: 비디오 업로드 처리
    """
    if request.method == 'POST':
        # 폼 데이터 가져오기 및 정제
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        tags_string = request.form.get('tags', '').strip()
        video_file = request.files.get('video')
        thumbnail_file = request.files.get('thumbnail')
        
        # 제목 검증
        is_valid, error = validate_video_title(title)
        if not is_valid:
            flash(error, 'error')
            return render_template('studio/upload.html', config=Config)
        
        # 설명 정제 (HTML 태그 제거, 최대 5000자)
        description = sanitize_text(description, max_length=5000)
        
        # 비디오 파일 검증
        is_valid, error = validate_video_file(video_file)
        if not is_valid:
            flash(error, 'error')
            return render_template('studio/upload.html', config=Config)
        
        # 파일 검증 후 파일 포인터를 처음으로 되돌림 (Cloudinary 업로드를 위해)
        video_file.seek(0)
        if thumbnail_file and thumbnail_file.filename:
            thumbnail_file.seek(0)
        
        # 파일 저장
        try:
            # Cloudinary 사용 여부 확인 (app/__init__.py에서 설정됨)
            use_cloudinary = current_app.config.get('USE_CLOUDINARY', False)
            
            # 상세 로그 출력
            current_app.logger.info("=" * 60)
            current_app.logger.info("[INFO] 미디어 저장소 설정 확인")
            current_app.logger.info(f"[INFO] 저장소 타입: {'Cloudinary' if use_cloudinary else '로컬 저장소'}")
            current_app.logger.info(f"[DEBUG] USE_CLOUDINARY: {use_cloudinary}")
            
            # Cloudinary 사용 시 필요한 패키지 확인
            if use_cloudinary:
                try:
                    import cloudinary
                except ImportError:
                    current_app.logger.error("[ERROR] cloudinary 패키지가 설치되지 않았습니다. 로컬 저장소로 자동 전환됩니다.")
                    use_cloudinary = False
            current_app.logger.info("=" * 60)
            
            # 데이터베이스에 먼저 저장 (video.id를 얻기 위해)
            video = Video(
                title=title,
                description=description,
                category=category if category and category in Config.VIDEO_CATEGORIES else None,
                video_path='',  # 임시로 빈 값, 나중에 업데이트
                user_id=current_user.id
            )
            
            db.session.add(video)
            db.session.flush()  # video.id를 얻기 위해 flush
            
            # 비디오 파일 저장
            if use_cloudinary:
                # ============================================================
                # Cloudinary 저장소 사용
                # ============================================================
                from app.utils.cloudinary_utils import upload_video, upload_thumbnail
                
                current_app.logger.info(f"[DEBUG] Cloudinary에 비디오 업로드 시작: video_id={video.id}")
                try:
                    # 비디오 업로드
                    video_result = upload_video(video_file, video.id)
                    video.video_path = video_result['url']
                    video.video_public_id = video_result['public_id']
                    current_app.logger.info(f"[DEBUG] Cloudinary 비디오 업로드 성공: {video_result['url']}")
                except Exception as e:
                    current_app.logger.error(f"[ERROR] Cloudinary 비디오 업로드 실패: {str(e)}")
                    flash(f'비디오 업로드 실패: {str(e)}', 'error')
                    db.session.rollback()
                    return render_template('studio/upload.html', config=Config)
                
                # 썸네일 업로드 (있는 경우)
                if thumbnail_file and thumbnail_file.filename:
                    is_valid, error = validate_image_file(thumbnail_file)
                    if is_valid:
                        try:
                            current_app.logger.info(f"[DEBUG] Cloudinary에 썸네일 업로드 시작: video_id={video.id}")
                            thumbnail_result = upload_thumbnail(thumbnail_file, video.id)
                            video.thumbnail_path = thumbnail_result['url']
                            video.thumbnail_public_id = thumbnail_result['public_id']
                            current_app.logger.info(f"[DEBUG] Cloudinary 썸네일 업로드 성공: {thumbnail_result['url']}")
                        except Exception as e:
                            current_app.logger.error(f"[ERROR] Cloudinary 썸네일 업로드 실패: {str(e)}")
                            flash(f'썸네일 업로드 실패: {str(e)}', 'warning')
                    else:
                        flash(f'썸네일 이미지 오류: {error}', 'warning')
            else:
                # ============================================================
                # 로컬 저장소 사용
                # ============================================================
                current_app.logger.info("[INFO] 로컬 파일 시스템에 저장 시작")
                current_app.logger.info(f"[INFO] 저장 위치: {Config.VIDEO_FOLDER}")
                
                video_filename = secure_filename(video_file.filename)
                video_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video_filename}"
                video_full_path = os.path.join(Config.VIDEO_FOLDER, video_filename)
                video_file.save(video_full_path)
                
                # 데이터베이스에는 파일명만 저장 (상대 경로)
                video.video_path = video_filename
                
                # 썸네일 파일 저장 (선택사항)
                if thumbnail_file and thumbnail_file.filename:
                    is_valid, error = validate_image_file(thumbnail_file)
                    if is_valid:
                        current_app.logger.info(f"[INFO] 로컬 저장소에 썸네일 저장: video_id={video.id}")
                        thumbnail_filename = secure_filename(thumbnail_file.filename)
                        thumbnail_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{thumbnail_filename}"
                        thumbnail_full_path = os.path.join(Config.THUMBNAIL_FOLDER, thumbnail_filename)
                        thumbnail_file.save(thumbnail_full_path)
                        video.thumbnail_path = thumbnail_filename
                    else:
                        flash(f'썸네일 이미지 오류: {error}', 'warning')
            
            # 태그 처리
            tags = process_tags(tags_string)
            video.tags = tags
            
            db.session.commit()
            
            flash('비디오가 업로드되었습니다.', 'success')
            return redirect(url_for('studio.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'업로드 중 오류가 발생했습니다: {str(e)}', 'error')
            return render_template('studio/upload.html', config=Config)
    
    return render_template('studio/upload.html', config=Config)


@studio_bp.route('/edit/<int:video_id>', methods=['GET', 'POST'])
@login_required
def edit(video_id):
    """
    비디오 수정 페이지
    
    Args:
        video_id: 비디오 ID
    
    Returns:
        GET: 수정 폼 렌더링
        POST: 비디오 수정 처리
    """
    video = Video.query.get_or_404(video_id)
    
    # 권한 확인 (작성자만 수정 가능)
    if video.user_id != current_user.id:
        flash('이 비디오를 수정할 권한이 없습니다.', 'error')
        return redirect(url_for('studio.index'))
    
    if request.method == 'POST':
        # 폼 데이터 가져오기
        title = request.form.get('title')
        description = request.form.get('description', '')
        category = request.form.get('category', '')
        tags_string = request.form.get('tags', '')
        video_file = request.files.get('video')
        thumbnail_file = request.files.get('thumbnail')
        delete_thumbnail = request.form.get('delete_thumbnail') == 'on'
        
        # 제목 검증 및 정제
        title = request.form.get('title', '').strip()
        is_valid, error = validate_video_title(title)
        if not is_valid:
            flash(error, 'error')
            return render_template('studio/edit.html', video=video, config=Config)
        
        # 설명 정제 (HTML 태그 제거, 최대 5000자)
        description = request.form.get('description', '').strip()
        description = sanitize_text(description, max_length=5000)
        
        # 비디오 파일이 업로드된 경우 검증
        if video_file and video_file.filename:
            is_valid, error = validate_video_file(video_file)
            if not is_valid:
                flash(error, 'error')
                return render_template('studio/edit.html', video=video, config=Config)
        
        try:
            # 제목, 설명, 카테고리 업데이트
            video.title = title
            video.description = description
            
            # 카테고리 검증 및 업데이트
            if category and category in Config.VIDEO_CATEGORIES:
                video.category = category
            else:
                video.category = None
            
            # 태그 업데이트
            tags = process_tags(tags_string)
            video.tags = tags
            
            # Cloudinary 사용 여부 확인
            use_cloudinary = current_app.config.get('USE_CLOUDINARY', False)
            
            # 비디오 파일 교체 (새 파일이 업로드된 경우)
            if video_file and video_file.filename:
                if use_cloudinary:
                    # Cloudinary에서 기존 파일 삭제
                    from app.utils.cloudinary_utils import delete_file
                    if video.video_public_id:
                        delete_file(video.video_public_id, resource_type='video')
                    
                    # 새 비디오 업로드
                    from app.utils.cloudinary_utils import upload_video
                    video_result = upload_video(video_file, video.id)
                    video.video_path = video_result['url']
                    video.video_public_id = video_result['public_id']
                else:
                    # 로컬 파일 시스템에서 기존 파일 삭제
                    old_video_path = os.path.join(Config.VIDEO_FOLDER, video.video_path)
                    delete_file_safely(old_video_path)
                    
                    # 새 비디오 파일 저장
                    video_filename = secure_filename(video_file.filename)
                    video_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video_filename}"
                    video_full_path = os.path.join(Config.VIDEO_FOLDER, video_filename)
                    video_file.save(video_full_path)
                    video.video_path = video_filename
            
            # 썸네일 처리
            if delete_thumbnail:
                if use_cloudinary:
                    # Cloudinary에서 기존 썸네일 삭제
                    from app.utils.cloudinary_utils import delete_file
                    if video.thumbnail_public_id:
                        delete_file(video.thumbnail_public_id, resource_type='image')
                    video.thumbnail_path = None
                    video.thumbnail_public_id = None
                else:
                    # 로컬 파일 시스템에서 기존 썸네일 삭제
                    if video.thumbnail_path:
                        old_thumbnail_path = os.path.join(Config.THUMBNAIL_FOLDER, video.thumbnail_path)
                        delete_file_safely(old_thumbnail_path)
                        video.thumbnail_path = None
            
            # 새 썸네일 업로드 (선택사항)
            if thumbnail_file and thumbnail_file.filename:
                is_valid, error = validate_image_file(thumbnail_file)
                if is_valid:
                    if use_cloudinary:
                        # Cloudinary에서 기존 썸네일 삭제
                        from app.utils.cloudinary_utils import delete_file, upload_thumbnail
                        if video.thumbnail_public_id:
                            delete_file(video.thumbnail_public_id, resource_type='image')
                        
                        # 새 썸네일 업로드
                        thumbnail_result = upload_thumbnail(thumbnail_file, video.id)
                        video.thumbnail_path = thumbnail_result['url']
                        video.thumbnail_public_id = thumbnail_result['public_id']
                    else:
                        # 로컬 파일 시스템에서 기존 썸네일 삭제
                        if video.thumbnail_path:
                            old_thumbnail_path = os.path.join(Config.THUMBNAIL_FOLDER, video.thumbnail_path)
                            delete_file_safely(old_thumbnail_path)
                        
                        # 새 썸네일 저장
                        thumbnail_filename = secure_filename(thumbnail_file.filename)
                        thumbnail_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{thumbnail_filename}"
                        thumbnail_full_path = os.path.join(Config.THUMBNAIL_FOLDER, thumbnail_filename)
                        thumbnail_file.save(thumbnail_full_path)
                        video.thumbnail_path = thumbnail_filename
                else:
                    flash(f'썸네일 이미지 오류: {error}', 'warning')
            
            db.session.commit()
            flash('비디오가 수정되었습니다.', 'success')
            return redirect(url_for('studio.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'수정 중 오류가 발생했습니다: {str(e)}', 'error')
            return render_template('studio/edit.html', video=video, config=Config)
    
    return render_template('studio/edit.html', video=video, config=Config)


@studio_bp.route('/delete/<int:video_id>', methods=['POST'])
@login_required
def delete(video_id):
    """
    비디오 삭제
    
    Args:
        video_id: 비디오 ID
    
    Returns:
        리다이렉트
    """
    video = Video.query.get_or_404(video_id)
    
    # 권한 확인 (작성자만 삭제 가능)
    if video.user_id != current_user.id:
        flash('이 비디오를 삭제할 권한이 없습니다.', 'error')
        return redirect(url_for('studio.index'))
    
    try:
        # Cloudinary 사용 여부 확인
        use_cloudinary = current_app.config.get('USE_CLOUDINARY', False)
        
        if use_cloudinary:
            # Cloudinary에서 파일 삭제
            from app.utils.cloudinary_utils import delete_file
            
            # 비디오 파일 삭제
            if video.video_public_id:
                delete_file(video.video_public_id, resource_type='video')
            
            # 썸네일 파일 삭제
            if video.thumbnail_public_id:
                delete_file(video.thumbnail_public_id, resource_type='image')
        else:
            # 로컬 파일 시스템에서 파일 삭제
            # 비디오 파일 삭제
            if video.video_path:
                video_file_path = os.path.join(Config.VIDEO_FOLDER, video.video_path)
                delete_file_safely(video_file_path)
            
            # 썸네일 파일 삭제
            if video.thumbnail_path:
                thumbnail_file_path = os.path.join(Config.THUMBNAIL_FOLDER, video.thumbnail_path)
                delete_file_safely(thumbnail_file_path)
        
        # 데이터베이스에서 삭제 (댓글은 cascade로 자동 삭제됨)
        db.session.delete(video)
        db.session.commit()
        
        flash('비디오가 삭제되었습니다.', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('studio.index'))


@studio_bp.route('/api/stats')
@login_required
def api_stats():
    """
    스튜디오 통계 API
    JSON 형식으로 통계 데이터를 반환합니다.
    
    Returns:
        JSON 응답
    """
    try:
        stats = get_studio_stats(current_user.id)
        
        # 일별 통계 (최근 30일)
        # SQLite 호환성을 위해 Python에서 날짜 추출
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_videos = Video.query.filter(
            and_(
                Video.user_id == current_user.id,
                Video.created_at >= thirty_days_ago
            )
        ).all()
        
        # 일별로 그룹화
        daily_dict = {}
        for video in recent_videos:
            date_key = video.created_at.date().isoformat()
            if date_key not in daily_dict:
                daily_dict[date_key] = {
                    'date': date_key,
                    'video_count': 0,
                    'views': 0,
                    'likes': 0
                }
            daily_dict[date_key]['video_count'] += 1
            daily_dict[date_key]['views'] += video.views or 0
            daily_dict[date_key]['likes'] += video.likes or 0
        
        # 날짜순으로 정렬
        daily_data = sorted(daily_dict.values(), key=lambda x: x['date'], reverse=True)
        
        stats['daily'] = daily_data
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


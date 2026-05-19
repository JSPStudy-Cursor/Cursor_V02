"""
데이터베이스 관리 라우트
SQLite 데이터베이스를 웹에서 조회하고 관리할 수 있는 기능을 제공합니다.
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Video, Comment
from sqlalchemy import text, inspect, func
import json
from datetime import datetime

admin_bp = Blueprint('admin', __name__)


def is_admin():
    """
    현재 사용자가 관리자인지 확인
    
    Returns:
        bool: 관리자이면 True
    """
    return current_user.is_authenticated and current_user.is_admin


@admin_bp.route('/')
@login_required
def index():
    """
    관리자 대시보드 메인 페이지
    통계 정보와 관리 메뉴를 표시합니다.
    
    Returns:
        HTML 템플릿 렌더링
    """
    if not is_admin():
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # 모델별 통계
        user_count = User.query.count()
        video_count = Video.query.count()
        comment_count = Comment.query.count()
        
        return render_template('admin/index.html', 
                             user_count=user_count,
                             video_count=video_count,
                             comment_count=comment_count)
    except Exception as e:
        flash(f'통계 조회 중 오류가 발생했습니다: {str(e)}', 'error')
        return render_template('admin/index.html', 
                             user_count=0,
                             video_count=0,
                             comment_count=0)


@admin_bp.route('/database')
@login_required
def database():
    """
    데이터베이스 관리 페이지
    테이블 목록과 기본 통계를 표시합니다.
    
    Returns:
        HTML 템플릿 렌더링
    """
    if not is_admin():
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # 테이블 목록 가져오기
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        # 각 테이블의 레코드 수 계산
        table_stats = {}
        for table in tables:
            try:
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                table_stats[table] = count
            except Exception as e:
                table_stats[table] = f"오류: {str(e)}"
        
        # 모델별 통계
        user_count = User.query.count()
        video_count = Video.query.count()
        comment_count = Comment.query.count()
        
        return render_template('admin/database.html', 
                             tables=tables,
                             table_stats=table_stats,
                             user_count=user_count,
                             video_count=video_count,
                             comment_count=comment_count)
    except Exception as e:
        flash(f'데이터베이스 조회 중 오류가 발생했습니다: {str(e)}', 'error')
        return render_template('admin/database.html', 
                             tables=[],
                             table_stats={},
                             user_count=0,
                             video_count=0,
                             comment_count=0)


@admin_bp.route('/table/<table_name>')
@login_required
def view_table(table_name):
    """
    특정 테이블의 데이터를 조회합니다.
    
    Args:
        table_name: 조회할 테이블명
    
    Returns:
        HTML 템플릿 렌더링 또는 JSON 응답
    """
    if not is_admin():
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # 페이지네이션
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # 테이블 존재 확인
        inspector = inspect(db.engine)
        if table_name not in inspector.get_table_names():
            flash(f'테이블 "{table_name}"을 찾을 수 없습니다.', 'error')
            return redirect(url_for('admin.index'))
        
        # 테이블 구조 가져오기
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        # 전체 레코드 수
        count_result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        total_count = count_result.scalar()
        
        # 페이지네이션 계산
        offset = (page - 1) * per_page
        
        # 데이터 조회
        query = text(f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {offset}")
        result = db.session.execute(query)
        rows = result.fetchall()
        
        # 딕셔너리 형태로 변환
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # datetime 객체를 문자열로 변환
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                row_dict[col] = value
            data.append(row_dict)
        
        # 페이지네이션 정보
        total_pages = (total_count + per_page - 1) // per_page
        
        return render_template('admin/table_view.html',
                             table_name=table_name,
                             columns=columns,
                             data=data,
                             page=page,
                             per_page=per_page,
                             total_count=total_count,
                             total_pages=total_pages)
    
    except Exception as e:
        flash(f'테이블 조회 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin.index'))


@admin_bp.route('/query', methods=['GET', 'POST'])
@login_required
def execute_query():
    """
    SQL 쿼리를 실행합니다.
    (보안을 위해 SELECT 쿼리만 허용)
    
    Returns:
        HTML 템플릿 렌더링 또는 JSON 응답
    """
    if not is_admin():
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            sql_query = request.form.get('sql_query', '').strip()
            
            if not sql_query:
                flash('SQL 쿼리를 입력해주세요.', 'error')
                return render_template('admin/query.html')
            
            # 보안: SELECT 쿼리만 허용 (대소문자 구분 없이)
            sql_upper = sql_query.upper().strip()
            if not sql_upper.startswith('SELECT'):
                flash('보안을 위해 SELECT 쿼리만 실행할 수 있습니다.', 'error')
                return render_template('admin/query.html')
            
            # 쿼리 실행
            result = db.session.execute(text(sql_query))
            
            # 결과 가져오기
            if result.returns_rows:
                rows = result.fetchall()
                columns = result.keys() if hasattr(result, 'keys') else []
                
                # 딕셔너리 형태로 변환
                data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # datetime 객체를 문자열로 변환
                        if isinstance(value, datetime):
                            value = value.strftime('%Y-%m-%d %H:%M:%S')
                        row_dict[col] = value
                    data.append(row_dict)
                
                return render_template('admin/query.html',
                                     sql_query=sql_query,
                                     columns=columns,
                                     data=data,
                                     row_count=len(data))
            else:
                flash('쿼리가 성공적으로 실행되었습니다.', 'success')
                return render_template('admin/query.html', sql_query=sql_query)
        
        except Exception as e:
            flash(f'쿼리 실행 중 오류가 발생했습니다: {str(e)}', 'error')
            return render_template('admin/query.html', sql_query=sql_query)
    
    return render_template('admin/query.html')


@admin_bp.route('/api/stats')
@login_required
def api_stats():
    """
    데이터베이스 통계 정보를 JSON으로 반환합니다.
    
    Returns:
        JSON 응답
    """
    if not is_admin():
        return jsonify({'error': '접근 권한이 없습니다.'}), 403
    
    try:
        stats = {
            'users': User.query.count(),
            'videos': Video.query.count(),
            'comments': Comment.query.count(),
            'total_views': db.session.query(func.sum(Video.views)).scalar() or 0,
            'total_likes': db.session.query(func.sum(Video.likes)).scalar() or 0,
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users')
@login_required
def manage_users():
    """
    회원관리 페이지
    회원 검색 및 목록 표시
    
    Returns:
        HTML 템플릿 렌더링
    """
    if not is_admin():
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    # 검색 쿼리
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 사용자 목록 조회
    query = User.query
    
    # 검색 기능
    if search_query:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%'),
                User.nickname.ilike(f'%{search_query}%')
            )
        )
    
    # 최신순 정렬
    query = query.order_by(User.created_at.desc())
    
    # 페이지네이션
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return render_template('admin/users.html', 
                         users=users,
                         pagination=pagination,
                         search_query=search_query)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """
    회원 탈퇴 처리
    
    Args:
        user_id: 삭제할 사용자 ID
    
    Returns:
        리다이렉트 응답
    """
    if not is_admin():
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    # 자기 자신은 삭제할 수 없음
    if user_id == current_user.id:
        flash('자기 자신은 삭제할 수 없습니다.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        user = User.query.get_or_404(user_id)
        
        # 관리자는 삭제할 수 없음
        if user.is_admin:
            flash('관리자 계정은 삭제할 수 없습니다.', 'error')
            return redirect(url_for('admin.manage_users'))
        
        # 사용자 삭제 (cascade로 관련 데이터도 함께 삭제됨)
        db.session.delete(user)
        db.session.commit()
        
        flash(f'회원 "{user.username}"이(가) 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'회원 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/videos')
@login_required
def manage_videos():
    """
    비디오 관리 페이지
    비디오 검색 및 목록 표시
    
    Returns:
        HTML 템플릿 렌더링
    """
    if not is_admin():
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    # 검색 쿼리
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 비디오 목록 조회
    query = Video.query
    
    # 검색 기능
    if search_query:
        query = query.filter(
            db.or_(
                Video.title.ilike(f'%{search_query}%'),
                Video.description.ilike(f'%{search_query}%'),
                User.username.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%')
            )
        )
    
    # 작성자 정보 join
    query = query.join(User)
    
    # 최신순 정렬
    query = query.order_by(Video.created_at.desc())
    
    # 페이지네이션
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    videos = pagination.items
    
    return render_template('admin/videos.html', 
                         videos=videos,
                         pagination=pagination,
                         search_query=search_query)


@admin_bp.route('/videos/<int:video_id>/delete', methods=['POST'])
@login_required
def delete_video(video_id):
    """
    비디오 삭제 처리
    
    Args:
        video_id: 삭제할 비디오 ID
    
    Returns:
        리다이렉트 응답
    """
    if not is_admin():
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        video = Video.query.get_or_404(video_id)
        video_title = video.title
        
        # Cloudinary 파일 삭제
        use_cloudinary = current_app.config.get('USE_CLOUDINARY', False)
        if use_cloudinary:
            try:
                from app.utils.cloudinary_utils import delete_file
                
                # 비디오 파일 삭제
                if video.video_public_id:
                    delete_file(video.video_public_id, resource_type='video')
                
                # 썸네일 파일 삭제
                if video.thumbnail_public_id:
                    delete_file(video.thumbnail_public_id, resource_type='image')
            except Exception as e:
                current_app.logger.error(f'Cloudinary 파일 삭제 오류: {str(e)}')
        else:
            # 로컬 파일 삭제
            from config import Config
            import os
            
            # 비디오 파일 삭제
            if video.video_path:
                video_file_path = os.path.join(Config.VIDEO_FOLDER, video.video_path)
                if os.path.exists(video_file_path):
                    try:
                        os.remove(video_file_path)
                    except Exception as e:
                        current_app.logger.error(f'비디오 파일 삭제 오류: {str(e)}')
            
            # 썸네일 파일 삭제
            if video.thumbnail_path:
                thumbnail_file_path = os.path.join(Config.THUMBNAIL_FOLDER, video.thumbnail_path)
                if os.path.exists(thumbnail_file_path):
                    try:
                        os.remove(thumbnail_file_path)
                    except Exception as e:
                        current_app.logger.error(f'썸네일 파일 삭제 오류: {str(e)}')
        
        # 데이터베이스에서 비디오 삭제 (cascade로 관련 댓글, 태그도 함께 삭제됨)
        db.session.delete(video)
        db.session.commit()
        
        flash(f'비디오 "{video_title}"이(가) 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'비디오 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_videos'))


@admin_bp.route('/comments')
@login_required
def manage_comments():
    """
    댓글 관리 페이지
    댓글 검색 및 목록 표시
    
    Returns:
        HTML 템플릿 렌더링
    """
    if not is_admin():
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    # 검색 쿼리
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 댓글 목록 조회
    query = Comment.query
    
    # 검색 기능
    if search_query:
        query = query.filter(
            db.or_(
                Comment.content.ilike(f'%{search_query}%'),
                User.username.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%'),
                Video.title.ilike(f'%{search_query}%')
            )
        )
    
    # 작성자 및 비디오 정보 join
    query = query.join(User).join(Video)
    
    # 최신순 정렬
    query = query.order_by(Comment.created_at.desc())
    
    # 페이지네이션
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    comments = pagination.items
    
    return render_template('admin/comments.html', 
                         comments=comments,
                         pagination=pagination,
                         search_query=search_query)


@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """
    댓글 삭제 처리
    
    Args:
        comment_id: 삭제할 댓글 ID
    
    Returns:
        리다이렉트 응답
    """
    if not is_admin():
        flash('접근 권한이 없습니다.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        comment = Comment.query.get_or_404(comment_id)
        comment_content = comment.content[:50] + '...' if len(comment.content) > 50 else comment.content
        
        # 대댓글이 있는 경우, 대댓글도 함께 삭제됨 (cascade)
        # 데이터베이스에서 댓글 삭제
        db.session.delete(comment)
        db.session.commit()
        
        flash(f'댓글이 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'댓글 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_comments'))


"""
메인 페이지 라우트
홈 화면 및 비디오 목록을 처리합니다.
"""
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
from app import db
from app.models import Video, Comment, User, Tag, video_tags
from config import Config

main_bp = Blueprint('main', __name__)


def get_related_videos(video, limit=10):
    """
    관련 동영상 추천
    
    우선순위:
    1. 같은 태그를 가진 비디오
    2. 같은 카테고리를 가진 비디오
    3. 같은 작성자의 다른 비디오
    4. 인기 비디오 (fallback)
    
    Args:
        video: 현재 비디오 객체
        limit: 추천할 비디오 개수 (기본값: 10)
    
    Returns:
        Video 객체 리스트
    """
    related = []
    video_ids_to_exclude = {video.id}  # 현재 비디오 제외
    
    # 1. 같은 태그를 가진 비디오 (우선순위 1)
    if video.tags.count() > 0:
        tag_ids = [tag.id for tag in video.tags.all()]
        tag_videos = Video.query.join(Video.tags)\
            .filter(Tag.id.in_(tag_ids))\
            .filter(Video.id != video.id)\
            .filter(~Video.id.in_(video_ids_to_exclude))\
            .order_by(Video.views.desc())\
            .limit(limit)\
            .all()
        
        for v in tag_videos:
            if v.id not in video_ids_to_exclude:
                related.append(v)
                video_ids_to_exclude.add(v.id)
                if len(related) >= limit:
                    return related
    
    # 2. 같은 카테고리를 가진 비디오 (우선순위 2, N+1 쿼리 방지를 위해 eager loading)
    if video.category and len(related) < limit:
        category_videos = Video.query.options(
            joinedload(Video.author)
        ).filter_by(category=video.category)\
            .filter(Video.id != video.id)\
            .filter(~Video.id.in_(video_ids_to_exclude))\
            .order_by(Video.views.desc())\
            .limit(limit - len(related))\
            .all()
        
        for v in category_videos:
            if v.id not in video_ids_to_exclude:
                related.append(v)
                video_ids_to_exclude.add(v.id)
                if len(related) >= limit:
                    return related
    
    # 3. 같은 작성자의 다른 비디오 (우선순위 3, N+1 쿼리 방지를 위해 eager loading)
    if len(related) < limit:
        author_videos = Video.query.options(
            joinedload(Video.author)
        ).filter_by(user_id=video.user_id)\
            .filter(Video.id != video.id)\
            .filter(~Video.id.in_(video_ids_to_exclude))\
            .order_by(Video.created_at.desc())\
            .limit(limit - len(related))\
            .all()
        
        for v in author_videos:
            if v.id not in video_ids_to_exclude:
                related.append(v)
                video_ids_to_exclude.add(v.id)
                if len(related) >= limit:
                    return related
    
    # 4. 인기 비디오 (fallback, N+1 쿼리 방지를 위해 eager loading) - 태그, 카테고리, 작성자 모두 없을 때만
    if len(related) == 0:
        popular_videos = Video.query.options(
            joinedload(Video.author)
        ).filter(Video.id != video.id)\
            .filter(~Video.id.in_(video_ids_to_exclude))\
            .order_by(Video.views.desc())\
            .limit(limit)\
            .all()
        
        for v in popular_videos:
            if v.id not in video_ids_to_exclude:
                related.append(v)
                video_ids_to_exclude.add(v.id)
                if len(related) >= limit:
                    return related
    
    return related


@main_bp.route('/')
def index():
    """
    메인 페이지 (홈 화면)
    정렬 옵션에 따라 비디오 목록을 표시합니다.
    
    정렬 옵션:
    - latest: 최신순 (기본값)
    - popular: 인기순 (좋아요 수 기준)
    - views: 조회수순
    
    Returns:
        HTML 템플릿 렌더링
    """
    # 페이지네이션을 위한 페이지 번호 가져오기
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'latest', type=str)
    category = request.args.get('category', '', type=str)
    
    # 쿼리 생성
    query = Video.query
    
    # 카테고리 필터 적용
    if category and category in Config.VIDEO_CATEGORIES:
        query = query.filter_by(category=category)
    
    # 정렬 옵션에 따라 쿼리 생성
    if sort_by == 'popular':
        # 인기순: 좋아요 수 기준 (내림차순)
        order_by = Video.likes.desc()
        sort_label = '인기 동영상'
    elif sort_by == 'views':
        # 조회수순: 조회수 기준 (내림차순)
        order_by = Video.views.desc()
        sort_label = '조회수 많은 동영상'
    else:
        # 최신순: 생성일 기준 (내림차순) - 기본값
        order_by = Video.created_at.desc()
        sort_label = '최신 동영상'
    
    # 카테고리 라벨 추가
    if category and category in Config.VIDEO_CATEGORIES:
        sort_label = f'{Config.VIDEO_CATEGORIES[category]} - {sort_label}'
    
    # 비디오 목록 조회 (N+1 쿼리 방지를 위해 eager loading)
    # author만 eager loading, tags는 dynamic이므로 별도 처리
    videos = query.options(
        joinedload(Video.author)
    ).order_by(order_by).paginate(
        page=page,
        per_page=Config.VIDEOS_PER_PAGE,
        error_out=False
    )
    
    # 인기 태그 조회 (비디오가 1개 이상인 태그만, 최대 10개)
    popular_tags = db.session.query(Tag)\
        .join(video_tags)\
        .join(Video)\
        .group_by(Tag.id)\
        .having(func.count(Video.id) > 0)\
        .order_by(func.count(Video.id).desc())\
        .limit(10)\
        .all()
    
    return render_template(
        'main/index.html', 
        videos=videos, 
        sort_by=sort_by, 
        sort_label=sort_label,
        current_category=category,
        popular_tags=popular_tags,
        config=Config
    )


@main_bp.route('/watch/<int:video_id>')
def watch(video_id):
    """
    비디오 시청 페이지
    
    Args:
        video_id: 비디오 ID
    
    Returns:
        HTML 템플릿 렌더링
    """
    # N+1 쿼리 방지를 위해 eager loading
    # author만 eager loading, tags는 dynamic이므로 별도 처리
    video = Video.query.options(
        joinedload(Video.author)
    ).get_or_404(video_id)
    
    # 조회수 증가
    video.views += 1
    db.session.commit()
    
    # 댓글 목록 조회 (최신순, N+1 쿼리 방지를 위해 eager loading)
    # 부모 댓글만 조회 (parent_id가 None인 댓글)
    comments = Comment.query.options(
        joinedload(Comment.author)
    ).filter_by(video_id=video_id, parent_id=None)\
        .order_by(Comment.created_at.desc()).all()
    
    # 각 댓글의 대댓글도 함께 로드 (N+1 쿼리 방지)
    for comment in comments:
        # 대댓글을 작성자 정보와 함께 로드
        comment._replies = Comment.query.options(
            joinedload(Comment.author)
        ).filter_by(parent_id=comment.id)\
            .order_by(Comment.created_at.asc()).all()
    
    # 좋아요 상태 확인 (로그인한 사용자만)
    is_liked = False
    if current_user.is_authenticated:
        is_liked = video.is_liked_by(current_user)
    
    # 구독 상태 확인 (로그인한 사용자만, 자기 자신 제외)
    is_subscribed = False
    if current_user.is_authenticated and current_user.id != video.author.id:
        is_subscribed = current_user.is_subscribed_to(video.author)
    
    # 관련 동영상 추천 (최대 10개)
    related_videos = get_related_videos(video, limit=10)
    
    return render_template('main/watch.html', video=video, comments=comments, is_liked=is_liked, is_subscribed=is_subscribed, related_videos=related_videos, config=Config)


@main_bp.route('/search')
def search():
    """
    비디오 검색 페이지
    제목과 설명에서 검색어를 찾습니다.
    
    Returns:
        HTML 템플릿 렌더링
    """
    # 검색어 가져오기
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    # 검색어가 없으면 메인 페이지로 리다이렉트
    if not query:
        return redirect(url_for('main.index'))
    
    # 검색 쿼리 생성 (제목 또는 설명에서 검색)
    search_filter = or_(
        Video.title.contains(query),
        Video.description.contains(query)
    )
    
    # 검색 결과 조회 (최신순)
    videos = Video.query.filter(search_filter)\
        .order_by(Video.created_at.desc())\
        .paginate(
            page=page,
            per_page=Config.VIDEOS_PER_PAGE,
            error_out=False
        )
    
    return render_template('main/search.html', videos=videos, query=query)


@main_bp.route('/user/<username>')
def user_profile(username):
    """
    사용자 프로필 페이지
    사용자 정보와 업로드한 비디오 목록을 표시합니다.
    
    Args:
        username: 사용자명
    
    Returns:
        HTML 템플릿 렌더링
    """
    # 사용자 조회
    user = User.query.filter_by(username=username).first_or_404()
    
    # 페이지네이션을 위한 페이지 번호 가져오기
    page = request.args.get('page', 1, type=int)
    
    # 사용자가 업로드한 비디오 목록 조회 (최신순, N+1 쿼리 방지를 위해 eager loading)
    videos = Video.query.options(
        joinedload(Video.author)
    ).filter_by(user_id=user.id)\
        .order_by(Video.created_at.desc())\
        .paginate(
            page=page,
            per_page=Config.VIDEOS_PER_PAGE,
            error_out=False
        )
    
    # 통계 정보 계산
    total_views = db.session.query(func.sum(Video.views))\
        .filter_by(user_id=user.id).scalar() or 0
    total_likes = db.session.query(func.sum(Video.likes))\
        .filter_by(user_id=user.id).scalar() or 0
    video_count = videos.total
    
    # 구독 정보 (로그인한 사용자만)
    is_subscribed = False
    if current_user.is_authenticated:
        is_subscribed = current_user.is_subscribed_to(user)
    
    # 구독자 수
    subscriber_count = user.subscribers.count()
    
    return render_template(
        'main/user_profile.html',
        profile_user=user,
        videos=videos,
        total_views=total_views,
        total_likes=total_likes,
        video_count=video_count,
        is_subscribed=is_subscribed,
        subscriber_count=subscriber_count
    )


@main_bp.route('/subscriptions')
@login_required
def subscriptions_feed():
    """
    구독한 사용자의 동영상 피드 페이지
    로그인한 사용자가 구독한 사용자들의 최신 동영상을 표시합니다.
    
    Returns:
        HTML 템플릿 렌더링
    """
    # 페이지네이션을 위한 페이지 번호 가져오기
    page = request.args.get('page', 1, type=int)
    
    # 구독한 사용자 ID 목록 가져오기
    subscribed_user_ids = [user.id for user in current_user.subscribed_to.all()]
    
    if not subscribed_user_ids:
        # 구독한 사용자가 없으면 빈 결과 반환
        from flask import make_response
        videos = Video.query.filter_by(id=0).paginate(
            page=page,
            per_page=Config.VIDEOS_PER_PAGE,
            error_out=False
        )
        return render_template('main/subscriptions.html', videos=videos)
    
    # 구독한 사용자들의 비디오만 조회 (최신순)
    videos = Video.query.filter(Video.user_id.in_(subscribed_user_ids))\
        .order_by(Video.created_at.desc())\
        .paginate(
            page=page,
            per_page=Config.VIDEOS_PER_PAGE,
            error_out=False
        )
    
    return render_template('main/subscriptions.html', videos=videos)


@main_bp.route('/tag/<tag_name>')
def tag_videos(tag_name):
    """
    태그별 비디오 목록 페이지
    
    Args:
        tag_name: 태그 이름
    
    Returns:
        HTML 템플릿 렌더링
    """
    # 태그 조회
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    
    # 페이지네이션을 위한 페이지 번호 가져오기
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'latest', type=str)
    
    # 정렬 옵션에 따라 쿼리 생성
    if sort_by == 'popular':
        order_by = Video.likes.desc()
        sort_label = '인기 동영상'
    elif sort_by == 'views':
        order_by = Video.views.desc()
        sort_label = '조회수 많은 동영상'
    else:
        order_by = Video.created_at.desc()
        sort_label = '최신 동영상'
    
    # 태그가 있는 비디오만 조회 (N+1 쿼리 방지를 위해 eager loading)
    videos = Video.query.options(
        joinedload(Video.author)
    ).join(Video.tags)\
        .filter(Tag.id == tag.id)\
        .order_by(order_by)\
        .paginate(
            page=page,
            per_page=Config.VIDEOS_PER_PAGE,
            error_out=False
        )
    
    # 인기 태그 조회
    popular_tags = db.session.query(Tag)\
        .join(video_tags)\
        .join(Video)\
        .group_by(Tag.id)\
        .having(func.count(Video.id) > 0)\
        .order_by(func.count(Video.id).desc())\
        .limit(10)\
        .all()
    
    return render_template(
        'main/tag.html',
        tag=tag,
        videos=videos,
        sort_by=sort_by,
        sort_label=sort_label,
        popular_tags=popular_tags,
        config=Config
    )


"""
API 라우트
RESTful API 엔드포인트를 제공합니다.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
from app import db
from app.models import Video, Comment, User, Tag, video_tags
from config import Config
from app.utils.pagination import cursor_paginate, create_cursor_response
from app.utils.security import validate_comment_content, sanitize_text

api_bp = Blueprint('api', __name__, url_prefix='/api')


def video_to_dict(video):
    """
    Video 객체를 딕셔너리로 변환
    
    Args:
        video: Video 객체
    
    Returns:
        dict: 비디오 정보 딕셔너리
    """
    return {
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'category': video.category,
        'category_name': Config.VIDEO_CATEGORIES.get(video.category) if video.category else None,
        'views': video.views,
        'likes': video.likes,
        'created_at': video.created_at.isoformat() if video.created_at else None,
        'updated_at': video.updated_at.isoformat() if video.updated_at else None,
        'author': {
            'id': video.author.id,
            'username': video.author.username,
            'nickname': video.author.nickname,
            'profile_image': video.author.profile_image
        },
        'thumbnail_path': video.thumbnail_path,
        'tags': [tag.name for tag in video.tags.all()],
        'video_path': video.video_path
    }


def comment_to_dict(comment):
    """
    Comment 객체를 딕셔너리로 변환
    
    Args:
        comment: Comment 객체
    
    Returns:
        dict: 댓글 정보 딕셔너리
    """
    return {
        'id': comment.id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat() if comment.created_at else None,
        'updated_at': comment.updated_at.isoformat() if comment.updated_at else None,
        'author': {
            'id': comment.author.id,
            'username': comment.author.username,
            'nickname': comment.author.nickname,
            'profile_image': comment.author.profile_image
        },
        'video_id': comment.video_id,
        'parent_id': comment.parent_id,
        'likes': comment.likes or 0,
        'dislikes': comment.dislikes or 0,
        'is_author': current_user.is_authenticated and comment.user_id == current_user.id,
        'is_liked': current_user.is_authenticated and comment.is_liked_by(current_user),
        'is_disliked': current_user.is_authenticated and comment.is_disliked_by(current_user)
    }


# ==================== 비디오 API ====================

@api_bp.route('/videos', methods=['GET'])
def get_videos():
    """
    비디오 목록 조회 API (커서 기반 페이지네이션)
    
    Query Parameters:
        - cursor: 커서 값 (다음 페이지 요청 시 사용)
        - limit: 페이지당 항목 수 (기본값: 20, 최대: 100)
        - sort: 정렬 옵션 (latest, popular, views)
        - category: 카테고리 필터
        - search: 검색어
    
    Returns:
        JSON 응답
    """
    cursor = request.args.get('cursor', None, type=str)
    limit = min(request.args.get('limit', Config.VIDEOS_PER_PAGE, type=int), 100)  # 최대 100개
    sort_by = request.args.get('sort', 'latest', type=str)
    category = request.args.get('category', None, type=str)
    search = request.args.get('search', None, type=str)
    
    # 쿼리 생성
    query = Video.query
    
    # 검색 필터
    if search:
        query = query.filter(
            or_(
                Video.title.contains(search),
                Video.description.contains(search)
            )
        )
    
    # 카테고리 필터
    if category and category in Config.VIDEO_CATEGORIES:
        query = query.filter_by(category=category)
    
    # 정렬에 따라 커서 필드 결정
    if sort_by == 'popular':
        cursor_field = 'likes'
        order_by_field = Video.likes
        reverse = True
    elif sort_by == 'views':
        cursor_field = 'views'
        order_by_field = Video.views
        reverse = True
    else:
        cursor_field = 'created_at'
        order_by_field = Video.created_at
        reverse = True  # 최신순은 내림차순
    
    # N+1 쿼리 방지를 위해 eager loading
    query = query.options(joinedload(Video.author))
    
    # 커서 기반 페이지네이션
    videos, next_cursor, has_next = cursor_paginate(
        query=query,
        cursor=cursor,
        limit=limit,
        cursor_field=cursor_field,
        order_by_field=order_by_field,
        reverse=reverse
    )
    
    return jsonify({
        'success': True,
        'data': {
            'videos': [video_to_dict(video) for video in videos],
            'pagination': {
                'limit': limit,
                'count': len(videos),
                'has_next': has_next,
                'next_cursor': next_cursor
            }
        }
    })


@api_bp.route('/videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """
    비디오 상세 조회 API
    
    Args:
        video_id: 비디오 ID
    
    Returns:
        JSON 응답
    """
    # N+1 쿼리 방지를 위해 eager loading
    # author는 backref이므로 eager loading 가능, tags는 dynamic이므로 별도 처리
    video = Video.query.options(
        joinedload(Video.author)
    ).get_or_404(video_id)
    
    # 조회수 증가
    video.views += 1
    db.session.commit()
    
    # 좋아요 상태 확인
    is_liked = False
    if current_user.is_authenticated:
        is_liked = video.is_liked_by(current_user)
    
    # 관련 동영상
    from app.routes.main import get_related_videos
    related_videos = get_related_videos(video, limit=10)
    
    return jsonify({
        'success': True,
        'data': {
            'video': video_to_dict(video),
            'is_liked': is_liked,
            'related_videos': [video_to_dict(v) for v in related_videos]
        }
    })


# ==================== 댓글 API ====================

@api_bp.route('/videos/<int:video_id>/comments', methods=['GET'])
def get_comments(video_id):
    """
    비디오 댓글 목록 조회 API
    
    Args:
        video_id: 비디오 ID
    
    Returns:
        JSON 응답
    """
    video = Video.query.get_or_404(video_id)
    
    # N+1 쿼리 방지를 위해 eager loading
    # 부모 댓글만 조회 (parent_id가 None인 댓글)
    parent_comments = Comment.query.options(
        joinedload(Comment.author)
    ).filter_by(video_id=video_id, parent_id=None)\
        .order_by(Comment.created_at.desc()).all()
    
    # 각 댓글의 대댓글도 함께 로드
    comments_data = []
    for comment in parent_comments:
        comment_dict = comment_to_dict(comment)
        # 대댓글 로드
        replies = Comment.query.options(
            joinedload(Comment.author)
        ).filter_by(parent_id=comment.id)\
            .order_by(Comment.created_at.asc()).all()
        comment_dict['replies'] = [comment_to_dict(reply) for reply in replies]
        comments_data.append(comment_dict)
    
    # 전체 댓글 수 계산 (부모 댓글 + 대댓글)
    total_count = Comment.query.filter_by(video_id=video_id).count()
    
    return jsonify({
        'success': True,
        'data': {
            'comments': comments_data,
            'count': total_count
        }
    })


@api_bp.route('/videos/<int:video_id>/comments', methods=['POST'])
@login_required
def create_comment(video_id):
    """
    댓글 작성 API
    
    Args:
        video_id: 비디오 ID
    
    Request Body:
        - content: 댓글 내용
    
    Returns:
        JSON 응답
    """
    video = Video.query.get_or_404(video_id)
    
    # JSON 또는 form 데이터 처리
    if request.is_json:
        data = request.get_json()
        content = data.get('content', '').strip()
    else:
        content = request.form.get('content', '').strip()
    
    # 댓글 내용 검증
    is_valid, error = validate_comment_content(content)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error
        }), 400
    
    # HTML 태그 제거 및 정제
    content = sanitize_text(content, max_length=1000)
    
    try:
        comment = Comment(
            content=content,
            user_id=current_user.id,
            video_id=video_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': comment_to_dict(comment)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/comments/<int:comment_id>', methods=['PUT'])
@login_required
def update_comment(comment_id):
    """
    댓글 수정 API
    
    Args:
        comment_id: 댓글 ID
    
    Request Body:
        - content: 댓글 내용
    
    Returns:
        JSON 응답
    """
    comment = Comment.query.get_or_404(comment_id)
    
    # 권한 확인
    if comment.user_id != current_user.id:
        return jsonify({
            'success': False,
            'error': '댓글을 수정할 권한이 없습니다.'
        }), 403
    
    # JSON 또는 form 데이터 처리
    if request.is_json:
        data = request.get_json()
        content = data.get('content', '').strip()
    else:
        content = request.form.get('content', '').strip()
    
    # 댓글 내용 검증
    is_valid, error = validate_comment_content(content)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error
        }), 400
    
    # HTML 태그 제거 및 정제
    content = sanitize_text(content, max_length=1000)
    
    try:
        comment.content = content
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': comment_to_dict(comment)
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """
    댓글 삭제 API
    
    Args:
        comment_id: 댓글 ID
    
    Returns:
        JSON 응답
    """
    comment = Comment.query.get_or_404(comment_id)
    
    # 권한 확인
    if comment.user_id != current_user.id:
        return jsonify({
            'success': False,
            'error': '댓글을 삭제할 권한이 없습니다.'
        }), 403
    
    try:
        video_id = comment.video_id
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '댓글이 삭제되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 태그 API ====================

@api_bp.route('/tags/popular', methods=['GET'])
def get_popular_tags():
    """
    인기 태그 조회 API
    
    Query Parameters:
        - limit: 조회할 태그 개수 (기본값: 10)
    
    Returns:
        JSON 응답
    """
    limit = request.args.get('limit', 10, type=int)
    
    popular_tags = db.session.query(Tag)\
        .join(video_tags)\
        .join(Video)\
        .group_by(Tag.id)\
        .having(func.count(Video.id) > 0)\
        .order_by(func.count(Video.id).desc())\
        .limit(limit)\
        .all()
    
    return jsonify({
        'success': True,
        'data': {
            'tags': [
                {
                    'id': tag.id,
                    'name': tag.name,
                    'video_count': tag.videos.count()
                }
                for tag in popular_tags
            ]
        }
    })


@api_bp.route('/tags/<tag_name>/videos', methods=['GET'])
def get_tag_videos(tag_name):
    """
    태그별 비디오 목록 조회 API
    
    Args:
        tag_name: 태그 이름
    
    Query Parameters:
        - page: 페이지 번호 (기본값: 1)
        - per_page: 페이지당 항목 수 (기본값: 20)
        - sort: 정렬 옵션 (latest, popular, views)
    
    Returns:
        JSON 응답
    """
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', Config.VIDEOS_PER_PAGE, type=int)
    sort_by = request.args.get('sort', 'latest', type=str)
    
    # 정렬
    if sort_by == 'popular':
        order_by = Video.likes.desc()
    elif sort_by == 'views':
        order_by = Video.views.desc()
    else:
        order_by = Video.created_at.desc()
    
    # 태그가 있는 비디오만 조회 (N+1 쿼리 방지를 위해 eager loading)
    pagination = Video.query.options(
        joinedload(Video.author)
    ).join(Video.tags)\
        .filter(Tag.id == tag.id)\
        .order_by(order_by)\
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    return jsonify({
        'success': True,
        'data': {
            'tag': {
                'id': tag.id,
                'name': tag.name
            },
            'videos': [video_to_dict(video) for video in pagination.items],
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_num': pagination.next_num,
                'prev_num': pagination.prev_num
            }
        }
    })


# ==================== 사용자 API ====================

@api_bp.route('/users/<username>', methods=['GET'])
def get_user_profile(username):
    """
    사용자 프로필 조회 API
    
    Args:
        username: 사용자명
    
    Returns:
        JSON 응답
    """
    user = User.query.filter_by(username=username).first_or_404()
    
    # 통계 정보
    total_views = db.session.query(func.sum(Video.views))\
        .filter_by(user_id=user.id).scalar() or 0
    total_likes = db.session.query(func.sum(Video.likes))\
        .filter_by(user_id=user.id).scalar() or 0
    video_count = Video.query.filter_by(user_id=user.id).count()
    subscriber_count = user.subscribers.count()
    
    # 구독 정보
    is_subscribed = False
    if current_user.is_authenticated:
        is_subscribed = current_user.is_subscribed_to(user)
    
    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'profile_image': user.profile_image,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            'stats': {
                'total_views': total_views,
                'total_likes': total_likes,
                'video_count': video_count,
                'subscriber_count': subscriber_count
            },
            'is_subscribed': is_subscribed,
            'is_own_profile': current_user.is_authenticated and current_user.id == user.id
        }
    })


@api_bp.route('/users/<username>/videos', methods=['GET'])
def get_user_videos(username):
    """
    사용자 비디오 목록 조회 API
    
    Args:
        username: 사용자명
    
    Query Parameters:
        - page: 페이지 번호 (기본값: 1)
        - per_page: 페이지당 항목 수 (기본값: 20)
    
    Returns:
        JSON 응답
    """
    user = User.query.filter_by(username=username).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', Config.VIDEOS_PER_PAGE, type=int)
    
    # N+1 쿼리 방지를 위해 eager loading
    pagination = Video.query.options(
        joinedload(Video.author)
    ).filter_by(user_id=user.id)\
        .order_by(Video.created_at.desc())\
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    return jsonify({
        'success': True,
        'data': {
            'videos': [video_to_dict(video) for video in pagination.items],
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_num': pagination.next_num,
                'prev_num': pagination.prev_num
            }
        }
    })


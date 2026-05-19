"""
댓글 좋아요/싫어요 라우트
댓글 좋아요/싫어요 추가/제거 기능을 처리합니다.
"""
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Comment

comment_likes_bp = Blueprint('comment_likes', __name__)


@comment_likes_bp.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def toggle_comment_like(comment_id):
    """
    댓글 좋아요 토글 (추가/제거)
    좋아요를 누르면 싫어요는 자동으로 취소됩니다.
    
    Args:
        comment_id: 댓글 ID
    
    Returns:
        JSON 응답 (좋아요 상태 및 개수)
    """
    comment = Comment.query.get_or_404(comment_id)
    
    # 이미 좋아요를 눌렀는지 확인
    is_liked = comment.is_liked_by(current_user)
    is_disliked = comment.is_disliked_by(current_user)
    
    try:
        if is_liked:
            # 좋아요 제거
            comment.liked_by_users.remove(current_user)
            comment.likes = max(0, comment.likes - 1)
            action = 'removed'
        else:
            # 좋아요 추가
            # 싫어요가 있으면 먼저 제거
            if is_disliked:
                comment.disliked_by_users.remove(current_user)
                comment.dislikes = max(0, comment.dislikes - 1)
            
            comment.liked_by_users.append(current_user)
            comment.likes = comment.likes + 1
            action = 'added'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': action,
            'likes_count': comment.likes,
            'dislikes_count': comment.dislikes,
            'is_liked': not is_liked,
            'is_disliked': False
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@comment_likes_bp.route('/comment/<int:comment_id>/dislike', methods=['POST'])
@login_required
def toggle_comment_dislike(comment_id):
    """
    댓글 싫어요 토글 (추가/제거)
    싫어요를 누르면 좋아요는 자동으로 취소됩니다.
    
    Args:
        comment_id: 댓글 ID
    
    Returns:
        JSON 응답 (싫어요 상태 및 개수)
    """
    comment = Comment.query.get_or_404(comment_id)
    
    # 이미 싫어요를 눌렀는지 확인
    is_disliked = comment.is_disliked_by(current_user)
    is_liked = comment.is_liked_by(current_user)
    
    try:
        if is_disliked:
            # 싫어요 제거
            comment.disliked_by_users.remove(current_user)
            comment.dislikes = max(0, comment.dislikes - 1)
            action = 'removed'
        else:
            # 싫어요 추가
            # 좋아요가 있으면 먼저 제거
            if is_liked:
                comment.liked_by_users.remove(current_user)
                comment.likes = max(0, comment.likes - 1)
            
            comment.disliked_by_users.append(current_user)
            comment.dislikes = comment.dislikes + 1
            action = 'added'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': action,
            'likes_count': comment.likes,
            'dislikes_count': comment.dislikes,
            'is_liked': False,
            'is_disliked': not is_disliked
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@comment_likes_bp.route('/comment/<int:comment_id>/like/status', methods=['GET'])
@login_required
def comment_like_status(comment_id):
    """
    댓글 좋아요/싫어요 상태 확인
    
    Args:
        comment_id: 댓글 ID
    
    Returns:
        JSON 응답 (좋아요/싫어요 상태 및 개수)
    """
    comment = Comment.query.get_or_404(comment_id)
    
    is_liked = comment.is_liked_by(current_user)
    is_disliked = comment.is_disliked_by(current_user)
    
    return jsonify({
        'is_liked': is_liked,
        'is_disliked': is_disliked,
        'likes_count': comment.likes,
        'dislikes_count': comment.dislikes
    })


"""
좋아요 라우트
비디오 좋아요 추가/제거 기능을 처리합니다.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Video

likes_bp = Blueprint('likes', __name__)


@likes_bp.route('/video/<int:video_id>/like', methods=['POST'])
@login_required
def toggle_like(video_id):
    """
    좋아요 토글 (추가/제거)
    
    Args:
        video_id: 비디오 ID
    
    Returns:
        JSON 응답 (좋아요 상태 및 개수)
    """
    video = Video.query.get_or_404(video_id)
    
    # 이미 좋아요를 눌렀는지 확인
    is_liked = video.is_liked_by(current_user)
    
    try:
        if is_liked:
            # 좋아요 제거
            video.liked_by_users.remove(current_user)
            video.likes = max(0, video.likes - 1)  # 음수 방지
            action = 'removed'
        else:
            # 좋아요 추가
            video.liked_by_users.append(current_user)
            video.likes = video.likes + 1
            action = 'added'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'action': action,
            'likes_count': video.likes,
            'is_liked': not is_liked
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@likes_bp.route('/video/<int:video_id>/like/status', methods=['GET'])
@login_required
def like_status(video_id):
    """
    좋아요 상태 확인
    
    Args:
        video_id: 비디오 ID
    
    Returns:
        JSON 응답 (좋아요 상태 및 개수)
    """
    video = Video.query.get_or_404(video_id)
    
    is_liked = video.is_liked_by(current_user)
    
    return jsonify({
        'is_liked': is_liked,
        'likes_count': video.likes
    })


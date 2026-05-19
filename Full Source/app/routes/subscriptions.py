"""
구독 라우트
사용자 구독/구독 취소 기능을 처리합니다.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import User

subscriptions_bp = Blueprint('subscriptions', __name__)


@subscriptions_bp.route('/user/<int:user_id>/subscribe', methods=['POST'])
@login_required
def toggle_subscribe(user_id):
    """
    구독 토글 (추가/제거)
    
    Args:
        user_id: 구독할 사용자 ID
    
    Returns:
        JSON 응답 (구독 상태 및 구독자 수)
    """
    # 자기 자신을 구독할 수 없도록 검증
    if user_id == current_user.id:
        return jsonify({
            'success': False,
            'error': '자기 자신을 구독할 수 없습니다.'
        }), 400
    
    subscribed_user = User.query.get_or_404(user_id)
    
    # 이미 구독 중인지 확인
    is_subscribed = current_user.is_subscribed_to(subscribed_user)
    
    try:
        if is_subscribed:
            # 구독 취소
            current_user.subscribed_to.remove(subscribed_user)
            action = 'unsubscribed'
        else:
            # 구독 추가
            current_user.subscribed_to.append(subscribed_user)
            action = 'subscribed'
        
        db.session.commit()
        
        # 구독자 수 계산
        subscriber_count = subscribed_user.subscribers.count()
        
        return jsonify({
            'success': True,
            'action': action,
            'subscriber_count': subscriber_count,
            'is_subscribed': not is_subscribed
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@subscriptions_bp.route('/user/<int:user_id>/subscribe/status', methods=['GET'])
@login_required
def subscribe_status(user_id):
    """
    구독 상태 확인
    
    Args:
        user_id: 확인할 사용자 ID
    
    Returns:
        JSON 응답 (구독 상태 및 구독자 수)
    """
    subscribed_user = User.query.get_or_404(user_id)
    
    is_subscribed = current_user.is_subscribed_to(subscribed_user)
    subscriber_count = subscribed_user.subscribers.count()
    
    return jsonify({
        'is_subscribed': is_subscribed,
        'subscriber_count': subscriber_count
    })


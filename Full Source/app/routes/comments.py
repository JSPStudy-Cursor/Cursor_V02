"""
댓글 라우트
비디오 댓글 작성, 조회, 수정, 삭제 기능을 처리합니다.
"""
from flask import Blueprint, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Comment, Video
from app.utils.security import validate_comment_content, sanitize_text

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/video/<int:video_id>/comment', methods=['POST'])
@login_required
def create_comment(video_id):
    """
    댓글 작성 (일반 댓글 또는 대댓글)
    
    Args:
        video_id: 비디오 ID
    
    Returns:
        JSON 응답 또는 리다이렉트
    """
    # 비디오 존재 확인
    video = Video.query.get_or_404(video_id)
    
    # 폼 데이터 가져오기 및 검증
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)  # 대댓글인 경우 부모 댓글 ID
    
    # 대댓글인 경우 부모 댓글 확인
    if parent_id:
        parent_comment = Comment.query.filter_by(id=parent_id, video_id=video_id).first()
        if not parent_comment:
            flash('존재하지 않는 댓글입니다.', 'error')
            return redirect(url_for('main.watch', video_id=video_id))
    
    # 댓글 내용 검증
    is_valid, error = validate_comment_content(content)
    if not is_valid:
        flash(error, 'error')
        return redirect(url_for('main.watch', video_id=video_id))
    
    # HTML 태그 제거 및 정제
    content = sanitize_text(content, max_length=1000)
    
    try:
        # 댓글 생성
        comment = Comment(
            content=content,
            user_id=current_user.id,
            video_id=video_id,
            parent_id=parent_id if parent_id else None
        )
        
        db.session.add(comment)
        db.session.commit()
        
        if parent_id:
            flash('답글이 작성되었습니다.', 'success')
        else:
            flash('댓글이 작성되었습니다.', 'success')
        return redirect(url_for('main.watch', video_id=video_id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'댓글 작성 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('main.watch', video_id=video_id))


@comments_bp.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    """
    댓글 수정
    
    Args:
        comment_id: 댓글 ID
    
    Returns:
        리다이렉트
    """
    comment = Comment.query.get_or_404(comment_id)
    
    # 권한 확인 (작성자만 수정 가능)
    if comment.user_id != current_user.id:
        flash('댓글을 수정할 권한이 없습니다.', 'error')
        return redirect(url_for('main.watch', video_id=comment.video_id))
    
    # 폼 데이터 가져오기 및 검증
    content = request.form.get('content', '').strip()
    
    # 댓글 내용 검증
    is_valid, error = validate_comment_content(content)
    if not is_valid:
        flash(error, 'error')
        return redirect(url_for('main.watch', video_id=comment.video_id))
    
    # HTML 태그 제거 및 정제
    content = sanitize_text(content, max_length=1000)
    
    try:
        # 댓글 수정
        comment.content = content
        db.session.commit()
        
        flash('댓글이 수정되었습니다.', 'success')
        return redirect(url_for('main.watch', video_id=comment.video_id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'댓글 수정 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('main.watch', video_id=comment.video_id))


@comments_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """
    댓글 삭제
    
    Args:
        comment_id: 댓글 ID
    
    Returns:
        리다이렉트
    """
    comment = Comment.query.get_or_404(comment_id)
    video_id = comment.video_id
    
    # 권한 확인 (작성자만 삭제 가능)
    if comment.user_id != current_user.id:
        flash('댓글을 삭제할 권한이 없습니다.', 'error')
        return redirect(url_for('main.watch', video_id=video_id))
    
    try:
        # 대댓글이 있는 경우 대댓글도 함께 삭제 (cascade)
        # 또는 대댓글만 삭제하는 경우
        db.session.delete(comment)
        db.session.commit()
        
        flash('댓글이 삭제되었습니다.', 'success')
        return redirect(url_for('main.watch', video_id=video_id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'댓글 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('main.watch', video_id=video_id))


@comments_bp.route('/comment/<int:parent_id>/reply', methods=['POST'])
@login_required
def create_reply(parent_id):
    """
    대댓글 작성 (API 엔드포인트)
    
    Args:
        parent_id: 부모 댓글 ID
    
    Returns:
        JSON 응답
    """
    parent_comment = Comment.query.get_or_404(parent_id)
    video_id = parent_comment.video_id
    
    # JSON 요청 데이터 가져오기
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '잘못된 요청입니다.'}), 400
    
    content = data.get('content', '').strip()
    
    # 댓글 내용 검증
    is_valid, error = validate_comment_content(content)
    if not is_valid:
        return jsonify({'success': False, 'error': error}), 400
    
    # HTML 태그 제거 및 정제
    content = sanitize_text(content, max_length=1000)
    
    try:
        # 대댓글 생성
        reply = Comment(
            content=content,
            user_id=current_user.id,
            video_id=video_id,
            parent_id=parent_id
        )
        
        db.session.add(reply)
        db.session.commit()
        
        # 작성자 정보 포함하여 반환
        return jsonify({
            'success': True,
            'message': '답글이 작성되었습니다.',
            'comment': {
                'id': reply.id,
                'content': reply.content,
                'user_id': reply.user_id,
                'username': reply.author.username if reply.author else None,
                'nickname': reply.author.nickname if reply.author else None,
                'created_at': reply.created_at.isoformat(),
                'parent_id': reply.parent_id
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


"""
댓글 좋아요/싫어요 기능 테스트
댓글 좋아요/싫어요 추가/제거 기능을 테스트합니다.
"""
import pytest
from app import db
from app.models import Comment, User


class TestCommentLikes:
    """댓글 좋아요/싫어요 테스트"""
    
    def test_toggle_comment_like_add(self, authenticated_client, test_user, test_video, app):
        """
        댓글 좋아요 추가 테스트
        """
        with app.app_context():
            # 댓글 생성
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # 좋아요 추가
        response = authenticated_client.post(f'/comment/{comment_id}/like')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['action'] == 'added'
        assert data['is_liked'] is True
        assert data['likes_count'] == 1
        assert data['is_disliked'] is False
    
    def test_toggle_comment_like_remove(self, authenticated_client, test_user, test_video, app):
        """
        댓글 좋아요 제거 테스트
        """
        with app.app_context():
            # 댓글 생성
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
            
            # 좋아요 추가
            comment.liked_by_users.append(test_user)
            comment.likes = 1
            db.session.commit()
        
        # 좋아요 제거
        response = authenticated_client.post(f'/comment/{comment_id}/like')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['action'] == 'removed'
        assert data['is_liked'] is False
        assert data['likes_count'] == 0
    
    def test_toggle_comment_dislike_add(self, authenticated_client, test_user, test_video, app):
        """
        댓글 싫어요 추가 테스트
        """
        with app.app_context():
            # 댓글 생성
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # 싫어요 추가
        response = authenticated_client.post(f'/comment/{comment_id}/dislike')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['action'] == 'added'
        assert data['is_disliked'] is True
        assert data['dislikes_count'] == 1
        assert data['is_liked'] is False
    
    def test_toggle_comment_dislike_remove(self, authenticated_client, test_user, test_video, app):
        """
        댓글 싫어요 제거 테스트
        """
        with app.app_context():
            # 댓글 생성
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
            
            # 싫어요 추가
            comment.disliked_by_users.append(test_user)
            comment.dislikes = 1
            db.session.commit()
        
        # 싫어요 제거
        response = authenticated_client.post(f'/comment/{comment_id}/dislike')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['action'] == 'removed'
        assert data['is_disliked'] is False
        assert data['dislikes_count'] == 0
    
    def test_like_cancels_dislike(self, authenticated_client, test_user, test_video, app):
        """
        좋아요를 누르면 싫어요가 자동으로 취소되는지 테스트
        """
        with app.app_context():
            # 댓글 생성
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
            
            # 싫어요 추가
            comment.disliked_by_users.append(test_user)
            comment.dislikes = 1
            db.session.commit()
        
        # 좋아요 추가 (싫어요가 취소되어야 함)
        response = authenticated_client.post(f'/comment/{comment_id}/like')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['is_liked'] is True
        assert data['is_disliked'] is False
        assert data['likes_count'] == 1
        assert data['dislikes_count'] == 0
    
    def test_dislike_cancels_like(self, authenticated_client, test_user, test_video, app):
        """
        싫어요를 누르면 좋아요가 자동으로 취소되는지 테스트
        """
        with app.app_context():
            # 댓글 생성
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
            
            # 좋아요 추가
            comment.liked_by_users.append(test_user)
            comment.likes = 1
            db.session.commit()
        
        # 싫어요 추가 (좋아요가 취소되어야 함)
        response = authenticated_client.post(f'/comment/{comment_id}/dislike')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['is_disliked'] is True
        assert data['is_liked'] is False
        assert data['dislikes_count'] == 1
        assert data['likes_count'] == 0
    
    def test_comment_like_status(self, authenticated_client, test_user, test_video, app):
        """
        댓글 좋아요/싫어요 상태 확인 테스트
        """
        with app.app_context():
            # 댓글 생성
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
            
            # 좋아요 추가
            comment.liked_by_users.append(test_user)
            comment.likes = 1
            db.session.commit()
        
        # 상태 확인
        response = authenticated_client.get(f'/comment/{comment_id}/like/status')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_liked'] is True
        assert data['is_disliked'] is False
        assert data['likes_count'] == 1
        assert data['dislikes_count'] == 0
    
    def test_comment_like_unauthorized(self, client, test_user, test_video, app):
        """
        로그인하지 않은 사용자의 좋아요 시도 테스트
        """
        with app.app_context():
            # 댓글 생성
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # 좋아요 시도
        response = client.post(f'/comment/{comment_id}/like')
        
        # 로그인 페이지로 리다이렉트되어야 함
        assert response.status_code in [302, 401]
    
    def test_comment_like_invalid_comment(self, authenticated_client):
        """
        존재하지 않는 댓글에 좋아요 시도 테스트
        """
        response = authenticated_client.post('/comment/99999/like')
        
        assert response.status_code == 404


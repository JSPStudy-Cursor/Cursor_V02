"""
좋아요 기능 테스트
비디오 좋아요 추가/제거 기능을 테스트합니다.
"""
import pytest
from app import db
from app.models import Video, User


class TestLikeRoutes:
    """좋아요 라우트 테스트"""
    
    def test_toggle_like_add(self, authenticated_client, test_video):
        """
        좋아요 추가 테스트
        """
        response = authenticated_client.post(
            f'/video/{test_video.id}/like',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['action'] == 'added'
        assert data['is_liked'] is True
        assert data['likes_count'] >= 1
        
        # 데이터베이스에서 확인
        with authenticated_client.application.app_context():
            video = Video.query.get(test_video.id)
            user = User.query.filter_by(username='testuser').first()
            assert video.is_liked_by(user) is True
    
    def test_toggle_like_remove(self, authenticated_client, test_video, test_user, app):
        """
        좋아요 제거 테스트
        """
        # 먼저 좋아요 추가
        with app.app_context():
            video = Video.query.get(test_video.id)
            video.liked_by_users.append(test_user)
            video.likes = 1
            db.session.commit()
        
        # 좋아요 제거
        response = authenticated_client.post(
            f'/video/{test_video.id}/like',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['action'] == 'removed'
        assert data['is_liked'] is False
        assert data['likes_count'] == 0
        
        # 데이터베이스에서 확인
        with authenticated_client.application.app_context():
            video = Video.query.get(test_video.id)
            user = User.query.filter_by(username='testuser').first()
            assert video.is_liked_by(user) is False
    
    def test_toggle_like_not_logged_in(self, client, test_video):
        """
        로그인하지 않은 사용자가 좋아요 시도 테스트
        """
        response = client.post(
            f'/video/{test_video.id}/like',
            content_type='application/json'
        )
        
        # 로그인 페이지로 리다이렉트되어야 함
        assert response.status_code in [302, 401]
    
    def test_like_status(self, authenticated_client, test_video, test_user, app):
        """
        좋아요 상태 확인 테스트
        """
        # 좋아요 추가
        with app.app_context():
            video = Video.query.get(test_video.id)
            video.liked_by_users.append(test_user)
            video.likes = 1
            db.session.commit()
        
        # 좋아요 상태 확인
        response = authenticated_client.get(
            f'/video/{test_video.id}/like/status'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_liked'] is True
        assert data['likes_count'] == 1


class TestLikeModel:
    """좋아요 모델 테스트"""
    
    def test_is_liked_by(self, app, test_user, test_video):
        """
        is_liked_by 메서드 테스트
        """
        with app.app_context():
            # test_video와 test_user를 다시 조회하여 같은 세션에서 사용
            video = Video.query.get(test_video.id)
            user = User.query.filter_by(username='testuser').first()
            
            # 좋아요 추가 전
            assert video.is_liked_by(user) is False
            
            # 좋아요 추가
            video.liked_by_users.append(user)
            db.session.commit()
            
            # 좋아요 확인
            assert video.is_liked_by(user) is True
    
    def test_like_relationship(self, app, test_user, test_video):
        """
        좋아요 관계 테스트
        """
        with app.app_context():
            # test_video와 test_user를 다시 조회하여 같은 세션에서 사용
            video = Video.query.get(test_video.id)
            user = User.query.filter_by(username='testuser').first()
            
            # 좋아요 추가
            video.liked_by_users.append(user)
            db.session.commit()
            
            # User에서 좋아요한 비디오 확인
            liked_videos = user.liked_videos.all()
            assert any(v.id == video.id for v in liked_videos)
            
            # Video에서 좋아요한 사용자 확인
            liked_users = video.liked_by_users.all()
            assert any(u.id == user.id for u in liked_users)
    
    def test_multiple_likes(self, app, test_user, test_user2, test_video):
        """
        여러 사용자가 같은 비디오에 좋아요 테스트
        """
        with app.app_context():
            # test_video와 test_user들을 다시 조회하여 같은 세션에서 사용
            video = Video.query.get(test_video.id)
            user = User.query.filter_by(username='testuser').first()
            user2 = User.query.filter_by(username='testuser2').first()
            
            # 두 사용자 모두 좋아요 추가
            video.liked_by_users.append(user)
            video.liked_by_users.append(user2)
            video.likes = 2
            db.session.commit()
            
            # 두 사용자 모두 좋아요를 눌렀는지 확인
            assert video.is_liked_by(user) is True
            assert video.is_liked_by(user2) is True
            assert video.likes == 2


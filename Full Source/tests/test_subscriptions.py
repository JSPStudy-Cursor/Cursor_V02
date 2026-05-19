"""
구독 기능 테스트
사용자 구독/구독 취소 기능을 테스트합니다.
"""
import pytest
from app import db
from app.models import User, Video


class TestSubscriptionRoutes:
    """구독 라우트 테스트"""
    
    def test_subscribe_success(self, authenticated_client, app, test_user2):
        """
        구독 성공 테스트
        """
        with app.app_context():
            user2 = User.query.filter_by(username='testuser2').first()
            user2_id = user2.id
        
        # 구독 요청
        response = authenticated_client.post(
            f'/user/{user2_id}/subscribe',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['action'] == 'subscribed'
        assert data['is_subscribed'] is True
        assert data['subscriber_count'] == 1
        
        # 데이터베이스에서 확인
        with app.app_context():
            user1 = User.query.filter_by(username='testuser').first()
            user2 = User.query.filter_by(username='testuser2').first()
            assert user1.is_subscribed_to(user2) is True
    
    def test_unsubscribe_success(self, authenticated_client, app, test_user2):
        """
        구독 취소 성공 테스트
        """
        with app.app_context():
            user1 = User.query.filter_by(username='testuser').first()
            user2 = User.query.filter_by(username='testuser2').first()
            # 먼저 구독 추가
            user1.subscribed_to.append(user2)
            db.session.commit()
            user2_id = user2.id
        
        # 구독 취소 요청
        response = authenticated_client.post(
            f'/user/{user2_id}/subscribe',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['action'] == 'unsubscribed'
        assert data['is_subscribed'] is False
        assert data['subscriber_count'] == 0
        
        # 데이터베이스에서 확인
        with app.app_context():
            user1 = User.query.filter_by(username='testuser').first()
            user2 = User.query.filter_by(username='testuser2').first()
            assert user1.is_subscribed_to(user2) is False
    
    def test_subscribe_self(self, authenticated_client, app):
        """
        자기 자신 구독 불가 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            user_id = user.id
        
        # 자기 자신 구독 시도
        response = authenticated_client.post(
            f'/user/{user_id}/subscribe',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '자기 자신을 구독할 수 없습니다' in data['error']
    
    def test_subscribe_not_logged_in(self, client, app, test_user2):
        """
        로그인하지 않은 사용자 구독 시도 테스트
        """
        with app.app_context():
            user2 = User.query.filter_by(username='testuser2').first()
            user2_id = user2.id
        
        # 구독 요청 (로그인 없이)
        response = client.post(
            f'/user/{user2_id}/subscribe',
            content_type='application/json'
        )
        
        # 로그인 페이지로 리다이렉트되어야 함
        assert response.status_code in [302, 401]
    
    def test_subscribe_status(self, authenticated_client, app, test_user2):
        """
        구독 상태 확인 테스트
        """
        with app.app_context():
            user1 = User.query.filter_by(username='testuser').first()
            user2 = User.query.filter_by(username='testuser2').first()
            # 구독 추가
            user1.subscribed_to.append(user2)
            db.session.commit()
            user2_id = user2.id
        
        # 구독 상태 확인
        response = authenticated_client.get(
            f'/user/{user2_id}/subscribe/status'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_subscribed'] is True
        assert data['subscriber_count'] == 1
    
    def test_subscribe_status_not_subscribed(self, authenticated_client, app, test_user2):
        """
        구독하지 않은 상태 확인 테스트
        """
        with app.app_context():
            user2 = User.query.filter_by(username='testuser2').first()
            user2_id = user2.id
        
        # 구독 상태 확인
        response = authenticated_client.get(
            f'/user/{user2_id}/subscribe/status'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_subscribed'] is False
        assert data['subscriber_count'] == 0


class TestSubscriptionModel:
    """구독 모델 테스트"""
    
    def test_is_subscribed_to(self, app, test_user, test_user2):
        """
        is_subscribed_to 메서드 테스트
        """
        with app.app_context():
            user1 = User.query.filter_by(username='testuser').first()
            user2 = User.query.filter_by(username='testuser2').first()
            
            # 구독 전
            assert user1.is_subscribed_to(user2) is False
            
            # 구독 추가
            user1.subscribed_to.append(user2)
            db.session.commit()
            
            # 구독 후
            assert user1.is_subscribed_to(user2) is True
    
    def test_subscription_relationship(self, app, test_user, test_user2):
        """
        구독 관계 테스트
        """
        with app.app_context():
            user1 = User.query.filter_by(username='testuser').first()
            user2 = User.query.filter_by(username='testuser2').first()
            
            # 구독 추가
            user1.subscribed_to.append(user2)
            db.session.commit()
            
            # 관계 확인
            assert user2 in user1.subscribed_to.all()
            assert user1 in user2.subscribers.all()
            
            # 구독자 수 확인
            assert user2.subscribers.count() == 1


class TestSubscriptionFeed:
    """구독 피드 테스트"""
    
    def test_subscriptions_feed_with_videos(self, authenticated_client, app, test_user, test_user2):
        """
        구독 피드에 비디오가 있는 경우 테스트
        """
        with app.app_context():
            user1 = User.query.filter_by(username='testuser').first()
            user2 = User.query.filter_by(username='testuser2').first()
            
            # 구독 추가
            user1.subscribed_to.append(user2)
            
            # user2의 비디오 생성
            video = Video(
                title='구독 테스트 비디오',
                description='설명',
                video_path='test.mp4',
                user_id=user2.id
            )
            db.session.add(video)
            db.session.commit()
        
        # 구독 피드 접근
        response = authenticated_client.get('/subscriptions')
        
        assert response.status_code == 200
        assert '구독한 채널의 동영상'.encode('utf-8') in response.data
        assert '구독 테스트 비디오'.encode('utf-8') in response.data
    
    def test_subscriptions_feed_no_subscriptions(self, authenticated_client):
        """
        구독한 사용자가 없는 경우 테스트
        """
        # 구독 피드 접근
        response = authenticated_client.get('/subscriptions')
        
        assert response.status_code == 200
        assert '구독한 채널의 동영상'.encode('utf-8') in response.data
        assert '구독한 채널의 동영상이 없습니다'.encode('utf-8') in response.data
    
    def test_subscriptions_feed_not_logged_in(self, client):
        """
        로그인하지 않은 사용자 구독 피드 접근 테스트
        """
        # 구독 피드 접근
        response = client.get('/subscriptions')
        
        # 로그인 페이지로 리다이렉트되어야 함
        assert response.status_code in [302, 401]


class TestUserProfileSubscription:
    """사용자 프로필 페이지 구독 기능 테스트"""
    
    def test_user_profile_subscribe_button(self, authenticated_client, app, test_user2):
        """
        사용자 프로필 페이지에 구독 버튼 표시 테스트
        """
        with app.app_context():
            user2 = User.query.filter_by(username='testuser2').first()
        
        # 사용자 프로필 페이지 접근
        response = authenticated_client.get(f'/user/{user2.username}')
        
        assert response.status_code == 200
        assert '구독'.encode('utf-8') in response.data or b'subscribe-btn' in response.data
    
    def test_user_profile_subscriber_count(self, authenticated_client, app, test_user, test_user2):
        """
        사용자 프로필 페이지에 구독자 수 표시 테스트
        """
        with app.app_context():
            user1 = User.query.filter_by(username='testuser').first()
            user2 = User.query.filter_by(username='testuser2').first()
            
            # 구독 추가
            user1.subscribed_to.append(user2)
            db.session.commit()
            
            # username을 먼저 가져와서 저장
            user2_username = user2.username
        
        # 사용자 프로필 페이지 접근
        response = authenticated_client.get(f'/user/{user2_username}')
        
        assert response.status_code == 200
        # 구독자 수가 표시되는지 확인 (1명)
        assert '구독자'.encode('utf-8') in response.data


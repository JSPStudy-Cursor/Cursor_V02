"""
정렬 기능 테스트
메인 페이지의 비디오 정렬 기능을 테스트합니다.
"""
import pytest
from app import db
from app.models import Video, User


class TestSortingRoutes:
    """정렬 라우트 테스트"""
    
    def test_sort_latest(self, client, app, test_user):
        """
        최신순 정렬 테스트
        """
        # 여러 비디오 생성 (다른 시간에)
        with app.app_context():
            from datetime import datetime, timedelta
            
            video1 = Video(
                title='최신 비디오',
                description='설명',
                video_path='latest.mp4',
                user_id=test_user.id,
                created_at=datetime.utcnow()
            )
            video2 = Video(
                title='오래된 비디오',
                description='설명',
                video_path='old.mp4',
                user_id=test_user.id,
                created_at=datetime.utcnow() - timedelta(days=1)
            )
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
        
        # 최신순 정렬 (기본값)
        response = client.get('/')
        assert response.status_code == 200
        assert '최신 동영상'.encode('utf-8') in response.data
        
        # 최신순 정렬 (명시적)
        response = client.get('/?sort=latest')
        assert response.status_code == 200
        assert '최신 동영상'.encode('utf-8') in response.data
    
    def test_sort_popular(self, client, app, test_user):
        """
        인기순 정렬 테스트 (좋아요 수 기준)
        """
        with app.app_context():
            video1 = Video(
                title='인기 비디오',
                description='설명',
                video_path='popular.mp4',
                user_id=test_user.id,
                likes=10
            )
            video2 = Video(
                title='덜 인기 비디오',
                description='설명',
                video_path='less_popular.mp4',
                user_id=test_user.id,
                likes=5
            )
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
        
        # 인기순 정렬
        response = client.get('/?sort=popular')
        assert response.status_code == 200
        assert '인기 동영상'.encode('utf-8') in response.data
    
    def test_sort_views(self, client, app, test_user):
        """
        조회수순 정렬 테스트
        """
        with app.app_context():
            video1 = Video(
                title='조회수 많은 비디오',
                description='설명',
                video_path='high_views.mp4',
                user_id=test_user.id,
                views=100
            )
            video2 = Video(
                title='조회수 적은 비디오',
                description='설명',
                video_path='low_views.mp4',
                user_id=test_user.id,
                views=10
            )
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
        
        # 조회수순 정렬
        response = client.get('/?sort=views')
        assert response.status_code == 200
        assert '조회수 많은 동영상'.encode('utf-8') in response.data
    
    def test_sort_with_pagination(self, client, app, test_user):
        """
        정렬과 페이지네이션 함께 사용 테스트
        """
        # 여러 비디오 생성
        with app.app_context():
            for i in range(15):
                video = Video(
                    title=f'비디오 {i}',
                    description='설명',
                    video_path=f'video{i}.mp4',
                    user_id=test_user.id,
                    likes=i
                )
                db.session.add(video)
            db.session.commit()
        
        # 인기순 정렬 + 페이지네이션
        response = client.get('/?sort=popular&page=1')
        assert response.status_code == 200
        
        response = client.get('/?sort=popular&page=2')
        assert response.status_code == 200
    
    def test_invalid_sort_option(self, client, app, test_user):
        """
        잘못된 정렬 옵션 테스트 (기본값으로 처리)
        """
        with app.app_context():
            video = Video(
                title='테스트 비디오',
                description='설명',
                video_path='test.mp4',
                user_id=test_user.id
            )
            db.session.add(video)
            db.session.commit()
        
        # 잘못된 정렬 옵션
        response = client.get('/?sort=invalid')
        assert response.status_code == 200
        # 기본값인 최신순으로 처리되어야 함
        assert '최신 동영상'.encode('utf-8') in response.data


class TestSortingFunctionality:
    """정렬 기능 테스트"""
    
    def test_latest_sort_order(self, client, app, test_user):
        """
        최신순 정렬 순서 확인
        """
        with app.app_context():
            from datetime import datetime, timedelta
            
            # 오래된 비디오
            old_video = Video(
                title='오래된 비디오',
                description='설명',
                video_path='old.mp4',
                user_id=test_user.id,
                created_at=datetime.utcnow() - timedelta(days=2)
            )
            # 최신 비디오
            new_video = Video(
                title='최신 비디오',
                description='설명',
                video_path='new.mp4',
                user_id=test_user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(old_video)
            db.session.add(new_video)
            db.session.commit()
        
        response = client.get('/?sort=latest')
        assert response.status_code == 200
        # 최신 비디오가 먼저 나와야 함
        content = response.data.decode('utf-8')
        new_index = content.find('최신 비디오')
        old_index = content.find('오래된 비디오')
        assert new_index < old_index or old_index == -1
    
    def test_popular_sort_order(self, client, app, test_user):
        """
        인기순 정렬 순서 확인
        """
        with app.app_context():
            # 좋아요 적은 비디오
            less_popular = Video(
                title='덜 인기 비디오',
                description='설명',
                video_path='less.mp4',
                user_id=test_user.id,
                likes=5
            )
            # 좋아요 많은 비디오
            more_popular = Video(
                title='더 인기 비디오',
                description='설명',
                video_path='more.mp4',
                user_id=test_user.id,
                likes=20
            )
            db.session.add(less_popular)
            db.session.add(more_popular)
            db.session.commit()
        
        response = client.get('/?sort=popular')
        assert response.status_code == 200
        # 좋아요 많은 비디오가 먼저 나와야 함
        content = response.data.decode('utf-8')
        more_index = content.find('더 인기 비디오')
        less_index = content.find('덜 인기 비디오')
        assert more_index < less_index or less_index == -1
    
    def test_views_sort_order(self, client, app, test_user):
        """
        조회수순 정렬 순서 확인
        """
        with app.app_context():
            # 조회수 적은 비디오
            low_views = Video(
                title='조회수 적은 비디오',
                description='설명',
                video_path='low.mp4',
                user_id=test_user.id,
                views=10
            )
            # 조회수 많은 비디오
            high_views = Video(
                title='조회수 많은 비디오',
                description='설명',
                video_path='high.mp4',
                user_id=test_user.id,
                views=100
            )
            db.session.add(low_views)
            db.session.add(high_views)
            db.session.commit()
        
        response = client.get('/?sort=views')
        assert response.status_code == 200
        # 조회수 많은 비디오가 먼저 나와야 함
        content = response.data.decode('utf-8')
        high_index = content.find('조회수 많은 비디오')
        low_index = content.find('조회수 적은 비디오')
        assert high_index < low_index or low_index == -1


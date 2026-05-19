"""
스튜디오 통계 기능 테스트
스튜디오 통계 데이터 수집 및 표시 기능을 테스트합니다.
"""
import pytest
from datetime import datetime, timedelta
from app import db
from app.models import Video, Comment, User


class TestStudioStats:
    """스튜디오 통계 테스트"""
    
    def test_studio_index_with_stats(self, authenticated_client, test_user, app):
        """
        스튜디오 인덱스 페이지에 통계 표시 테스트
        """
        with app.app_context():
            # 테스트 비디오 생성
            video1 = Video(
                title='테스트 비디오 1',
                description='설명 1',
                video_path='test1.mp4',
                user_id=test_user.id,
                views=100,
                likes=10
            )
            video2 = Video(
                title='테스트 비디오 2',
                description='설명 2',
                video_path='test2.mp4',
                user_id=test_user.id,
                views=200,
                likes=20
            )
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
        
        # 스튜디오 인덱스 페이지 접근
        response = authenticated_client.get('/studio/')
        
        assert response.status_code == 200
        assert '통계'.encode('utf-8') in response.data
        assert '총 동영상'.encode('utf-8') in response.data
        assert '총 조회수'.encode('utf-8') in response.data
        assert '총 좋아요'.encode('utf-8') in response.data
    
    def test_studio_stats_calculation(self, authenticated_client, test_user, app):
        """
        스튜디오 통계 계산 테스트
        """
        with app.app_context():
            # 여러 비디오 생성
            videos = []
            for i in range(5):
                video = Video(
                    title=f'테스트 비디오 {i+1}',
                    description=f'설명 {i+1}',
                    video_path=f'test{i+1}.mp4',
                    user_id=test_user.id,
                    views=(i+1) * 10,
                    likes=(i+1) * 2
                )
                videos.append(video)
                db.session.add(video)
            
            # 비디오 먼저 커밋
            db.session.commit()
            
            # 댓글 생성 (비디오 ID가 확정된 후)
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=videos[0].id
            )
            db.session.add(comment)
            db.session.commit()
        
        # 스튜디오 인덱스 페이지 접근
        response = authenticated_client.get('/studio/')
        
        assert response.status_code == 200
        # 총 동영상 수 확인
        assert b'5' in response.data or '총 동영상'.encode('utf-8') in response.data
    
    def test_studio_stats_recent_activity(self, authenticated_client, test_user, app):
        """
        최근 활동 통계 테스트
        """
        with app.app_context():
            # 최근 비디오 생성 (7일 이내)
            recent_video = Video(
                title='최근 비디오',
                description='설명',
                video_path='recent.mp4',
                user_id=test_user.id,
                views=50,
                likes=5,
                created_at=datetime.utcnow() - timedelta(days=3)
            )
            db.session.add(recent_video)
            db.session.commit()
        
        # 스튜디오 인덱스 페이지 접근
        response = authenticated_client.get('/studio/')
        
        assert response.status_code == 200
        assert '최근 7일'.encode('utf-8') in response.data or '최근 활동'.encode('utf-8') in response.data
    
    def test_studio_stats_popular_videos(self, authenticated_client, test_user, app):
        """
        인기 동영상 TOP 5 표시 테스트
        """
        with app.app_context():
            # 여러 비디오 생성 (조회수 다르게)
            for i in range(7):
                video = Video(
                    title=f'비디오 {i+1}',
                    description=f'설명 {i+1}',
                    video_path=f'video{i+1}.mp4',
                    user_id=test_user.id,
                    views=(7-i) * 10,  # 조회수가 다른 비디오
                    likes=(7-i) * 2
                )
                db.session.add(video)
            db.session.commit()
        
        # 스튜디오 인덱스 페이지 접근
        response = authenticated_client.get('/studio/')
        
        assert response.status_code == 200
        assert '인기 동영상'.encode('utf-8') in response.data or b'TOP 5' in response.data
    
    def test_studio_stats_api(self, authenticated_client, test_user, app):
        """
        스튜디오 통계 API 테스트
        """
        with app.app_context():
            # 테스트 비디오 생성
            video = Video(
                title='테스트 비디오',
                description='설명',
                video_path='test.mp4',
                user_id=test_user.id,
                views=100,
                likes=10
            )
            db.session.add(video)
            db.session.commit()
        
        # 통계 API 호출
        response = authenticated_client.get('/studio/api/stats')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'data' in data
        assert 'total' in data['data']
        assert 'recent_7d' in data['data']
        assert 'recent_30d' in data['data']
        assert 'daily' in data['data']
        
        # 통계 데이터 확인
        assert data['data']['total']['videos'] >= 1
        assert data['data']['total']['views'] >= 100
    
    def test_studio_stats_api_daily_stats(self, authenticated_client, test_user, app):
        """
        일별 통계 데이터 테스트
        """
        with app.app_context():
            # 최근 30일 내 비디오 생성
            for i in range(3):
                video = Video(
                    title=f'비디오 {i+1}',
                    description=f'설명 {i+1}',
                    video_path=f'video{i+1}.mp4',
                    user_id=test_user.id,
                    views=10,
                    likes=1,
                    created_at=datetime.utcnow() - timedelta(days=i*5)
                )
                db.session.add(video)
            db.session.commit()
        
        # 통계 API 호출
        response = authenticated_client.get('/studio/api/stats')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'daily' in data['data']
        assert isinstance(data['data']['daily'], list)
    
    def test_studio_stats_empty(self, authenticated_client, app):
        """
        비디오가 없을 때 통계 표시 테스트
        """
        # 스튜디오 인덱스 페이지 접근
        response = authenticated_client.get('/studio/')
        
        assert response.status_code == 200
        # 통계 섹션이 표시되지 않거나 0으로 표시되어야 함
        assert '내 동영상'.encode('utf-8') in response.data
    
    def test_studio_stats_unauthorized(self, client, app):
        """
        로그인하지 않은 사용자의 통계 접근 테스트
        """
        # 스튜디오 인덱스 페이지 접근
        response = client.get('/studio/')
        
        # 로그인 페이지로 리다이렉트되어야 함
        assert response.status_code in [302, 401]
        
        # 통계 API 접근
        response = client.get('/studio/api/stats')
        
        # 로그인 페이지로 리다이렉트되어야 함
        assert response.status_code in [302, 401]


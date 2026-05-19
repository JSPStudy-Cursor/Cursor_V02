"""
사용자 프로필 기능 테스트
사용자 프로필 페이지 기능을 테스트합니다.
"""
import pytest
from app import db
from app.models import Video, User


class TestUserProfileRoutes:
    """사용자 프로필 라우트 테스트"""
    
    def test_user_profile_exists(self, client, app, test_user):
        """
        존재하는 사용자 프로필 페이지 테스트
        """
        response = client.get(f'/user/{test_user.username}')
        
        assert response.status_code == 200
        assert test_user.username.encode('utf-8') in response.data
        assert (test_user.nickname or test_user.username).encode('utf-8') in response.data
    
    def test_user_profile_not_found(self, client):
        """
        존재하지 않는 사용자 프로필 페이지 테스트
        """
        response = client.get('/user/nonexistent')
        
        assert response.status_code == 404
    
    def test_user_profile_with_videos(self, client, app, test_user):
        """
        비디오가 있는 사용자 프로필 페이지 테스트
        """
        # 비디오 생성
        with app.app_context():
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
        
        response = client.get(f'/user/{test_user.username}')
        
        assert response.status_code == 200
        assert '테스트 비디오'.encode('utf-8') in response.data
    
    def test_user_profile_statistics(self, client, app, test_user):
        """
        사용자 통계 정보 테스트
        """
        # 여러 비디오 생성
        with app.app_context():
            for i in range(3):
                video = Video(
                    title=f'비디오 {i}',
                    description='설명',
                    video_path=f'video{i}.mp4',
                    user_id=test_user.id,
                    views=10 * (i + 1),
                    likes=5 * (i + 1)
                )
                db.session.add(video)
            db.session.commit()
        
        response = client.get(f'/user/{test_user.username}')
        
        assert response.status_code == 200
        # 통계 정보 확인 (비디오 수: 3, 총 조회수: 60, 총 좋아요: 30)
        assert b'3' in response.data  # 비디오 수
    
    def test_user_profile_pagination(self, client, app, test_user):
        """
        사용자 프로필 페이지네이션 테스트
        """
        # 여러 비디오 생성
        with app.app_context():
            for i in range(15):
                video = Video(
                    title=f'비디오 {i}',
                    description='설명',
                    video_path=f'video{i}.mp4',
                    user_id=test_user.id
                )
                db.session.add(video)
            db.session.commit()
        
        # 첫 페이지
        response = client.get(f'/user/{test_user.username}')
        assert response.status_code == 200
        
        # 두 번째 페이지
        response = client.get(f'/user/{test_user.username}?page=2')
        assert response.status_code == 200
    
    def test_user_profile_no_videos(self, client, app, test_user):
        """
        비디오가 없는 사용자 프로필 페이지 테스트
        """
        response = client.get(f'/user/{test_user.username}')
        
        assert response.status_code == 200
        assert '아직 업로드한 동영상이 없습니다'.encode('utf-8') in response.data


class TestUserProfileLinks:
    """사용자 프로필 링크 테스트"""
    
    def test_author_link_in_video_card(self, client, app, test_user):
        """
        비디오 카드에 작성자 프로필 링크가 있는지 테스트
        """
        # 비디오 생성
        with app.app_context():
            video = Video(
                title='테스트 비디오',
                description='설명',
                video_path='test.mp4',
                user_id=test_user.id
            )
            db.session.add(video)
            db.session.commit()
        
        # 메인 페이지에서 확인
        response = client.get('/')
        assert response.status_code == 200
        # 작성자 프로필 링크 확인
        assert f'/user/{test_user.username}'.encode('utf-8') in response.data
    
    def test_author_link_in_search_results(self, client, app, test_user):
        """
        검색 결과에 작성자 프로필 링크가 있는지 테스트
        """
        # 비디오 생성
        with app.app_context():
            video = Video(
                title='검색 테스트',
                description='설명',
                video_path='search.mp4',
                user_id=test_user.id
            )
            db.session.add(video)
            db.session.commit()
        
        # 검색 결과에서 확인
        response = client.get('/search?q=검색')
        assert response.status_code == 200
        # 작성자 프로필 링크 확인
        assert f'/user/{test_user.username}'.encode('utf-8') in response.data


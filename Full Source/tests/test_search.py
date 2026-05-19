"""
검색 기능 테스트
비디오 검색 기능을 테스트합니다.
"""
import pytest
from app import db
from app.models import Video, User


class TestSearchRoutes:
    """검색 라우트 테스트"""
    
    def test_search_with_results(self, client, app, test_user):
        """
        검색 결과가 있는 경우 테스트
        """
        # 테스트 비디오 생성
        with app.app_context():
            video1 = Video(
                title='Python 튜토리얼',
                description='Python 프로그래밍 강의',
                video_path='python.mp4',
                user_id=test_user.id
            )
            video2 = Video(
                title='JavaScript 기초',
                description='JavaScript 프로그래밍',
                video_path='js.mp4',
                user_id=test_user.id
            )
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
        
        # 검색 실행
        response = client.get('/search?q=Python')
        
        assert response.status_code == 200
        assert b'Python' in response.data
        assert '검색 결과'.encode('utf-8') in response.data
    
    def test_search_no_results(self, client, app, test_user):
        """
        검색 결과가 없는 경우 테스트
        """
        # 테스트 비디오 생성
        with app.app_context():
            video = Video(
                title='Python 튜토리얼',
                description='Python 프로그래밍 강의',
                video_path='python.mp4',
                user_id=test_user.id
            )
            db.session.add(video)
            db.session.commit()
        
        # 검색 실행 (일치하지 않는 검색어)
        response = client.get('/search?q=JavaScript')
        
        assert response.status_code == 200
        assert '검색 결과가 없습니다'.encode('utf-8') in response.data
    
    def test_search_empty_query(self, client):
        """
        빈 검색어로 검색 시도 테스트
        """
        response = client.get('/search?q=')
        
        # 메인 페이지로 리다이렉트되어야 함
        assert response.status_code == 302
    
    def test_search_in_title(self, client, app, test_user):
        """
        제목에서 검색 테스트
        """
        with app.app_context():
            video = Video(
                title='Flask 웹 개발',
                description='설명',
                video_path='flask.mp4',
                user_id=test_user.id
            )
            db.session.add(video)
            db.session.commit()
        
        response = client.get('/search?q=Flask')
        
        assert response.status_code == 200
        assert 'Flask 웹 개발'.encode('utf-8') in response.data
    
    def test_search_in_description(self, client, app, test_user):
        """
        설명에서 검색 테스트
        """
        with app.app_context():
            video = Video(
                title='비디오 제목',
                description='Flask 프레임워크 강의입니다',
                video_path='video.mp4',
                user_id=test_user.id
            )
            db.session.add(video)
            db.session.commit()
        
        response = client.get('/search?q=Flask')
        
        assert response.status_code == 200
        assert '비디오 제목'.encode('utf-8') in response.data
    
    def test_search_pagination(self, client, app, test_user):
        """
        검색 결과 페이지네이션 테스트
        """
        # 여러 비디오 생성
        with app.app_context():
            for i in range(15):
                video = Video(
                    title=f'Python 튜토리얼 {i}',
                    description='Python 강의',
                    video_path=f'python{i}.mp4',
                    user_id=test_user.id
                )
                db.session.add(video)
            db.session.commit()
        
        # 첫 페이지 검색
        response = client.get('/search?q=Python')
        assert response.status_code == 200
        
        # 두 번째 페이지 검색
        response = client.get('/search?q=Python&page=2')
        assert response.status_code == 200


class TestSearchFunctionality:
    """검색 기능 테스트"""
    
    def test_search_case_insensitive(self, client, app, test_user):
        """
        대소문자 구분 없이 검색 테스트
        """
        with app.app_context():
            video = Video(
                title='Python Tutorial',
                description='Python programming',
                video_path='python.mp4',
                user_id=test_user.id
            )
            db.session.add(video)
            db.session.commit()
        
        # 소문자로 검색
        response = client.get('/search?q=python')
        assert response.status_code == 200
        assert b'Python Tutorial' in response.data
        
        # 대문자로 검색
        response = client.get('/search?q=PYTHON')
        assert response.status_code == 200
        assert b'Python Tutorial' in response.data
    
    def test_search_partial_match(self, client, app, test_user):
        """
        부분 일치 검색 테스트
        """
        with app.app_context():
            video = Video(
                title='Python 프로그래밍 기초',
                description='설명',
                video_path='python.mp4',
                user_id=test_user.id
            )
            db.session.add(video)
            db.session.commit()
        
        # 부분 검색어로 검색
        response = client.get('/search?q=Python')
        assert response.status_code == 200
        assert 'Python 프로그래밍 기초'.encode('utf-8') in response.data


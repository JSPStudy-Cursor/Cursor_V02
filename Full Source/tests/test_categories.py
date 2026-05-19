"""
비디오 카테고리 기능 테스트
비디오 카테고리 분류 기능을 테스트합니다.
"""
import pytest
from io import BytesIO
from app import db
from app.models import Video, User
from config import Config


class TestCategoryRoutes:
    """카테고리 라우트 테스트"""
    
    def test_index_with_category_filter(self, client, app, test_user):
        """
        카테고리 필터가 있는 메인 페이지 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            # 카테고리가 있는 비디오 생성
            video = Video(
                title='엔터테인먼트 비디오',
                description='설명',
                video_path='test.mp4',
                category='entertainment',
                user_id=user.id
            )
            db.session.add(video)
            db.session.commit()
        
        # 카테고리 필터로 메인 페이지 접근
        response = client.get('/?category=entertainment')
        
        assert response.status_code == 200
        assert '엔터테인먼트' in response.data.decode('utf-8')
    
    def test_index_without_category_filter(self, client, app, test_user):
        """
        카테고리 필터 없이 메인 페이지 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            # 카테고리가 있는 비디오 생성
            video = Video(
                title='일반 비디오',
                description='설명',
                video_path='test.mp4',
                category='entertainment',
                user_id=user.id
            )
            db.session.add(video)
            db.session.commit()
        
        # 카테고리 필터 없이 메인 페이지 접근
        response = client.get('/')
        
        assert response.status_code == 200
        # 모든 비디오가 표시되어야 함
        assert '일반 비디오' in response.data.decode('utf-8')
    
    def test_index_with_invalid_category(self, client, app, test_user):
        """
        잘못된 카테고리 필터 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            # 비디오 생성
            video = Video(
                title='테스트 비디오',
                description='설명',
                video_path='test.mp4',
                user_id=user.id
            )
            db.session.add(video)
            db.session.commit()
        
        # 잘못된 카테고리로 접근
        response = client.get('/?category=invalid_category')
        
        assert response.status_code == 200
        # 모든 비디오가 표시되어야 함 (잘못된 카테고리는 무시)
        assert '테스트 비디오' in response.data.decode('utf-8')
    
    def test_index_category_with_sorting(self, client, app, test_user):
        """
        카테고리 필터와 정렬 옵션 조합 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            # 여러 카테고리 비디오 생성
            video1 = Video(
                title='음악 비디오 1',
                description='설명',
                video_path='test1.mp4',
                category='music',
                likes=10,
                user_id=user.id
            )
            video2 = Video(
                title='음악 비디오 2',
                description='설명',
                video_path='test2.mp4',
                category='music',
                likes=20,
                user_id=user.id
            )
            db.session.add(video1)
            db.session.add(video2)
            db.session.commit()
        
        # 카테고리 필터와 정렬 옵션 조합
        response = client.get('/?category=music&sort=popular')
        
        assert response.status_code == 200
        assert '음악' in response.data.decode('utf-8')
        assert '음악 비디오 1' in response.data.decode('utf-8')
        assert '음악 비디오 2' in response.data.decode('utf-8')


class TestCategoryModel:
    """카테고리 모델 테스트"""
    
    def test_video_with_category(self, app, test_user):
        """
        카테고리가 있는 비디오 생성 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            video = Video(
                title='카테고리 테스트',
                description='설명',
                video_path='test.mp4',
                category='entertainment',
                user_id=user.id
            )
            db.session.add(video)
            db.session.commit()
            
            assert video.category == 'entertainment'
    
    def test_video_without_category(self, app, test_user):
        """
        카테고리가 없는 비디오 생성 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            video = Video(
                title='카테고리 없음',
                description='설명',
                video_path='test.mp4',
                user_id=user.id
            )
            db.session.add(video)
            db.session.commit()
            
            assert video.category is None
    
    def test_video_category_filter(self, app, test_user):
        """
        카테고리로 비디오 필터링 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            # 다양한 카테고리 비디오 생성
            video1 = Video(
                title='엔터테인먼트',
                video_path='test1.mp4',
                category='entertainment',
                user_id=user.id
            )
            video2 = Video(
                title='음악',
                video_path='test2.mp4',
                category='music',
                user_id=user.id
            )
            video3 = Video(
                title='카테고리 없음',
                video_path='test3.mp4',
                user_id=user.id
            )
            db.session.add_all([video1, video2, video3])
            db.session.commit()
            
            # 엔터테인먼트 카테고리만 필터링
            entertainment_videos = Video.query.filter_by(category='entertainment').all()
            assert len(entertainment_videos) == 1
            assert entertainment_videos[0].title == '엔터테인먼트'
            
            # 음악 카테고리만 필터링
            music_videos = Video.query.filter_by(category='music').all()
            assert len(music_videos) == 1
            assert music_videos[0].title == '음악'


class TestCategoryUpload:
    """카테고리 업로드 폼 테스트"""
    
    def test_upload_form_has_category_field(self, authenticated_client):
        """
        업로드 폼에 카테고리 필드가 있는지 테스트
        """
        response = authenticated_client.get('/studio/upload')
        
        assert response.status_code == 200
        assert '카테고리' in response.data.decode('utf-8')
        # 모든 카테고리 옵션이 있는지 확인
        for category_name in Config.VIDEO_CATEGORIES.values():
            assert category_name in response.data.decode('utf-8')


class TestCategoryEdit:
    """카테고리 수정 테스트"""
    
    def test_edit_video_category(self, authenticated_client, app, test_user, test_video):
        """
        비디오 카테고리 수정 테스트
        """
        with app.app_context():
            video = Video.query.filter_by(title='테스트 비디오').first()
            video_id = video.id
        
        # 카테고리 수정
        response = authenticated_client.post(
            f'/studio/edit/{video_id}',
            data={
                'title': '테스트 비디오',
                'description': '설명',
                'category': 'music'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # 데이터베이스에서 확인
        with app.app_context():
            video = Video.query.get(video_id)
            assert video.category == 'music'
    
    def test_edit_remove_category(self, authenticated_client, app, test_user):
        """
        비디오 카테고리 제거 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            video = Video(
                title='카테고리 있음',
                description='설명',
                video_path='test.mp4',
                category='entertainment',
                user_id=user.id
            )
            db.session.add(video)
            db.session.commit()
            video_id = video.id
        
        # 카테고리 제거 (빈 값)
        response = authenticated_client.post(
            f'/studio/edit/{video_id}',
            data={
                'title': '카테고리 있음',
                'description': '설명',
                'category': ''
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # 데이터베이스에서 확인
        with app.app_context():
            video = Video.query.get(video_id)
            assert video.category is None


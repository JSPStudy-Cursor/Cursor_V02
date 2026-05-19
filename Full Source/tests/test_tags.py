"""
비디오 태그 기능 테스트
비디오 태그 기능을 테스트합니다.
"""
import pytest
from app import db
from app.models import Video, User, Tag


class TestTagModel:
    """태그 모델 테스트"""
    
    def test_tag_creation(self, app):
        """
        태그 생성 테스트
        """
        with app.app_context():
            tag = Tag(name='테스트태그')
            db.session.add(tag)
            db.session.commit()
            
            assert tag.id is not None
            assert tag.name == '테스트태그'
    
    def test_tag_unique(self, app):
        """
        태그 이름 중복 방지 테스트
        """
        with app.app_context():
            tag1 = Tag(name='중복태그')
            db.session.add(tag1)
            db.session.commit()
            
            # 같은 이름의 태그 생성 시도
            tag2 = Tag(name='중복태그')
            db.session.add(tag2)
            
            # 중복 에러 발생해야 함
            with pytest.raises(Exception):
                db.session.commit()
    
    def test_video_tag_relationship(self, app, test_user):
        """
        비디오-태그 관계 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag = Tag(name='테스트태그')
            db.session.add(tag)
            db.session.flush()
            
            # 비디오 생성
            video = Video(
                title='태그 테스트 비디오',
                description='설명',
                video_path='test.mp4',
                user_id=user.id
            )
            db.session.add(video)
            db.session.flush()
            
            # 태그 연결
            video.tags.append(tag)
            db.session.commit()
            
            # 관계 확인
            assert tag in video.tags.all()
            assert video in tag.videos.all()


class TestTagRoutes:
    """태그 라우트 테스트"""
    
    def test_tag_videos_page(self, client, app, test_user):
        """
        태그별 비디오 목록 페이지 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag = Tag(name='테스트태그')
            db.session.add(tag)
            db.session.flush()
            
            # 태그가 있는 비디오 생성
            video = Video(
                title='태그 비디오',
                description='설명',
                video_path='test.mp4',
                user_id=user.id
            )
            video.tags.append(tag)
            db.session.add(video)
            db.session.commit()
        
        # 태그별 비디오 목록 페이지 접근
        response = client.get('/tag/테스트태그')
        
        assert response.status_code == 200
        assert '테스트태그' in response.data.decode('utf-8')
        assert '태그 비디오' in response.data.decode('utf-8')
    
    def test_tag_videos_not_found(self, client):
        """
        존재하지 않는 태그 페이지 테스트
        """
        response = client.get('/tag/존재하지않는태그')
        
        assert response.status_code == 404
    
    def test_tag_videos_with_sorting(self, client, app, test_user):
        """
        태그별 비디오 목록 정렬 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag = Tag(name='정렬태그')
            db.session.add(tag)
            db.session.flush()
            
            # 여러 비디오 생성
            video1 = Video(
                title='비디오1',
                video_path='test1.mp4',
                likes=10,
                user_id=user.id
            )
            video2 = Video(
                title='비디오2',
                video_path='test2.mp4',
                likes=20,
                user_id=user.id
            )
            video1.tags.append(tag)
            video2.tags.append(tag)
            db.session.add_all([video1, video2])
            db.session.commit()
        
        # 인기순 정렬
        response = client.get('/tag/정렬태그?sort=popular')
        
        assert response.status_code == 200
        assert '정렬태그' in response.data.decode('utf-8')


class TestTagUpload:
    """태그 업로드 테스트"""
    
    def test_upload_form_has_tag_field(self, authenticated_client):
        """
        업로드 폼에 태그 필드가 있는지 테스트
        """
        response = authenticated_client.get('/studio/upload')
        
        assert response.status_code == 200
        assert '태그' in response.data.decode('utf-8')
        assert '쉼표로 구분' in response.data.decode('utf-8')
    
    def test_edit_form_has_tag_field(self, authenticated_client, test_video):
        """
        수정 폼에 태그 필드가 있는지 테스트
        """
        response = authenticated_client.get(f'/studio/edit/{test_video.id}')
        
        assert response.status_code == 200
        assert '태그' in response.data.decode('utf-8')


class TestTagEdit:
    """태그 수정 테스트"""
    
    def test_edit_video_tags(self, authenticated_client, app, test_user, test_video):
        """
        비디오 태그 수정 테스트
        """
        with app.app_context():
            video = Video.query.filter_by(title='테스트 비디오').first()
            video_id = video.id
        
        # 태그 수정
        response = authenticated_client.post(
            f'/studio/edit/{video_id}',
            data={
                'title': '테스트 비디오',
                'description': '설명',
                'tags': '태그1, 태그2, 태그3'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # 데이터베이스에서 확인
        with app.app_context():
            video = Video.query.get(video_id)
            tag_names = [tag.name for tag in video.tags.all()]
            assert '태그1' in tag_names
            assert '태그2' in tag_names
            assert '태그3' in tag_names
    
    def test_edit_remove_tags(self, authenticated_client, app, test_user):
        """
        비디오 태그 제거 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag = Tag(name='제거태그')
            db.session.add(tag)
            db.session.flush()
            
            # 태그가 있는 비디오 생성
            video = Video(
                title='태그 있음',
                description='설명',
                video_path='test.mp4',
                user_id=user.id
            )
            video.tags.append(tag)
            db.session.add(video)
            db.session.commit()
            video_id = video.id
        
        # 태그 제거 (빈 값)
        response = authenticated_client.post(
            f'/studio/edit/{video_id}',
            data={
                'title': '태그 있음',
                'description': '설명',
                'tags': ''
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # 데이터베이스에서 확인
        with app.app_context():
            video = Video.query.get(video_id)
            assert video.tags.count() == 0


class TestTagDisplay:
    """태그 표시 테스트"""
    
    def test_popular_tags_on_index(self, client, app, test_user):
        """
        메인 페이지에 인기 태그 표시 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag = Tag(name='인기태그')
            db.session.add(tag)
            db.session.flush()
            
            # 태그가 있는 비디오 생성
            video = Video(
                title='인기 비디오',
                video_path='test.mp4',
                user_id=user.id
            )
            video.tags.append(tag)
            db.session.add(video)
            db.session.commit()
        
        # 메인 페이지 접근
        response = client.get('/')
        
        assert response.status_code == 200
        assert '인기 태그' in response.data.decode('utf-8')
        assert '인기태그' in response.data.decode('utf-8')
    
    def test_tags_on_watch_page(self, client, app, test_user):
        """
        비디오 시청 페이지에 태그 표시 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag1 = Tag(name='태그1')
            tag2 = Tag(name='태그2')
            db.session.add_all([tag1, tag2])
            db.session.flush()
            
            # 태그가 있는 비디오 생성
            video = Video(
                title='태그 비디오',
                description='설명',
                video_path='test.mp4',
                user_id=user.id
            )
            video.tags.append(tag1)
            video.tags.append(tag2)
            db.session.add(video)
            db.session.commit()
            video_id = video.id
        
        # 비디오 시청 페이지 접근
        response = client.get(f'/watch/{video_id}')
        
        assert response.status_code == 200
        assert '태그1' in response.data.decode('utf-8')
        assert '태그2' in response.data.decode('utf-8')


class TestTagProcessing:
    """태그 처리 로직 테스트"""
    
    def test_tag_processing_comma_separated(self, app, test_user):
        """
        쉼표로 구분된 태그 처리 테스트
        """
        from app.routes.studio import process_tags
        
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 처리
            tags = process_tags('태그1, 태그2, 태그3')
            
            assert len(tags) == 3
            tag_names = [tag.name for tag in tags]
            assert '태그1' in tag_names
            assert '태그2' in tag_names
            assert '태그3' in tag_names
    
    def test_tag_processing_duplicate_removal(self, app, test_user):
        """
        중복 태그 제거 테스트
        """
        from app.routes.studio import process_tags
        
        with app.app_context():
            # 태그 처리 (중복 포함)
            tags = process_tags('태그1, 태그2, 태그1, 태그3')
            
            assert len(tags) == 3  # 중복 제거됨
            tag_names = [tag.name for tag in tags]
            assert tag_names.count('태그1') == 1
    
    def test_tag_processing_empty_string(self, app, test_user):
        """
        빈 문자열 태그 처리 테스트
        """
        from app.routes.studio import process_tags
        
        with app.app_context():
            tags = process_tags('')
            
            assert len(tags) == 0
    
    def test_tag_processing_whitespace(self, app, test_user):
        """
        공백이 포함된 태그 처리 테스트
        """
        from app.routes.studio import process_tags
        
        with app.app_context():
            tags = process_tags('  태그1  ,  태그2  ,  태그3  ')
            
            assert len(tags) == 3
            tag_names = [tag.name for tag in tags]
            assert '태그1' in tag_names
            assert '태그2' in tag_names
            assert '태그3' in tag_names


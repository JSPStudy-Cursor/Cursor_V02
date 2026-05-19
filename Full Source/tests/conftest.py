"""
pytest 설정 파일
테스트에 필요한 공통 픽스처를 정의합니다.
"""
import pytest
import os
import tempfile
import shutil
from app import create_app, db
from app.models import User, Video, Comment
from config import TestingConfig


@pytest.fixture
def app():
    """
    테스트용 Flask 애플리케이션 생성
    
    Returns:
        Flask 애플리케이션 인스턴스
    """
    # 임시 디렉토리 생성 (업로드 폴더용)
    test_upload_dir = tempfile.mkdtemp()
    test_video_dir = os.path.join(test_upload_dir, 'videos')
    test_thumbnail_dir = os.path.join(test_upload_dir, 'thumbnails')
    test_profile_dir = os.path.join(test_upload_dir, 'profiles')
    os.makedirs(test_video_dir, exist_ok=True)
    os.makedirs(test_thumbnail_dir, exist_ok=True)
    os.makedirs(test_profile_dir, exist_ok=True)
    
    # 테스트 설정 수정
    TestingConfig.UPLOAD_FOLDER = test_upload_dir
    TestingConfig.VIDEO_FOLDER = test_video_dir
    TestingConfig.THUMBNAIL_FOLDER = test_thumbnail_dir
    TestingConfig.PROFILE_IMAGE_FOLDER = test_profile_dir
    
    # 테스트 환경에서는 Cloudinary 사용 안 함 (로컬 저장소 사용)
    import os
    if 'CLOUDINARY_CLOUD_NAME' in os.environ:
        del os.environ['CLOUDINARY_CLOUD_NAME']
    
    app = create_app('testing')
    
    # 테스트 환경에서는 Cloudinary 미사용으로 설정
    app.config['USE_CLOUDINARY'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # 임시 디렉토리 정리
    shutil.rmtree(test_upload_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    """
    테스트 클라이언트 생성
    
    Args:
        app: Flask 애플리케이션
    
    Returns:
        Flask 테스트 클라이언트
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    CLI 테스트 러너 생성
    
    Args:
        app: Flask 애플리케이션
    
    Returns:
        Flask CLI 테스트 러너
    """
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """
    테스트용 사용자 생성
    
    Args:
        app: Flask 애플리케이션
    
    Returns:
        User 객체
    """
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            nickname='테스트유저'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        # 세션 분리 방지를 위해 id를 저장
        user_id = user.id
        db.session.expunge(user)
        # 다시 조회하여 반환
        return User.query.get(user_id)


@pytest.fixture
def test_user2(app):
    """
    테스트용 두 번째 사용자 생성
    
    Args:
        app: Flask 애플리케이션
    
    Returns:
        User 객체
    """
    with app.app_context():
        user = User(
            username='testuser2',
            email='test2@example.com',
            nickname='테스트유저2'
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        # 세션 분리 방지를 위해 id를 저장
        user_id = user.id
        db.session.expunge(user)
        # 다시 조회하여 반환
        return User.query.get(user_id)


@pytest.fixture
def test_video(app, test_user):
    """
    테스트용 비디오 생성
    
    Args:
        app: Flask 애플리케이션
        test_user: 테스트 사용자
    
    Returns:
        Video 객체
    """
    with app.app_context():
        # test_user를 다시 조회하여 같은 세션에서 사용
        user = User.query.filter_by(username='testuser').first()
        video = Video(
            title='테스트 비디오',
            description='테스트 설명',
            video_path='test_video.mp4',
            user_id=user.id
        )
        db.session.add(video)
        db.session.commit()
        db.session.refresh(video)
        return video


@pytest.fixture
def authenticated_client(client, test_user):
    """
    로그인된 테스트 클라이언트 생성
    
    Args:
        client: 테스트 클라이언트
        test_user: 테스트 사용자
    
    Returns:
        로그인된 테스트 클라이언트
    """
    # 로그인
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    }, follow_redirects=True)
    return client


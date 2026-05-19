"""
Cloudinary 기능 테스트
Cloudinary 미디어 저장소 연동 기능을 테스트합니다.
"""
import pytest
import os
from io import BytesIO
from unittest.mock import patch, MagicMock
from app import db
from app.models import Video, User
from app.utils.cloudinary_utils import upload_video, upload_thumbnail, upload_profile_image, delete_file


class TestCloudinaryUtils:
    """Cloudinary 유틸리티 함수 테스트"""
    
    @patch('app.utils.cloudinary_utils.cloudinary.uploader.upload')
    def test_upload_video_success(self, mock_upload, app):
        """
        비디오 업로드 성공 테스트
        """
        # Mock 설정
        mock_upload.return_value = {
            'secure_url': 'https://res.cloudinary.com/test/video/upload/v123/test.mp4',
            'public_id': 'wetube/videos/videos/1',
            'format': 'mp4'
        }
        
        # 테스트 파일 생성
        test_file = BytesIO(b'fake video content')
        test_file.name = 'test.mp4'
        
        with app.app_context():
            result = upload_video(test_file, 1)
            
            assert result['url'] == 'https://res.cloudinary.com/test/video/upload/v123/test.mp4'
            assert result['public_id'] == 'wetube/videos/videos/1'
            assert result['format'] == 'mp4'
            
            # Cloudinary upload 호출 확인
            mock_upload.assert_called_once()
            call_args = mock_upload.call_args
            assert call_args[1]['resource_type'] == 'video'
            assert call_args[1]['folder'] == 'wetube/videos'
    
    @patch('app.utils.cloudinary_utils.cloudinary.uploader.upload')
    def test_upload_video_failure(self, mock_upload, app):
        """
        비디오 업로드 실패 테스트
        """
        # Mock 설정 - 예외 발생
        mock_upload.side_effect = Exception("Cloudinary API 오류")
        
        test_file = BytesIO(b'fake video content')
        test_file.name = 'test.mp4'
        
        with app.app_context():
            with pytest.raises(Exception) as exc_info:
                upload_video(test_file, 1)
            
            assert "Cloudinary API 오류" in str(exc_info.value)
    
    @patch('app.utils.cloudinary_utils.cloudinary.uploader.upload')
    def test_upload_thumbnail_success(self, mock_upload, app):
        """
        썸네일 업로드 성공 테스트
        """
        # Mock 설정
        mock_upload.return_value = {
            'secure_url': 'https://res.cloudinary.com/test/image/upload/v123/test.jpg',
            'public_id': 'wetube/thumbnails/thumbnails/1'
        }
        
        # 테스트 이미지 생성
        test_file = BytesIO(b'fake image content')
        test_file.name = 'test.jpg'
        
        with app.app_context():
            result = upload_thumbnail(test_file, 1)
            
            assert result['url'] == 'https://res.cloudinary.com/test/image/upload/v123/test.jpg'
            assert result['public_id'] == 'wetube/thumbnails/thumbnails/1'
            
            # Cloudinary upload 호출 확인
            mock_upload.assert_called_once()
            call_args = mock_upload.call_args
            assert call_args[1]['resource_type'] == 'image'
            assert call_args[1]['folder'] == 'wetube/thumbnails'
    
    @patch('app.utils.cloudinary_utils.cloudinary.uploader.upload')
    def test_upload_profile_image_success(self, mock_upload, app):
        """
        프로필 이미지 업로드 성공 테스트
        """
        # Mock 설정
        mock_upload.return_value = {
            'secure_url': 'https://res.cloudinary.com/test/image/upload/v123/profile.jpg',
            'public_id': 'wetube/profiles/profiles/1'
        }
        
        test_file = BytesIO(b'fake image content')
        test_file.name = 'profile.jpg'
        
        with app.app_context():
            result = upload_profile_image(test_file, 1)
            
            assert result['url'] == 'https://res.cloudinary.com/test/image/upload/v123/profile.jpg'
            assert result['public_id'] == 'wetube/profiles/profiles/1'
            
            # Cloudinary upload 호출 확인
            mock_upload.assert_called_once()
            call_args = mock_upload.call_args
            assert call_args[1]['resource_type'] == 'image'
            assert call_args[1]['folder'] == 'wetube/profiles'
    
    @patch('app.utils.cloudinary_utils.cloudinary.uploader.destroy')
    def test_delete_file_success(self, mock_destroy, app):
        """
        파일 삭제 성공 테스트
        """
        mock_destroy.return_value = {'result': 'ok'}
        
        with app.app_context():
            delete_file('test_public_id', resource_type='video')
            
            mock_destroy.assert_called_once_with('test_public_id', resource_type='video')
    
    @patch('app.utils.cloudinary_utils.cloudinary.uploader.destroy')
    def test_delete_file_failure(self, mock_destroy, app):
        """
        파일 삭제 실패 테스트 (이미 삭제된 파일)
        """
        mock_destroy.side_effect = Exception("파일을 찾을 수 없음")
        
        with app.app_context():
            # 예외가 발생해도 계속 진행되어야 함
            delete_file('test_public_id', resource_type='image')
            
            mock_destroy.assert_called_once()


class TestCloudinaryConfig:
    """Cloudinary 설정 테스트"""
    
    def test_use_cloudinary_true_when_configured(self, app):
        """
        Cloudinary 설정이 있을 때 USE_CLOUDINARY가 True인지 테스트
        """
        with app.app_context():
            # 환경 변수 설정
            os.environ['CLOUDINARY_CLOUD_NAME'] = 'test-cloud'
            os.environ['CLOUDINARY_API_KEY'] = 'test-key'
            os.environ['CLOUDINARY_API_SECRET'] = 'test-secret'
            
            from config import Config
            use_cloudinary = Config.get_use_cloudinary()
            
            assert use_cloudinary is True
    
    def test_use_cloudinary_false_when_not_configured(self, app):
        """
        Cloudinary 설정이 없을 때 USE_CLOUDINARY가 False인지 테스트
        """
        with app.app_context():
            # 환경 변수 제거
            if 'CLOUDINARY_CLOUD_NAME' in os.environ:
                del os.environ['CLOUDINARY_CLOUD_NAME']
            
            from config import Config
            use_cloudinary = Config.get_use_cloudinary()
            
            assert use_cloudinary is False


class TestCloudinaryVideoUpload:
    """Cloudinary를 사용한 비디오 업로드 테스트"""
    
    @patch('app.utils.cloudinary_utils.upload_video')
    @patch('app.utils.cloudinary_utils.upload_thumbnail')
    def test_video_upload_with_cloudinary(self, mock_upload_thumbnail, mock_upload_video, authenticated_client, app, test_user):
        """
        Cloudinary를 사용한 비디오 업로드 테스트
        """
        # Mock 설정
        mock_upload_video.return_value = {
            'url': 'https://res.cloudinary.com/test/video/upload/v123/test.mp4',
            'public_id': 'wetube/videos/videos/1',
            'format': 'mp4'
        }
        
        # Cloudinary 사용 설정
        with app.app_context():
            app.config['USE_CLOUDINARY'] = True
            
            # 테스트 비디오 파일 생성
            test_video = BytesIO(b'fake video content')
            test_video.name = 'test_video.mp4'
            
            # 업로드 요청
            response = authenticated_client.post('/studio/upload', data={
                'title': 'Cloudinary 테스트 비디오',
                'description': 'Cloudinary 업로드 테스트',
                'video': (test_video, 'test_video.mp4')
            }, content_type='multipart/form-data', follow_redirects=True)
            
            # 응답 확인
            assert response.status_code == 200
            
            # 데이터베이스 확인
            video = Video.query.filter_by(title='Cloudinary 테스트 비디오').first()
            assert video is not None
            # Cloudinary를 사용하는 경우 URL이 저장됨
            if app.config.get('USE_CLOUDINARY'):
                assert 'cloudinary.com' in video.video_path or video.video_public_id is not None
    
    def test_video_upload_without_cloudinary(self, authenticated_client, app, test_user):
        """
        Cloudinary 없이 로컬 저장소에 업로드 테스트
        """
        # Cloudinary 미사용 설정
        with app.app_context():
            app.config['USE_CLOUDINARY'] = False
            
            # 테스트 비디오 파일 생성
            test_video = BytesIO(b'fake video content')
            test_video.name = 'test_video.mp4'
            
            # 업로드 요청
            response = authenticated_client.post('/studio/upload', data={
                'title': '로컬 저장소 테스트 비디오',
                'description': '로컬 저장소 업로드 테스트',
                'video': (test_video, 'test_video.mp4')
            }, content_type='multipart/form-data', follow_redirects=True)
            
            # 응답 확인
            assert response.status_code == 200
            
            # 데이터베이스 확인
            video = Video.query.filter_by(title='로컬 저장소 테스트 비디오').first()
            assert video is not None
            assert 'cloudinary.com' not in video.video_path
            assert video.video_public_id is None


class TestCloudinaryProfileImage:
    """Cloudinary를 사용한 프로필 이미지 업로드 테스트"""
    
    @patch('app.utils.cloudinary_utils.upload_profile_image')
    def test_profile_image_upload_with_cloudinary(self, mock_upload, authenticated_client, app, test_user):
        """
        Cloudinary를 사용한 프로필 이미지 업로드 테스트
        """
        # Mock 설정
        mock_upload.return_value = {
            'url': 'https://res.cloudinary.com/test/image/upload/v123/profile.jpg',
            'public_id': 'wetube/profiles/profiles/1'
        }
        
        # Cloudinary 사용 설정
        with app.app_context():
            app.config['USE_CLOUDINARY'] = True
            
            # 테스트 이미지 생성 (실제 PNG 이미지)
            from PIL import Image
            import io
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # 프로필 이미지 업로드 요청
            response = authenticated_client.post('/auth/profile', data={
                'nickname': '테스트유저',
                'email': 'test@example.com',
                'profile_image': (img_bytes, 'profile.png')
            }, content_type='multipart/form-data', follow_redirects=True)
            
            # 응답 확인
            assert response.status_code == 200
            
            # 데이터베이스 확인
            user = User.query.get(test_user.id)
            # Cloudinary를 사용하는 경우 URL이 저장됨
            if app.config.get('USE_CLOUDINARY'):
                assert 'cloudinary.com' in user.profile_image or user.profile_image_public_id is not None


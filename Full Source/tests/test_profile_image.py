"""
프로필 이미지 업로드 기능 테스트
프로필 이미지 업로드 및 표시 기능을 테스트합니다.
"""
import pytest
import os
import io
from PIL import Image
from app import db
from app.models import User
from config import Config


class TestProfileImageUpload:
    """프로필 이미지 업로드 테스트"""
    
    def test_profile_image_upload_page(self, authenticated_client):
        """
        프로필 이미지 업로드 페이지 접근 테스트
        """
        response = authenticated_client.get('/auth/profile')
        
        assert response.status_code == 200
        assert '프로필 이미지'.encode('utf-8') in response.data
        assert b'profile_image' in response.data
    
    def test_profile_image_upload_success(self, authenticated_client, app):
        """
        프로필 이미지 업로드 성공 테스트
        """
        # 실제 PNG 이미지 파일 생성
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            old_profile_image = user.profile_image
        
        # 프로필 이미지 업로드
        response = authenticated_client.post(
            '/auth/profile',
            data={
                'nickname': '테스트유저',
                'email': 'test@example.com',
                'profile_image': (img_bytes, 'test.png')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # 데이터베이스에서 프로필 이미지 확인
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user.profile_image is not None
            assert user.profile_image != old_profile_image
            assert user.profile_image.endswith('.png')
    
    def test_profile_image_upload_invalid_format(self, authenticated_client, app):
        """
        잘못된 형식의 이미지 업로드 테스트
        """
        # 텍스트 파일을 이미지로 업로드 시도
        text_data = b'This is not an image'
        
        response = authenticated_client.post(
            '/auth/profile',
            data={
                'nickname': '테스트유저',
                'email': 'test@example.com',
                'profile_image': (io.BytesIO(text_data), 'test.txt')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert '지원하지 않는 이미지 형식'.encode('utf-8') in response.data
        
        # 데이터베이스에서 프로필 이미지가 변경되지 않았는지 확인
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            # 기존 프로필 이미지가 없으므로 None이어야 함
            assert user.profile_image is None or user.profile_image == ''
    
    def test_profile_image_replace(self, authenticated_client, app):
        """
        기존 프로필 이미지 교체 테스트
        """
        # 첫 번째 이미지 업로드
        img1 = Image.new('RGB', (100, 100), color='blue')
        img_bytes1 = io.BytesIO()
        img1.save(img_bytes1, format='PNG')
        img_bytes1.seek(0)
        
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            old_profile_image = user.profile_image
        
        response1 = authenticated_client.post(
            '/auth/profile',
            data={
                'nickname': '테스트유저',
                'email': 'test@example.com',
                'profile_image': (img_bytes1, 'test1.png')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        assert response1.status_code == 200
        
        # 두 번째 이미지로 교체
        img2 = Image.new('RGB', (100, 100), color='green')
        img_bytes2 = io.BytesIO()
        img2.save(img_bytes2, format='PNG')
        img_bytes2.seek(0)
        
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            first_profile_image = user.profile_image
        
        response2 = authenticated_client.post(
            '/auth/profile',
            data={
                'nickname': '테스트유저',
                'email': 'test@example.com',
                'profile_image': (img_bytes2, 'test2.png')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        assert response2.status_code == 200
        
        # 데이터베이스에서 새로운 프로필 이미지 확인
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user.profile_image is not None
            assert user.profile_image != first_profile_image
            assert user.profile_image.endswith('.png')
    
    def test_profile_image_display_in_profile_page(self, authenticated_client, app):
        """
        프로필 페이지에서 프로필 이미지 표시 테스트
        """
        # 프로필 이미지 업로드
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        authenticated_client.post(
            '/auth/profile',
            data={
                'nickname': '테스트유저',
                'email': 'test@example.com',
                'profile_image': (img_bytes, 'test.png')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        # 프로필 페이지 접근
        response = authenticated_client.get('/auth/profile')
        
        assert response.status_code == 200
        
        # 프로필 이미지가 표시되는지 확인
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            if user.profile_image:
                assert user.profile_image.encode('utf-8') in response.data or \
                       b'profile-image-preview' in response.data
    
    def test_profile_image_display_in_user_profile(self, authenticated_client, app):
        """
        사용자 프로필 페이지에서 프로필 이미지 표시 테스트
        """
        # 프로필 이미지 업로드
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        authenticated_client.post(
            '/auth/profile',
            data={
                'nickname': '테스트유저',
                'email': 'test@example.com',
                'profile_image': (img_bytes, 'test.png')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        # 사용자 프로필 페이지 접근
        response = authenticated_client.get('/user/testuser')
        
        assert response.status_code == 200
        
        # 프로필 이미지가 표시되는지 확인
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            if user.profile_image:
                # 프로필 이미지 URL이 포함되어 있는지 확인
                assert b'uploads/profiles' in response.data or \
                       b'serve_profile_image' in response.data
    
    def test_profile_image_serving(self, authenticated_client, app):
        """
        프로필 이미지 서빙 테스트
        """
        # 프로필 이미지 업로드
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        authenticated_client.post(
            '/auth/profile',
            data={
                'nickname': '테스트유저',
                'email': 'test@example.com',
                'profile_image': (img_bytes, 'test.png')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        
        # 업로드된 이미지 파일명 가져오기
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            if user.profile_image:
                # 프로필 이미지 서빙 엔드포인트 접근
                response = authenticated_client.get(
                    f'/uploads/profiles/{user.profile_image}'
                )
                
                # 이미지 파일이 제공되는지 확인
                assert response.status_code == 200
                assert response.content_type.startswith('image/')
    
    def test_profile_image_placeholder_when_no_image(self, authenticated_client, app):
        """
        프로필 이미지가 없을 때 플레이스홀더 표시 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            user.profile_image = None
            db.session.commit()
        
        # 사용자 프로필 페이지 접근
        response = authenticated_client.get('/user/testuser')
        
        assert response.status_code == 200
        # 플레이스홀더가 표시되는지 확인 (사용자명의 첫 글자)
        assert b'profile-avatar-placeholder' in response.data or \
               b'testuser'[0].encode('utf-8') in response.data


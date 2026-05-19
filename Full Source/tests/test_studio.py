"""
스튜디오 기능 테스트
비디오 수정 및 삭제 기능을 테스트합니다.
"""
import pytest
import os
from io import BytesIO
from app import db
from app.models import Video, User


class TestVideoEdit:
    """비디오 수정 기능 테스트"""
    
    def test_edit_video_get(self, authenticated_client, test_video, test_user):
        """
        비디오 수정 페이지 접근 테스트 (GET)
        """
        response = authenticated_client.get(f'/studio/edit/{test_video.id}')
        
        assert response.status_code == 200
        assert '동영상 수정'.encode('utf-8') in response.data
        assert test_video.title.encode('utf-8') in response.data
    
    def test_edit_video_unauthorized(self, authenticated_client, test_video, test_user2, app):
        """
        다른 사용자의 비디오 수정 시도 테스트 (권한 없음)
        """
        # 다른 사용자의 비디오 생성
        with app.app_context():
            other_video = Video(
                title='다른 사용자 비디오',
                description='설명',
                video_path='other_video.mp4',
                user_id=test_user2.id
            )
            db.session.add(other_video)
            db.session.commit()
            video_id = other_video.id
        
        response = authenticated_client.get(f'/studio/edit/{video_id}', follow_redirects=True)
        
        assert response.status_code == 200
        assert '권한이 없습니다'.encode('utf-8') in response.data
    
    def test_edit_video_title_description(self, authenticated_client, test_video):
        """
        비디오 제목과 설명 수정 테스트
        """
        response = authenticated_client.post(
            f'/studio/edit/{test_video.id}',
            data={
                'title': '수정된 제목',
                'description': '수정된 설명'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert '비디오가 수정되었습니다'.encode('utf-8') in response.data
        
        # 데이터베이스에서 수정 확인
        with authenticated_client.application.app_context():
            updated_video = Video.query.get(test_video.id)
            assert updated_video.title == '수정된 제목'
            assert updated_video.description == '수정된 설명'
    
    def test_edit_video_empty_title(self, authenticated_client, test_video):
        """
        빈 제목으로 수정 시도 테스트
        """
        response = authenticated_client.post(
            f'/studio/edit/{test_video.id}',
            data={
                'title': '',
                'description': '설명'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        # 검증 함수에서 반환하는 에러 메시지 확인
        assert ('제목을 입력해주세요' in response.data.decode('utf-8') or 
                '제목은 필수입니다' in response.data.decode('utf-8'))


class TestVideoDelete:
    """비디오 삭제 기능 테스트"""
    
    def test_delete_video_success(self, authenticated_client, test_video, app):
        """
        비디오 삭제 성공 테스트
        """
        video_id = test_video.id
        
        response = authenticated_client.post(
            f'/studio/delete/{video_id}',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert '비디오가 삭제되었습니다'.encode('utf-8') in response.data
        
        # 데이터베이스에서 삭제 확인
        with app.app_context():
            deleted_video = Video.query.get(video_id)
            assert deleted_video is None
    
    def test_delete_video_unauthorized(self, authenticated_client, test_user2, app):
        """
        다른 사용자의 비디오 삭제 시도 테스트 (권한 없음)
        """
        # 다른 사용자의 비디오 생성
        with app.app_context():
            other_video = Video(
                title='다른 사용자 비디오',
                description='설명',
                video_path='other_video.mp4',
                user_id=test_user2.id
            )
            db.session.add(other_video)
            db.session.commit()
            video_id = other_video.id
        
        response = authenticated_client.post(
            f'/studio/delete/{video_id}',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert '권한이 없습니다'.encode('utf-8') in response.data
        
        # 비디오가 삭제되지 않았는지 확인
        with app.app_context():
            video = Video.query.get(video_id)
            assert video is not None
    
    def test_delete_video_with_comments(self, authenticated_client, test_video, test_user, app):
        """
        댓글이 있는 비디오 삭제 테스트 (cascade 삭제 확인)
        """
        # 댓글 생성
        with app.app_context():
            from app.models import Comment
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        video_id = test_video.id
        
        # 비디오 삭제
        response = authenticated_client.post(
            f'/studio/delete/{video_id}',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        
        # 비디오와 댓글이 모두 삭제되었는지 확인
        with app.app_context():
            from app.models import Comment
            deleted_video = Video.query.get(video_id)
            deleted_comment = Comment.query.get(comment_id)
            assert deleted_video is None
            assert deleted_comment is None


class TestVideoModel:
    """비디오 모델 테스트"""
    
    def test_video_creation(self, app, test_user):
        """
        비디오 모델 생성 테스트
        """
        with app.app_context():
            video = Video(
                title='테스트 비디오',
                description='테스트 설명',
                video_path='test.mp4',
                user_id=test_user.id
            )
            db.session.add(video)
            db.session.commit()
            
            assert video.id is not None
            assert video.title == '테스트 비디오'
            assert video.user_id == test_user.id
            assert video.author == test_user
            assert video.views == 0
            assert video.likes == 0


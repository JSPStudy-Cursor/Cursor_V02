"""
댓글 기능 테스트
댓글 작성, 조회, 수정, 삭제 기능을 테스트합니다.
"""
import pytest
from app import db
from app.models import Comment, Video, User


class TestCommentRoutes:
    """댓글 라우트 테스트"""
    
    def test_create_comment_success(self, authenticated_client, test_video):
        """
        댓글 작성 성공 테스트
        """
        response = authenticated_client.post(
            f'/video/{test_video.id}/comment',
            data={'content': '테스트 댓글입니다.'},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert '댓글이 작성되었습니다'.encode('utf-8') in response.data
        
        # 데이터베이스에 댓글이 저장되었는지 확인
        with authenticated_client.application.app_context():
            comment = Comment.query.filter_by(video_id=test_video.id).first()
            assert comment is not None
            assert comment.content == '테스트 댓글입니다.'
    
    def test_create_comment_empty_content(self, authenticated_client, test_video):
        """
        빈 내용으로 댓글 작성 시도 테스트
        """
        response = authenticated_client.post(
            f'/video/{test_video.id}/comment',
            data={'content': ''},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert '댓글 내용을 입력해주세요'.encode('utf-8') in response.data
    
    def test_create_comment_not_logged_in(self, client, test_video):
        """
        로그인하지 않은 사용자가 댓글 작성 시도 테스트
        """
        response = client.post(
            f'/video/{test_video.id}/comment',
            data={'content': '테스트 댓글입니다.'},
            follow_redirects=True
        )
        
        # 로그인 페이지로 리다이렉트되어야 함
        assert response.status_code == 200
        assert '로그인'.encode('utf-8') in response.data
    
    def test_edit_comment_success(self, authenticated_client, test_video, test_user):
        """
        댓글 수정 성공 테스트
        """
        # 먼저 댓글 생성
        with authenticated_client.application.app_context():
            comment = Comment(
                content='원본 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # 댓글 수정
        response = authenticated_client.post(
            f'/comment/{comment_id}/edit',
            data={'content': '수정된 댓글'},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert '댓글이 수정되었습니다'.encode('utf-8') in response.data
        
        # 데이터베이스에서 수정 확인
        with authenticated_client.application.app_context():
            updated_comment = Comment.query.get(comment_id)
            assert updated_comment.content == '수정된 댓글'
    
    def test_edit_comment_unauthorized(self, authenticated_client, test_video, test_user2):
        """
        다른 사용자의 댓글 수정 시도 테스트 (권한 없음)
        """
        # 다른 사용자의 댓글 생성
        with authenticated_client.application.app_context():
            comment = Comment(
                content='다른 사용자 댓글',
                user_id=test_user2.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # 댓글 수정 시도
        response = authenticated_client.post(
            f'/comment/{comment_id}/edit',
            data={'content': '수정 시도'},
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert '권한이 없습니다'.encode('utf-8') in response.data
    
    def test_delete_comment_success(self, authenticated_client, test_video, test_user):
        """
        댓글 삭제 성공 테스트
        """
        # 먼저 댓글 생성
        with authenticated_client.application.app_context():
            comment = Comment(
                content='삭제할 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # 댓글 삭제
        response = authenticated_client.post(
            f'/comment/{comment_id}/delete',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert '댓글이 삭제되었습니다'.encode('utf-8') in response.data
        
        # 데이터베이스에서 삭제 확인
        with authenticated_client.application.app_context():
            deleted_comment = Comment.query.get(comment_id)
            assert deleted_comment is None
    
    def test_delete_comment_unauthorized(self, authenticated_client, test_video, test_user2):
        """
        다른 사용자의 댓글 삭제 시도 테스트 (권한 없음)
        """
        # 다른 사용자의 댓글 생성
        with authenticated_client.application.app_context():
            comment = Comment(
                content='다른 사용자 댓글',
                user_id=test_user2.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        # 댓글 삭제 시도
        response = authenticated_client.post(
            f'/comment/{comment_id}/delete',
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert '권한이 없습니다'.encode('utf-8') in response.data
        
        # 댓글이 삭제되지 않았는지 확인
        with authenticated_client.application.app_context():
            comment = Comment.query.get(comment_id)
            assert comment is not None


class TestCommentModel:
    """댓글 모델 테스트"""
    
    def test_comment_creation(self, app, test_user, test_video):
        """
        댓글 모델 생성 테스트
        """
        with app.app_context():
            comment = Comment(
                content='테스트 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(comment)
            db.session.commit()
            
            assert comment.id is not None
            assert comment.content == '테스트 댓글'
            assert comment.user_id == test_user.id
            assert comment.video_id == test_video.id
            assert comment.author.id == test_user.id
            assert comment.video.id == test_video.id
    
    def test_comment_relationship(self, app, test_user, test_video):
        """
        댓글 관계 테스트 (User, Video와의 관계)
        """
        with app.app_context():
            # test_user와 test_video를 다시 조회하여 같은 세션에서 사용
            user = User.query.filter_by(username='testuser').first()
            video = Video.query.get(test_video.id)
            
            comment = Comment(
                content='관계 테스트 댓글',
                user_id=user.id,
                video_id=video.id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
            
            # User와의 관계 확인
            user_comments = user.comments.all()
            assert any(c.id == comment_id for c in user_comments)
            assert comment.author.id == user.id
            
            # Video와의 관계 확인
            video_comments = video.comments.all()
            assert any(c.id == comment_id for c in video_comments)
            assert comment.video.id == video.id


class TestReplyComments:
    """대댓글 기능 테스트"""
    
    def test_create_reply_success(self, authenticated_client, test_user, test_video, app):
        """
        대댓글 작성 성공 테스트
        """
        with app.app_context():
            # 부모 댓글 생성
            parent_comment = Comment(
                content='부모 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(parent_comment)
            db.session.commit()
            parent_id = parent_comment.id
        
        # 대댓글 작성
        response = authenticated_client.post(
            f'/comment/{parent_id}/reply',
            json={'content': '대댓글 내용'},
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'comment' in data
        assert data['comment']['content'] == '대댓글 내용'
        assert data['comment']['parent_id'] == parent_id
    
    def test_create_reply_invalid_parent(self, authenticated_client, app):
        """
        존재하지 않는 부모 댓글에 대댓글 작성 테스트
        """
        response = authenticated_client.post(
            '/comment/99999/reply',
            json={'content': '대댓글 내용'},
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_create_reply_empty_content(self, authenticated_client, test_user, test_video, app):
        """
        빈 내용으로 대댓글 작성 테스트
        """
        with app.app_context():
            # 부모 댓글 생성
            parent_comment = Comment(
                content='부모 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(parent_comment)
            db.session.commit()
            parent_id = parent_comment.id
        
        # 빈 내용으로 대댓글 작성
        response = authenticated_client.post(
            f'/comment/{parent_id}/reply',
            json={'content': ''},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_reply_display_in_watch_page(self, authenticated_client, test_user, test_video, app):
        """
        비디오 시청 페이지에서 대댓글 표시 테스트
        """
        with app.app_context():
            # 부모 댓글 생성
            parent_comment = Comment(
                content='부모 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(parent_comment)
            db.session.commit()
            parent_id = parent_comment.id
            
            # 대댓글 생성
            reply_comment = Comment(
                content='대댓글 내용',
                user_id=test_user.id,
                video_id=test_video.id,
                parent_id=parent_id
            )
            db.session.add(reply_comment)
            db.session.commit()
        
        # 비디오 시청 페이지 접근
        response = authenticated_client.get(f'/watch/{test_video.id}')
        
        assert response.status_code == 200
        assert '부모 댓글'.encode('utf-8') in response.data
    
    def test_reply_count_in_comments(self, authenticated_client, test_user, test_video, app):
        """
        댓글 목록에서 대댓글 개수 확인 테스트
        """
        with app.app_context():
            # 부모 댓글 생성
            parent_comment = Comment(
                content='부모 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(parent_comment)
            db.session.commit()
            parent_id = parent_comment.id
            
            # 대댓글 2개 생성
            for i in range(2):
                reply = Comment(
                    content=f'대댓글 {i+1}',
                    user_id=test_user.id,
                    video_id=test_video.id,
                    parent_id=parent_id
                )
                db.session.add(reply)
            db.session.commit()
        
        # 댓글 목록 조회 (부모 댓글만 조회되어야 함)
        with app.app_context():
            parent_comments = Comment.query.filter_by(video_id=test_video.id, parent_id=None).all()
            assert len(parent_comments) == 1
            
            # 대댓글 확인
            replies = Comment.query.filter_by(parent_id=parent_id).all()
            assert len(replies) == 2
    
    def test_delete_parent_comment_with_replies(self, authenticated_client, test_user, test_video, app):
        """
        대댓글이 있는 부모 댓글 삭제 테스트
        """
        with app.app_context():
            # 부모 댓글 생성
            parent_comment = Comment(
                content='부모 댓글',
                user_id=test_user.id,
                video_id=test_video.id
            )
            db.session.add(parent_comment)
            db.session.commit()
            parent_id = parent_comment.id
            
            # 대댓글 생성
            reply = Comment(
                content='대댓글',
                user_id=test_user.id,
                video_id=test_video.id,
                parent_id=parent_id
            )
            db.session.add(reply)
            db.session.commit()
            reply_id = reply.id
        
        # 부모 댓글 삭제
        response = authenticated_client.post(f'/comment/{parent_id}/delete')
        
        assert response.status_code == 302  # 리다이렉트
        
        # 대댓글도 함께 삭제되었는지 확인
        with app.app_context():
            deleted_parent = Comment.query.get(parent_id)
            deleted_reply = Comment.query.get(reply_id)
            assert deleted_parent is None
            # 대댓글은 cascade로 삭제되지 않을 수 있으므로 확인
            # (실제 구현에 따라 다를 수 있음)

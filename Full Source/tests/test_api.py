"""
API 엔드포인트 테스트
RESTful API 엔드포인트를 테스트합니다.
"""
import pytest
import json
from app import db
from app.models import Video, Comment, User, Tag


class TestVideoAPI:
    """비디오 API 테스트"""
    
    def test_get_videos(self, client, app, test_user, test_video):
        """
        비디오 목록 조회 API 테스트
        """
        response = client.get('/api/videos')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'videos' in data['data']
        assert 'pagination' in data['data']
    
    def test_get_videos_with_pagination(self, client, app, test_user):
        """
        비디오 목록 커서 기반 페이지네이션 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 여러 비디오 생성
            for i in range(25):
                video = Video(
                    title=f'비디오 {i}',
                    video_path=f'video{i}.mp4',
                    user_id=user.id
                )
                db.session.add(video)
            db.session.commit()
        
        # 첫 페이지 요청
        response = client.get('/api/videos?limit=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']['videos']) == 10
        assert 'next_cursor' in data['data']['pagination']
        assert data['data']['pagination']['has_next'] is True
        
        # 다음 페이지 요청 (커서 사용)
        next_cursor = data['data']['pagination']['next_cursor']
        assert next_cursor is not None
        
        response2 = client.get(f'/api/videos?limit=10&cursor={next_cursor}')
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert len(data2['data']['videos']) == 10
    
    def test_get_videos_with_sort(self, client, app, test_user):
        """
        비디오 목록 정렬 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            video1 = Video(title='비디오1', video_path='v1.mp4', likes=10, user_id=user.id)
            video2 = Video(title='비디오2', video_path='v2.mp4', likes=20, user_id=user.id)
            db.session.add_all([video1, video2])
            db.session.commit()
        
        response = client.get('/api/videos?sort=popular')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['videos'][0]['likes'] >= data['data']['videos'][1]['likes']
    
    def test_get_video_detail(self, client, app, test_user, test_video):
        """
        비디오 상세 조회 API 테스트
        """
        with app.app_context():
            video = Video.query.filter_by(title='테스트 비디오').first()
            video_id = video.id
            initial_views = video.views
        
        response = client.get(f'/api/videos/{video_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['video']['id'] == video_id
        assert data['data']['video']['views'] == initial_views + 1  # 조회수 증가 확인


class TestCommentAPI:
    """댓글 API 테스트"""
    
    def test_get_comments(self, client, app, test_user, test_video):
        """
        댓글 목록 조회 API 테스트
        """
        with app.app_context():
            video = Video.query.filter_by(title='테스트 비디오').first()
            video_id = video.id
            
            # 댓글 생성
            user = User.query.filter_by(username='testuser').first()
            comment = Comment(
                content='테스트 댓글',
                user_id=user.id,
                video_id=video_id
            )
            db.session.add(comment)
            db.session.commit()
        
        response = client.get(f'/api/videos/{video_id}/comments')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']['comments']) > 0
    
    def test_create_comment(self, authenticated_client, app, test_user, test_video):
        """
        댓글 작성 API 테스트
        """
        with app.app_context():
            video = Video.query.filter_by(title='테스트 비디오').first()
            video_id = video.id
        
        response = authenticated_client.post(
            f'/api/videos/{video_id}/comments',
            data=json.dumps({'content': '새 댓글'}),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['content'] == '새 댓글'
    
    def test_create_comment_empty_content(self, authenticated_client, app, test_user, test_video):
        """
        빈 내용 댓글 작성 테스트
        """
        with app.app_context():
            video = Video.query.filter_by(title='테스트 비디오').first()
            video_id = video.id
        
        response = authenticated_client.post(
            f'/api/videos/{video_id}/comments',
            data=json.dumps({'content': ''}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_comment(self, authenticated_client, app, test_user, test_video):
        """
        댓글 수정 API 테스트
        """
        with app.app_context():
            video = Video.query.filter_by(title='테스트 비디오').first()
            video_id = video.id
            
            user = User.query.filter_by(username='testuser').first()
            comment = Comment(
                content='원본 댓글',
                user_id=user.id,
                video_id=video_id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        response = authenticated_client.put(
            f'/api/comments/{comment_id}',
            data=json.dumps({'content': '수정된 댓글'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['content'] == '수정된 댓글'
    
    def test_delete_comment(self, authenticated_client, app, test_user, test_video):
        """
        댓글 삭제 API 테스트
        """
        with app.app_context():
            video = Video.query.filter_by(title='테스트 비디오').first()
            video_id = video.id
            
            user = User.query.filter_by(username='testuser').first()
            comment = Comment(
                content='삭제할 댓글',
                user_id=user.id,
                video_id=video_id
            )
            db.session.add(comment)
            db.session.commit()
            comment_id = comment.id
        
        response = authenticated_client.delete(f'/api/comments/{comment_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestTagAPI:
    """태그 API 테스트"""
    
    def test_get_popular_tags(self, client, app, test_user):
        """
        인기 태그 조회 API 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            tag = Tag(name='인기태그')
            db.session.add(tag)
            db.session.flush()
            
            video = Video(
                title='태그 비디오',
                video_path='test.mp4',
                user_id=user.id
            )
            video.tags.append(tag)
            db.session.add(video)
            db.session.commit()
        
        response = client.get('/api/tags/popular')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']['tags']) > 0
    
    def test_get_tag_videos(self, client, app, test_user):
        """
        태그별 비디오 목록 조회 API 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            tag = Tag(name='테스트태그')
            db.session.add(tag)
            db.session.flush()
            
            video = Video(
                title='태그 비디오',
                video_path='test.mp4',
                user_id=user.id
            )
            video.tags.append(tag)
            db.session.add(video)
            db.session.commit()
        
        response = client.get('/api/tags/테스트태그/videos')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']['videos']) > 0


class TestUserAPI:
    """사용자 API 테스트"""
    
    def test_get_user_profile(self, client, app, test_user):
        """
        사용자 프로필 조회 API 테스트
        """
        response = client.get('/api/users/testuser')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['user']['username'] == 'testuser'
        assert 'stats' in data['data']
    
    def test_get_user_videos(self, client, app, test_user, test_video):
        """
        사용자 비디오 목록 조회 API 테스트
        """
        response = client.get('/api/users/testuser/videos')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']['videos']) > 0


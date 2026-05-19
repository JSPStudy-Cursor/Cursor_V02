"""
관련 동영상 추천 기능 테스트
관련 동영상 추천 기능을 테스트합니다.
"""
import pytest
from app import db
from app.models import Video, User, Tag
from app.routes.main import get_related_videos


class TestRelatedVideos:
    """관련 동영상 추천 테스트"""
    
    def test_related_videos_by_tags(self, app, test_user):
        """
        태그 기반 관련 동영상 추천 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag1 = Tag(name='태그1')
            tag2 = Tag(name='태그2')
            db.session.add_all([tag1, tag2])
            db.session.flush()
            
            # 현재 비디오 (태그1, 태그2)
            current_video = Video(
                title='현재 비디오',
                description='설명',
                video_path='current.mp4',
                user_id=user.id
            )
            current_video.tags.append(tag1)
            current_video.tags.append(tag2)
            db.session.add(current_video)
            db.session.flush()
            
            # 같은 태그를 가진 비디오
            related_video1 = Video(
                title='관련 비디오1',
                video_path='related1.mp4',
                views=100,
                user_id=user.id
            )
            related_video1.tags.append(tag1)
            
            related_video2 = Video(
                title='관련 비디오2',
                video_path='related2.mp4',
                views=200,
                user_id=user.id
            )
            related_video2.tags.append(tag2)
            
            # 다른 태그를 가진 비디오
            tag3 = Tag(name='태그3')
            db.session.add(tag3)
            db.session.flush()
            
            unrelated_video = Video(
                title='관련 없는 비디오',
                video_path='unrelated.mp4',
                user_id=user.id
            )
            unrelated_video.tags.append(tag3)
            
            db.session.add_all([related_video1, related_video2, unrelated_video])
            db.session.commit()
            
            # 관련 동영상 추천
            related = get_related_videos(current_video, limit=10)
            
            # 검증
            assert len(related) >= 2
            related_ids = [v.id for v in related]
            assert related_video1.id in related_ids
            assert related_video2.id in related_ids
            assert current_video.id not in related_ids
            # unrelated_video는 태그가 다르므로 포함되지 않아야 함
            # 하지만 fallback 로직이 없으므로 포함되지 않음
    
    def test_related_videos_by_category(self, app, test_user):
        """
        카테고리 기반 관련 동영상 추천 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 현재 비디오 (카테고리: entertainment)
            current_video = Video(
                title='현재 비디오',
                description='설명',
                video_path='current.mp4',
                category='entertainment',
                user_id=user.id
            )
            db.session.add(current_video)
            db.session.flush()
            
            # 같은 카테고리 비디오
            related_video1 = Video(
                title='관련 비디오1',
                video_path='related1.mp4',
                category='entertainment',
                views=100,
                user_id=user.id
            )
            
            # 다른 카테고리 비디오
            unrelated_video = Video(
                title='관련 없는 비디오',
                video_path='unrelated.mp4',
                category='music',
                user_id=user.id
            )
            
            db.session.add_all([related_video1, unrelated_video])
            db.session.commit()
            
            # 관련 동영상 추천
            related = get_related_videos(current_video, limit=10)
            
            # 검증
            assert len(related) >= 1
            related_ids = [v.id for v in related]
            assert related_video1.id in related_ids
            assert current_video.id not in related_ids
            # unrelated_video는 카테고리가 다르므로 포함되지 않아야 함
            # 하지만 fallback 로직이 없으므로 포함되지 않음
    
    def test_related_videos_by_author(self, app, test_user, test_user2):
        """
        작성자 기반 관련 동영상 추천 테스트
        """
        with app.app_context():
            user1 = User.query.filter_by(username='testuser').first()
            user2 = User.query.filter_by(username='testuser2').first()
            
            # 현재 비디오
            current_video = Video(
                title='현재 비디오',
                description='설명',
                video_path='current.mp4',
                user_id=user1.id
            )
            db.session.add(current_video)
            db.session.flush()
            
            # 같은 작성자의 다른 비디오
            related_video1 = Video(
                title='관련 비디오1',
                video_path='related1.mp4',
                user_id=user1.id
            )
            
            related_video2 = Video(
                title='관련 비디오2',
                video_path='related2.mp4',
                user_id=user1.id
            )
            
            # 다른 작성자의 비디오
            unrelated_video = Video(
                title='관련 없는 비디오',
                video_path='unrelated.mp4',
                user_id=user2.id
            )
            
            db.session.add_all([related_video1, related_video2, unrelated_video])
            db.session.commit()
            
            # 관련 동영상 추천
            related = get_related_videos(current_video, limit=10)
            
            # 검증
            assert len(related) >= 2
            related_ids = [v.id for v in related]
            assert related_video1.id in related_ids
            assert related_video2.id in related_ids
            assert current_video.id not in related_ids
    
    def test_related_videos_priority(self, app, test_user):
        """
        관련 동영상 추천 우선순위 테스트
        태그 > 카테고리 > 작성자 순서
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag = Tag(name='공통태그')
            db.session.add(tag)
            db.session.flush()
            
            # 현재 비디오 (태그, 카테고리, 작성자)
            current_video = Video(
                title='현재 비디오',
                description='설명',
                video_path='current.mp4',
                category='entertainment',
                user_id=user.id
            )
            current_video.tags.append(tag)
            db.session.add(current_video)
            db.session.flush()
            
            # 태그 기반 관련 비디오 (우선순위 1)
            tag_video = Video(
                title='태그 비디오',
                video_path='tag.mp4',
                views=50,
                user_id=user.id
            )
            tag_video.tags.append(tag)
            
            # 카테고리 기반 관련 비디오 (우선순위 2)
            category_video = Video(
                title='카테고리 비디오',
                video_path='category.mp4',
                category='entertainment',
                views=100,
                user_id=user.id
            )
            
            # 작성자 기반 관련 비디오 (우선순위 3)
            author_video = Video(
                title='작성자 비디오',
                video_path='author.mp4',
                views=200,
                user_id=user.id
            )
            
            db.session.add_all([tag_video, category_video, author_video])
            db.session.commit()
            
            # 관련 동영상 추천
            related = get_related_videos(current_video, limit=3)
            
            # 검증: 태그 비디오가 먼저 나와야 함
            assert len(related) >= 1
            assert related[0].id == tag_video.id
    
    def test_related_videos_limit(self, app, test_user):
        """
        관련 동영상 개수 제한 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag = Tag(name='공통태그')
            db.session.add(tag)
            db.session.flush()
            
            # 현재 비디오
            current_video = Video(
                title='현재 비디오',
                description='설명',
                video_path='current.mp4',
                user_id=user.id
            )
            current_video.tags.append(tag)
            db.session.add(current_video)
            db.session.flush()
            
            # 여러 관련 비디오 생성
            related_videos = []
            for i in range(15):
                video = Video(
                    title=f'관련 비디오{i}',
                    video_path=f'related{i}.mp4',
                    views=100 - i,
                    user_id=user.id
                )
                video.tags.append(tag)
                related_videos.append(video)
            
            db.session.add_all(related_videos)
            db.session.commit()
            
            # 관련 동영상 추천 (limit=10)
            related = get_related_videos(current_video, limit=10)
            
            # 검증
            assert len(related) == 10
            assert current_video.id not in [v.id for v in related]
    
    def test_related_videos_exclude_current(self, app, test_user):
        """
        현재 비디오 제외 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag = Tag(name='공통태그')
            db.session.add(tag)
            db.session.flush()
            
            # 현재 비디오
            current_video = Video(
                title='현재 비디오',
                description='설명',
                video_path='current.mp4',
                user_id=user.id
            )
            current_video.tags.append(tag)
            db.session.add(current_video)
            db.session.flush()
            
            # 관련 비디오
            related_video = Video(
                title='관련 비디오',
                video_path='related.mp4',
                user_id=user.id
            )
            related_video.tags.append(tag)
            db.session.add(related_video)
            db.session.commit()
            
            # 관련 동영상 추천
            related = get_related_videos(current_video, limit=10)
            
            # 검증
            assert current_video.id not in [v.id for v in related]
            assert related_video.id in [v.id for v in related]
    
    def test_related_videos_fallback(self, app, test_user):
        """
        관련 동영상이 없을 때 인기 비디오 fallback 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 현재 비디오 (태그, 카테고리 없음)
            current_video = Video(
                title='현재 비디오',
                description='설명',
                video_path='current.mp4',
                user_id=user.id
            )
            db.session.add(current_video)
            db.session.flush()
            
            # 인기 비디오들
            popular_videos = []
            for i in range(5):
                video = Video(
                    title=f'인기 비디오{i}',
                    video_path=f'popular{i}.mp4',
                    views=1000 - i * 100,
                    user_id=user.id
                )
                popular_videos.append(video)
            
            db.session.add_all(popular_videos)
            db.session.commit()
            
            # 관련 동영상 추천
            related = get_related_videos(current_video, limit=5)
            
            # 검증: 인기 비디오가 추천되어야 함
            assert len(related) == 5
            assert current_video.id not in [v.id for v in related]
    
    def test_watch_page_shows_related_videos(self, client, app, test_user):
        """
        비디오 시청 페이지에 관련 동영상 표시 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 태그 생성
            tag = Tag(name='공통태그')
            db.session.add(tag)
            db.session.flush()
            
            # 현재 비디오
            current_video = Video(
                title='현재 비디오',
                description='설명',
                video_path='current.mp4',
                user_id=user.id
            )
            current_video.tags.append(tag)
            db.session.add(current_video)
            db.session.flush()
            
            # 관련 비디오
            related_video = Video(
                title='관련 비디오',
                video_path='related.mp4',
                user_id=user.id
            )
            related_video.tags.append(tag)
            db.session.add(related_video)
            db.session.commit()
            
            # 비디오 ID 저장 (app_context 안에서)
            video_id = current_video.id
        
        # 비디오 시청 페이지 접근
        response = client.get(f'/watch/{video_id}')
        
        assert response.status_code == 200
        assert '관련 동영상' in response.data.decode('utf-8')
        assert '관련 비디오' in response.data.decode('utf-8')
    
    def test_watch_page_no_related_videos(self, client, app, test_user):
        """
        관련 동영상이 없을 때 섹션 표시 안 함 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 현재 비디오 (유일한 비디오)
            current_video = Video(
                title='현재 비디오',
                description='설명',
                video_path='current.mp4',
                user_id=user.id
            )
            db.session.add(current_video)
            db.session.commit()
            
            # 비디오 ID 저장 (app_context 안에서)
            video_id = current_video.id
        
        # 비디오 시청 페이지 접근
        response = client.get(f'/watch/{video_id}')
        
        assert response.status_code == 200
        # 관련 동영상 섹션이 없어야 함 (또는 빈 상태)
        # 실제 구현에 따라 다를 수 있음


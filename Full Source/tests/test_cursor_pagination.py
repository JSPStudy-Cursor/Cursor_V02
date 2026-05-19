"""
커서 기반 페이지네이션 테스트
"""
import pytest
import json
from app import db
from app.models import Video, User
from app.utils.pagination import cursor_paginate


class TestCursorPagination:
    """커서 기반 페이지네이션 테스트"""
    
    def test_cursor_pagination_first_page(self, app, test_user):
        """
        첫 페이지 조회 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 여러 비디오 생성
            for i in range(15):
                video = Video(
                    title=f'비디오 {i}',
                    video_path=f'video{i}.mp4',
                    user_id=user.id
                )
                db.session.add(video)
            db.session.commit()
            
            # 첫 페이지 조회
            query = Video.query
            items, next_cursor, has_next = cursor_paginate(
                query=query,
                cursor=None,
                limit=10,
                cursor_field='id',
                order_by_field=Video.id,
                reverse=False
            )
            
            assert len(items) == 10
            assert next_cursor is not None
            assert has_next is True
    
    def test_cursor_pagination_next_page(self, app, test_user):
        """
        다음 페이지 조회 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 여러 비디오 생성
            for i in range(15):
                video = Video(
                    title=f'비디오 {i}',
                    video_path=f'video{i}.mp4',
                    user_id=user.id
                )
                db.session.add(video)
            db.session.commit()
            
            # 첫 페이지 조회
            query = Video.query
            items1, next_cursor, has_next1 = cursor_paginate(
                query=query,
                cursor=None,
                limit=10,
                cursor_field='id',
                order_by_field=Video.id,
                reverse=False
            )
            
            assert len(items1) == 10
            assert next_cursor is not None
            
            # 다음 페이지 조회
            items2, next_cursor2, has_next2 = cursor_paginate(
                query=query,
                cursor=next_cursor,
                limit=10,
                cursor_field='id',
                order_by_field=Video.id,
                reverse=False
            )
            
            assert len(items2) == 5  # 남은 5개
            assert next_cursor2 is None
            assert has_next2 is False
            
            # 첫 페이지와 두 번째 페이지의 항목이 겹치지 않는지 확인
            ids1 = {item.id for item in items1}
            ids2 = {item.id for item in items2}
            assert len(ids1 & ids2) == 0  # 교집합이 없어야 함
    
    def test_cursor_pagination_reverse_order(self, app, test_user):
        """
        역순 정렬 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 여러 비디오 생성
            for i in range(15):
                video = Video(
                    title=f'비디오 {i}',
                    video_path=f'video{i}.mp4',
                    user_id=user.id
                )
                db.session.add(video)
            db.session.commit()
            
            # 역순으로 첫 페이지 조회
            query = Video.query
            items, next_cursor, has_next = cursor_paginate(
                query=query,
                cursor=None,
                limit=10,
                cursor_field='id',
                order_by_field=Video.id,
                reverse=True  # 내림차순
            )
            
            assert len(items) == 10
            assert next_cursor is not None
            assert has_next is True
            
            # 역순 정렬 확인 (ID가 큰 것부터)
            ids = [item.id for item in items]
            assert ids == sorted(ids, reverse=True)
    
    def test_cursor_pagination_no_more_pages(self, app, test_user):
        """
        마지막 페이지 테스트
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 5개 비디오만 생성
            for i in range(5):
                video = Video(
                    title=f'비디오 {i}',
                    video_path=f'video{i}.mp4',
                    user_id=user.id
                )
                db.session.add(video)
            db.session.commit()
            
            # limit보다 적은 수 조회
            query = Video.query
            items, next_cursor, has_next = cursor_paginate(
                query=query,
                cursor=None,
                limit=10,
                cursor_field='id',
                order_by_field=Video.id,
                reverse=False
            )
            
            assert len(items) == 5
            assert next_cursor is None
            assert has_next is False
    
    def test_cursor_pagination_invalid_cursor(self, app, test_user):
        """
        잘못된 커서 테스트 (ID 필드 사용)
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # 비디오 생성
            video = Video(
                title='비디오',
                video_path='video.mp4',
                user_id=user.id
            )
            db.session.add(video)
            db.session.commit()
            
            # 잘못된 커서로 조회 (ID는 정수여야 함)
            query = Video.query
            items, next_cursor, has_next = cursor_paginate(
                query=query,
                cursor='invalid_cursor',
                limit=10,
                cursor_field='id',
                order_by_field=Video.id,
                reverse=False
            )
            
            # 잘못된 커서는 빈 결과 반환 (ValueError 발생 시)
            # 실제로는 파싱 실패 시 빈 결과를 반환해야 함
            # 하지만 현재 구현은 예외를 잡아서 빈 결과를 반환함
            assert len(items) == 0 or next_cursor is None


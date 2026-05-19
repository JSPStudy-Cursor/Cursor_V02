"""
커서 기반 페이지네이션 유틸리티
대용량 데이터에서 성능이 우수한 커서 기반 페이지네이션을 제공합니다.
"""
from typing import Optional, Tuple, List, Any
from sqlalchemy.orm import Query
from sqlalchemy import and_


def cursor_paginate(
    query: Query,
    cursor: Optional[str] = None,
    limit: int = 20,
    cursor_field: str = 'id',
    order_by_field: Any = None,
    reverse: bool = False
) -> Tuple[List[Any], Optional[str], bool]:
    """
    커서 기반 페이지네이션
    
    Args:
        query: SQLAlchemy 쿼리 객체
        cursor: 커서 값 (이전 페이지의 마지막 항목 값)
        limit: 조회할 항목 수
        cursor_field: 커서로 사용할 필드명 (기본값: 'id')
        order_by_field: 정렬 필드 (필수)
        reverse: 역순 정렬 여부 (True: 내림차순, False: 오름차순)
    
    Returns:
        (items, next_cursor, has_next) 튜플
        - items: 조회된 항목 리스트
        - next_cursor: 다음 페이지 커서 (더 이상 없으면 None)
        - has_next: 다음 페이지 존재 여부
    """
    if order_by_field is None:
        raise ValueError("order_by_field는 필수입니다.")
    
    # 정렬 적용
    if reverse:
        query = query.order_by(order_by_field.desc())
    else:
        query = query.order_by(order_by_field.asc())
    
    # 커서가 있으면 해당 커서 이후의 데이터만 조회
    if cursor:
        try:
            # 커서 값을 적절한 타입으로 변환
            cursor_value = _parse_cursor(cursor, order_by_field)
            
            if reverse:
                # 내림차순: 커서 값보다 작은 값
                query = query.filter(order_by_field < cursor_value)
            else:
                # 오름차순: 커서 값보다 큰 값
                query = query.filter(order_by_field > cursor_value)
        except (ValueError, TypeError) as e:
            # 커서 파싱 실패 시 빈 결과 반환
            return [], None, False
    
    # limit + 1개 조회하여 다음 페이지 존재 여부 확인
    items = query.limit(limit + 1).all()
    
    # 다음 페이지 존재 여부 확인
    has_next = len(items) > limit
    if has_next:
        items = items[:limit]
        # 다음 커서 생성 (마지막 항목의 커서 필드 값)
        next_cursor = _encode_cursor(getattr(items[-1], cursor_field))
    else:
        next_cursor = None
    
    return items, next_cursor, has_next


def _parse_cursor(cursor: str, field_type: Any) -> Any:
    """
    커서 문자열을 적절한 타입으로 파싱
    
    Args:
        cursor: 커서 문자열
        field_type: 필드 타입
    
    Returns:
        파싱된 커서 값
    """
    # ID는 정수
    if hasattr(field_type, 'python_type'):
        python_type = field_type.python_type
        if python_type == int:
            return int(cursor)
        elif python_type == str:
            return cursor
        # datetime 등은 ISO 형식으로 인코딩/디코딩
        elif hasattr(python_type, 'fromisoformat'):
            from datetime import datetime
            return datetime.fromisoformat(cursor)
    
    # 기본적으로 정수로 시도
    try:
        return int(cursor)
    except ValueError:
        return cursor


def _encode_cursor(value: Any) -> str:
    """
    커서 값을 문자열로 인코딩
    
    Args:
        value: 커서 값
    
    Returns:
        인코딩된 커서 문자열
    """
    if isinstance(value, int):
        return str(value)
    elif hasattr(value, 'isoformat'):
        # datetime 객체
        return value.isoformat()
    else:
        return str(value)


def create_cursor_response(
    items: List[Any],
    next_cursor: Optional[str],
    has_next: bool,
    limit: int
) -> dict:
    """
    커서 기반 페이지네이션 응답 생성
    
    Args:
        items: 조회된 항목 리스트
        next_cursor: 다음 페이지 커서
        has_next: 다음 페이지 존재 여부
        limit: 요청한 limit
    
    Returns:
        페이지네이션 정보가 포함된 딕셔너리
    """
    return {
        'items': items,
        'pagination': {
            'limit': limit,
            'count': len(items),
            'has_next': has_next,
            'next_cursor': next_cursor
        }
    }


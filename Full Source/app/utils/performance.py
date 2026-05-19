"""
성능 최적화 유틸리티
메모리 누수 방지 및 리소스 관리를 위한 헬퍼 함수들
"""
import os
import gc
from functools import wraps
from flask import g
from app import db


def cleanup_session(func):
    """
    요청 후 데이터베이스 세션 정리 데코레이터
    메모리 누수 방지를 위해 사용
    
    Args:
        func: 뷰 함수
    
    Returns:
        래핑된 함수
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # 에러 발생 시 세션 롤백
            db.session.rollback()
            raise e
        finally:
            # 세션 정리 (Flask-SQLAlchemy가 자동으로 처리하지만 명시적으로 정리)
            db.session.remove()
            # 가비지 컬렉션 강제 실행 (선택사항)
            gc.collect()
    
    return wrapper


def safe_file_operation(file_path, operation, *args, **kwargs):
    """
    안전한 파일 작업 수행
    
    Args:
        file_path: 파일 경로
        operation: 수행할 작업 함수
        *args, **kwargs: 작업 함수에 전달할 인자
    
    Returns:
        작업 결과 또는 None (실패 시)
    """
    try:
        if os.path.exists(file_path):
            return operation(file_path, *args, **kwargs)
    except Exception as e:
        print(f'파일 작업 오류: {str(e)}')
        return None
    finally:
        # 파일 핸들러가 열려있다면 닫기
        pass  # Python의 with 문이나 컨텍스트 매니저가 자동으로 처리


def optimize_query(query, eager_loads=None):
    """
    쿼리 최적화 (eager loading 적용)
    
    Args:
        query: SQLAlchemy 쿼리 객체
        eager_loads: eager load할 관계 리스트
    
    Returns:
        최적화된 쿼리
    """
    if eager_loads:
        from sqlalchemy.orm import joinedload
        for load in eager_loads:
            query = query.options(joinedload(load))
    return query


def clear_cache():
    """
    캐시 정리 (필요시 구현)
    """
    gc.collect()


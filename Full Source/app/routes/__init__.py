"""
라우트 모듈 초기화
블루프린트를 여기서 임포트하여 사용합니다.
"""
from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.studio import studio_bp

__all__ = ['main_bp', 'auth_bp', 'studio_bp']


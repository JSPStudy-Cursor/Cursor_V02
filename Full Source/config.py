"""
위튜브 프로젝트 설정 파일
환경 변수 및 애플리케이션 설정을 관리합니다.
"""
import os
from pathlib import Path

# Cloudinary import (선택적)
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).parent

# Flask 기본 설정
class Config:
    """기본 설정 클래스"""
    # 보안 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # CSRF 보호 설정
    WTF_CSRF_ENABLED = True  # CSRF 보호 활성화
    WTF_CSRF_HEADERS = ['X-CSRFToken']  # CSRF 토큰을 헤더에서 읽기
    WTF_CSRF_TIME_LIMIT = 3600  # CSRF 토큰 유효 시간 (1시간)
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "wetube.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 업로드 설정
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    VIDEO_FOLDER = UPLOAD_FOLDER / 'videos'
    THUMBNAIL_FOLDER = UPLOAD_FOLDER / 'thumbnails'
    PROFILE_IMAGE_FOLDER = UPLOAD_FOLDER / 'profiles'  # 프로필 이미지 저장 폴더
    
    # 업로드 파일 크기 제한
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 전체 요청 크기 제한 (100MB)
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 비디오 파일 최대 크기 (100MB)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 이미지 파일 최대 크기 (5MB)
    MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024  # 프로필 이미지 최대 크기 (5MB)
    
    # 허용된 파일 확장자
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    
    # 허용된 MIME 타입
    ALLOWED_VIDEO_MIMES = {
        'video/mp4', 'video/x-msvideo', 'video/quicktime', 
        'video/x-matroska', 'video/webm'
    }
    ALLOWED_IMAGE_MIMES = {
        'image/jpeg', 'image/jpg', 'image/png', 
        'image/gif', 'image/webp'
    }
    
    # 페이지네이션
    VIDEOS_PER_PAGE = 12
    
    # 비디오 카테고리 목록
    VIDEO_CATEGORIES = {
        'entertainment': '엔터테인먼트',
        'music': '음악',
        'sports': '스포츠',
        'gaming': '게임',
        'education': '교육',
        'tech': '기술',
        'comedy': '코미디',
        'travel': '여행',
        'food': '음식',
        'lifestyle': '라이프스타일',
        'news': '뉴스',
        'other': '기타'
    }
    
    # Cloudinary 설정 (선택적)
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

    # Cloudinary 플레이스홀더 값 목록 (예시 값이면 실제 설정으로 간주하지 않음)
    CLOUDINARY_PLACEHOLDERS = {
        'your-api-key', 'your-api-key-here', 'your-cloud-name',
        'your-api-secret', 'your-api-secret-here'
    }

    @classmethod
    def is_cloudinary_configured(cls):
        """
        Cloudinary가 실제 credentials로 설정되어 있는지 확인.
        플레이스홀더 값(your-api-key 등)이면 False 반환.
        """
        if not CLOUDINARY_AVAILABLE:
            return False
        cloud_name = (cls.CLOUDINARY_CLOUD_NAME or '').strip()
        api_key = (cls.CLOUDINARY_API_KEY or '').strip()
        api_secret = (cls.CLOUDINARY_API_SECRET or '').strip()
        if not cloud_name or not api_key or not api_secret:
            return False
        if (cloud_name.lower() in cls.CLOUDINARY_PLACEHOLDERS or
                api_key.lower() in cls.CLOUDINARY_PLACEHOLDERS or
                api_secret.lower() in cls.CLOUDINARY_PLACEHOLDERS):
            return False
        return True

    # Cloudinary 초기화 (설정이 있을 때만)
    @classmethod
    def init_cloudinary(cls):
        """
        Cloudinary 초기화
        
        Returns:
            bool: 초기화 성공 여부
        """
        if not CLOUDINARY_AVAILABLE:
            return False

        if not cls.is_cloudinary_configured():
            return False
        
        if cls.CLOUDINARY_CLOUD_NAME:
            try:
                cloudinary.config(
                    cloud_name=cls.CLOUDINARY_CLOUD_NAME,
                    api_key=cls.CLOUDINARY_API_KEY,
                    api_secret=cls.CLOUDINARY_API_SECRET
                )
                return True
            except Exception as e:
                print(f"Cloudinary 초기화 실패: {str(e)}")
                return False
        return False
    
    # 미디어 저장 방식 설정
    @property
    def USE_CLOUDINARY(self):
        """Cloudinary 사용 여부 확인 (플레이스홀더 값 제외)"""
        return self.get_use_cloudinary()

    # 클래스 속성으로도 접근 가능하도록 추가
    @classmethod
    def get_use_cloudinary(cls):
        """Cloudinary 사용 여부 확인 (실제 credentials만 인정, 플레이스홀더 제외)"""
        return cls.is_cloudinary_configured()

# 개발 환경 설정
class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False

# 프로덕션 환경 설정
class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False
    TESTING = False

# 테스트 환경 설정
class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # 테스트 환경에서는 CSRF 비활성화

# 설정 매핑
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


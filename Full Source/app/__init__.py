"""
위튜브 Flask 애플리케이션 초기화 모듈
애플리케이션 팩토리 패턴을 사용하여 Flask 앱을 생성합니다.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config
import os

# 데이터베이스 및 로그인 매니저 인스턴스 생성
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # 로그인 필요 시 리다이렉트할 뷰
login_manager.login_message = '로그인이 필요합니다.'
login_manager.login_message_category = 'info'

# CSRF 보호 인스턴스 생성
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login이 사용자 세션을 관리하기 위해 사용하는 함수
    
    Args:
        user_id: 사용자 ID
    
    Returns:
        User 객체 또는 None
    """
    from app.models import User
    return User.query.get(int(user_id))


def create_app(config_name=None):
    """
    Flask 애플리케이션 팩토리 함수
    
    Args:
        config_name: 사용할 설정 환경 (development, production, testing)
                    None인 경우 환경 변수 FLASK_ENV에서 가져옴
    
    Returns:
        Flask 애플리케이션 인스턴스
    """
    app = Flask(__name__)
    
    # 설정 로드
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Cloudinary 사용 여부를 Flask config에 추가
    # 플레이스홀더 값(your-api-key 등)이면 로컬 저장소 사용
    from config import Config
    use_cloudinary = Config.get_use_cloudinary()
    app.config['USE_CLOUDINARY'] = use_cloudinary
    app.logger.info(f"[DEBUG] USE_CLOUDINARY 설정: {use_cloudinary}")
    
    # 확장 초기화
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # CSRF 보호 활성화
    
    # 업로드 폴더 생성
    from config import Config
    os.makedirs(Config.VIDEO_FOLDER, exist_ok=True)
    os.makedirs(Config.THUMBNAIL_FOLDER, exist_ok=True)
    os.makedirs(Config.PROFILE_IMAGE_FOLDER, exist_ok=True)  # 프로필 이미지 폴더 생성
    
    # Cloudinary 초기화 (설정이 있는 경우, 플레이스홀더 제외)
    if Config.init_cloudinary():
        app.logger.info("Cloudinary 초기화 완료")
    else:
        app.logger.info("Cloudinary 미사용 (로컬 저장소 사용). .env에서 플레이스홀더(your-api-key 등) 제거 또는 실제 키 입력 후 사용 가능")
    
    # 블루프린트 등록
    from app.routes import main_bp, auth_bp, studio_bp
    from app.routes.uploads import uploads_bp
    from app.routes.admin import admin_bp
    from app.routes.comments import comments_bp
    from app.routes.likes import likes_bp
    from app.routes.comment_likes import comment_likes_bp
    from app.routes.subscriptions import subscriptions_bp
    from app.routes.api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(studio_bp, url_prefix='/studio')
    app.register_blueprint(uploads_bp, url_prefix='/uploads')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(comments_bp)
    app.register_blueprint(likes_bp)
    app.register_blueprint(comment_likes_bp)
    app.register_blueprint(subscriptions_bp)
    app.register_blueprint(api_bp)
    
    # 데이터베이스 초기화 및 스키마 업데이트
    with app.app_context():
        # 기존 테이블이 있는 경우 스키마 업데이트
        try:
            # videos 테이블에 category 컬럼이 있는지 확인
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            
            if 'videos' in inspector.get_table_names():
                # 직접 SQL로 컬럼 존재 여부 확인
                with db.engine.connect() as conn:
                    result = conn.execute(text("PRAGMA table_info(videos)"))
                    columns = [row[1] for row in result.fetchall()]
                    
                    if 'category' not in columns:
                        conn.execute(text("ALTER TABLE videos ADD COLUMN category VARCHAR(50)"))
                        conn.commit()
                        print("[INFO] Added category column to videos table")
                    
                    # Cloudinary 관련 컬럼 추가
                    if 'video_public_id' not in columns:
                        conn.execute(text("ALTER TABLE videos ADD COLUMN video_public_id VARCHAR(255)"))
                        conn.commit()
                        print("[INFO] Added video_public_id column to videos table")
                    
                    if 'thumbnail_public_id' not in columns:
                        conn.execute(text("ALTER TABLE videos ADD COLUMN thumbnail_public_id VARCHAR(255)"))
                        conn.commit()
                        print("[INFO] Added thumbnail_public_id column to videos table")
            
            if 'comments' in inspector.get_table_names():
                with db.engine.connect() as conn:
                    result = conn.execute(text("PRAGMA table_info(comments)"))
                    columns = [row[1] for row in result.fetchall()]
                    
                    if 'parent_id' not in columns:
                        conn.execute(text("ALTER TABLE comments ADD COLUMN parent_id INTEGER"))
                        conn.commit()
                        print("[INFO] Added parent_id column to comments table")
                    
                    if 'likes' not in columns:
                        conn.execute(text("ALTER TABLE comments ADD COLUMN likes INTEGER DEFAULT 0"))
                        conn.commit()
                        print("[INFO] Added likes column to comments table")
                    
                    if 'dislikes' not in columns:
                        conn.execute(text("ALTER TABLE comments ADD COLUMN dislikes INTEGER DEFAULT 0"))
                        conn.commit()
                        print("[INFO] Added dislikes column to comments table")
            
            # users 테이블에 profile_image_public_id 및 is_admin 컬럼 추가
            if 'users' in inspector.get_table_names():
                with db.engine.connect() as conn:
                    result = conn.execute(text("PRAGMA table_info(users)"))
                    columns = [row[1] for row in result.fetchall()]
                    
                    if 'profile_image_public_id' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN profile_image_public_id VARCHAR(255)"))
                        conn.commit()
                        print("[INFO] Added profile_image_public_id column to users table")
                    
                    if 'is_admin' not in columns:
                        conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                        conn.commit()
                        print("[INFO] Added is_admin column to users table")
        except Exception as e:
            # 오류가 발생해도 계속 진행 (이미 컬럼이 존재할 수 있음)
            print(f"[WARNING] Schema update check failed: {e}")
        
        # 모든 테이블 생성 (없는 테이블만 생성됨)
        db.create_all()
        
        # 관리자 계정 생성 (없는 경우에만)
        from app.models import User
        admin_email = 'admin@wetube.com'
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email=admin_email,
                nickname='관리자',
                is_admin=True
            )
            admin_user.set_password('admin1234')
            db.session.add(admin_user)
            db.session.commit()
            print(f"[INFO] Created admin account: admin (pw: admin1234)")
        else:
            # 관리자 정보 강제 업데이트 (비밀번호 및 권한 고정)
            admin_user.is_admin = True
            admin_user.set_password('admin1234')
            if admin_user.email != admin_email:
                admin_user.email = admin_email
            db.session.commit()
            print(f"[INFO] Updated admin account: admin (pw: admin1234)")
    
    return app

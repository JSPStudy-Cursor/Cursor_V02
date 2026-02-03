"""Flask 앱 팩토리 – 템플릿/정적 파일 제공만, DB·백엔드 없음."""

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev-frontend-only",
    )

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.studio import studio_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(studio_bp)
    app.register_blueprint(admin_bp)

    return app


# flask run / FLASK_APP=app 사용 시 동일 앱 로드
app = create_app()

# 직접 실행 시 (python -m app 또는 python app/__init__.py)
if __name__ == "__main__":
    print("등록된 라우트: / /auth/login /auth/register /auth/profile /studio ...")
    print("중요: 5000 포트를 쓰는 다른 프로그램(기존 Flask 등)이 있으면 먼저 종료하세요.")
    print("      그렇지 않으면 /studio/ 에서 404가 납니다.")
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)

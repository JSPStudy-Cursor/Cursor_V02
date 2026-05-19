"""
위튜브 Flask 애플리케이션 실행 파일
개발 서버를 시작합니다.
"""
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
# .env 파일이 있으면 먼저 로드하고, 없으면 .env_dev 파일을 로드합니다.
if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists('.env_dev'):
    load_dotenv('.env_dev')
    print("[INFO] .env_dev 파일에서 환경 변수를 로드했습니다.")
else:
    load_dotenv() # 기본 .env 로드 시도

from app import create_app
from app.models import User
from app import db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Flask shell에서 사용할 컨텍스트를 제공합니다.
    """
    return {'db': db, 'User': User}

if __name__ == '__main__':
    # 개발 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)


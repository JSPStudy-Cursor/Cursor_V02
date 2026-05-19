"""
PythonAnywhere 배포용 WSGI 파일 예제
이 파일을 PythonAnywhere의 WSGI configuration file에 복사하여 사용하세요.
"""
import sys
import os

# ============================================================
# 1. 프로젝트 경로 설정
# ============================================================
# ⚠️ 중요: username을 자신의 PythonAnywhere 사용자명으로 변경하세요!
# 예: lsy3709 → /home/lsy3709/Wetube-Clone-coding-Book-Test
project_home = '/home/lsy3709/Wetube-Clone-coding-Book-Test'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ============================================================
# 2. 환경 변수 설정 (필수!)
# ============================================================
# ⚠️ 중요: 아래 값들을 실제 값으로 변경하세요!

# Flask 환경 설정
os.environ['FLASK_ENV'] = 'production'

# 보안 키 (강력한 랜덤 문자열로 변경하세요!)
# PythonAnywhere 콘솔에서 생성:
# python3.10
# >>> import secrets
# >>> print(secrets.token_hex(32))
os.environ['SECRET_KEY'] = 'your-secret-key-here-change-this-to-random-string'

# Cloudinary 설정 (실제 값으로 변경하세요!)
os.environ['CLOUDINARY_CLOUD_NAME'] = 'dm4mpl8fr'
os.environ['CLOUDINARY_API_KEY'] = 'your-api-key-here'
os.environ['CLOUDINARY_API_SECRET'] = 'your-api-secret-here'

# ============================================================
# 3. .env 파일 로드 (선택사항)
# ============================================================
# .env 파일을 업로드한 경우 아래 주석을 해제하세요
# from dotenv import load_dotenv
# load_dotenv('/home/lsy3709/Wetube-Clone-coding-Book-Test/.env')

# ============================================================
# 4. Flask 애플리케이션 생성
# ============================================================
from app import create_app

# 프로덕션 환경으로 애플리케이션 생성
application = create_app('production')

# ⚠️ 중요: PythonAnywhere는 'application' 변수를 찾습니다
# 'app'이 아닌 'application'을 사용해야 합니다


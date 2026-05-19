"""
PythonAnywhere 배포용 WSGI 파일
이 파일은 PythonAnywhere에서 Flask 애플리케이션을 실행하기 위해 사용됩니다.
"""
import sys
import os

# 프로젝트 경로를 Python 경로에 추가
# PythonAnywhere에서 프로젝트가 /home/username/mysite/ 에 있다고 가정
# 실제 경로는 PythonAnywhere의 Files 탭에서 확인하세요
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ============================================================
# 환경 변수 설정
# ============================================================
# ⚠️ 중요: 아래 값들을 실제 값으로 변경하세요!
# PythonAnywhere의 Web 탭에 Environment variables 섹션이 없는 경우
# 여기서 직접 설정해야 합니다.

# Flask 환경 설정
os.environ['FLASK_ENV'] = 'production'

# 보안 키 (강력한 랜덤 문자열로 변경하세요!)
# Python에서 생성: import secrets; print(secrets.token_hex(32))
os.environ['SECRET_KEY'] = 'your-secret-key-here-change-this-to-random-string'

# Cloudinary 설정 (실제 값으로 변경하세요!)
os.environ['CLOUDINARY_CLOUD_NAME'] = 'your-cloud-name'
os.environ['CLOUDINARY_API_KEY'] = 'your-api-key'
os.environ['CLOUDINARY_API_SECRET'] = 'your-api-secret'

# .env 파일 로드 (있는 경우)
from dotenv import load_dotenv
load_dotenv()

# Flask 애플리케이션 생성
from app import create_app

# 프로덕션 환경으로 설정
application = create_app('production')

# PythonAnywhere는 'application' 변수를 찾습니다
# 'app'이 아닌 'application'을 사용해야 합니다


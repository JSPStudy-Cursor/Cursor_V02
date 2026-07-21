# 위튜브 (WeTube) - 유튜브 클론 코딩 프로젝트

## 프로젝트 소개

위튜브는 유튜브를 클론한 비디오 공유 플랫폼입니다. Flask를 사용한 서버사이드 렌더링 방식으로 구현되었습니다.

## 기술 스택

- **Python**: 3.14
- **웹 프레임워크**: Flask 3.0.0
- **데이터베이스**: SQLite
- **렌더링**: 서버사이드 렌더링 (SSR)
- **인증**: Flask-Login

## 주요 기능

### 구현 완료

- ✅ 회원가입 / 로그인 / 로그아웃
- ✅ 회원 정보 수정
- ✅ 비디오 업로드
- ✅ 비디오 목록 조회
- ✅ 비디오 시청
- ✅ 스튜디오 (내 동영상 관리)
- ✅ 댓글 시스템 (대댓글 포함)
- ✅ 좋아요/싫어요 기능
- ✅ 비디오 검색 및 정렬
- ✅ 비디오 수정/삭제
- ✅ 구독 기능
- ✅ 사용자 프로필 페이지
- ✅ 스튜디오 통계 대시보드
- ✅ 비디오 태그 및 카테고리 기능
- ✅ RESTful API
- ✅ 단위 테스트 (145개 테스트)

## 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/lsy3709/Wetube-Clone-coding-Book-Test.git
cd Wetube-Clone-coding-Book-Test
```

### 2. 가상 환경 생성 및 활성화

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정 (선택사항)

`.env` 파일을 생성하고 다음 내용을 추가:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### 5. 데이터베이스 초기화

애플리케이션을 처음 실행하면 자동으로 데이터베이스가 생성됩니다.

### 6. 서버 실행

```bash
python run.py
```

서버가 실행되면 브라우저에서 `http://localhost:5000`으로 접속할 수 있습니다.

## 프로젝트 구조

```
0-Wetube/
├── app/                    # 애플리케이션 메인 패키지
│   ├── __init__.py        # Flask 앱 초기화
│   ├── models.py          # 데이터베이스 모델
│   ├── routes/            # 라우트 블루프린트
│   │   ├── main.py       # 메인 페이지
│   │   ├── auth.py       # 인증 관련
│   │   ├── studio.py     # 스튜디오
│   │   ├── api.py        # RESTful API
│   │   └── ...           # 기타 라우트
│   ├── templates/         # HTML 템플릿
│   ├── static/           # 정적 파일 (CSS, JS)
│   └── utils/            # 유틸리티 함수
├── uploads/              # 업로드된 미디어 파일
│   ├── videos/           # 비디오 파일
│   ├── thumbnails/       # 썸네일 이미지
│   └── profiles/         # 프로필 이미지
├── tests/                # 테스트 코드
├── config.py             # 설정 파일
├── requirements.txt      # Python 패키지 의존성
├── run.py               # 애플리케이션 실행 파일
└── *.md                 # 문서 파일들
```

## 프로젝트 문서 목차

프로젝트에 포함된 모든 문서는 숫자 넘버링으로 정리되어 있습니다. 다음 순서로 읽으시면 프로젝트를 이해하기 쉽습니다.

### 📚 필수 문서 (시작하기 전에 읽어야 할 문서)

1. 초기 설정 가이드

   - 프로젝트 초기 설정 방법
   - 가상 환경 설정
   - 의존성 설치
   - 데이터베이스 초기화
   - 서버 실행 방법

2. Git 설정 가이드
   - Git 저장소 초기화
   - 원격 저장소 연결
   - 커밋 및 푸시 방법
   - 브랜치 관리

### 📖 프로젝트 개요 문서

3. 프로젝트 요약
   - 프로젝트 구조 설명
   - 완료된 작업 목록
   - 주요 기능 개요

### 🔧 개발 가이드 문서

4. API 명세서

   - RESTful API 엔드포인트 목록
   - 요청/응답 형식
   - API 사용 예제
   - 프론트엔드 통합 가이드

5. 테스트 가이드

   - 테스트 환경 설정
   - 테스트 실행 방법
   - 테스트 작성 가이드
   - 코드 커버리지 확인

6. 데이터베이스 GUI 가이드

   - 웹 기반 데이터베이스 관리 인터페이스 사용법
   - 테이블 조회 방법
   - SQL 쿼리 실행 방법
   - 데이터베이스 통계 확인

7. 성능 최적화 가이드
   - N+1 쿼리 문제 해결
   - 메모리 누수 방지
   - 데이터베이스 세션 관리
   - 성능 모니터링 방법

### 📝 작업 및 변경 이력 문서

8. 작업 로그

   - 프로젝트 진행 상황
   - 완료된 작업 내역
   - 작업 환경 설정 정보
   - 다음 작업 계획

9.  변경 이력

   - 주요 기능 추가 내역
   - 버그 수정 내역
   - 변경사항 상세 설명
   - 날짜별 변경 기록

10.  Git 커밋 로그

    - 커밋 메시지 형식 규칙
    - 모든 커밋 내역
    - 커밋 해시 및 통계 정보
    - 커밋별 상세 변경사항

11. 커밋 요약
    - 커밋 요약 정보
    - 주요 변경사항 정리

### ✅ 체크리스트 및 계획 문서

12. 기능 체크리스트

### 📝 개발 과정 기록 문서

22.  프롬프트 히스토리
    - 프로젝트 개발 과정에서 사용된 모든 프롬프트 기록
    - 작업 내용 및 결과 포함
    - 참고 자료로 활용 가능
    - 구현 완료된 기능 목록
    - 예정된 기능 목록
    - 기능별 완료 상태

### 📚 집필 및 학습 자료

13.  책 집필용 프롬프트 모음집

    - 프로젝트 기획부터 배포까지 단계별 프롬프트
    - 7개 Part로 구성된 체계적인 프롬프트
    - 각 기능별 상세 프롬프트
    - AI 도구 활용 가이드

14.  점진적 작업 단계 가이드

    - 교재 목차 구조를 참고한 11단계 작업 가이드
    - 각 단계별 목표 및 작업 내용
    - 완료 체크리스트
    - 프롬프트 작성 팁 및 문제 해결 가이드
    - 진행 상황 추적 테이블

15. README 마이그레이션 가이드

    - README 파일 마이그레이션 관련 문서

16. 배포 가이드 (PythonAnywhere & Cloudinary)

    - PythonAnywhere를 이용한 웹 애플리케이션 배포
    - Cloudinary를 이용한 미디어 파일 저장
    - 초보자 및 입문자를 위한 단계별 배포 가이드
    - 코드 수정 방법 및 문제 해결

17. .env 파일 설정 가이드

    - 환경 변수 설정 방법
    - Cloudinary 설정 방법
    - 보안 주의사항
    - 문제 해결 가이드

18. Cloudinary 테스트 가이드

    - Cloudinary 초기화 확인
    - 비디오 업로드 테스트
    - 이미지 업로드 테스트
    - Cloudinary 대시보드 확인
    - 문제 해결

19. Cloudinary 문제 해결 가이드

    - Cloudinary 업로드 문제 진단 방법
    - 로그 확인 방법
    - 일반적인 문제 해결
    - 데이터베이스 확인 방법
    - Cloudinary 대시보드 확인 방법
    - 체크리스트

20. Cloudinary 대시보드 사용 가이드
    - Cloudinary 대시보드 접속 방법
    - 업로드된 파일 확인 방법
    - 폴더 구조 설명
    - Cloudinary vs 로컬 저장소 구분
    - 파일 관리 방법
    - 통계 및 분석

21. PythonAnywhere 배포 단계별 가이드
    - PythonAnywhere 계정 생성
    - 프로젝트 업로드 방법
    - 환경 설정
    - 데이터베이스 초기화
    - 웹 앱 설정
    - 배포 확인 및 문제 해결
    - 체크리스트

23. 책 집필 단원별 상세 목차
    - 각 단원별 학습 목표 및 상세 내용
    - 18개 장으로 구성된 체계적인 목차
    - 각 장별 실습 과제 포함
    - 프로젝트 기능을 반영한 실용적인 구성
    - 초보자부터 고급자까지 단계별 학습 가능

24. 책 집필용 프롬프트 명령어 Part 1
    - Part 1: 프로젝트 기획 및 개발 환경 구축 프롬프트 목록
    - 각 섹션별 실제 사용 가능한 프롬프트 명령어
    - Cursor AI에 바로 입력 가능한 형태
    - 학습 목표 및 실습 과제 포함

25. 책 집필용 프롬프트 명령어 Part 2
    - Part 2: UI First 전략 - 화면부터 그리기 프롬프트 목록
    - Jinja2 템플릿, 레이아웃, CSS 스타일링 프롬프트
    - 반응형 디자인 구현 프롬프트
    - 실습 과제 및 체크리스트 포함

26. 책 집필용 프롬프트 명령어 Part 3
    - Part 3: 데이터베이스 설계 및 모델링 프롬프트 목록
    - SQLAlchemy ORM 모델 구현 프롬프트
    - 관계형 데이터베이스 설계 프롬프트
    - 마이그레이션 및 초기화 프롬프트
    - 실습 과제 및 체크리스트 포함

27. 책 집필용 프롬프트 명령어 Part 4 (4장~8장)
    - Part 4: 백엔드 핵심 기능 구현
    - 4장: 비디오 업로드 및 관리
    - 5장: 비디오 재생과 라우팅
    - 6장: 코드 정리와 구조화 (리팩토링)
    - 7장: 회원가입과 인증
    - 8장: 댓글과 좋아요
    - 실습 과제 및 체크리스트 포함

28. 책 집필용 프롬프트 명령어 Part 5 (9장~11장)
    - Part 5: 프론트엔드 구현 및 사용자 경험 개선
    - 9장: 검색, 정렬, 필터링 기능
    - 10장: 스튜디오 통계 대시보드
    - 11장: 사용자 경험 개선
    - 실습 과제 및 체크리스트 포함

29. 책 집필용 프롬프트 명령어 Part 6 (12장~13장)
    - Part 6: 고급 기능 구현
    - 12장: RESTful API 구현
    - 13장: 관리자 기능 구현
    - 실습 과제 및 체크리스트 포함

30. 책 집필용 프롬프트 명령어 Part 7 (14장~15장)
    - Part 7: 보안 강화 및 성능 최적화
    - 14장: 보안 강화 (CSRF, XSS, 파일 업로드, SQL 인젝션, 비밀번호, 세션)
    - 15장: 성능 최적화 (쿼리 최적화, 페이지네이션, 캐싱, 이미지, 정적 파일)
    - 실습 과제 및 체크리스트 포함

31. 책 집필용 프롬프트 명령어 Part 8 (16장~18장)
    - Part 8: 테스트 및 배포
    - 16장: 단위 테스트 작성 (pytest, 모델/라우트 테스트, 커버리지)
    - 17장: 배포 준비 및 실전 배포 (Cloudinary, PythonAnywhere)
    - 18장: AI 매니지먼트와 에러 대응
    - 실습 과제 및 체크리스트 포함

### 용어 및 개념 정리 문서

32. Part 1 용어 및 개념 정리
    - Part 1 (1장) 관련 용어, 개념, 문법 정리
    - 유튜브 클론, Cursor AI, Python, Flask, Git 등 핵심 용어
    - 어원, 역사, 기본 문법, 설명, 속성 소개 포함

33. Part 2 용어 및 개념 정리
    - Part 2 (2장) 관련 용어, 개념, 문법 정리
    - UI First 전략, Jinja2, CSS, 반응형 디자인 등 핵심 용어
    - 어원, 역사, 기본 문법, 설명, 속성 소개 포함

34. Part 3 용어 및 개념 정리
    - Part 3 (3장) 관련 용어, 개념, 문법 정리
    - 데이터베이스, SQLite, SQLAlchemy, ORM, 모델 등 핵심 용어
    - 어원, 역사, 기본 문법, 설명, 속성 소개 포함

35. Part 4 용어 및 개념 정리
    - Part 4 (4장~8장) 관련 용어, 개념, 문법 정리
    - 파일 업로드, 라우팅, 리팩토링, 인증, 댓글, 좋아요, 구독 등 핵심 용어
    - 어원, 역사, 기본 문법, 설명, 속성 소개 포함

36. Part 5 용어 및 개념 정리
    - Part 5 (9장~11장) 관련 용어, 개념, 문법 정리
    - 검색, 정렬, 필터링, 통계, 페이지네이션, 플래시 메시지, 반응형 디자인, 다크 모드 등 핵심 용어
    - 어원, 역사, 기본 문법, 설명, 속성 소개 포함

37. Part 6 용어 및 개념 정리
    - Part 6 (12장~13장) 관련 용어, 개념, 문법 정리
    - RESTful API, HTTP 메서드, JSON, CRUD, RBAC, 관리자 기능 등 핵심 용어
    - 어원, 역사, 기본 문법, 설명, 속성 소개 포함

38. Part 7 용어 및 개념 정리
    - Part 7 (14장~15장) 관련 용어, 개념, 문법 정리
    - CSRF, XSS, SQL 인젝션, 비밀번호 해싱, 세션 보안, N+1 문제, 캐싱, 이미지 최적화 등 핵심 용어
    - 어원, 역사, 기본 문법, 설명, 속성 소개 포함

39. Part 8 용어 및 개념 정리
    - Part 8 (16장~18장) 관련 용어, 개념, 문법 정리
    - 단위 테스트, TDD, pytest, 테스트 커버리지, 배포, Cloudinary, WSGI, AI 환각, 디버깅 등 핵심 용어
    - 어원, 역사, 기본 문법, 설명, 속성 소개 포함

### 테스트 및 검증 문서

40. 기능별 테스트 가이드
    - 서버 실행 방법 안내
    - 각 기능별 상세 테스트 체크리스트 (20개 기능)
    - 디버깅 팁 및 브라우저 개발자 도구 활용법
    - 테스트 결과 기록 방법

41. TestSprite MCP 서버 사용 가이드
    - TestSprite MCP 서버 사용 방법 상세 안내
    - 단계별 워크플로우 (코드 분석 → PRD → 부트스트랩 → 테스트 플랜 → 실행)
    - 프론트엔드/백엔드 테스트 예시
    - 위튜브 프로젝트 설정 값 (포트 5000, 경로 등) 명시
    - 문제 해결 가이드 및 사용 팁

42. TestSprite 문제 해결 가이드
    - TestSprite 터널 연결 실패 문제 분석
    - 서버 설정 확인 방법
    - 네트워크 및 방화벽 확인 방법
    - 단계별 해결 방법 및 체크리스트
    - 대안 방법 제시

43. TestSprite 실행 명령어 가이드
    - MCP 도구를 사용한 실행 방법
    - 터미널 명령어를 사용한 실행 방법
    - 전체 워크플로우 예시
    - 명령어 옵션 상세 설명
    - 문제 해결 방법
   
44. SQLite VS Code 확장 프로그램 가이드
   - VS Code에서 SQLite 데이터베이스 조회 및 관리 방법
   - 확장 프로그램 설치 및 사용법
   - SQL 쿼리 실행 방법

45. Git 커밋 및 푸시 가이드
    
47. Part 5 책 원고 초안 (백엔드 핵심 기능 구현)
   - 표준 작업 순서 및 커밋 메시지 규칙
   - 환경 변수 관리 및 주의사항
   - 문제 해결 방법

## 상세 실행 가이드

### 개발 환경 설정

1. **Python 버전 확인**

   ```bash
   python --version  # Python 3.14 이상 필요
   ```

2. **가상 환경 생성 및 활성화**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **의존성 설치**

   ```bash
   pip install -r requirements.txt
   ```

4. **환경 변수 설정** (선택사항)

   `.env` 파일을 생성하고 다음 내용을 추가:

   ```env
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here-change-this-in-production
   DATABASE_URL=sqlite:///wetube.db
   ```

### 서버 실행

1. **개발 모드로 실행**

   ```bash
   python run.py
   ```

   또는 Flask 명령어 사용:

   ```bash
   flask run
   ```

2. **프로덕션 모드로 실행**

   ```bash
   export FLASK_ENV=production  # Linux/Mac
   set FLASK_ENV=production     # Windows
   python run.py
   ```

3. **포트 변경하여 실행**
   ```bash
   python run.py --port 8080
   ```

### 데이터베이스 관리

1. **데이터베이스 초기화**

   - 애플리케이션을 처음 실행하면 자동으로 데이터베이스가 생성됩니다.
   - 데이터베이스 파일: `instance/wetube.db`

2. **웹 기반 데이터베이스 관리**
   - 서버 실행 후 `http://localhost:5000/admin` 접속
   - 로그인 후 데이터베이스 관리 인터페이스 사용
   - 자세한 내용은 [06-DATABASE_GUI_GUIDE.md](06-DATABASE_GUI_GUIDE.md) 참조

### 테스트 실행

1. **전체 테스트 실행**

   ```bash
   pytest
   ```

2. **코드 커버리지와 함께 실행**

   ```bash
   pytest --cov=app --cov-report=html
   ```

3. **특정 테스트 파일 실행**

   ```bash
   pytest tests/test_comments.py
   ```

4. **자세한 출력과 함께 실행**
   ```bash
   pytest -v
   ```

자세한 내용은 [05-TESTING_GUIDE.md](05-TESTING_GUIDE.md) 참조

### API 사용

프로젝트는 RESTful API를 제공합니다. API 문서는 [04-API_DOCUMENTATION.md](04-API_DOCUMENTATION.md)를 참조하세요.

**예제: 비디오 목록 조회**

```bash
curl http://localhost:5000/api/videos
```

**예제: 댓글 작성**

```bash
curl -X POST http://localhost:5000/api/videos/1/comments \
  -H "Content-Type: application/json" \
  -d '{"content": "좋은 영상이네요!"}'
```

### 문제 해결

#### 포트가 이미 사용 중인 경우

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID [PID번호] /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

#### 가상 환경 활성화 오류

```bash
# Windows PowerShell에서는 다음 명령어 사용
venv\Scripts\Activate.ps1

# 실행 정책 오류 시
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 의존성 설치 오류

```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 캐시 없이 설치
pip install --no-cache-dir -r requirements.txt
```

## 문서 관리 규칙

프로젝트의 모든 문서는 숫자 넘버링으로 관리됩니다:

- **형식**: `NN-FILE_NAME.md` (예: `01-SETUP_GUIDE.md`)
- **순서**: 논리적 순서로 정렬 (설정 → 개요 → 가이드 → 이력 → 계획)
- **README.md**: 넘버링 없음 (메인 문서)

새 문서를 추가할 때는:

1. 적절한 번호 할당
2. README.md의 목차에 추가
3. .cursorrules 파일에 규칙 기록

## 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

## 기여

이슈 및 풀 리퀘스트를 환영합니다!

## 관련 링크

- **GitHub 저장소**: https://github.com/lsy3709/Wetube-Clone-coding-Book-Test
- **프로젝트 개요**: [03-PROJECT_SUMMARY.md](03-PROJECT_SUMMARY.md)
- **API 문서**: [04-API_DOCUMENTATION.md](04-API_DOCUMENTATION.md)

"""
보안 유틸리티 함수
XSS 방지 및 입력 검증을 위한 헬퍼 함수들
"""
import re
import html
try:
    from bleach import clean
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False


def sanitize_html(text, allowed_tags=None):
    """
    HTML 태그를 제거하고 안전한 텍스트로 변환
    
    Args:
        text: 입력 텍스트
        allowed_tags: 허용할 HTML 태그 리스트 (기본값: None, 모든 태그 제거)
    
    Returns:
        str: 정제된 텍스트
    """
    if not text:
        return ''
    
    # 기본적으로 모든 HTML 태그 제거
    if allowed_tags is None:
        allowed_tags = []
    
    # bleach를 사용하여 HTML 정제 (사용 가능한 경우)
    if BLEACH_AVAILABLE:
        cleaned = clean(text, tags=allowed_tags, strip=True)
    else:
        # bleach가 없는 경우 기본 HTML 태그 제거
        import html
        cleaned = html.escape(text)
        # HTML 태그 제거 (간단한 정규식 사용)
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
    
    return cleaned


def sanitize_text(text, max_length=None):
    """
    일반 텍스트 입력 정제 (HTML 태그 제거, 길이 제한)
    
    Args:
        text: 입력 텍스트
        max_length: 최대 길이 (None이면 제한 없음)
    
    Returns:
        str: 정제된 텍스트
    """
    if not text:
        return ''
    
    # HTML 태그 제거
    text = sanitize_html(text)
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    # 길이 제한
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_username(username):
    """
    사용자명 검증
    
    Args:
        username: 사용자명
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not username:
        return False, '사용자명을 입력해주세요.'
    
    if len(username) < 3:
        return False, '사용자명은 최소 3자 이상이어야 합니다.'
    
    if len(username) > 20:
        return False, '사용자명은 최대 20자까지 가능합니다.'
    
    # 영문, 숫자, 언더스코어만 허용
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, '사용자명은 영문, 숫자, 언더스코어(_)만 사용 가능합니다.'
    
    return True, None


def validate_email(email):
    """
    이메일 주소 검증
    
    Args:
        email: 이메일 주소
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not email:
        return False, '이메일을 입력해주세요.'
    
    # 기본적인 이메일 형식 검증
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, '올바른 이메일 형식이 아닙니다.'
    
    if len(email) > 100:
        return False, '이메일 주소가 너무 깁니다.'
    
    return True, None


def validate_password(password):
    """
    비밀번호 검증
    
    Args:
        password: 비밀번호
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, '비밀번호를 입력해주세요.'
    
    if len(password) < 6:
        return False, '비밀번호는 최소 6자 이상이어야 합니다.'
    
    if len(password) > 128:
        return False, '비밀번호가 너무 깁니다.'
    
    return True, None


def validate_video_title(title):
    """
    비디오 제목 검증
    
    Args:
        title: 비디오 제목
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not title:
        return False, '제목을 입력해주세요.'
    
    # HTML 태그 제거 후 검증
    title = sanitize_text(title)
    
    if len(title) < 1:
        return False, '제목을 입력해주세요.'
    
    if len(title) > 200:
        return False, '제목은 최대 200자까지 가능합니다.'
    
    return True, None


def validate_comment_content(content):
    """
    댓글 내용 검증
    
    Args:
        content: 댓글 내용
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not content:
        return False, '댓글 내용을 입력해주세요.'
    
    # HTML 태그 제거 후 검증
    content = sanitize_text(content)
    
    if len(content) < 1:
        return False, '댓글 내용을 입력해주세요.'
    
    if len(content) > 1000:
        return False, '댓글은 최대 1000자까지 가능합니다.'
    
    return True, None


def escape_user_input(text):
    """
    사용자 입력을 HTML 이스케이프 (Jinja2가 자동으로 처리하지만, 추가 보안을 위해)
    
    Args:
        text: 입력 텍스트
    
    Returns:
        str: 이스케이프된 텍스트
    """
    if not text:
        return ''
    return html.escape(str(text))


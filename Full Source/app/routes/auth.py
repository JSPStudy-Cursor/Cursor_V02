"""
인증 관련 라우트
회원가입, 로그인, 로그아웃, 회원 정보 수정을 처리합니다.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from sqlalchemy import or_
from urllib.parse import urlparse, urljoin
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User
from config import Config
from app.utils.security import (
    validate_username, validate_email, validate_password,
    sanitize_text
)
from datetime import datetime
import os

auth_bp = Blueprint('auth', __name__)


def is_safe_redirect_url(target):
    """
    next 파라미터가 같은 사이트 내 URL인지 검증 (오픈 리다이렉트 방지)
    """
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def allowed_file(filename, allowed_extensions):
    """
    파일 확장자 확인
    
    Args:
        filename: 파일명
        allowed_extensions: 허용된 확장자 집합
    
    Returns:
        bool: 허용된 확장자면 True
    """
    if not filename or '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_file_size(file, max_size):
    """
    파일 크기 검증
    
    Args:
        file: 업로드된 파일 객체
        max_size: 최대 크기 (바이트)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file:
        return True, None
    
    # 파일 크기 확인 (Content-Length 헤더 또는 파일 크기)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # 파일 포인터를 처음으로 되돌림
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f'파일 크기가 너무 큽니다. 최대 {max_size_mb:.0f}MB까지 업로드 가능합니다.'
    
    return True, None


def validate_image_file(file):
    """
    이미지 파일 검증 (확장자, 크기, 실제 이미지 여부)
    
    Args:
        file: 업로드된 파일 객체
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file or not file.filename:
        return True, None
    
    # 확장자 검증
    if not allowed_file(file.filename, Config.ALLOWED_IMAGE_EXTENSIONS):
        return False, '지원하지 않는 이미지 형식입니다. (jpg, jpeg, png, gif, webp만 가능)'
    
    # 파일 크기 검증
    is_valid, error = validate_file_size(file, Config.MAX_PROFILE_IMAGE_SIZE)
    if not is_valid:
        return False, error
    
    # 실제 이미지 파일인지 확인 (Pillow 사용)
    try:
        from PIL import Image
        file.seek(0)
        img = Image.open(file)
        img.verify()  # 이미지 파일 검증
        file.seek(0)  # 파일 포인터를 처음으로 되돌림
    except Exception:
        return False, '유효하지 않은 이미지 파일입니다.'
    
    return True, None


def delete_file_safely(file_path):
    """
    파일을 안전하게 삭제하는 헬퍼 함수
    
    Args:
        file_path: 삭제할 파일의 전체 경로
    
    Returns:
        bool: 삭제 성공 시 True, 실패 시 False
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f'파일 삭제 오류: {str(e)}')
    return False


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    회원가입 페이지
    
    Returns:
        GET: 회원가입 폼 렌더링
        POST: 회원가입 처리 후 로그인 페이지로 리다이렉트
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        nickname = request.form.get('nickname', '').strip()
        
        # 입력 검증
        is_valid, error = validate_username(username)
        if not is_valid:
            flash(error, 'error')
            return render_template('auth/register.html')
        
        is_valid, error = validate_email(email)
        if not is_valid:
            flash(error, 'error')
            return render_template('auth/register.html')
        
        is_valid, error = validate_password(password)
        if not is_valid:
            flash(error, 'error')
            return render_template('auth/register.html')
        
        # 비밀번호 확인 일치 검증
        password_confirm = request.form.get('password_confirm', '')
        if password != password_confirm:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('auth/register.html')
        
        # 닉네임 정제 (HTML 태그 제거)
        nickname = sanitize_text(nickname, max_length=50)
        
        # 중복 확인
        if User.query.filter_by(username=username).first():
            flash('이미 사용 중인 사용자명입니다.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('이미 사용 중인 이메일입니다.', 'error')
            return render_template('auth/register.html')
        
        # 새 사용자 생성
        user = User(
            username=username,
            email=email,
            nickname=nickname or username
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    로그인 페이지
    
    Returns:
        GET: 로그인 폼 렌더링
        POST: 로그인 처리 후 메인 페이지로 리다이렉트
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        if not username_or_email or not password:
            flash('사용자명(또는 이메일)과 비밀번호를 입력해주세요.', 'error')
            return render_template('auth/login.html')
        
        # 이메일 또는 사용자명으로 사용자 조회
        user = User.query.filter(
            or_(User.username == username_or_email, User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('로그인되었습니다.', 'success')
            next_page = request.form.get('next') or request.args.get('next')
            if next_page and is_safe_redirect_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('사용자명 또는 비밀번호가 올바르지 않습니다.', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    로그아웃 처리
    
    Returns:
        메인 페이지로 리다이렉트
    """
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    회원 정보 수정 페이지
    
    Returns:
        GET: 회원 정보 수정 폼 렌더링
        POST: 회원 정보 수정 처리
    """
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        profile_image_file = request.files.get('profile_image')
        
        # 닉네임 업데이트 (정제)
        if nickname:
            nickname = sanitize_text(nickname, max_length=50)
            current_user.nickname = nickname
        
        # 이메일 업데이트 (중복 확인 및 검증)
        if email and email != current_user.email:
            is_valid, error = validate_email(email)
            if not is_valid:
                flash(error, 'error')
                return render_template('auth/profile.html')
            
            if User.query.filter_by(email=email).first():
                flash('이미 사용 중인 이메일입니다.', 'error')
                return render_template('auth/profile.html')
            current_user.email = email
        
        # 프로필 이미지 업로드 처리
        if profile_image_file and profile_image_file.filename:
            # 이미지 파일 검증 (확장자, 크기, 실제 이미지 여부)
            is_valid, error = validate_image_file(profile_image_file)
            if not is_valid:
                flash(error, 'error')
                return render_template('auth/profile.html')
            
            try:
                # Cloudinary 사용 여부 확인 (app/__init__.py에서 설정됨)
                use_cloudinary = current_app.config.get('USE_CLOUDINARY', False)
                
                # 상세 로그 출력
                current_app.logger.info("=" * 60)
                current_app.logger.info("[INFO] 프로필 이미지 저장소 설정 확인")
                current_app.logger.info(f"[INFO] 저장소 타입: {'Cloudinary' if use_cloudinary else '로컬 저장소'}")
                current_app.logger.info(f"[DEBUG] USE_CLOUDINARY: {use_cloudinary}")
                current_app.logger.info("=" * 60)
                
                if use_cloudinary:
                    # ============================================================
                    # Cloudinary 저장소 사용
                    # ============================================================
                    from app.utils.cloudinary_utils import upload_profile_image, delete_file
                    
                    # 기존 프로필 이미지 삭제 (Cloudinary에서)
                    if current_user.profile_image_public_id:
                        delete_file(current_user.profile_image_public_id, resource_type='image')
                    
                    # 새 프로필 이미지 업로드
                    profile_result = upload_profile_image(profile_image_file, current_user.id)
                    current_user.profile_image = profile_result['url']
                    current_user.profile_image_public_id = profile_result['public_id']
                    flash('프로필 이미지가 Cloudinary에 업로드되었습니다.', 'success')
                else:
                    # ============================================================
                    # 로컬 저장소 사용
                    # ============================================================
                    # 기존 프로필 이미지 삭제 (있는 경우)
                    if current_user.profile_image:
                        old_image_path = os.path.join(Config.PROFILE_IMAGE_FOLDER, current_user.profile_image)
                        delete_file_safely(old_image_path)
                    
                    # 새 프로필 이미지 저장
                    image_filename = secure_filename(profile_image_file.filename)
                    image_filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image_filename}"
                    image_full_path = os.path.join(Config.PROFILE_IMAGE_FOLDER, image_filename)
                    profile_image_file.save(image_full_path)
                    
                    # 데이터베이스에는 파일명만 저장
                    current_user.profile_image = image_filename
                    flash('프로필 이미지가 로컬 저장소에 업로드되었습니다.', 'success')
            except Exception as e:
                flash(f'프로필 이미지 업로드 중 오류가 발생했습니다: {str(e)}', 'error')
                return render_template('auth/profile.html')
        
        # 비밀번호 변경
        new_password_confirm = request.form.get('new_password_confirm', '')
        if current_password and new_password:
            if new_password != new_password_confirm:
                flash('새 비밀번호가 일치하지 않습니다.', 'error')
                return render_template('auth/profile.html')
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                flash('비밀번호가 변경되었습니다.', 'success')
            else:
                flash('현재 비밀번호가 올바르지 않습니다.', 'error')
                return render_template('auth/profile.html')
        
        db.session.commit()
        flash('회원 정보가 수정되었습니다.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')


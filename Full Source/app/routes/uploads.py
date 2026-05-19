"""
업로드된 파일 제공 라우트
비디오 및 썸네일 이미지를 제공합니다.

참고: Cloudinary를 사용하는 경우, video_path와 thumbnail_path에 이미 URL이 저장되어 있으므로
이 라우트는 사용되지 않습니다. 로컬 파일 시스템을 사용할 때만 필요합니다.
"""
from flask import Blueprint, send_from_directory, abort
from config import Config
import os

uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.route('/videos/<filename>')
def serve_video(filename):
    """
    비디오 파일 제공
    
    Args:
        filename: 비디오 파일명
    
    Returns:
        비디오 파일 스트림
    """
    try:
        # 보안을 위해 파일명 검증
        if '..' in filename or '/' in filename or '\\' in filename:
            abort(404)
        
        return send_from_directory(
            Config.VIDEO_FOLDER,
            filename,
            mimetype='video/mp4'
        )
    except FileNotFoundError:
        abort(404)


@uploads_bp.route('/thumbnails/<filename>')
def serve_thumbnail(filename):
    """
    썸네일 이미지 제공
    
    Args:
        filename: 썸네일 파일명
    
    Returns:
        이미지 파일
    """
    try:
        # 보안을 위해 파일명 검증
        if '..' in filename or '/' in filename or '\\' in filename:
            abort(404)
        
        return send_from_directory(
            Config.THUMBNAIL_FOLDER,
            filename
        )
    except FileNotFoundError:
        abort(404)


@uploads_bp.route('/profiles/<filename>')
def serve_profile_image(filename):
    """
    프로필 이미지 제공
    
    Args:
        filename: 프로필 이미지 파일명
    
    Returns:
        이미지 파일
    """
    try:
        # 보안을 위해 파일명 검증
        if '..' in filename or '/' in filename or '\\' in filename:
            abort(404)
        
        return send_from_directory(
            Config.PROFILE_IMAGE_FOLDER,
            filename
        )
    except FileNotFoundError:
        abort(404)

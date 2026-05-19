"""
Cloudinary 유틸리티 함수
미디어 파일 업로드 및 관리를 담당합니다.
"""
import cloudinary
import cloudinary.uploader
from flask import current_app
from config import Config

def upload_video(file, video_id):
    """
    비디오 파일을 Cloudinary에 업로드
    
    Args:
        file: 업로드할 파일 객체
        video_id: 비디오 ID (파일명에 사용)
    
    Returns:
        dict: 업로드 결과 {'url': '...', 'public_id': '...'}
    """
    try:
        # Cloudinary 설정 확인
        import cloudinary
        current_app.logger.info(f"[DEBUG] Cloudinary 설정 확인")
        current_app.logger.info(f"[DEBUG] cloud_name: {cloudinary.config().cloud_name}")
        current_app.logger.info(f"[DEBUG] api_key: {cloudinary.config().api_key[:10] if cloudinary.config().api_key else 'None'}...")
        
        # 파일 포인터를 처음으로 이동 (이전 검증에서 이동했을 수 있음)
        file.seek(0)
        
        # 파일명 생성 (비디오 ID 사용)
        # folder를 사용하면 public_id는 상대 경로만 지정
        public_id = f"videos/{video_id}"
        
        current_app.logger.info(f"[DEBUG] Cloudinary 비디오 업로드 시작")
        current_app.logger.info(f"[DEBUG] folder: wetube/videos")
        current_app.logger.info(f"[DEBUG] public_id: {public_id}")
        current_app.logger.info(f"[DEBUG] 파일 크기: {file.tell() if hasattr(file, 'tell') else 'N/A'}")
        
        # 파일 포인터를 다시 처음으로 이동
        file.seek(0)
        
        # Cloudinary에 업로드
        result = cloudinary.uploader.upload(
            file,
            resource_type="video",
            folder="wetube/videos",
            public_id=public_id,
            overwrite=True,
            chunk_size=6000000,  # 6MB 청크로 분할 업로드
            eager=[
                {"format": "mp4", "video_codec": "h264"}  # 자동 변환
            ]
        )
        
        current_app.logger.info(f"[DEBUG] Cloudinary 업로드 응답: {result}")
        
        current_app.logger.info(f"[DEBUG] Cloudinary 비디오 업로드 성공: {result.get('secure_url', 'N/A')}")
        
        return {
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'format': result.get('format', 'mp4')
        }
    except Exception as e:
        current_app.logger.error(f"비디오 업로드 실패: {str(e)}")
        current_app.logger.exception(e)  # 전체 스택 트레이스 출력
        raise


def upload_thumbnail(file, video_id):
    """
    썸네일 이미지를 Cloudinary에 업로드
    
    Args:
        file: 업로드할 파일 객체
        video_id: 비디오 ID (파일명에 사용)
    
    Returns:
        dict: 업로드 결과 {'url': '...', 'public_id': '...'}
    """
    try:
        # 파일 포인터를 처음으로 이동
        file.seek(0)
        
        public_id = f"thumbnails/{video_id}"
        
        current_app.logger.info(f"[DEBUG] Cloudinary 썸네일 업로드 시작")
        current_app.logger.info(f"[DEBUG] folder: wetube/thumbnails")
        current_app.logger.info(f"[DEBUG] public_id: {public_id}")
        
        # 파일 포인터를 다시 처음으로 이동
        file.seek(0)
        
        result = cloudinary.uploader.upload(
            file,
            resource_type="image",
            folder="wetube/thumbnails",
            public_id=public_id,
            overwrite=True,
            transformation=[
                {'width': 640, 'height': 360, 'crop': 'limit'}  # 최적 크기로 리사이즈
            ]
        )
        
        current_app.logger.info(f"[DEBUG] Cloudinary 썸네일 업로드 응답: {result}")
        
        current_app.logger.info(f"[DEBUG] Cloudinary 썸네일 업로드 성공: {result.get('secure_url', 'N/A')}")
        
        return {
            'url': result['secure_url'],
            'public_id': result['public_id']
        }
    except Exception as e:
        current_app.logger.error(f"썸네일 업로드 실패: {str(e)}")
        current_app.logger.exception(e)  # 전체 스택 트레이스 출력
        raise


def upload_profile_image(file, user_id):
    """
    프로필 이미지를 Cloudinary에 업로드
    
    Args:
        file: 업로드할 파일 객체
        user_id: 사용자 ID (파일명에 사용)
    
    Returns:
        dict: 업로드 결과 {'url': '...', 'public_id': '...'}
    """
    try:
        # 파일 포인터를 처음으로 이동
        file.seek(0)
        
        public_id = f"profiles/{user_id}"
        
        current_app.logger.info(f"[DEBUG] Cloudinary 프로필 이미지 업로드 시작")
        current_app.logger.info(f"[DEBUG] folder: wetube/profiles")
        current_app.logger.info(f"[DEBUG] public_id: {public_id}")
        
        # 파일 포인터를 다시 처음으로 이동
        file.seek(0)
        
        result = cloudinary.uploader.upload(
            file,
            resource_type="image",
            folder="wetube/profiles",
            public_id=public_id,
            overwrite=True,
            transformation=[
                {'width': 200, 'height': 200, 'crop': 'fill', 'gravity': 'face'}  # 정사각형, 얼굴 중심
            ]
        )
        
        current_app.logger.info(f"[DEBUG] Cloudinary 프로필 이미지 업로드 응답: {result}")
        
        current_app.logger.info(f"[DEBUG] Cloudinary 프로필 이미지 업로드 성공: {result.get('secure_url', 'N/A')}")
        
        return {
            'url': result['secure_url'],
            'public_id': result['public_id']
        }
    except Exception as e:
        current_app.logger.error(f"프로필 이미지 업로드 실패: {str(e)}")
        current_app.logger.exception(e)  # 전체 스택 트레이스 출력
        raise


def delete_file(public_id, resource_type='image'):
    """
    Cloudinary에서 파일 삭제
    
    Args:
        public_id: 삭제할 파일의 public_id
        resource_type: 'image' 또는 'video'
    """
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception as e:
        current_app.logger.error(f"파일 삭제 실패: {str(e)}")
        # 삭제 실패해도 계속 진행 (이미 삭제된 파일일 수 있음)


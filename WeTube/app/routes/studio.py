"""Studio 라우트 – 동영상 관리 페이지. 프론트 전용, DB/백엔드 없음."""

from flask import Blueprint, render_template

studio_bp = Blueprint("studio", __name__, url_prefix="/studio")


@studio_bp.route("/")
@studio_bp.route("")  # /studio (끝 슬래시 없음)도 처리
def index():
    return render_template("studio/index.html")


@studio_bp.route("/upload")
def upload():
    return render_template("studio/upload.html")


@studio_bp.route("/edit/<int:video_id>")
def edit(video_id):
    return render_template("studio/edit.html", video_id=video_id)

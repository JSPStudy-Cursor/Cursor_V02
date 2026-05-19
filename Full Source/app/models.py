"""
위튜브 데이터베이스 모델 정의
사용자, 비디오, 댓글 등의 데이터 모델을 정의합니다.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """
    사용자 모델
    Flask-Login과 호환되도록 UserMixin을 상속받습니다.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(80), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)  # 프로필 이미지 경로 또는 Cloudinary URL
    profile_image_public_id = db.Column(db.String(255), nullable=True)  # Cloudinary 프로필 이미지 public_id
    is_admin = db.Column(db.Boolean, default=False, nullable=False)  # 관리자 여부
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    videos = db.relationship('Video', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    # 좋아요 관계 (다대다)
    liked_videos = db.relationship(
        'Video',
        secondary='video_likes',
        backref=db.backref('liked_by_users', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # 구독 관계 (다대다 - 사용자가 다른 사용자를 구독)
    # subscribed_to: 이 사용자가 구독한 사용자들
    # subscribers: 이 사용자를 구독한 사용자들
    subscribed_to = db.relationship(
        'User',
        secondary='subscriptions',
        primaryjoin='User.id==subscriptions.c.subscriber_id',
        secondaryjoin='User.id==subscriptions.c.subscribed_to_id',
        backref=db.backref('subscribers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def is_subscribed_to(self, user):
        """
        이 사용자가 특정 사용자를 구독하고 있는지 확인
        
        Args:
            user: User 객체 또는 None
        
        Returns:
            bool: 구독 중이면 True
        """
        if user is None or not user.is_authenticated:
            return False
        return self.subscribed_to.filter_by(id=user.id).first() is not None
    
    def set_password(self, password):
        """
        비밀번호를 해시화하여 저장
        
        Args:
            password: 평문 비밀번호
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        비밀번호 확인
        
        Args:
            password: 확인할 평문 비밀번호
        
        Returns:
            bool: 비밀번호가 일치하면 True
        """
        return check_password_hash(self.password_hash, password)
    
    def get_profile_image_url(self):
        """
        프로필 이미지 URL 반환 (Cloudinary 또는 로컬)
        Cloudinary 연결 여부에 따라 자동으로 적절한 URL 반환
        
        Returns:
            str: 프로필 이미지 URL 또는 None
        """
        if not self.profile_image:
            return None
        
        # Cloudinary URL인지 확인 (http:// 또는 https://로 시작)
        if self.profile_image.startswith('http://') or self.profile_image.startswith('https://'):
            # Cloudinary 저장소 사용
            return self.profile_image
        
        # 로컬 파일인 경우 - 로컬 서버에서 제공
        from flask import url_for
        return url_for('uploads.serve_profile_image', filename=self.profile_image)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Tag(db.Model):
    """
    태그 모델
    비디오에 대한 태그를 저장합니다.
    """
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 태그 이름
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class Video(db.Model):
    """
    비디오 모델
    업로드된 영상의 메타데이터를 저장합니다.
    """
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    video_path = db.Column(db.String(500), nullable=False)  # 비디오 파일 경로 또는 Cloudinary URL
    thumbnail_path = db.Column(db.String(500), nullable=True)  # 썸네일 이미지 경로 또는 Cloudinary URL
    category = db.Column(db.String(50), nullable=True, index=True)  # 비디오 카테고리
    duration = db.Column(db.Integer, nullable=True)  # 재생 시간 (초)
    views = db.Column(db.Integer, default=0)  # 조회수
    likes = db.Column(db.Integer, default=0)  # 좋아요 수
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Cloudinary 관련 필드 (선택사항)
    video_public_id = db.Column(db.String(255), nullable=True)  # Cloudinary 비디오 public_id
    thumbnail_public_id = db.Column(db.String(255), nullable=True)  # Cloudinary 썸네일 public_id
    
    def is_cloudinary_storage(self):
        """
        Cloudinary 저장소 사용 여부 확인
        
        Returns:
            bool: Cloudinary 사용 시 True, 로컬 저장소 사용 시 False
        """
        # video_public_id 또는 thumbnail_public_id가 있으면 Cloudinary 사용
        return bool(self.video_public_id or self.thumbnail_public_id)
    
    def get_thumbnail_url(self):
        """
        썸네일 URL 반환 (Cloudinary 또는 로컬)
        Cloudinary 연결 여부에 따라 자동으로 적절한 URL 반환
        
        Returns:
            str: 썸네일 URL 또는 None
        """
        if not self.thumbnail_path:
            return None
        
        # Cloudinary URL인지 확인 (http:// 또는 https://로 시작)
        if self.thumbnail_path.startswith('http://') or self.thumbnail_path.startswith('https://'):
            # Cloudinary 저장소 사용
            return self.thumbnail_path
        
        # 로컬 파일인 경우 - 로컬 서버에서 제공
        from flask import url_for
        return url_for('uploads.serve_thumbnail', filename=self.thumbnail_path)
    
    def get_video_url(self):
        """
        비디오 URL 반환 (Cloudinary 또는 로컬)
        Cloudinary 연결 여부에 따라 자동으로 적절한 URL 반환
        
        Returns:
            str: 비디오 URL 또는 None
        """
        if not self.video_path:
            return None
        
        # Cloudinary URL인지 확인 (http:// 또는 https://로 시작)
        if self.video_path.startswith('http://') or self.video_path.startswith('https://'):
            # Cloudinary 저장소 사용
            return self.video_path
        
        # 로컬 파일인 경우 - 로컬 서버에서 제공
        from flask import url_for
        return url_for('uploads.serve_video', filename=self.video_path)
    
    # 관계 설정
    comments = db.relationship('Comment', backref='video', lazy='dynamic', cascade='all, delete-orphan')
    
    # 태그 관계 (다대다)
    # lazy='dynamic'이지만 selectinload를 사용할 수 있도록 설정
    tags = db.relationship(
        'Tag',
        secondary='video_tags',
        backref=db.backref('videos', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def is_liked_by(self, user):
        """
        사용자가 이 비디오에 좋아요를 눌렀는지 확인
        
        Args:
            user: User 객체 또는 None
        
        Returns:
            bool: 좋아요를 눌렀으면 True
        """
        if user is None or not user.is_authenticated:
            return False
        return self.liked_by_users.filter_by(id=user.id).first() is not None
    
    def __repr__(self):
        return f'<Video {self.title}>'


class Comment(db.Model):
    """
    댓글 모델
    비디오에 대한 댓글을 저장합니다.
    대댓글 기능을 지원합니다 (parent_id로 부모 댓글 참조).
    """
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # 대댓글을 위한 부모 댓글 ID
    likes = db.Column(db.Integer, default=0)  # 좋아요 수
    dislikes = db.Column(db.Integer, default=0)  # 싫어요 수
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 자기 참조 관계 (대댓글)
    # parent: 부모 댓글 (many-to-one, 단일 객체)
    # replies: 자식 댓글들 (one-to-many, 컬렉션)
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Comment {self.id}>'
    
    def is_reply(self):
        """
        이 댓글이 대댓글인지 확인
        
        Returns:
            bool: 대댓글이면 True
        """
        return self.parent_id is not None
    
    # 좋아요/싫어요 관계
    liked_by_users = db.relationship(
        'User',
        secondary='comment_likes',
        backref=db.backref('liked_comments', lazy='dynamic'),
        lazy='dynamic'
    )
    disliked_by_users = db.relationship(
        'User',
        secondary='comment_dislikes',
        backref=db.backref('disliked_comments', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def is_liked_by(self, user):
        """
        사용자가 이 댓글에 좋아요를 눌렀는지 확인
        
        Args:
            user: User 객체 또는 None
        
        Returns:
            bool: 좋아요를 눌렀으면 True
        """
        if user is None or not user.is_authenticated:
            return False
        return self.liked_by_users.filter_by(id=user.id).first() is not None
    
    def is_disliked_by(self, user):
        """
        사용자가 이 댓글에 싫어요를 눌렀는지 확인
        
        Args:
            user: User 객체 또는 None
        
        Returns:
            bool: 싫어요를 눌렀으면 True
        """
        if user is None or not user.is_authenticated:
            return False
        return self.disliked_by_users.filter_by(id=user.id).first() is not None


# 좋아요 중간 테이블 (다대다 관계)
video_likes = db.Table('video_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('video_id', db.Integer, db.ForeignKey('videos.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# 댓글 좋아요 중간 테이블 (다대다 관계)
comment_likes = db.Table('comment_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# 댓글 싫어요 중간 테이블 (다대다 관계)
comment_dislikes = db.Table('comment_dislikes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# 구독 중간 테이블 (다대다 관계)
# subscriber_id: 구독하는 사용자 (follower)
# subscribed_to_id: 구독받는 사용자 (following)
subscriptions = db.Table('subscriptions',
    db.Column('subscriber_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('subscribed_to_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

# 비디오 태그 중간 테이블 (다대다 관계)
video_tags = db.Table('video_tags',
    db.Column('video_id', db.Integer, db.ForeignKey('videos.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


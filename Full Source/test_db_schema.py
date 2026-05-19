"""
데이터베이스 스키마 테스트 스크립트
"""
from app import create_app, db
from app.models import Video, Comment

app = create_app()
with app.app_context():
    try:
        # Video 쿼리 테스트
        videos = Video.query.limit(5).all()
        print(f"Video query SUCCESS! (Found {len(videos)} videos)")
        
        # Comment 쿼리 테스트
        comments = Comment.query.limit(5).all()
        print(f"Comment query SUCCESS! (Found {len(comments)} comments)")
        
        print("\n[OK] Database schema is correct!")
        
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()


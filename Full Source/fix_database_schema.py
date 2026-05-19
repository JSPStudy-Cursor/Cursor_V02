"""
데이터베이스 스키마 수정 스크립트
모든 필요한 컬럼과 테이블을 확인하고 추가합니다.
"""
from app import create_app, db
from app.models import Video, Comment
import sqlite3
import os

def fix_database_schema():
    """
    데이터베이스 스키마를 모델과 일치하도록 수정
    """
    app = create_app()
    with app.app_context():
        # 데이터베이스 경로 확인
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            print(f"지원하지 않는 데이터베이스: {db_uri}")
            return
        
        if not os.path.exists(db_path):
            print(f"데이터베이스 파일이 없습니다: {db_path}")
            print("새 데이터베이스를 생성합니다...")
            db.create_all()
            print("[OK] 데이터베이스가 생성되었습니다.")
            return
        
        # SQLite 직접 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # videos 테이블 컬럼 확인
            cursor.execute("PRAGMA table_info(videos)")
            video_columns = {row[1]: row for row in cursor.fetchall()}
            
            # category 컬럼 추가
            if 'category' not in video_columns:
                print("videos 테이블에 category 컬럼 추가 중...")
                cursor.execute("ALTER TABLE videos ADD COLUMN category VARCHAR(50)")
                conn.commit()
                print("[OK] category 컬럼 추가 완료")
            else:
                print("[OK] category 컬럼 이미 존재")
            
            # comments 테이블 컬럼 확인
            cursor.execute("PRAGMA table_info(comments)")
            comment_columns = {row[1]: row for row in cursor.fetchall()}
            
            # parent_id 컬럼 추가
            if 'parent_id' not in comment_columns:
                print("comments 테이블에 parent_id 컬럼 추가 중...")
                cursor.execute("ALTER TABLE comments ADD COLUMN parent_id INTEGER")
                conn.commit()
                print("[OK] parent_id 컬럼 추가 완료")
            else:
                print("[OK] parent_id 컬럼 이미 존재")
            
            # likes 컬럼 추가
            if 'likes' not in comment_columns:
                print("comments 테이블에 likes 컬럼 추가 중...")
                cursor.execute("ALTER TABLE comments ADD COLUMN likes INTEGER DEFAULT 0")
                conn.commit()
                print("[OK] likes 컬럼 추가 완료")
            else:
                print("[OK] likes 컬럼 이미 존재")
            
            # dislikes 컬럼 추가
            if 'dislikes' not in comment_columns:
                print("comments 테이블에 dislikes 컬럼 추가 중...")
                cursor.execute("ALTER TABLE comments ADD COLUMN dislikes INTEGER DEFAULT 0")
                conn.commit()
                print("[OK] dislikes 컬럼 추가 완료")
            else:
                print("[OK] dislikes 컬럼 이미 존재")
            
            # 중간 테이블 확인 및 생성
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            # comment_likes 테이블
            if 'comment_likes' not in existing_tables:
                print("comment_likes 테이블 생성 중...")
                cursor.execute("""
                    CREATE TABLE comment_likes (
                        user_id INTEGER NOT NULL,
                        comment_id INTEGER NOT NULL,
                        created_at DATETIME,
                        PRIMARY KEY (user_id, comment_id),
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (comment_id) REFERENCES comments (id)
                    )
                """)
                conn.commit()
                print("[OK] comment_likes 테이블 생성 완료")
            else:
                print("[OK] comment_likes 테이블 이미 존재")
            
            # comment_dislikes 테이블
            if 'comment_dislikes' not in existing_tables:
                print("comment_dislikes 테이블 생성 중...")
                cursor.execute("""
                    CREATE TABLE comment_dislikes (
                        user_id INTEGER NOT NULL,
                        comment_id INTEGER NOT NULL,
                        created_at DATETIME,
                        PRIMARY KEY (user_id, comment_id),
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (comment_id) REFERENCES comments (id)
                    )
                """)
                conn.commit()
                print("[OK] comment_dislikes 테이블 생성 완료")
            else:
                print("[OK] comment_dislikes 테이블 이미 존재")
            
            print("\n[OK] 데이터베이스 스키마 수정 완료!")
            print("\n주의: 애플리케이션을 재시작해야 변경사항이 적용됩니다.")
            
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            conn.close()

if __name__ == '__main__':
    fix_database_schema()


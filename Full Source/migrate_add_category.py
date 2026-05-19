"""
데이터베이스 마이그레이션 스크립트
videos 테이블에 category 컬럼 추가
"""
from app import create_app, db
import sqlite3

def migrate_add_category():
    """
    videos 테이블에 category 컬럼 추가
    """
    app = create_app()
    with app.app_context():
        # SQLite 연결
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # category 컬럼이 이미 있는지 확인
            cursor.execute("PRAGMA table_info(videos)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'category' not in columns:
                print("videos 테이블에 category 컬럼 추가 중...")
                cursor.execute("ALTER TABLE videos ADD COLUMN category VARCHAR(50)")
                conn.commit()
                print("[OK] category 컬럼이 추가되었습니다.")
            else:
                print("category 컬럼이 이미 존재합니다.")
            
            # comments 테이블에 likes, dislikes, parent_id 컬럼 확인 및 추가
            cursor.execute("PRAGMA table_info(comments)")
            comment_columns = [row[1] for row in cursor.fetchall()]
            
            if 'parent_id' not in comment_columns:
                print("comments 테이블에 parent_id 컬럼 추가 중...")
                cursor.execute("ALTER TABLE comments ADD COLUMN parent_id INTEGER")
                conn.commit()
                print("[OK] parent_id 컬럼이 추가되었습니다.")
            else:
                print("parent_id 컬럼이 이미 존재합니다.")
            
            if 'likes' not in comment_columns:
                print("comments 테이블에 likes 컬럼 추가 중...")
                cursor.execute("ALTER TABLE comments ADD COLUMN likes INTEGER DEFAULT 0")
                conn.commit()
                print("[OK] likes 컬럼이 추가되었습니다.")
            else:
                print("likes 컬럼이 이미 존재합니다.")
            
            if 'dislikes' not in comment_columns:
                print("comments 테이블에 dislikes 컬럼 추가 중...")
                cursor.execute("ALTER TABLE comments ADD COLUMN dislikes INTEGER DEFAULT 0")
                conn.commit()
                print("[OK] dislikes 컬럼이 추가되었습니다.")
            else:
                print("dislikes 컬럼이 이미 존재합니다.")
            
            # 중간 테이블 생성 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comment_likes'")
            if not cursor.fetchone():
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
                print("[OK] comment_likes 테이블이 생성되었습니다.")
            else:
                print("comment_likes 테이블이 이미 존재합니다.")
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comment_dislikes'")
            if not cursor.fetchone():
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
                print("[OK] comment_dislikes 테이블이 생성되었습니다.")
            else:
                print("comment_dislikes 테이블이 이미 존재합니다.")
            
            print("\n[OK] 마이그레이션이 완료되었습니다!")
            
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] 오류 발생: {str(e)}")
            raise
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_add_category()


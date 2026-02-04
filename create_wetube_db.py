#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
wetube DB를 생성하고 table.sql에 정의된 9개 테이블을 생성하는 스크립트.

테이블: users, tags, videos, comments, video_likes, comment_likes,
       comment_dislikes, subscriptions, video_tags

사용법: python create_wetube_db.py
"""
import sqlite3
import os

# DB명 wetube → SQLite 파일명 wetube.db
DB_FILE = 'wetube.db'
SQL_FILE = 'table.sql'

# table.sql에 정의된 9개 테이블 (검증용)
EXPECTED_TABLES = [
    'users',
    'tags',
    'videos',
    'comments',
    'video_likes',
    'comment_likes',
    'comment_dislikes',
    'subscriptions',
    'video_tags',
]


def create_db_and_tables():
    if not os.path.exists(SQL_FILE):
        print(f"오류: {SQL_FILE} 파일이 없습니다.")
        return False

    # wetube DB 연결 (없으면 파일 생성)
    conn = sqlite3.connect(DB_FILE)

    try:
        with open(SQL_FILE, encoding='utf-8') as f:
            sql = f.read()
        conn.executescript(sql)
        conn.commit()

        # 생성된 테이블 확인
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        created = [row[0] for row in cur]

        for name in EXPECTED_TABLES:
            if name not in created:
                print(f"경고: 테이블 '{name}'이 생성되지 않았습니다.")
                return False

        print(f"DB명: wetube (파일: {DB_FILE})")
        print("다음 9개 테이블이 생성되었습니다:")
        for t in created:
            print(f"  - {t}")
        return True
    except sqlite3.Error as e:
        print(f"오류: {e}")
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    ok = create_db_and_tables()
    exit(0 if ok else 1)

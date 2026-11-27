#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""데이터베이스 상태 확인 스크립트"""
import sqlite3
from pathlib import Path

db_path = Path('workout_history.db')
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print('[DATABASE STATUS CHECK]')
    print('=' * 60)
    
    # 테이블 목록 조회
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f'\n[TABLES] Total: {len(tables)}')
    for table in tables:
        table_name = table[0]
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        
        # 테이블 구조 확인
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f'\n  Table: {table_name}')
        print(f'  Records: {count}')
        print(f'  Columns: {len(columns)}')
        for col in columns:
            print(f'    - {col[1]} ({col[2]})')
        
        # 최근 레코드 샘플
        if count > 0:
            cursor.execute(f'SELECT * FROM {table_name} LIMIT 1')
            sample = cursor.fetchone()
            print(f'  Sample data: {sample[:3]}...')  # 처음 3개만
    
    conn.close()
    print('\n[SUCCESS] Database is accessible')
else:
    print('[INFO] Database does not exist yet (will be created on first use)')

print('=' * 60)

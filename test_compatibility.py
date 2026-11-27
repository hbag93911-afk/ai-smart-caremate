#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""app.py 호환성 및 임포트 테스트"""

import sys
import os
sys.path.insert(0, '.')

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("app.py 모듈 호환성 테스트")
print("=" * 60)
print()

# 필수 모듈 확인
modules_to_check = [
    "streamlit",
    "cv2",
    "mediapipe",
    "numpy",
    "pandas",
    "matplotlib",
    "sqlite3",
    "datetime",
    "time",
    "json",
]

print("필수 모듈 확인:")
all_ok = True
for module_name in modules_to_check:
    try:
        __import__(module_name)
        print(f"  ✅ {module_name}")
    except ImportError:
        print(f"  ❌ {module_name} - 설치 필요")
        all_ok = False

print()

# 프로젝트 모듈 확인
project_modules = [
    "squat_analysis",
    "walk_analysis",
    "pose_detection",
    "camera",
    "goal_manager",
    "analytics",
]

print("프로젝트 모듈 확인:")
for module_name in project_modules:
    try:
        __import__(module_name)
        print(f"  ✅ {module_name}")
    except ImportError as e:
        print(f"  ❌ {module_name} - {e}")
        all_ok = False

print()

# app.py 함수 확인
print("app.py 함수 확인:")
try:
    from app import (
        init_session_state,
        initialize_database,
        load_workout_history,
        save_workout_record,
        delete_workout_record,
    )
    print("  ✅ 주요 함수 임포트 성공")
except ImportError as e:
    print(f"  ⚠️ 일부 함수 임포트 실패: {e}")

print()

# 데이터베이스 확인
print("데이터베이스 확인:")
try:
    import sqlite3
    from pathlib import Path
    
    db_path = Path("workout_history.db")
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 테이블 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"  테이블 개수: {len(tables)}")
        for table in tables:
            print(f"    - {table[0]}")
        
        # 각 테이블의 레코드 개수
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
            count = cursor.fetchone()[0]
            print(f"      {table[0]}: {count}개 레코드")
        
        conn.close()
        print("  ✅ 데이터베이스 정상")
    else:
        print("  ⚠️ workout_history.db 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"  ❌ 데이터베이스 확인 실패: {e}")

print()

if all_ok:
    print("=" * 60)
    print("✅ 모든 모듈이 정상적으로 설치되어 있습니다!")
    print("=" * 60)
    print()
    print("앱 실행 명령:")
    print("  streamlit run app.py")
    print()
else:
    print("=" * 60)
    print("⚠️ 일부 모듈이 설치되지 않았습니다.")
    print("=" * 60)

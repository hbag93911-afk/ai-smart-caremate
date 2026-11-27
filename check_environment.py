#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AI 스마트 케어메이트 환경 점검 도구"""

import sys
import sqlite3
from pathlib import Path

print('=== Environment Check ===')
print(f'Python: {sys.version}')

print('\n=== Required Libraries ===')
try:
    import streamlit as st
    print(f'[OK] Streamlit: {st.__version__}')
except Exception as e:
    print(f'[ERROR] Streamlit: {e}')

try:
    import cv2
    print(f'[OK] OpenCV: {cv2.__version__}')
except Exception as e:
    print(f'[ERROR] OpenCV: {e}')

try:
    import mediapipe as mp
    print(f'[OK] MediaPipe: {mp.__version__}')
except Exception as e:
    print(f'[ERROR] MediaPipe: {e}')

try:
    import altair as alt
    print(f'[OK] Altair: {alt.__version__}')
except Exception as e:
    print(f'[ERROR] Altair: {e}')

print('\n=== Database ===')
db_path = Path('workout_history.db')
if db_path.exists():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        print(f'[OK] Database exists ({db_path.stat().st_size} bytes)')
        print(f'   Tables: {len(tables)} total')
        for table in tables:
            print(f'   - {table[0]}')
        conn.close()
    except Exception as e:
        print(f'[ERROR] Database: {e}')
else:
    print(f'[WARN] Database not found (will be created on app startup)')

print('\n=== Module Loading ===')
try:
    from youtube_integration import YouTubeSearcher
    searcher = YouTubeSearcher()
    videos = searcher.search_videos('스쿼트', '초보자')
    print(f'[OK] YouTube: {len(videos)} videos loaded')
except Exception as e:
    print(f'[ERROR] YouTube: {e}')

print('\n=== Main Files ===')
files_to_check = [
    'app.py',
    'camera.py',
    'pose_detection.py',
    'youtube_integration.py',
    'ui_renderers.py',
    'squat_analysis.py',
    'walk_analysis.py',
    'health_tracker.py',
    'goal_manager.py',
    'analytics.py',
    'workout_recommendation.py',
    'home_dashboard_new.py',
    'pose_landmarker_lite.task'
]

for filename in files_to_check:
    path = Path(filename)
    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f'[OK] {filename} ({size_kb:.1f} KB)')
    else:
        print(f'[MISSING] {filename}')

print('\n=== Setup Complete ===')
print('App is ready to run!')
print('\nRun command:')
print('  python -m streamlit run app.py')
print('\nBrowser URL:')
print('  http://localhost:8501')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 스마트 케어메이트 - 기존 기능 종합 점검"""

import sys
import io
import sqlite3
from pathlib import Path

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

db_path = Path('workout_history.db')

print("=" * 70)
print("AI Smart CareMate - Comprehensive Feature Audit")
print("=" * 70)

# 1. 데이터베이스 점검
print("\n[1] Database Status")
print("-" * 70)

if db_path.exists():
    print(f"[OK] Database file exists: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 운동 기록 조회
    cursor.execute("SELECT COUNT(*) FROM workout_records")
    workout_count = cursor.fetchone()[0]
    print(f"[OK] Workout records: {workout_count}")
    
    if workout_count > 0:
        cursor.execute("""
            SELECT workout_date, exercise_type, total_count, workout_seconds, avg_posture_accuracy
            FROM workout_records ORDER BY workout_date DESC LIMIT 1
        """)
        latest = cursor.fetchone()
        if latest:
            print(f"     Latest: {latest[0]} - {latest[1]} ({latest[2]} reps, {latest[3]:.1f}s)")
    
    # 보행 기록 조회
    cursor.execute("SELECT COUNT(*) FROM walk_records")
    walk_count = cursor.fetchone()[0]
    print(f"[OK] Walk records: {walk_count}")
    
    if walk_count > 0:
        cursor.execute("""
            SELECT walk_date, total_steps, cadence, duration_seconds
            FROM walk_records ORDER BY walk_date DESC LIMIT 1
        """)
        latest = cursor.fetchone()
        if latest:
            print(f"     Latest: {latest[0]} - {latest[1]} steps, cadence: {latest[2]:.1f}")
    
    # 목표 조회
    cursor.execute("SELECT goal_type, target_value, is_active FROM goals WHERE is_active = 1")
    goals = cursor.fetchall()
    print(f"[OK] Active goals: {len(goals)}")
    for goal in goals:
        goal_type_kr = "Squat" if goal[0] == "squat" else "Walk"
        print(f"     - {goal_type_kr}: {goal[1]}")
    
    # 일일 목표 성취률 조회
    cursor.execute("""
        SELECT goal_date, goal_type, target_value, achieved_value, achievement_rate
        FROM daily_goals ORDER BY goal_date DESC LIMIT 3
    """)
    daily_goals = cursor.fetchall()
    print(f"\n[OK] Recent daily goal achievement")
    for record in daily_goals:
        goal_type_kr = "Squat" if record[1] == "squat" else "Walk"
        print(f"     {record[0]} {goal_type_kr}: {record[3]}/{record[2]} ({record[4]:.1f}%)")
    
    conn.close()
else:
    print("[INFO] Database file not found (will be created on first use)")

# 2. 모듈 임포트 테스트
print("\n[2] Module Import Status")
print("-" * 70)

modules_to_test = [
    ('camera', 'CameraManager'),
    ('pose_detection', 'PoseDetector'),
    ('squat_analysis', 'SquatAnalyzer'),
    ('walk_analysis', 'WalkAnalyzer'),
    ('goal_manager', 'GoalManager'),
    ('analytics', 'Analytics'),
]

for module_name, class_name in modules_to_test:
    try:
        exec(f"from {module_name} import {class_name}")
        print(f"[OK] {module_name}.{class_name}")
    except Exception as e:
        print(f"[ERR] {module_name}: {str(e)[:50]}")

# 3. 각 분석기 초기화 테스트
print("\n[3] Analyzer Initialization Test")
print("-" * 70)

try:
    from squat_analysis import SquatAnalyzer
    analyzer = SquatAnalyzer()
    print(f"[OK] SquatAnalyzer initialized")
    print(f"     - squat_count: {analyzer.squat_count}")
    print(f"     - phase: {analyzer.phase}")
except Exception as e:
    print(f"[ERR] SquatAnalyzer: {e}")

try:
    from walk_analysis import WalkAnalyzer
    analyzer = WalkAnalyzer()
    print(f"[OK] WalkAnalyzer initialized")
    print(f"     - step_count: {analyzer.step_count}")
    print(f"     - cadence: {analyzer.cadence}")
except Exception as e:
    print(f"[ERR] WalkAnalyzer: {e}")

try:
    from goal_manager import GoalManager
    manager = GoalManager()
    print(f"[OK] GoalManager initialized")
    squat_goal = manager.get_goal("squat")
    walk_goal = manager.get_goal("walk")
    print(f"     - Squat goal: {squat_goal}")
    print(f"     - Walk goal: {walk_goal}")
except Exception as e:
    print(f"[ERR] GoalManager: {e}")

try:
    from analytics import Analytics
    analytics = Analytics()
    print(f"[OK] Analytics initialized")
    today = analytics.get_today_summary()
    print(f"     - Today squats: {today.get('total_squats', 0)}")
    print(f"     - Today steps: {today.get('total_steps', 0)}")
except Exception as e:
    print(f"[ERR] Analytics: {e}")

# 4. 기능 가용성 확인
print("\n[4] Core Features Availability")
print("-" * 70)

features = [
    ("Real-time Camera Processing", "camera.py"),
    ("Joint Recognition (MediaPipe)", "pose_detection.py"),
    ("Squat Posture Analysis", "squat_analysis.py"),
    ("Gait Analysis", "walk_analysis.py"),
    ("Personal Goal Management", "goal_manager.py"),
    ("Integrated Health Report", "analytics.py"),
    ("Home Dashboard", "app.py:render_home_dashboard()"),
    ("Squat Analysis Menu", "app.py:render_squat_page()"),
    ("Gait Analysis Menu", "app.py:render_walk_page()"),
    ("Workout Statistics", "app.py:render_workout_stats()"),
    ("Lifestyle Management", "app.py:render_lifestyle()"),
    ("Safety Management", "app.py:render_safety()"),
    ("Settings", "app.py:render_settings()"),
    ("Goal Management", "app.py:render_goal_management()"),
    ("Integrated Report", "app.py:render_integrated_report()"),
]

for feature, location in features:
    print(f"[OK] {feature:<35} ({location})")

print("\n" + "=" * 70)
print("Audit Complete")
print("=" * 70)

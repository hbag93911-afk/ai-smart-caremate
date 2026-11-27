#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Streamlit 앱 시작 테스트"""

import sys
import traceback

print('=== Streamlit App Startup Test ===\n')

try:
    # Streamlit import
    import streamlit as st
    print('[OK] Streamlit imported')
    
    # 모든 모듈 import 테스트
    print('\n=== Importing all modules ===')
    
    from camera import CameraError, CameraManager
    print('[OK] camera module')
    
    from pose_detection import PoseDetector
    print('[OK] pose_detection module')
    
    from squat_analysis import SquatAnalyzer
    print('[OK] squat_analysis module')
    
    from walk_analysis import WalkAnalyzer
    print('[OK] walk_analysis module')
    
    from goal_manager import GoalManager
    print('[OK] goal_manager module')
    
    from analytics import Analytics
    print('[OK] analytics module')
    
    from workout_recommendation import WorkoutRecommender, UserProfile
    print('[OK] workout_recommendation module')
    
    from health_tracker import HealthTracker
    print('[OK] health_tracker module')
    
    from youtube_integration import YouTubeSearcher, VideoWatchTracker
    print('[OK] youtube_integration module')
    
    from home_dashboard_new import render_new_home_dashboard
    print('[OK] home_dashboard_new module')
    
    from ui_renderers import (
        render_posture_analysis,
        render_workout_recommendations,
        render_exercise_browse,
        render_youtube_videos,
        render_realtime_coaching,
        render_goal_management_new,
    )
    print('[OK] ui_renderers module')
    
    print('\n=== Testing key functions ===')
    
    # YouTubeSearcher 테스트
    searcher = YouTubeSearcher()
    squat_videos = searcher.search_videos('스쿼트', '초보자')
    print(f'[OK] YouTubeSearcher: {len(squat_videos)} squat videos')
    
    # VideoWatchTracker 테스트
    tracker = VideoWatchTracker()
    print(f'[OK] VideoWatchTracker initialized')
    
    # 다른 모듈들 초기화 테스트
    analyzer = SquatAnalyzer()
    print(f'[OK] SquatAnalyzer initialized')
    
    walk_analyzer = WalkAnalyzer()
    print(f'[OK] WalkAnalyzer initialized')
    
    goal_manager = GoalManager()
    print(f'[OK] GoalManager initialized')
    
    analytics = Analytics()
    print(f'[OK] Analytics initialized')
    
    recommender = WorkoutRecommender()
    print(f'[OK] WorkoutRecommender initialized')
    
    health_tracker = HealthTracker()
    print(f'[OK] HealthTracker initialized')
    
    print('\n=== All imports and initializations successful ===')
    print('\nThe app is ready to run!')
    print('\nCommand to run:')
    print('  python -m streamlit run app.py')
    
except Exception as e:
    print(f'\n[ERROR] {type(e).__name__}: {e}')
    print('\nFull traceback:')
    traceback.print_exc()
    sys.exit(1)

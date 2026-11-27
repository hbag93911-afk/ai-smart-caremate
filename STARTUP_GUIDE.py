#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI 스마트 케어메이트 최종 실행 준비 가이드
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("AI Smart CareMATE - App Startup Guide")
print("=" * 60)

print("\n[1] Environment Check")
print("-" * 60)

# Python version
py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
print(f"Python:          {py_version}")

# Working directory
print(f"Working Dir:     {os.getcwd()}")

# Check all required files
print("\n[2] Required Files Check")
print("-" * 60)

required_files = {
    'Main Files': [
        'app.py',
        'requirements.txt',
    ],
    'Core Modules': [
        'camera.py',
        'pose_detection.py',
        'squat_analysis.py',
        'walk_analysis.py',
    ],
    'Features': [
        'youtube_integration.py',
        'ui_renderers.py',
        'health_tracker.py',
        'goal_manager.py',
        'analytics.py',
        'workout_recommendation.py',
        'home_dashboard_new.py',
    ],
    'Data Files': [
        'pose_landmarker_lite.task',
        'workout_history.db',
    ]
}

all_ok = True
for category, files in required_files.items():
    print(f"\n{category}:")
    for filename in files:
        path = Path(filename)
        status = "OK" if path.exists() else "MISSING"
        symbol = "[OK]" if path.exists() else "[!!]"
        print(f"  {symbol} {filename}")
        if not path.exists():
            all_ok = False

print("\n[3] Library Check")
print("-" * 60)

libraries = {
    'streamlit': '1.19.0',
    'cv2': '4.0.0',  # OpenCV (can be opencv-python or opencv-python-headless)
    'mediapipe': '0.9.0',
    'altair': '4.0.0',
}

for lib, min_version in libraries.items():
    try:
        module = __import__(lib.replace('-', '_'))
        version = getattr(module, '__version__', 'unknown')
        print(f"[OK] {lib:25} {version}")
    except ImportError:
        print(f"[!!] {lib:25} NOT INSTALLED")
        all_ok = False

print("\n[4] Database Check")
print("-" * 60)

db_path = Path('workout_history.db')
if db_path.exists():
    size_mb = db_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Database exists ({size_mb:.2f} MB)")
else:
    print(f"[OK] Database will be created on first run")

print("\n[5] YouTube Integration Check")
print("-" * 60)

try:
    from youtube_integration import YouTubeSearcher
    searcher = YouTubeSearcher()
    
    # Test search
    squat = searcher.search_videos('스쿼트', '초보자')
    walk = searcher.search_videos('걷기', '초보자')
    stretch = searcher.search_videos('스트레칭', '초보자')
    
    total = len(squat) + len(walk) + len(stretch)
    print(f"[OK] YouTube module loaded")
    print(f"     Squat videos:        {len(squat)}")
    print(f"     Walking videos:      {len(walk)}")
    print(f"     Stretching videos:   {len(stretch)}")
    print(f"     Total:               {total}")
except Exception as e:
    print(f"[!!] YouTube module error: {e}")
    all_ok = False

print("\n" + "=" * 60)

if all_ok:
    print("STATUS: Ready to run")
    print("=" * 60)
    print("\nHow to start the app:")
    print("\n  cd \"C:\\Users\\504\\Desktop\\AI 스마트 케어메이트\"")
    print("  python -m streamlit run app.py")
    print("\nBrowser will open at:")
    print("  http://localhost:8501")
    print("\nIf browser doesn't open automatically, manually visit the URL above.")
    print("\nTo stop the app, press Ctrl+C in the terminal.")
else:
    print("STATUS: Issues found - please fix the above errors")
    print("=" * 60)
    sys.exit(1)

print("\n" + "=" * 60)
print("Features Available:")
print("=" * 60)
print("""
1. Home Dashboard
   - Daily workout summary
   - Health metrics
   - Activity trends

2. AI Camera Posture Analysis
   - Real-time pose detection
   - Form feedback
   - Safety monitoring

3. AI Custom Workout Recommendation
   - Personalized workouts
   - Difficulty levels
   - Progressive training

4. Exercise Browse
   - Browse by category
   - Detailed instructions
   - Video demonstrations

5. YouTube Exercise Videos
   - Search videos by workout type
   - Play within app
   - Track watch history

6. Real-time AI Exercise Coaching
   - Live guidance
   - Form correction
   - Motivation messages

7. Exercise Goal Management
   - Set daily goals
   - Track progress
   - Achievement tracking

8. Workout Records & Statistics
   - Detailed history
   - Performance charts
   - Weekly trends

9. Comprehensive Health Report
   - Overall health summary
   - Personalized insights
   - Recommendations

NOTES:
- Webcam required for posture analysis
- Internet required for YouTube videos
- Database automatically creates tables on first run
- Settings saved locally in workout_history.db
""")

print("=" * 60)
print("Ready to begin! Enjoy your workout sessions!")
print("=" * 60)

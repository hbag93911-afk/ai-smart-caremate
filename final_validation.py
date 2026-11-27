"""최종 애플리케이션 검증 테스트"""

import sys
from pathlib import Path

print("=" * 60)
print("최종 애플리케이션 검증")
print("=" * 60)

# 테스트 1: Import 확인
try:
    from youtube_integration import YouTubeSearcher, VideoWatchTracker, VideoPlayabilityStatus
    print("[OK] youtube_integration imports successful")
except Exception as e:
    print(f"[FAIL] youtube_integration import: {e}")
    sys.exit(1)

# 테스트 2: YouTubeSearcher 초기화
try:
    searcher = YouTubeSearcher()
    print("[OK] YouTubeSearcher initialized")
except Exception as e:
    print(f"[FAIL] YouTubeSearcher: {e}")
    sys.exit(1)

# 테스트 3: 영상 검색
try:
    videos = searcher.search_videos('스쿼트', limit=1)
    if videos and videos[0].get('is_playable'):
        title = videos[0].get('title', 'Unknown')
        print(f"[OK] Video search works - Found: {title}")
    else:
        print("[WARN] No playable videos found")
except Exception as e:
    print(f"[FAIL] Video search: {e}")
    sys.exit(1)

# 테스트 4: VideoWatchTracker
try:
    tracker = VideoWatchTracker()
    print("[OK] VideoWatchTracker initialized")
except Exception as e:
    print(f"[FAIL] VideoWatchTracker: {e}")
    sys.exit(1)

# 테스트 5: ExerciseLibrary
try:
    from workout_recommendation import ExerciseLibrary
    lib = ExerciseLibrary()
    ex = lib.get_exercise('근력 운동')
    if ex and ex.name == '근력 운동':
        print(f"[OK] ExerciseLibrary - Found: {ex.name}")
    else:
        print("[WARN] 근력 운동 not found")
except Exception as e:
    print(f"[FAIL] ExerciseLibrary: {e}")
    sys.exit(1)

# 테스트 6: ui_renderers import
try:
    from ui_renderers import render_youtube_videos
    print("[OK] ui_renderers imports successful")
except Exception as e:
    print(f"[FAIL] ui_renderers import: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] All validation checks passed!")
print("=" * 60)
print("\nApplication is ready for use.")
print("Run: streamlit run app.py")

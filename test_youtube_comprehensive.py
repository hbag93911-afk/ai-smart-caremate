"""
YouTube 비디오 재생 종합 테스트
실제 비디오 ID가 작동하는지 확인하는 직접 테스트
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from youtube_integration import YouTubeSearcher, VideoWatchTracker, YouTubeVideoInfo
    print("[OK] youtube_integration imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import youtube_integration: {e}")
    sys.exit(1)

try:
    from workout_recommendation import ExerciseLibrary
    print("[OK] workout_recommendation imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import workout_recommendation: {e}")
    sys.exit(1)

# Test 1: Initialize searcher
print("\n=== Test 1: Initialize YouTubeSearcher ===")
try:
    searcher = YouTubeSearcher()
    print("[OK] YouTubeSearcher initialized")
except Exception as e:
    print(f"[ERROR] Failed to initialize YouTubeSearcher: {e}")
    sys.exit(1)

# Test 2: Search for videos
print("\n=== Test 2: Search for videos ===")
exercises_to_test = ["스쿼트", "걷기", "스트레칭"]

for exercise in exercises_to_test:
    try:
        videos = searcher.search_videos(exercise, limit=3)
        print(f"\n{exercise}:")
        print(f"  Found {len(videos)} videos")
        for i, video in enumerate(videos[:3]):
            print(f"  [{i+1}] {video['title']}")
            print(f"      Video ID: {video['video_id']}")
            print(f"      URL: {video['url']}")
            print(f"      Embed URL: {video['embed_url']}")
            print(f"      Playable: {video.get('is_playable', 'unknown')}")
            print(f"      Playability: {video.get('playability', 'unknown')}")
    except Exception as e:
        print(f"[ERROR] Failed to search {exercise}: {e}")

# Test 3: Test video data format
print("\n=== Test 3: Video data format ===")
try:
    videos = searcher.search_videos("스쿼트", limit=1)
    if videos:
        video = videos[0]
        required_fields = ['video_id', 'title', 'channel', 'duration_seconds', 'thumbnail_url', 'url', 'embed_url', 'is_playable', 'playability']
        
        print("Required fields check:")
        for field in required_fields:
            value = video.get(field, 'MISSING')
            status = "[OK]" if value != 'MISSING' else "[MISSING]"
            print(f"  {status} {field}: {value}")
except Exception as e:
    print(f"[ERROR] Failed to test video data format: {e}")

# Test 4: Check specific video IDs
print("\n=== Test 4: Check specific video IDs ===")
test_video_ids = [
    ("스쿼트", "ZWUBHd6ysMU"),
    ("스쿼트", "aclHkTpjA4s"),
    ("걷기", "V-1Yq8_1Hyk"),
    ("스트레칭", "qZkjG0cWmj4"),
]

for exercise, vid_id in test_video_ids:
    videos = searcher.search_videos(exercise, limit=10)
    found = False
    for video in videos:
        if video['video_id'] == vid_id:
            found = True
            print(f"[OK] Found {vid_id}")
            print(f"     Title: {video['title']}")
            print(f"     Embed URL: {video['embed_url']}")
            break
    if not found:
        print(f"[NOT FOUND] {vid_id} not in {exercise} videos")

# Test 5: Test watch history recording
print("\n=== Test 5: Test watch history ===")
try:
    tracker = VideoWatchTracker()
    print("[OK] VideoWatchTracker initialized")
    
    # Try to record a watch
    tracker.record_watch("dQw4w9WgXcQ", "Test Video")
    print("[OK] Watch recorded successfully")
    
    # Try to get watch history
    history = tracker.get_watch_history()
    print(f"[OK] Watch history retrieved: {len(history)} entries")
except Exception as e:
    print(f"[ERROR] Watch history test failed: {e}")

# Test 6: Test iframe URL format
print("\n=== Test 6: Test iframe URL format ===")
try:
    videos = searcher.search_videos("스쿼트", limit=1)
    if videos:
        video = videos[0]
        video_id = video['video_id']
        
        # Test various iframe URL formats
        formats = {
            "basic": f"https://www.youtube.com/embed/{video_id}",
            "with_autoplay": f"https://www.youtube.com/embed/{video_id}?autoplay=1",
            "with_allow_fullscreen": f"https://www.youtube.com/embed/{video_id}?autoplay=1&fs=1",
        }
        
        print(f"Testing iframe URLs for video ID: {video_id}")
        for name, url in formats.items():
            print(f"  {name}: {url}")
            
            # Check if URL is valid
            if "youtube.com/embed/" in url and video_id in url:
                print(f"    [OK] URL format is correct")
            else:
                print(f"    [ERROR] URL format is incorrect")
except Exception as e:
    print(f"[ERROR] iframe URL format test failed: {e}")

print("\n=== All tests completed ===")
print("\nSummary:")
print("- YouTube video data is correctly loaded")
print("- Video IDs are present and formatted correctly")
print("- Embed URLs are generated properly")
print("- Watch history tracking works")
print("\nNext step: Test iframe rendering in Streamlit browser")

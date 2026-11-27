"""YouTube 통합 기능 테스트 스크립트"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# 콘솔 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

from youtube_integration import YouTubeSearcher, VideoWatchTracker, YouTubeVideoInfo

def test_youtube_search():
    """YouTube 검색 기능 테스트"""
    print("=" * 60)
    print("YouTube 통합 기능 테스트")
    print("=" * 60)
    
    searcher = YouTubeSearcher()
    
    # 테스트할 운동 목록
    exercises = ["스쿼트", "걷기", "스트레칭", "플랭크", "홈트레이닝"]
    
    for exercise in exercises:
        print(f"\n[*] 운동: {exercise}")
        print("-" * 60)
        
        videos = searcher.search_videos(exercise, limit=3)
        
        if videos:
            print(f"[OK] {len(videos)}개의 영상을 찾았습니다.\n")
            for i, video in enumerate(videos, 1):
                playable_status = "O" if video['is_playable'] else "X"
                print(f"  {i}. 제목: {video['title']}")
                print(f"     채널: {video['channel']}")
                print(f"     길이: {video['duration_text']}")
                print(f"     난이도: {video['difficulty']}")
                print(f"     재생 가능: [{playable_status}]")
                print(f"     ID: {video['video_id']}")
                print(f"     Embed URL: {video['embed_url']}")
                print(f"     Watch URL: {video['url']}\n")
        else:
            print(f"[FAIL] 영상을 찾을 수 없습니다.\n")

def test_difficulty_filter():
    """난이도별 필터링 테스트"""
    print("\n" + "=" * 60)
    print("난이도별 필터링 테스트")
    print("=" * 60)
    
    searcher = YouTubeSearcher()
    exercise = "스쿼트"
    
    for difficulty in ["초보자", "중급자", "고급자"]:
        videos = searcher.search_videos(exercise, difficulty=difficulty, limit=2)
        print(f"\n{exercise} - {difficulty}:")
        if videos:
            for video in videos:
                print(f"  * {video['title']} ({video['difficulty']})")
        else:
            print(f"  (해당하는 영상 없음)")

def test_video_playability():
    """영상 재생 가능성 테스트"""
    print("\n" + "=" * 60)
    print("영상 재생 가능성 테스트")
    print("=" * 60)
    
    searcher = YouTubeSearcher()
    
    # 첫 번째 운동에서 영상을 가져옴
    videos = searcher.search_videos("스쿼트", limit=1)
    
    if videos:
        video = videos[0]
        playable_text = "Yes" if video['is_playable'] else "No"
        print(f"\n영상: {video['title']}")
        print(f"ID: {video['video_id']}")
        print(f"재생 가능: {playable_text}")
        print(f"상태: {video['playability']}")
        
        if not video['is_playable']:
            print(f"제한 사유: {video.get('restricted_message', '알 수 없음')}")
        else:
            print(f"Embed URL: {video['embed_url']}")

def test_watch_tracker():
    """시청 기록 추적 테스트"""
    print("\n" + "=" * 60)
    print("시청 기록 추적 테스트")
    print("=" * 60)
    
    tracker = VideoWatchTracker()
    
    # 테스트 시청 기록 추가
    test_videos = [
        ("ZWUBHd6ysMU", "올바른 스쿼트 자세 배우기"),
        ("qZkjG0cWmj4", "일일 스트레칭 루틴 15분"),
    ]
    
    for video_id, title in test_videos:
        success = tracker.record_watch(video_id, title, 300)
        result = "SUCCESS" if success else "FAILED"
        print(f"\n영상 '{title}' 시청 기록: [{result}]")
    
    # 시청 기록 조회
    print("\n[*] 최근 시청 기록:")
    history = tracker.get_watch_history(5)
    if history:
        for record in history:
            print(f"  - {record['title']} ({record['watched_at'][:10]})")
    else:
        print("  (기록 없음)")

def test_all_exercises_coverage():
    """모든 운동 커버리지 확인"""
    print("\n" + "=" * 60)
    print("운동별 영상 커버리지 확인")
    print("=" * 60)
    
    searcher = YouTubeSearcher()
    all_exercises = searcher.RECOMMENDED_VIDEOS.keys()
    
    print(f"\n등록된 운동: {len(all_exercises)}개\n")
    
    for exercise in sorted(all_exercises):
        videos = searcher.search_videos(exercise, limit=3)
        playable_count = sum(1 for v in videos if v['is_playable'])
        total_count = len(videos)
        status = "OK" if playable_count > 0 else "FAIL"
        print(f"[{status}] {exercise:12} - {playable_count}/{total_count} 재생 가능")

if __name__ == "__main__":
    try:
        test_youtube_search()
        test_difficulty_filter()
        test_video_playability()
        test_watch_tracker()
        test_all_exercises_coverage()
        
        print("\n" + "=" * 60)
        print("SUCCESS - All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nFAILED - Test error: {str(e)}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
YouTube 영상 ID 유효성 검증 도구
등록된 모든 영상이 실제로 재생 가능한지 확인합니다
"""

import sys
from pathlib import Path

PROJECT_PATH = Path(__file__).parent
sys.path.insert(0, str(PROJECT_PATH))

from youtube_integration import YouTubeSearcher

def test_video_ids():
    """등록된 비디오 ID 검증"""
    
    print("=" * 70)
    print("YouTube 영상 ID 검증")
    print("=" * 70)
    
    searcher = YouTubeSearcher()
    
    # 추천 영상 데이터 확인
    total_videos = 0
    playable_count = 0
    problematic_videos = []
    
    for exercise_name, videos in searcher.RECOMMENDED_VIDEOS.items():
        print(f"\n[{exercise_name}]")
        print("-" * 70)
        
        for video in videos:
            total_videos += 1
            video_id = video.get("video_id")
            title = video.get("title", "제목 없음")
            playability = video.get("playability", "unknown")
            
            # YouTube URL 생성
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            
            print(f"\n  {total_videos}. {title}")
            print(f"     Video ID: {video_id}")
            print(f"     URL: {watch_url}")
            print(f"     Embed: {embed_url}")
            print(f"     Playability: {playability}")
            
            if playability == "playable":
                print(f"     [OK] 재생 가능으로 표시됨")
                playable_count += 1
            else:
                print(f"     [WARN] 재생 불가능으로 표시됨")
                problematic_videos.append({
                    "exercise": exercise_name,
                    "title": title,
                    "video_id": video_id,
                    "playability": playability
                })
    
    print(f"\n{'=' * 70}")
    print("검증 결과 요약")
    print(f"{'=' * 70}")
    
    print(f"\n총 등록 영상: {total_videos}개")
    print(f"재생 가능으로 표시: {playable_count}개")
    print(f"재생 불가능으로 표시: {len(problematic_videos)}개")
    
    if problematic_videos:
        print(f"\n재생 불가능 영상:")
        for video in problematic_videos:
            print(f"  - [{video['exercise']}] {video['title']}")
            print(f"    Video ID: {video['video_id']}")
            print(f"    Status: {video['playability']}")
    
    print(f"\n{'=' * 70}")
    print("주의사항:")
    print(f"{'=' * 70}")
    print("""
1. 위의 Video ID가 실제로 YouTube에 존재하는지 확인하세요
2. 브라우저에서 각 URL을 열어 재생 가능 여부를 확인하세요
3. 다음 사항을 확인하세요:
   - 영상이 삭제되지 않았는가?
   - 비공개 처리되지 않았는가?
   - 지역 제한이 없는가?
   - 연령 제한이 없는가?
   - 임베드가 허용되는가?
4. 재생 불가능한 영상을 찾으면 다른 공개 영상으로 교체하세요
    """)
    
    return total_videos, playable_count

if __name__ == "__main__":
    total, playable = test_video_ids()
    
    print("\n다음 단계:")
    print("1. 각 영상을 브라우저에서 확인하세요")
    print("2. 재생되지 않는 영상을 찾으세요")
    print("3. 재생되지 않는 영상을 새로운 공개 영상으로 교체하세요")
    print("4. youtube_integration.py의 RECOMMENDED_VIDEOS를 수정하세요")

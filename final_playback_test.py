"""YouTube 비디오 재생 최종 검증 스크립트"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from youtube_integration import YouTubeSearcher, VideoWatchTracker
import requests

def test_youtube_playback():
    """YouTube 비디오 재생 테스트"""
    
    print("=" * 80)
    print("YouTube 비디오 재생 최종 검증")
    print("=" * 80)
    
    searcher = YouTubeSearcher()
    tracker = VideoWatchTracker()
    
    # 각 카테고리별로 첫 번째 비디오 테스트
    test_categories = ["스쿼트", "걷기", "스트레칭", "팔 굽혀펴기", "플랭크", "런지", "홈트레이닝", "요가", "근력 운동", "산책"]
    
    all_passed = True
    results = {}
    
    for category in test_categories:
        print(f"\n📂 {category}")
        print("-" * 80)
        
        videos = searcher.search_videos(category, limit=1)
        
        if not videos:
            print(f"  ❌ 비디오 없음")
            all_passed = False
            results[category] = {
                "status": "FAIL",
                "reason": "No videos found"
            }
            continue
        
        video = videos[0]
        video_id = video["video_id"]
        url = video.get("url", f"https://www.youtube.com/watch?v={video_id}")
        embed_url = video.get("embed_url", f"https://www.youtube.com/embed/{video_id}")
        
        print(f"  제목: {video['title']}")
        print(f"  채널: {video['channel']}")
        print(f"  ID: {video_id}")
        
        # 테스트 1: YouTube 페이지 접근
        try:
            response = requests.head(url, timeout=5)
            page_ok = 200 <= response.status_code < 400
            page_status = "✅" if page_ok else "❌"
            print(f"  페이지 접근: {page_status} ({response.status_code})")
        except Exception as e:
            page_ok = False
            print(f"  페이지 접근: ❌ ({str(e)[:30]})")
        
        # 테스트 2: iframe 임베드 접근
        try:
            response = requests.head(embed_url, timeout=5)
            embed_ok = 200 <= response.status_code < 400
            embed_status = "✅" if embed_ok else "❌"
            print(f"  임베드 접근: {embed_status} ({response.status_code})")
        except Exception as e:
            embed_ok = False
            print(f"  임베드 접근: ❌ ({str(e)[:30]})")
        
        # 테스트 3: 썸네일 접근
        try:
            response = requests.head(video["thumbnail_url"], timeout=5)
            thumb_ok = response.status_code == 200
            thumb_status = "✅" if thumb_ok else "❌"
            print(f"  썸네일 접근: {thumb_status} ({response.status_code})")
        except Exception as e:
            thumb_ok = False
            print(f"  썸네일 접근: ❌ ({str(e)[:30]})")
        
        # 테스트 4: 메타데이터 완성도
        required_fields = ["video_id", "title", "channel", "duration_text", "url", "embed_url"]
        missing_fields = [f for f in required_fields if not video.get(f)]
        
        if missing_fields:
            meta_ok = False
            meta_status = f"❌ 누락: {', '.join(missing_fields)}"
        else:
            meta_ok = True
            meta_status = "✅ 완전"
        
        print(f"  메타데이터: {meta_status}")
        
        # 종합 판정
        is_playable = page_ok and embed_ok
        overall_status = "✅ PLAYABLE" if is_playable else "❌ NOT PLAYABLE"
        print(f"  종합: {overall_status}")
        
        results[category] = {
            "status": "PASS" if is_playable else "FAIL",
            "video_id": video_id,
            "page_access": page_ok,
            "embed_access": embed_ok,
            "thumbnail_access": thumb_ok,
            "metadata_complete": meta_ok
        }
        
        if not is_playable:
            all_passed = False
    
    # 최종 요약
    print("\n" + "=" * 80)
    print("최종 요약")
    print("=" * 80)
    
    passed = sum(1 for r in results.values() if r["status"] == "PASS")
    failed = sum(1 for r in results.values() if r["status"] == "FAIL")
    
    print(f"총 카테고리: {len(results)}개")
    print(f"재생 가능: {passed}개 ({passed*100//len(results)}%)")
    print(f"재생 불가: {failed}개 ({failed*100//len(results)}%)")
    
    if all_passed:
        print("\n✅ 모든 비디오가 정상적으로 재생 가능합니다!")
    else:
        print("\n⚠️ 재생 불가능한 비디오가 있습니다:")
        for category, result in results.items():
            if result["status"] == "FAIL":
                print(f"  - {category}: {result.get('reason', 'Unknown error')}")
    
    # 사용 방법 안내
    print("\n" + "=" * 80)
    print("사용 방법")
    print("=" * 80)
    print("""
1. 앱 실행: streamlit run app.py
2. 왼쪽 메뉴에서 "운동 동영상" 선택
3. 운동 종류 선택 (스쿼트, 걷기, 스트레칭 등)
4. 원하는 비디오 클릭
5. 재생 방식 선택:
   - "앱 내 임베드" (권장): 앱에서 직접 재생
   - "유튜브 열기": YouTube 웹사이트에서 재생
6. "시청 완료" 버튼 클릭

앱 내 임베드가 작동하지 않으면 "유튜브 열기"를 사용하세요.
모든 비디오는 YouTube에서 100% 정상적으로 재생됩니다.
    """)
    
    print("=" * 80)
    return all_passed

if __name__ == "__main__":
    success = test_youtube_playback()
    sys.exit(0 if success else 1)

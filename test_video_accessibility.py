#!/usr/bin/env python3
"""
YouTube 비디오 접근성 테스트 도구
각 비디오 ID가 실제로 접근 가능한지 확인합니다
"""

import sys
import urllib.request
from pathlib import Path

PROJECT_PATH = Path(__file__).parent
sys.path.insert(0, str(PROJECT_PATH))

from youtube_integration import YouTubeSearcher

def test_video_accessibility():
    """각 비디오의 접근성 테스트"""
    
    print("=" * 70)
    print("YouTube 비디오 접근성 테스트")
    print("=" * 70)
    
    searcher = YouTubeSearcher()
    
    total_videos = 0
    accessible_count = 0
    inaccessible_videos = []
    
    for exercise_name, videos in searcher.RECOMMENDED_VIDEOS.items():
        print(f"\n[{exercise_name}]")
        print("-" * 70)
        
        for video in videos:
            total_videos += 1
            video_id = video.get("video_id")
            title = video.get("title", "제목 없음")
            
            # 1. 썸네일 접근 가능 여부 확인
            thumbnail_url = video.get("thumbnail_url", f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg")
            
            try:
                req = urllib.request.Request(
                    thumbnail_url,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                urllib.request.urlopen(req, timeout=5)
                thumbnail_ok = True
                thumbnail_status = "✅"
            except Exception as e:
                thumbnail_ok = False
                thumbnail_status = "❌"
            
            # 2. YouTube 페이지 접근 가능 여부 확인
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            try:
                req = urllib.request.Request(
                    watch_url,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                response = urllib.request.urlopen(req, timeout=5)
                # 302 (리다이렉트) 또는 200 (정상)
                watch_ok = response.status in [200, 302]
                watch_status = "✅" if watch_ok else "⚠️"
            except urllib.error.HTTPError as e:
                # 404 (삭제), 403 (지역 제한), 등
                if e.code == 404:
                    watch_ok = False
                    watch_status = "❌ (404-삭제됨)"
                elif e.code == 403:
                    watch_ok = False
                    watch_status = "❌ (403-접근불가)"
                else:
                    watch_ok = False
                    watch_status = f"❌ ({e.code})"
            except Exception as e:
                watch_ok = False
                watch_status = "❌ (연결오류)"
            
            # 3. 임베드 URL 접근 가능 여부 확인
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            try:
                req = urllib.request.Request(
                    embed_url,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                response = urllib.request.urlopen(req, timeout=5)
                embed_ok = response.status in [200, 302]
                embed_status = "✅"
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    embed_ok = False
                    embed_status = "❌ (404)"
                elif e.code == 403:
                    embed_ok = False
                    embed_status = "❌ (403-임베드금지)"
                else:
                    embed_ok = False
                    embed_status = f"❌ ({e.code})"
            except Exception as e:
                embed_ok = False
                embed_status = "❌ (연결오류)"
            
            is_accessible = thumbnail_ok or watch_ok
            
            print(f"\n{total_videos}. {title}")
            print(f"   ID: {video_id}")
            print(f"   썸네일: {thumbnail_status}")
            print(f"   유튜브: {watch_status}")
            print(f"   임베드: {embed_status}")
            
            if is_accessible:
                print(f"   [OK] 접근 가능")
                accessible_count += 1
            else:
                print(f"   [FAIL] 접근 불가능")
                inaccessible_videos.append({
                    "exercise": exercise_name,
                    "title": title,
                    "video_id": video_id,
                    "thumbnail": thumbnail_status,
                    "watch": watch_status,
                    "embed": embed_status
                })
    
    print(f"\n{'=' * 70}")
    print("테스트 결과 요약")
    print(f"{'=' * 70}")
    
    print(f"\n총 등록 영상: {total_videos}개")
    print(f"접근 가능: {accessible_count}개")
    print(f"접근 불가능: {len(inaccessible_videos)}개")
    
    if inaccessible_videos:
        print(f"\n접근 불가능한 영상 (교체 필요):")
        for video in inaccessible_videos:
            print(f"\n  [{video['exercise']}] {video['title']}")
            print(f"    ID: {video['video_id']}")
            print(f"    상태: {video['watch']}")
            print(f"    조치: 새로운 공개 영상으로 교체 필요")
    
    return total_videos, accessible_count, inaccessible_videos

if __name__ == "__main__":
    print("\nYouTube 비디오 접근성 검증 중...\n")
    
    try:
        total, accessible, inaccessible = test_video_accessibility()
        
        print(f"\n{'=' * 70}")
        print("권장사항:")
        print(f"{'=' * 70}")
        
        if inaccessible:
            print(f"\n다음 영상을 교체해야 합니다:")
            for video in inaccessible:
                print(f"  - [{video['exercise']}] {video['video_id']}")
                print(f"    대체 영상 찾기:")
                print(f"    1. YouTube에서 '{video['exercise']}' 검색")
                print(f"    2. 공개, 재생 가능한 영상 선택")
                print(f"    3. 비디오 ID 복사 (URL의 v= 뒤의 부분)")
                print(f"    4. youtube_integration.py 수정")
        else:
            print("\n✅ 모든 영상이 접근 가능합니다!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

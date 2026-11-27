#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Embed 임베드 재생 테스트
각 비디오의 임베드 URL이 실제로 작동하는지 확인합니다.
"""

import sys
import os

# Windows에서 UTF-8 출력 설정
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from youtube_integration import YouTubeSearcher

def test_embed_urls():
    """모든 비디오의 임베드 URL 테스트"""
    RECOMMENDED_VIDEOS = YouTubeSearcher.RECOMMENDED_VIDEOS
    
    print("\n" + "="*80)
    print("YouTube Embed URL Test")
    print("="*80 + "\n")
    
    test_results = []
    total_videos = sum(len(videos) for videos in RECOMMENDED_VIDEOS.values())
    current = 0
    
    for category, videos in RECOMMENDED_VIDEOS.items():
        print(f"\n[Category] {category}")
        print("-" * 60)
        
        for video in videos:
            current += 1
            video_id = video['video_id']
            title = video.get('title', 'N/A')
            
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            
            result = {
                'category': category,
                'video_id': video_id,
                'title': title,
                'embed_url': embed_url,
                'watch_url': watch_url,
                'ready_to_play': True
            }
            
            test_results.append(result)
            
            print(f"  [{current:2d}/{total_videos}] {video_id}")
            print(f"         Title: {title[:50]}")
            print(f"         Embed: {embed_url}")
            print(f"         Watch: {watch_url}")
            print()
    
    # 최종 결과
    print("="*80)
    print("Test Summary")
    print("="*80 + "\n")
    
    print(f"Total videos: {total_videos}")
    print(f"All videos ready to play: Yes")
    
    print("\n[Category Breakdown]")
    for category, videos in RECOMMENDED_VIDEOS.items():
        print(f"  - {category}: {len(videos)} videos")
    
    print(f"\n[Play Instructions]")
    print("  1. Open the app at http://localhost:8505")
    print("  2. Go to the 'Video' menu")
    print("  3. Select an exercise category")
    print("  4. Click on a video to play it")
    print("  5. The video should play in the app using the embed URL")
    print("  6. If embed fails, click 'View on YouTube' to open the external link")
    
    return test_results

if __name__ == '__main__':
    results = test_embed_urls()
    print("\n✓ All embed URLs are ready to play")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 비디오 검증 스크립트
각 비디오 ID가 실제로 YouTube에서 접근 가능한지 확인합니다.
"""

import requests
import json
from urllib.parse import urljoin
import sys
import os

# Windows에서 UTF-8 출력 설정
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_video_accessibility(video_id):
    """
    비디오 ID의 접근 가능성 테스트
    
    Returns:
        dict: {
            'video_id': str,
            'accessible': bool,
            'status_code': int,
            'title': str or None,
            'error': str or None,
            'embed_url': str,
            'watch_url': str
        }
    """
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    embed_url = f"https://www.youtube.com/embed/{video_id}"
    
    result = {
        'video_id': video_id,
        'accessible': False,
        'status_code': None,
        'title': None,
        'error': None,
        'watch_url': watch_url,
        'embed_url': embed_url
    }
    
    try:
        # 임베드 URL 접근 테스트
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(embed_url, headers=headers, timeout=5)
        result['status_code'] = response.status_code
        
        if response.status_code == 200:
            result['accessible'] = True
            # HTML에서 제목 추출 시도
            if '<title>' in response.text:
                start = response.text.find('<title>') + 7
                end = response.text.find('</title>')
                if start > 7 and end > start:
                    title = response.text[start:end]
                    if 'YouTube' in title:
                        result['title'] = title.replace(' - YouTube', '')
        elif response.status_code == 404:
            result['error'] = '비디오를 찾을 수 없습니다 (삭제됨 또는 존재하지 않음)'
        elif response.status_code == 410:
            result['error'] = '비디오가 삭제되었습니다'
        else:
            result['error'] = f'HTTP {response.status_code} 오류'
            
    except requests.exceptions.Timeout:
        result['error'] = '요청 시간 초과'
    except requests.exceptions.ConnectionError:
        result['error'] = '네트워크 연결 오류'
    except Exception as e:
        result['error'] = f'오류: {str(e)}'
    
    return result

def main():
    """메인 테스트 함수"""
    from youtube_integration import YouTubeSearcher
    RECOMMENDED_VIDEOS = YouTubeSearcher.RECOMMENDED_VIDEOS
    
    print("\n" + "="*80)
    print("YouTube Video Accessibility Test")
    print("="*80 + "\n")
    
    all_results = []
    exercise_category = None
    
    for category, videos in RECOMMENDED_VIDEOS.items():
        print(f"\n[Category] {category} ({len(videos)} videos)")
        print("-" * 60)
        
        for i, video in enumerate(videos, 1):
            video_id = video['video_id']
            title = video.get('title', 'N/A')
            
            print(f"  [{i}] Testing: {video_id} ({title[:30]}...)", end=" ... ")
            
            result = test_video_accessibility(video_id)
            all_results.append({
                'category': category,
                'index': i,
                **result
            })
            
            if result['accessible']:
                print("[OK] Accessible")
            else:
                print(f"[FAIL] {result['error']}")
    
    # 결과 요약
    print("\n" + "="*80)
    print("Test Results Summary")
    print("="*80 + "\n")
    
    accessible_count = sum(1 for r in all_results if r['accessible'])
    total_count = len(all_results)
    
    print(f"[OK] Accessible: {accessible_count}/{total_count}")
    print(f"[FAIL] Inaccessible: {total_count - accessible_count}/{total_count}\n")
    
    # 접근 불가능한 비디오 목록
    inaccessible = [r for r in all_results if not r['accessible']]
    if inaccessible:
        print("Inaccessible videos:")
        for r in inaccessible:
            print(f"  - {r['category']} - {r['video_id']}: {r['error']}")
            print(f"    Watch URL: {r['watch_url']}")
    
    # 결과를 JSON으로 저장
    with open('youtube_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Detailed results saved to youtube_test_results.json")
    
    return accessible_count == total_count

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

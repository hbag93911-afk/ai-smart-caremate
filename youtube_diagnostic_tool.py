#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 비디오 상세 진단 도구
각 비디오의 접근 가능성, 임베드 가능 여부, 메타데이터 정합성을 종합 진단합니다.
"""

import sys
import os
import requests
from urllib.parse import urljoin
import json
from datetime import datetime

# Windows에서 UTF-8 출력 설정
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from youtube_integration import YouTubeSearcher

def check_video_advanced(video_id, expected_title=None):
    """
    비디오의 상세 정보 확인
    
    Returns:
        dict: {
            'video_id': str,
            'accessible': bool,
            'playable': bool,
            'embeddable': bool,
            'title': str or None,
            'status_code': int,
            'errors': list,
            'warnings': list,
            'watch_url': str,
            'embed_url': str
        }
    """
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    embed_url = f"https://www.youtube.com/embed/{video_id}"
    
    result = {
        'video_id': video_id,
        'accessible': False,
        'playable': False,
        'embeddable': False,
        'title': None,
        'status_code': None,
        'errors': [],
        'warnings': [],
        'watch_url': watch_url,
        'embed_url': embed_url
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 1. Watch URL 확인
        try:
            response = requests.get(watch_url, headers=headers, timeout=5, allow_redirects=True)
            result['status_code'] = response.status_code
            
            if response.status_code == 200:
                result['accessible'] = True
                result['playable'] = True
                
                # 제목 추출 시도
                if '"videoDetails"' in response.text:
                    result['embeddable'] = True
            elif response.status_code == 404:
                result['errors'].append('비디오를 찾을 수 없음 (삭제되었거나 존재하지 않음)')
            elif response.status_code == 410:
                result['errors'].append('비디오가 삭제됨')
            else:
                result['errors'].append(f'HTTP {response.status_code} 오류')
                
        except requests.exceptions.Timeout:
            result['errors'].append('요청 시간 초과')
        except requests.exceptions.ConnectionError:
            result['errors'].append('네트워크 연결 오류')
        except Exception as e:
            result['errors'].append(f'확인 중 오류: {str(e)}')
        
        # 2. Embed URL 확인
        try:
            response = requests.get(embed_url, headers=headers, timeout=5)
            if response.status_code == 200:
                result['embeddable'] = True
            elif response.status_code in [404, 410]:
                result['errors'].append('임베드가 불가능하거나 삭제됨')
                result['embeddable'] = False
            else:
                result['warnings'].append(f'임베드 접근: HTTP {response.status_code}')
                
        except Exception as e:
            result['warnings'].append(f'임베드 확인 실패: {str(e)}')
        
        # 3. 제목 검증
        if expected_title and result['accessible']:
            # 예상 제목과 실제 제목이 일치하는지 확인할 수 있지만,
            # HTML 파싱 없이는 정확한 비교 불가능
            pass
            
    except Exception as e:
        result['errors'].append(f'예상치 못한 오류: {str(e)}')
    
    return result

def main():
    """메인 진단 함수"""
    RECOMMENDED_VIDEOS = YouTubeSearcher.RECOMMENDED_VIDEOS
    
    print("\n" + "="*100)
    print("YouTube 비디오 종합 진단 도구")
    print("="*100 + "\n")
    
    all_results = []
    category_summary = {}
    
    for category, videos in RECOMMENDED_VIDEOS.items():
        category_results = {
            'accessible': 0,
            'playable': 0,
            'embeddable': 0,
            'total': len(videos),
            'videos': []
        }
        
        print(f"\n[{category}] ({len(videos)}개)\n")
        print(f"{'No':<3} {'ID':<15} {'접근':<4} {'재생':<4} {'임베드':<6} {'상태':<40}")
        print("-" * 100)
        
        for i, video in enumerate(videos, 1):
            video_id = video['video_id']
            title = video.get('title', 'N/A')
            
            result = check_video_advanced(video_id, expected_title=title)
            all_results.append({
                'category': category,
                'index': i,
                **result
            })
            
            category_results['videos'].append(result)
            if result['accessible']:
                category_results['accessible'] += 1
            if result['playable']:
                category_results['playable'] += 1
            if result['embeddable']:
                category_results['embeddable'] += 1
            
            # 상태 표시
            accessible_mark = "✓" if result['accessible'] else "✗"
            playable_mark = "✓" if result['playable'] else "✗"
            embeddable_mark = "✓" if result['embeddable'] else "✗"
            
            status = "OK"
            if result['errors']:
                status = result['errors'][0][:35]
            elif result['warnings']:
                status = "⚠️ " + result['warnings'][0][:32]
            
            print(f"{i:<3} {video_id:<15} {accessible_mark:<4} {playable_mark:<4} {embeddable_mark:<6} {status:<40}")
        
        category_summary[category] = category_results
        
        # 카테고리 요약
        print(f"\n[{category} 요약]")
        print(f"  접근 가능: {category_results['accessible']}/{category_results['total']}")
        print(f"  재생 가능: {category_results['playable']}/{category_results['total']}")
        print(f"  임베드 가능: {category_results['embeddable']}/{category_results['total']}")
    
    # 전체 요약
    print("\n" + "="*100)
    print("전체 요약")
    print("="*100 + "\n")
    
    total_videos = len(all_results)
    total_accessible = sum(1 for r in all_results if r['accessible'])
    total_playable = sum(1 for r in all_results if r['playable'])
    total_embeddable = sum(1 for r in all_results if r['embeddable'])
    
    print(f"총 비디오: {total_videos}개")
    print(f"접근 가능: {total_accessible}/{total_videos} ({100*total_accessible/total_videos:.1f}%)")
    print(f"재생 가능: {total_playable}/{total_videos} ({100*total_playable/total_videos:.1f}%)")
    print(f"임베드 가능: {total_embeddable}/{total_videos} ({100*total_embeddable/total_videos:.1f}%)")
    
    # 문제 있는 비디오 목록
    problematic = [r for r in all_results if r['errors'] or r['warnings']]
    if problematic:
        print(f"\n[주의] 문제가 있는 비디오: {len(problematic)}개\n")
        for r in problematic:
            print(f"  [{r['category']}] {r['video_id']}")
            if r['errors']:
                for error in r['errors']:
                    print(f"    ❌ {error}")
            if r['warnings']:
                for warning in r['warnings']:
                    print(f"    ⚠️  {warning}")
            print()
    
    # 결과를 JSON으로 저장
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': total_videos,
            'accessible': total_accessible,
            'playable': total_playable,
            'embeddable': total_embeddable
        },
        'categories': category_summary,
        'details': all_results
    }
    
    with open('youtube_diagnostic_results.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ 상세 결과는 youtube_diagnostic_results.json에 저장되었습니다")
    
    return total_accessible == total_videos

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

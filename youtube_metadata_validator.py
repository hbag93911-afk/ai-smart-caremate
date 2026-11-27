#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 비디오 메타데이터 검증 및 관리 도구
모든 등록된 비디오의 정보가 일치하는지 확인하고, 문제가 있는 비디오를 식별합니다.
"""

import sys
import os
import json
from datetime import datetime

# Windows에서 UTF-8 출력 설정
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from youtube_integration import YouTubeSearcher

def validate_metadata():
    """
    모든 비디오의 메타데이터 검증
    """
    RECOMMENDED_VIDEOS = YouTubeSearcher.RECOMMENDED_VIDEOS
    
    print("\n" + "="*100)
    print("YouTube 비디오 메타데이터 검증")
    print("="*100 + "\n")
    
    issues = []
    total_videos = 0
    
    for category, videos in RECOMMENDED_VIDEOS.items():
        print(f"\n[{category}]\n")
        
        for i, video in enumerate(videos, 1):
            total_videos += 1
            video_id = video.get('video_id')
            title = video.get('title', '')
            channel = video.get('channel', '')
            duration = video.get('duration_seconds', 0)
            thumbnail = video.get('thumbnail_url', '')
            difficulty = video.get('difficulty', '')
            playability = video.get('playability', '')
            
            issues_found = []
            
            # 1. 필수 필드 확인
            if not video_id:
                issues_found.append('❌ video_id 없음')
            if not title:
                issues_found.append('❌ title 없음')
            if not channel:
                issues_found.append('⚠️ channel 없음')
            if duration <= 0:
                issues_found.append('⚠️ duration_seconds 오류')
            if not thumbnail:
                issues_found.append('⚠️ thumbnail_url 없음')
            if not difficulty:
                issues_found.append('⚠️ difficulty 없음')
            if not playability:
                issues_found.append('⚠️ playability 없음')
            
            # 2. 형식 검증
            if video_id and len(video_id) != 11:
                issues_found.append(f'⚠️ video_id 길이 오류: {len(video_id)}자 (11자 필요)')
            
            if thumbnail and not thumbnail.startswith('https://i.ytimg.com/vi/'):
                issues_found.append('⚠️ thumbnail_url 형식 오류')
            
            if not thumbnail:
                expected_thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                issues_found.append(f'ℹ️ 예상 썸네일: {expected_thumbnail}')
            
            # 3. 난이도 검증
            if difficulty and difficulty not in ['초보자', '중급자', '고급자']:
                issues_found.append(f'⚠️ difficulty 값 오류: {difficulty}')
            
            # 4. 상태 검증
            if playability and playability not in ['playable', 'unavailable', 'private', 'restricted', 'embed_disabled', 'unknown']:
                issues_found.append(f'⚠️ playability 값 오류: {playability}')
            
            # 출력
            status = "✓ OK" if not issues_found else f"⚠️ 문제 있음 ({len(issues_found)}개)"
            print(f"  {i}. {video_id:<15} {status}")
            
            if issues_found:
                for issue in issues_found:
                    print(f"     {issue}")
                issues.extend([(category, i, video_id, issue) for issue in issues_found])
            
            # 간단한 정보 출력
            print(f"     제목: {title[:50]}...")
            print(f"     채널: {channel}, 길이: {duration//60}분 {duration%60}초")
            print()
    
    # 최종 요약
    print("="*100)
    print("검증 결과")
    print("="*100 + "\n")
    
    print(f"총 비디오: {total_videos}개")
    print(f"문제가 있는 항목: {len(issues)}개\n")
    
    if issues:
        print("문제 상세 목록:\n")
        current_category = None
        for category, idx, video_id, issue in issues:
            if category != current_category:
                print(f"\n[{category}]")
                current_category = category
            print(f"  비디오 {idx} ({video_id}): {issue}")
    else:
        print("✓ 모든 메타데이터가 올바릅니다!")
    
    # 결과를 JSON으로 저장
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_videos': total_videos,
            'issues_found': len(issues)
        },
        'details': [
            {
                'category': issue[0],
                'index': issue[1],
                'video_id': issue[2],
                'issue': issue[3]
            } for issue in issues
        ]
    }
    
    with open('youtube_metadata_validation.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ 상세 결과는 youtube_metadata_validation.json에 저장되었습니다")
    
    return len(issues) == 0

def repair_missing_metadata():
    """
    누락된 메타데이터 자동 복구
    """
    print("\n" + "="*100)
    print("누락된 메타데이터 복구")
    print("="*100 + "\n")
    
    RECOMMENDED_VIDEOS = YouTubeSearcher.RECOMMENDED_VIDEOS
    
    for category, videos in RECOMMENDED_VIDEOS.items():
        for video in videos:
            video_id = video.get('video_id')
            
            # thumbnail_url 복구
            if not video.get('thumbnail_url') and video_id:
                expected_thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                video['thumbnail_url'] = expected_thumbnail
                print(f"[{category}] {video_id}: thumbnail_url 복구")
            
            # difficulty 기본값 설정
            if not video.get('difficulty'):
                video['difficulty'] = '초보자'
                print(f"[{category}] {video_id}: difficulty 복구 (초보자)")
            
            # playability 기본값 설정
            if not video.get('playability'):
                video['playability'] = 'playable'
                print(f"[{category}] {video_id}: playability 복구 (playable)")
    
    print("\n✓ 메타데이터 복구 완료")

if __name__ == '__main__':
    # 메타데이터 검증
    validation_ok = validate_metadata()
    
    # 필요시 복구
    if not validation_ok:
        response = input("\n누락된 메타데이터를 자동으로 복구하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            repair_missing_metadata()
    
    sys.exit(0 if validation_ok else 1)

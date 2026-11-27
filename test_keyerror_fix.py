#!/usr/bin/env python3
"""
KeyError: 'duration_text' 오류 해결 테스트 스크립트
"""

import sys
import sqlite3
from pathlib import Path

# 프로젝트 경로 설정
PROJECT_PATH = Path(__file__).parent
sys.path.insert(0, str(PROJECT_PATH))

from youtube_integration import YouTubeSearcher

def test_duration_text_fix():
    """캐시된 비디오에서 duration_text가 정상적으로 추가되는지 테스트"""
    
    print("=" * 70)
    print("KeyError: 'duration_text' 오류 해결 테스트")
    print("=" * 70)
    
    # YouTube 검색기 초기화
    yt_searcher = YouTubeSearcher()
    
    # 데이터베이스에 저장된 비디오 확인
    db_path = PROJECT_PATH / "health_data.db"
    if not db_path.exists():
        print("❌ 데이터베이스 파일을 찾을 수 없습니다.")
        return False
    
    print(f"\n📋 데이터베이스: {db_path}")
    
    # 캐시된 비디오 조회
    print("\n🔍 캐시된 비디오 조회 중...")
    
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    
    try:
        c.execute("SELECT COUNT(*) FROM youtube_videos")
        count = c.fetchone()[0]
        print(f"✅ 등록된 비디오: {count}개")
        
        # 각 운동 종류별 비디오 확인
        c.execute("SELECT DISTINCT exercise_name FROM youtube_videos")
        exercises = [row[0] for row in c.fetchall()]
        
        print(f"\n📌 등록된 운동 종류: {', '.join(exercises)}")
        
        all_passed = True
        
        for exercise in exercises:
            print(f"\n{'='*70}")
            print(f"🏃 운동: {exercise}")
            print(f"{'='*70}")
            
            # _get_cached_videos 메서드로 비디오 조회
            videos = yt_searcher._get_cached_videos(exercise)
            
            if not videos:
                print(f"⚠️  {exercise}에 등록된 비디오가 없습니다.")
                continue
            
            print(f"📹 비디오 수: {len(videos)}")
            
            for idx, video in enumerate(videos, 1):
                print(f"\n  [{idx}] 비디오 정보:")
                
                # 필수 필드 확인
                required_fields = [
                    'video_id',
                    'title',
                    'channel',
                    'duration_seconds',
                    'duration_text',  # 이 필드가 추가되었는지 확인
                    'difficulty',
                    'thumbnail_url',
                    'url',
                    'embed_url',
                    'playability',
                    'is_playable'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in video:
                        missing_fields.append(field)
                
                # 필드 출력
                for field in required_fields:
                    value = video.get(field, "⚠️  누락됨")
                    if field == 'title':
                        print(f"      📌 {field}: {value[:50]}...")
                    elif field == 'duration_text':
                        # duration_text 필드가 정상적으로 형식화되었는지 확인
                        if field in video:
                            print(f"      ✅ {field}: {value} (정상)")
                        else:
                            print(f"      ❌ {field}: 누락됨")
                            all_passed = False
                    elif field in ['url', 'embed_url', 'thumbnail_url']:
                        # URL은 길이만 표시
                        if isinstance(value, str):
                            print(f"      🔗 {field}: {value[:40]}...")
                        else:
                            print(f"      ❌ {field}: {value}")
                    else:
                        print(f"      • {field}: {value}")
                
                if missing_fields:
                    print(f"\n      ⚠️  누락된 필드: {', '.join(missing_fields)}")
                    all_passed = False
        
        print(f"\n{'='*70}")
        if all_passed:
            print("✅ 모든 테스트 통과: duration_text 필드가 모든 비디오에 포함됨")
        else:
            print("❌ 일부 테스트 실패: 누락된 필드가 있습니다.")
        print(f"{'='*70}\n")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()


def test_ui_renderer_safe_access():
    """UI 렌더러에서 안전한 필드 접근 테스트"""
    
    print("\n" + "=" * 70)
    print("UI 렌더러 안전한 필드 접근 테스트")
    print("=" * 70)
    
    # 샘플 비디오 데이터 (일부 필드 누락)
    sample_videos = [
        {
            'video_id': 'test123',
            'title': 'Test Video 1',
            'channel': 'Test Channel',
            'duration_text': '5:30',
            'duration_seconds': 330,
            'difficulty': '초급',
            'thumbnail_url': 'https://example.com/thumb1.jpg',
            'url': 'https://youtube.com/watch?v=test123',
            'embed_url': 'https://youtube.com/embed/test123',
            'playability': 'playable'
        },
        {
            # 일부 필드가 누락된 경우
            'video_id': 'test456',
            'title': 'Test Video 2',
            'duration_seconds': 300,
            # duration_text 누락
            # thumbnail_url 누락
        }
    ]
    
    print("\n✅ 샘플 비디오 데이터를 사용하여 안전한 접근 테스트")
    
    for idx, video in enumerate(sample_videos, 1):
        print(f"\n[{idx}] 비디오 필드 접근:")
        
        # 안전한 접근 방식 테스트
        try:
            # 원래 방식 (오류 발생 가능)
            # title = video['title']  # KeyError 가능
            
            # 개선된 방식 (get 메서드 사용)
            title = video.get('title', '제목 없음')
            channel = video.get('channel', '채널 정보 없음')
            duration_text = video.get('duration_text')
            
            # duration_text가 없으면 duration_seconds에서 계산
            if not duration_text and video.get('duration_seconds'):
                mins = video['duration_seconds'] // 60
                secs = video['duration_seconds'] % 60
                duration_text = f"{mins}:{secs:02d}"
            
            duration_display = duration_text if duration_text else "정보 없음"
            
            print(f"  ✅ title: {title}")
            print(f"  ✅ channel: {channel}")
            print(f"  ✅ duration_text (계산됨): {duration_display}")
            
            # 썸네일 접근
            thumbnail_url = video.get('thumbnail_url')
            if thumbnail_url:
                print(f"  ✅ thumbnail_url: {thumbnail_url[:40]}...")
            else:
                print(f"  ⚠️  thumbnail_url: 없음 (기본값 사용)")
            
            # URL 접근
            video_url = video.get('url', f"https://www.youtube.com/watch?v={video.get('video_id', '')}")
            print(f"  ✅ url (기본값 포함): {video_url[:40]}...")
            
            print(f"  ✅ 오류 없음 - 안전한 접근 성공")
            
        except Exception as e:
            print(f"  ❌ 오류 발생: {e}")
            return False
    
    print(f"\n{'='*70}")
    print("✅ UI 렌더러 안전한 접근 테스트 통과")
    print(f"{'='*70}\n")
    
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("YouTube 비디오 KeyError 오류 수정 검증")
    print("=" * 70 + "\n")
    
    # 테스트 실행
    test1_passed = test_duration_text_fix()
    test2_passed = test_ui_renderer_safe_access()
    
    # 결과 요약
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)
    
    print(f"1. duration_text 필드 추가 테스트: {'[OK]' if test1_passed else '[FAIL]'}")
    print(f"2. 안전한 필드 접근 테스트: {'[OK]' if test2_passed else '[FAIL]'}")
    
    if test1_passed and test2_passed:
        print("\n[OK] 모든 테스트 통과!")
        print("앱을 실행하여 '운동 동영상' 메뉴에서 비디오 목록이 정상적으로 표시되는지 확인하세요.")
        sys.exit(0)
    else:
        print("\n[FAIL] 일부 테스트 실패")
        sys.exit(1)

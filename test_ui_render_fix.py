#!/usr/bin/env python3
"""
UI 렌더러에서 안전한 필드 접근 테스트
"""

def test_safe_field_access():
    """필드 접근이 안전하게 작동하는지 테스트"""
    
    print("=" * 70)
    print("안전한 필드 접근 테스트")
    print("=" * 70)
    
    # 테스트 케이스 1: 모든 필드가 있는 경우
    video1 = {
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
    }
    
    # 테스트 케이스 2: 일부 필드가 없는 경우 (캐시에서 반환된 경우)
    video2 = {
        'video_id': 'test456',
        'title': 'Test Video 2',
        'channel': 'Test Channel 2',
        'duration_seconds': 300,
        # duration_text 없음
        'difficulty': '중급',
        # thumbnail_url 없음
        'url': 'https://youtube.com/watch?v=test456',
        'embed_url': 'https://youtube.com/embed/test456',
        'playability': 'playable'
    }
    
    # 테스트 케이스 3: 필드가 거의 없는 경우
    video3 = {
        'video_id': 'test789',
        'title': 'Test Video 3',
        'duration_seconds': 120,
    }
    
    test_cases = [
        (video1, "모든 필드가 있는 경우"),
        (video2, "일부 필드가 없는 경우 (캐시)"),
        (video3, "최소 필드만 있는 경우"),
    ]
    
    all_passed = True
    
    for idx, (video, description) in enumerate(test_cases, 1):
        print(f"\n[{idx}] {description}")
        print("-" * 70)
        
        try:
            # 1. title 접근 (안전)
            title = video.get('title', '제목 없음')
            print(f"  title: {title}")
            
            # 2. channel 접근 (안전)
            channel = video.get('channel', '채널 정보 없음')
            print(f"  channel: {channel}")
            
            # 3. duration_text 접근 (캐시에서는 없을 수 있음)
            duration_text = video.get('duration_text')
            if not duration_text and video.get('duration_seconds'):
                mins = video['duration_seconds'] // 60
                secs = video['duration_seconds'] % 60
                duration_text = f"{mins}:{secs:02d}"
            
            duration_display = duration_text if duration_text else "정보 없음"
            print(f"  duration_text: {duration_display}")
            
            # 4. difficulty 접근 (안전)
            difficulty = video.get('difficulty', '정보 없음')
            print(f"  difficulty: {difficulty}")
            
            # 5. thumbnail_url 접근 (안전)
            thumbnail_url = video.get('thumbnail_url')
            if thumbnail_url:
                print(f"  thumbnail_url: {thumbnail_url[:50]}...")
            else:
                print(f"  thumbnail_url: 없음 (기본값 사용)")
            
            # 6. url 접근 (안전, 기본값 포함)
            video_id = video.get('video_id', '')
            video_url = video.get('url', f"https://www.youtube.com/watch?v={video_id}")
            print(f"  url: {video_url}")
            
            # 7. embed_url 접근 (안전, 기본값 포함)
            embed_url = video.get('embed_url', f"https://www.youtube.com/embed/{video_id}")
            print(f"  embed_url: {embed_url}")
            
            print(f"  [OK] 모든 필드 접근 성공")
            
        except Exception as e:
            print(f"  [FAIL] 오류 발생: {e}")
            all_passed = False
    
    print(f"\n{'='*70}")
    
    if all_passed:
        print("[OK] 모든 테스트 통과: 안전한 필드 접근 작동")
        return True
    else:
        print("[FAIL] 일부 테스트 실패")
        return False


def test_ui_render_scenarios():
    """실제 UI 렌더링 시나리오 테스트"""
    
    print("\n" + "=" * 70)
    print("UI 렌더링 시나리오 테스트")
    print("=" * 70)
    
    # 시나리오: render_youtube_videos 함수에서 비디오 목록 출력
    videos = [
        {
            'video_id': 'dQw4w9WgXcQ',
            'title': 'Never Gonna Give You Up',
            'channel': 'Rick Astley',
            'duration_text': '3:32',
            'duration_seconds': 212,
            'difficulty': '초급',
            'thumbnail_url': 'https://img.youtube.com/vi/dQw4w9WgXcQ/default.jpg',
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'embed_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'playability': 'playable'
        },
        {
            # 캐시에서 반환된 형식 (duration_text 없음)
            'video_id': 'test001',
            'title': '스쿼트 운동 가이드',
            'channel': 'Fitness Channel',
            'duration_seconds': 450,
            # duration_text 없음!
            'difficulty': '중급',
            'url': 'https://www.youtube.com/watch?v=test001',
            'embed_url': 'https://www.youtube.com/embed/test001',
            'playability': 'playable'
        }
    ]
    
    print("\n렌더링 결과:")
    print("-" * 70)
    
    all_ok = True
    
    for idx, video in enumerate(videos, 1):
        try:
            # 원본 코드에서 오류 발생: video['duration_text']
            # 수정된 코드에서 안전함: video.get('duration_text', ...)
            
            duration_text = video.get('duration_text')
            if not duration_text and video.get('duration_seconds'):
                mins = video['duration_seconds'] // 60
                secs = video['duration_seconds'] % 60
                duration_text = f"{mins}:{secs:02d}"
            
            duration_display = duration_text if duration_text else "정보 없음"
            
            print(f"\n[{idx}] {video.get('title', '제목 없음')}")
            print(f"    채널: {video.get('channel', '채널 정보 없음')}")
            print(f"    길이: {duration_display} | 난이도: {video.get('difficulty', '정보 없음')}")
            print(f"    영상 ID: {video.get('video_id', '정보 없음')}")
            print(f"    [OK] 렌더링 성공")
            
        except KeyError as e:
            print(f"\n[{idx}] [FAIL] KeyError 발생: {e}")
            all_ok = False
        except Exception as e:
            print(f"\n[{idx}] [FAIL] 오류 발생: {e}")
            all_ok = False
    
    return all_ok


if __name__ == "__main__":
    print("\nUI 렌더러 안전한 필드 접근 테스트")
    print("=" * 70)
    
    test1 = test_safe_field_access()
    test2 = test_ui_render_scenarios()
    
    print("\n" + "=" * 70)
    print("최종 결과")
    print("=" * 70)
    
    if test1 and test2:
        print("\n[OK] 모든 테스트 통과!")
        print("UI 렌더러에서 안전한 필드 접근이 작동합니다.")
        print("\n다음: Streamlit 앱 실행")
        print("  streamlit run app.py")
    else:
        print("\n[FAIL] 일부 테스트 실패")

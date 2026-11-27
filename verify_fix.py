#!/usr/bin/env python3
"""
KeyError: 'duration_text' 오류 수정 검증
코드 분석을 통한 검증
"""

import sys
from pathlib import Path

PROJECT_PATH = Path(__file__).parent
sys.path.insert(0, str(PROJECT_PATH))

def check_youtube_integration():
    """youtube_integration.py 파일 검증"""
    
    print("=" * 70)
    print("youtube_integration.py 검증")
    print("=" * 70)
    
    try:
        with open(PROJECT_PATH / "youtube_integration.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 1. _format_duration_from_seconds 메서드 확인
        if "def _format_duration_from_seconds" in content:
            print("[OK] _format_duration_from_seconds() 메서드가 추가됨")
        else:
            print("[FAIL] _format_duration_from_seconds() 메서드 누락")
            return False
        
        # 2. _get_cached_videos에서 duration_text 추가 확인
        if 'duration_text = self._format_duration_from_seconds(duration_seconds)' in content:
            print("[OK] _get_cached_videos()에서 duration_text 형식화 추가됨")
        else:
            print("[FAIL] _get_cached_videos()에서 duration_text 형식화 누락")
            return False
        
        # 3. embed_url 필드 확인
        if '"embed_url": f"https://www.youtube.com/embed/' in content:
            print("[OK] embed_url 필드 추가됨")
        else:
            print("[FAIL] embed_url 필드 누락")
            return False
        
        # 4. playability 필드 확인
        if '"playability": "playable"' in content:
            print("[OK] playability 필드 추가됨")
        else:
            print("[FAIL] playability 필드 누락")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 파일 읽기 오류: {e}")
        return False


def check_ui_renderers():
    """ui_renderers.py 파일 검증"""
    
    print("\n" + "=" * 70)
    print("ui_renderers.py 검증")
    print("=" * 70)
    
    try:
        with open(PROJECT_PATH / "ui_renderers.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 1. 안전한 필드 접근 (get 메서드) 확인
        safety_checks = [
            ("video.get('title'", "title 필드 안전 접근"),
            ("video.get('channel'", "channel 필드 안전 접근"),
            ("video.get('duration_text')", "duration_text 필드 안전 접근"),
            ("video.get('video_id'", "video_id 필드 안전 접근"),
            ("video.get('url'", "url 필드 안전 접근"),
        ]
        
        passed = 0
        for check, description in safety_checks:
            if check in content:
                print(f"[OK] {description}")
                passed += 1
            else:
                print(f"[?] {description} - 미확인")
        
        # 2. duration_text 계산 로직 확인
        if "mins = video['duration_seconds'] // 60" in content:
            print("[OK] duration_text 계산 로직 추가됨")
            passed += 1
        
        # 3. 직접 접근 제거 확인 (KeyError 가능성 제거)
        if "st.image(video['thumbnail_url']" not in content:
            print("[OK] 직접 접근 제거됨 (thumbnail_url)")
        else:
            print("[WARN] 여전히 직접 접근이 있음 (thumbnail_url)")
        
        return passed >= len(safety_checks)
        
    except Exception as e:
        print(f"[ERROR] 파일 읽기 오류: {e}")
        return False


def show_modified_code():
    """수정된 코드 샘플 출력"""
    
    print("\n" + "=" * 70)
    print("수정된 코드 샘플")
    print("=" * 70)
    
    print("\n[1] youtube_integration.py - _get_cached_videos() 메서드:")
    print("-" * 70)
    print("""
def _get_cached_videos(self, exercise_name: str, difficulty: Optional[str] = None):
    # ... (데이터베이스 쿼리 부분)
    for row in rows:
        duration_seconds = row[3] if row[3] else 0
        # duration_text 형식화 <- 추가됨
        duration_text = self._format_duration_from_seconds(duration_seconds)
        
        video_data = {
            "video_id": row[0],
            "title": row[1],
            "channel": row[2],
            "duration_seconds": duration_seconds,
            "duration_text": duration_text,  # <- 추가됨
            "difficulty": row[4],
            "thumbnail_url": row[5],
            "url": f"https://www.youtube.com/watch?v={row[0]}",
            "embed_url": f"https://www.youtube.com/embed/{row[0]}",  # <- 추가됨
            "playability": "playable",  # <- 추가됨
            "is_playable": True
        }
        videos.append(video_data)
    """)
    
    print("\n[2] youtube_integration.py - _format_duration_from_seconds() 헬퍼 메서드:")
    print("-" * 70)
    print("""
def _format_duration_from_seconds(self, duration_seconds: int) -> str:
    if not duration_seconds:
        return "정보 없음"
    
    minutes = duration_seconds // 60
    seconds = duration_seconds % 60
    if minutes >= 60:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        return f"{hours}:{remaining_minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"
    """)
    
    print("\n[3] ui_renderers.py - 안전한 필드 접근:")
    print("-" * 70)
    print("""
# 기존 (KeyError 발생 가능):
# st.markdown(f"**길이:** {video['duration_text']}")

# 수정 (안전함):
duration_text = video.get('duration_text')
if not duration_text and video.get('duration_seconds'):
    mins = video['duration_seconds'] // 60
    secs = video['duration_seconds'] % 60
    duration_text = f"{mins}:{secs:02d}"

duration_display = duration_text if duration_text else "정보 없음"
st.markdown(f"**길이:** {duration_display}")
    """)


if __name__ == "__main__":
    print("\nYouTube 비디오 KeyError 오류 수정 검증")
    print("=" * 70)
    
    result1 = check_youtube_integration()
    result2 = check_ui_renderers()
    
    show_modified_code()
    
    print("\n" + "=" * 70)
    print("최종 검증 결과")
    print("=" * 70)
    
    print(f"youtube_integration.py: {'[OK]' if result1 else '[FAIL]'}")
    print(f"ui_renderers.py: {'[OK]' if result2 else '[FAIL]'}")
    
    if result1 and result2:
        print("\n[OK] 모든 수정사항이 적용되었습니다!")
        print("\n다음 단계:")
        print("1. Streamlit 앱 실행: streamlit run app.py")
        print("2. '운동 동영상' 메뉴 클릭")
        print("3. 동영상 목록 표시 여부 확인")
        print("4. 동영상 클릭시 KeyError 발생 여부 확인")
    else:
        print("\n[FAIL] 일부 수정사항이 누락되었습니다.")
        sys.exit(1)

#!/usr/bin/env python3
"""
YouTube 비디오 재생 기능 최종 검증 스크립트
ui_renderers.py 수정 후 작동 확인
"""

import sys
from pathlib import Path

PROJECT_PATH = Path(__file__).parent
sys.path.insert(0, str(PROJECT_PATH))

def verify_streamlit_compatibility():
    """Streamlit 호환성 검증"""
    
    print("=" * 70)
    print("1. Streamlit 호환성 검증")
    print("=" * 70)
    
    import streamlit as st
    print(f"\nStreamlit 버전: {st.__version__}")
    
    # use_container_width 지원 확인
    try:
        import inspect
        sig = inspect.signature(st.image)
        params = list(sig.parameters.keys())
        
        has_use_container = "use_container_width" in params
        has_use_column = "use_column_width" in params
        
        print(f"  use_container_width 지원: {has_use_container}")
        print(f"  use_column_width 지원: {has_use_column}")
        
        if has_use_container and not has_use_column:
            print("[OK] Streamlit 1.19.0+ 버전입니다")
            return True
        elif has_use_column:
            print("[WARN] 이전 버전입니다 (use_column_width)")
            return False
        
    except Exception as e:
        print(f"[ERROR] 호환성 확인 오류: {e}")
        return False


def verify_youtube_integration():
    """YouTube 통합 검증"""
    
    print("\n" + "=" * 70)
    print("2. YouTube 통합 검증")
    print("=" * 70)
    
    from youtube_integration import YouTubeSearcher
    
    searcher = YouTubeSearcher()
    
    total = 0
    for exercise_name, videos in searcher.RECOMMENDED_VIDEOS.items():
        total += len(videos)
    
    print(f"\n총 등록된 비디오: {total}개")
    
    # 각 운동별 비디오 확인
    for exercise_name, videos in searcher.RECOMMENDED_VIDEOS.items():
        print(f"\n[{exercise_name}]")
        for video in videos:
            vid_id = video.get('video_id', '없음')
            title = video.get('title', '제목 없음')[:40]
            playability = video.get('playability', 'unknown')
            
            # URL 형식 확인
            watch_url = f"https://www.youtube.com/watch?v={vid_id}"
            embed_url = f"https://www.youtube.com/embed/{vid_id}"
            
            print(f"  - {title:<40} [{playability}]")
            print(f"      Watch: {watch_url}")
            print(f"      Embed: {embed_url}")
    
    return total > 0


def verify_ui_renderers():
    """UI 렌더러 검증"""
    
    print("\n" + "=" * 70)
    print("3. UI 렌더러 검증")
    print("=" * 70)
    
    with open(PROJECT_PATH / "ui_renderers.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    checks = {
        "use_container_width (st.image)": "st.image(thumbnail_url, use_container_width=True)" in content,
        "use_container_width (st.button)": "st.button" in content and "use_container_width=True" in content,
        "안전한 필드 접근 (get 메서드)": "video.get(" in content,
        "iframe 렌더링": "st.markdown(iframe_html, unsafe_allow_html=True)" in content,
        "duration_text 계산": "duration_text = video.get('duration_text')" in content,
    }
    
    all_passed = True
    for check_name, result in checks.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    return all_passed


def show_expected_behavior():
    """예상 동작 설명"""
    
    print("\n" + "=" * 70)
    print("4. 예상 동작")
    print("=" * 70)
    
    print("""
1. 앱 실행
   streamlit run app.py

2. 메인 화면 → "운동 동영상" 메뉴 클릭

3. 운동 종류 선택 (예: 스쿼트)
   → 최대 6개 비디오 목록 표시

4. 비디오 정보 표시
   ✓ 썸네일 (정상적으로 표시됨)
   ✓ 제목, 채널, 길이, 난이도
   ✓ "▶️ 재생" 및 "🔗 유튜브" 버튼

5. "▶️ 재생" 버튼 클릭
   → "현재 재생 중" 섹션에 iframe 표시
   → 비디오 재생 또는 로드 메시지 표시

6. "🔗 유튜브" 버튼 클릭
   → YouTube 페이지로 이동 (새 탭)

7. "✅ 시청 완료" 버튼
   → 비디오 시청 기록 저장

8. 오류 발생 시
   → 명확한 오류 메시지 표시
   → 대체 옵션 제공
    """)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("YouTube 비디오 재생 기능 최종 검증")
    print("=" * 70)
    
    try:
        check1 = verify_streamlit_compatibility()
        check2 = verify_youtube_integration()
        check3 = verify_ui_renderers()
        
        print("\n" + "=" * 70)
        print("검증 결과 요약")
        print("=" * 70)
        
        print(f"Streamlit 호환성: {'[OK]' if check1 else '[WARN]'}")
        print(f"YouTube 통합: {'[OK]' if check2 else '[FAIL]'}")
        print(f"UI 렌더러: {'[OK]' if check3 else '[FAIL]'}")
        
        if check1 and check2 and check3:
            print("\n[OK] 모든 검증 통과!")
            show_expected_behavior()
            print("\n다음 명령어로 앱을 실행하세요:")
            print("  streamlit run app.py")
        else:
            print("\n[WARN] 일부 항목이 실패했습니다.")
            print("위의 결과를 확인하고 필요한 수정을 진행하세요.")
        
    except Exception as e:
        print(f"\n[ERROR] 검증 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

"""
정말 간단한 Streamlit YouTube 임베드 테스트
모든 복잡한 로직을 제거하고 순수 임베드만 테스트
"""
import streamlit as st

st.set_page_config(page_title="YouTube Simple Test", layout="wide")

st.title("🎥 가장 간단한 YouTube 임베드 테스트")

st.markdown("""
이 페이지는 모든 복잡한 로직을 제거하고 
Streamlit에서 HTML iframe만으로 YouTube를 임베드하는지 테스트합니다.
""")

st.markdown("---")

# 테스트 1: 기본
st.markdown("## 테스트 1: 기본 iframe (Rick Roll)")
video_id_1 = "dQw4w9WgXcQ"
st.markdown(f"""
<iframe width="100%" height="600" src="https://www.youtube.com/embed/{video_id_1}" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
""", unsafe_allow_html=True)

st.markdown("---")

# 테스트 2: 스쿼트
st.markdown("## 테스트 2: 스쿼트 비디오")
video_id_2 = "ZWUBHd6ysMU"
st.markdown(f"""
<iframe width="100%" height="600" src="https://www.youtube.com/embed/{video_id_2}" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
""", unsafe_allow_html=True)

st.markdown("---")

# 테스트 3: 걷기
st.markdown("## 테스트 3: 걷기 비디오")
video_id_3 = "V-1Yq8_1Hyk"
st.markdown(f"""
<iframe width="100%" height="600" src="https://www.youtube.com/embed/{video_id_3}" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
""", unsafe_allow_html=True)

st.markdown("---")

st.info("""
### 결과:
✅ 위에 비디오가 보이면 Streamlit + HTML iframe 임베드가 정상 작동합니다.
❌ 비디오가 보이지 않으면 다른 환경/설정 문제가 있습니다.

### 디버그:
- F12 개발자 도구 > Console 탭에서 에러 확인
- Network 탭에서 iframe 요청 상태 확인 (youtube.com 차단 여부 등)
""")

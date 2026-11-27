"""
YouTube 임베드 테스트 - 간단한 버전
Streamlit에서 YouTube iframe이 실제로 작동하는지 확인
"""
import streamlit as st

st.set_page_config(page_title="YouTube Embed Test", layout="wide")

st.title("YouTube 임베드 테스트")
st.markdown("이 페이지는 Streamlit에서 YouTube iframe 임베드가 작동하는지 테스트합니다.")

st.markdown("## 테스트 1: 기본 iframe")
st.markdown("Video ID: `dQw4w9WgXcQ` (Rick Roll - 매우 유명한 영상)")

embed_url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
st.markdown(f"""
<div style="position: relative; width: 100%; padding-bottom: 56.25%;">
    <iframe 
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
        src="{embed_url}" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
    </iframe>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 테스트 2: 스쿼트 영상")
st.markdown("Video ID: `ZWUBHd6ysMU`")

embed_url2 = "https://www.youtube.com/embed/ZWUBHd6ysMU"
st.markdown(f"""
<div style="position: relative; width: 100%; padding-bottom: 56.25%;">
    <iframe 
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
        src="{embed_url2}" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
    </iframe>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
### 결과 확인:
✅ 위의 비디오가 재생되면 Streamlit + HTML iframe이 정상 작동합니다.
❌ 비디오가 재생되지 않으면 다른 문제가 있습니다.

### 디버그 방법:
1. F12 (개발자 도구) 열기
2. Console 탭에서 에러 확인
3. Network 탭에서 iframe 요청 상태 확인
""")

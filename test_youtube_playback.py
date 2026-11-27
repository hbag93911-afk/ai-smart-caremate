"""YouTube 동영상 재생 기능 테스트"""
import streamlit as st

st.set_page_config(page_title="YouTube 재생 테스트", layout="wide")

st.title("🎥 YouTube 재생 기능 테스트")

st.markdown("## 테스트 1: 직접 HTML iframe 임베드")
st.markdown("유튜브 Video ID: `dQw4w9WgXcQ` (Rick Roll - 매우 유명한 비디오)")

# 테스트 1: 기본 iframe
st.markdown("### HTML iframe으로 임베드")
iframe_html = """
<iframe width="100%" height="600" src="https://www.youtube.com/embed/dQw4w9WgXcQ" 
    frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
    allowfullscreen></iframe>
"""
st.markdown(iframe_html, unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 테스트 2: 동적 비디오 선택")
video_id = st.text_input("유튜브 Video ID 입력", value="dQw4w9WgXcQ")
if video_id:
    st.write(f"입력된 ID: `{video_id}`")
    iframe_html = f"""
    <iframe width="100%" height="600" src="https://www.youtube.com/embed/{video_id}" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen></iframe>
    """
    st.markdown(iframe_html, unsafe_allow_html=True)

st.markdown("---")

st.markdown("## 테스트 3: 여러 비디오")
test_videos = {
    "Rick Roll": "dQw4w9WgXcQ",
    "스쿼트 초보자": "ZWUBHd6ysMU",
    "걷기 운동": "V-1Yq8_1Hyk"
}

for title, vid_id in test_videos.items():
    st.markdown(f"### {title}")
    st.markdown(f"Video ID: `{vid_id}`")
    iframe_html = f"""
    <iframe width="100%" height="400" src="https://www.youtube.com/embed/{vid_id}" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen></iframe>
    """
    st.markdown(iframe_html, unsafe_allow_html=True)
    st.markdown("---")

st.markdown("## 테스트 결과 확인")
st.info("""
✅ 위의 비디오들이 재생되면 Streamlit + HTML iframe 방식이 작동하는 것입니다.
❌ 위의 비디오들이 재생되지 않으면 다른 문제가 있는 것입니다.

### 문제 진단:
1. 브라우저 콘솔(F12)에서 에러 메시지 확인
2. 네트워크 탭에서 iframe 요청 상태 확인
3. 로컬 호스트가 아닌 다른 환경에서 테스트해보기
""")

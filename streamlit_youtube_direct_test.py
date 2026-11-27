"""
Streamlit YouTube 직접 임베드 테스트
"""
import streamlit as st

st.set_page_config(page_title="YouTube Embed Direct Test", layout="wide")

st.title("🎥 YouTube 임베드 직접 테스트")
st.markdown("이 페이지는 Streamlit에서 YouTube iframe이 실제로 임베드되는지 테스트합니다.")

# 테스트용 비디오
test_videos = {
    "Rick Roll (기준 테스트)": "dQw4w9WgXcQ",
    "스쿼트 초보자": "ZWUBHd6ysMU",
    "스쿼트 완벽 가이드": "aclHkTpjA4s",
    "올바른 걷기": "V-1Yq8_1Hyk",
    "실내 걷기 20분": "W_8LjhN-wR0",
    "스트레칭 15분": "qZkjG0cWmj4",
}

st.markdown("## 비디오 선택")
selected_video = st.selectbox("재생할 비디오 선택:", list(test_videos.keys()))

if selected_video:
    video_id = test_videos[selected_video]
    
    st.markdown(f"### {selected_video}")
    st.markdown(f"**Video ID:** `{video_id}`")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**Embed URL:** `https://www.youtube.com/embed/{video_id}`")
    
    with col2:
        st.markdown(f"[유튜브 열기](https://www.youtube.com/watch?v={video_id})")
    
    st.markdown("---")
    
    # 임베드 방식 선택
    st.markdown("## 임베드 방식 선택")
    embed_style = st.radio(
        "어떤 방식으로 임베드할까요?",
        [
            "방식 1: 기본 iframe (고정 크기)",
            "방식 2: Responsive iframe",
            "방식 3: 위험한 HTML (최대한 간단)",
        ]
    )
    
    st.markdown("---")
    st.markdown("## 임베드 결과")
    
    if embed_style == "방식 1: 기본 iframe (고정 크기)":
        try:
            st.markdown(f"""
            <iframe width="100%" height="600" 
                    src="https://www.youtube.com/embed/{video_id}" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen></iframe>
            """, unsafe_allow_html=True)
            st.success("✅ 임베드 성공 (방식 1)")
        except Exception as e:
            st.error(f"❌ 임베드 실패 (방식 1): {e}")
    
    elif embed_style == "방식 2: Responsive iframe":
        try:
            st.markdown(f"""
            <div style="position: relative; width: 100%; padding-bottom: 56.25%;">
                <iframe 
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                    src="https://www.youtube.com/embed/{video_id}" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
                </iframe>
            </div>
            """, unsafe_allow_html=True)
            st.success("✅ 임베드 성공 (방식 2)")
        except Exception as e:
            st.error(f"❌ 임베드 실패 (방식 2): {e}")
    
    elif embed_style == "방식 3: 위험한 HTML (최대한 간단)":
        try:
            dangerous_html = f'<iframe src="https://www.youtube.com/embed/{video_id}" width="100%" height="600" allowfullscreen></iframe>'
            st.markdown(dangerous_html, unsafe_allow_html=True)
            st.success("✅ 임베드 성공 (방식 3)")
        except Exception as e:
            st.error(f"❌ 임베드 실패 (방식 3): {e}")
    
    st.markdown("---")
    st.markdown("""
    ### 디버그 정보:
    - 위에 비디오가 보이면 Streamlit + HTML iframe이 정상 작동합니다.
    - 비디오가 보이지 않으면 F12 (개발자 도구)를 열어서:
      1. Console 탭에서 에러 확인
      2. Network 탭에서 iframe 요청 상태 확인
      3. Elements 탭에서 iframe 태그 확인
    """)

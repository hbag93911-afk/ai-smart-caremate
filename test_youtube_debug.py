"""YouTube 재생 디버그 버전 - 실제 앱의 render_youtube_videos 함수 단순화"""
import streamlit as st
import sys
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from youtube_integration import YouTubeSearcher, VideoWatchTracker
    from workout_recommendation import ExerciseLibrary
except Exception as e:
    st.error(f"Import error: {e}")

st.set_page_config(page_title="YouTube 재생 테스트 (디버그)", layout="wide")

st.title("🎥 YouTube 재생 디버그 테스트")

# Initialize session state
if "youtube_searcher" not in st.session_state:
    try:
        st.session_state.youtube_searcher = YouTubeSearcher()
        st.session_state.video_tracker = VideoWatchTracker()
        st.session_state.selected_video = None
        st.session_state.selected_video_title = None
        st.session_state.selected_video_playability = "playable"
    except Exception as e:
        st.error(f"Session state error: {e}")

try:
    searcher = st.session_state.youtube_searcher
    
    # Exercise selection
    library = ExerciseLibrary()
    all_exercises = [ex.name for ex in library.get_all_exercises()]
    
    st.markdown("## 운동 선택")
    col1, col2 = st.columns(2)
    
    with col1:
        selected_exercise = st.selectbox("운동 선택", all_exercises, key="youtube_exercise_select")
    
    with col2:
        difficulty_filter = st.selectbox(
            "난이도 필터",
            ["모두", "초보자", "중급자", "고급자"],
            key="youtube_difficulty"
        )
    
    if selected_exercise:
        st.markdown(f"### {selected_exercise} 관련 영상")
        
        # Get exercise info
        exercise_info = library.get_exercise(selected_exercise)
        if exercise_info:
            st.info(f"**{selected_exercise}** - {exercise_info.description}")
        
        # Search videos
        difficulty_param = None if difficulty_filter == "모두" else difficulty_filter
        videos = searcher.search_videos(selected_exercise, difficulty_param, limit=6)
        
        st.markdown(f"**찾은 영상 수:** {len(videos)}")
        
        if not videos:
            st.warning(f"{selected_exercise}의 추천 영상이 없습니다.")
        else:
            # Separate playable and unavailable
            playable_videos = [v for v in videos if v.get("is_playable", True)]
            unavailable_videos = [v for v in videos if not v.get("is_playable", True)]
            
            st.markdown(f"**재생 가능:** {len(playable_videos)} | **재생 불가:** {len(unavailable_videos)}")
            
            # Display videos in grid
            cols = st.columns(2)
            for idx, video in enumerate(playable_videos):
                with cols[idx % 2]:
                    st.markdown(f"#### {video['title']}")
                    st.markdown(f"**Video ID:** `{video['video_id']}`")
                    st.markdown(f"**채널:** {video['channel']}")
                    st.markdown(f"**길이:** {video['duration_text']} | **난이도:** {video['difficulty']}")
                    
                    # Show thumbnail
                    try:
                        st.image(video['thumbnail_url'], use_column_width=True)
                    except Exception as e:
                        st.warning(f"썸네일 오류: {e}")
                    
                    # Play button
                    col_play, col_external = st.columns(2)
                    with col_play:
                        if st.button("▶️ 앱에서 보기", key=f"play_{video['video_id']}"):
                            st.session_state.selected_video = video['video_id']
                            st.session_state.selected_video_title = video['title']
                            st.session_state.selected_video_playability = video.get("playability", "playable")
                            st.rerun()
                    
                    with col_external:
                        st.markdown(f"[🔗 유튜브]({video['url']})")
                    
                    st.markdown("---")
        
        # Play selected video
        if st.session_state.get("selected_video"):
            st.markdown("---")
            st.markdown("### 🎬 현재 재생 중")
            
            video_id = st.session_state.selected_video
            playability = st.session_state.get("selected_video_playability", "playable")
            
            st.markdown(f"**Video ID:** `{video_id}`")
            st.markdown(f"**제목:** {st.session_state.selected_video_title}")
            st.markdown(f"**재생 가능성:** {playability}")
            
            if playability == "playable":
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                st.markdown(f"**Embed URL:** `{embed_url}`")
                
                st.markdown("### HTML Iframe 임베드:")
                try:
                    iframe_html = f"""
                    <div style="position: relative; width: 100%; padding-bottom: 56.25%;">
                        <iframe 
                            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                            src="{embed_url}" 
                            frameborder="0" 
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                            allowfullscreen>
                        </iframe>
                    </div>
                    """
                    st.markdown(iframe_html, unsafe_allow_html=True)
                    
                    col_complete, col_external = st.columns(2)
                    with col_complete:
                        if st.button("✅ 시청 완료", key="video_watch_complete"):
                            st.session_state.video_tracker.record_watch(video_id, st.session_state.selected_video_title)
                            st.success("영상 시청이 기록되었습니다!")
                            st.session_state.selected_video = None
                            st.rerun()
                    
                    with col_external:
                        st.markdown(f"[🔗 유튜브에서 열기](https://www.youtube.com/watch?v={video_id})")
                    
                except Exception as e:
                    st.error(f"❌ 오류: {e}")
                    st.markdown(f"[유튜브에서 직접 보기](https://www.youtube.com/watch?v={video_id})")
            else:
                st.warning("🚫 이 영상은 재생할 수 없습니다.")
                st.markdown(f"**상태:** {playability}")
                st.markdown(f"[유튜브에서 직접 보기](https://www.youtube.com/watch?v={video_id})")

except Exception as e:
    st.error(f"❌ 에러 발생: {e}")
    import traceback
    st.code(traceback.format_exc())

st.markdown("---")
st.markdown("""
### 디버그 정보:
- Streamlit이 HTML iframe을 `unsafe_allow_html=True`로 렌더링하고 있습니다.
- 위에 비디오가 보이면 임베드가 작동하는 것입니다.
- 비디오가 보이지 않으면 F12로 브라우저 콘솔을 확인하세요.
""")

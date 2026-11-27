"""UI 렌더 함수들 - 새로운 메뉴 화면을 렌더링합니다."""

import streamlit as st
from workout_recommendation import WorkoutRecommender, UserProfile, ExerciseLibrary
from health_tracker import HealthTracker
from youtube_integration import YouTubeSearcher, VideoWatchTracker


def render_posture_analysis() -> None:
    """AI 카메라 자세 분석 화면을 렌더링합니다."""
    st.title("🎥 AI 카메라 자세 분석")
    st.subheader("현재 자세를 카메라로 촬영하여 분석합니다")

    st.markdown("""
    이 메뉴에서는:
    - 카메라로 현재 자세를 촬영합니다
    - 실시간으로 신체 관절을 인식합니다
    - 자세의 정확도를 평가합니다
    - 개선점을 제시합니다
    """)

    col1, col2 = st.columns(2)

    with col1:
        analysis_type = st.radio("분석 종류", ["전신 자세", "상체 자세", "하체 자세"], key="analysis_type")

    with col2:
        view_angle = st.radio("촬영 각도", ["정면", "측면"], key="view_angle")

    if st.button("🎬 카메라 시작", key="start_posture_camera"):
        st.session_state.current_menu = "💪 실시간 AI 운동 코칭"
        st.session_state.coaching_mode = "자세_분석"
        st.rerun()

    st.markdown("---")
    st.info("💡 팁: 밝은 환경에서 충분한 거리를 두고 촬영해주세요. (약 1-2m)")


def render_posture_analysis_legacy() -> None:
    """기존 자세 분석 함수 (호환성 유지)"""
    # 기존 render_pose_page() 로직을 여기에 넣음
    pass


def render_workout_recommendations() -> None:
    """AI 맞춤 운동 추천 화면을 렌더링합니다."""
    st.title("🤖 AI 맞춤 운동 추천")
    st.subheader("당신의 체력과 목표에 맞는 최적의 운동을 추천합니다")

    recommender: WorkoutRecommender = st.session_state.workout_recommender
    user_profile: UserProfile = st.session_state.user_profile

    with st.expander("👤 개인 프로필 설정", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            fitness_level = st.selectbox(
                "현재 체력 수준",
                ["초보자", "중급자", "고급자"],
                key="fitness_level"
            )
            user_profile.set_fitness_level(fitness_level)

        with col2:
            available_time = st.slider(
                "하루 운동 가능 시간 (분)",
                5, 120, user_profile.available_time_minutes,
                key="available_time"
            )
            user_profile.available_time_minutes = available_time

        st.markdown("---")

        # 운동 목표 선택
        goals = st.multiselect(
            "운동 목표",
            ["근력 향상", "체력 증진", "유연성", "체중 관리"],
            default=user_profile.goals if user_profile.goals else [],
            key="exercise_goals"
        )
        user_profile.goals = goals

        # 신체적 제한사항
        limitations = st.multiselect(
            "신체적 제한사항 (해당하는 항목 선택)",
            ["무릎", "허리", "어깨", "목", "팔목", "발목"],
            default=user_profile.physical_limitations if user_profile.physical_limitations else [],
            key="physical_limitations"
        )
        user_profile.physical_limitations = limitations

    st.markdown("---")

    # 추천 운동 생성
    if st.button("✨ 운동 추천받기", key="get_recommendations"):
        st.session_state.show_recommendations = True

    if st.session_state.get("show_recommendations", False):
        st.markdown("### 추천 운동")

        recommendations = recommender.get_recommended_exercises(user_profile, limit=5)

        if recommendations:
            for idx, rec in enumerate(recommendations, 1):
                with st.container():
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**{idx}. {rec['exercise'].name}**")
                        st.markdown(f"**추천 이유:** {rec['reason']}")
                        st.markdown(f"**설명:** {rec['exercise'].description}")
                        st.markdown(f"**효과:** {rec['benefits']}")
                        st.markdown(f"**주의사항:** {rec['exercise'].precautions}")

                    with col2:
                        st.markdown(f"**난이도:** {rec['difficulty']}")
                        st.markdown(f"**소요 시간:** {rec['duration']}")
                        if st.button("🎬 이 운동 시작", key=f"start_rec_{idx}"):
                            st.session_state.current_menu = "💪 실시간 AI 운동 코칭"
                            st.session_state.selected_exercise = rec['exercise'].name
                            st.rerun()

                    st.markdown("---")
        else:
            st.warning("현재 프로필에 맞는 추천 운동이 없습니다.")


def render_exercise_browse() -> None:
    """운동 종류별 탐색 화면을 렌더링합니다."""
    st.title("📚 운동 종류별 탐색")
    st.subheader("원하는 운동을 카테고리별로 탐색합니다")

    library = ExerciseLibrary()
    categories = set(ex.category for ex in library.get_all_exercises())

    selected_category = st.selectbox("운동 카테고리 선택", sorted(categories), key="category_select")

    if selected_category:
        exercises = library.get_exercises_by_category(selected_category)

        st.markdown(f"### {selected_category} 운동 목록")

        for exercise in exercises:
            with st.container():
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**{exercise.name}**")
                    st.markdown(f"{exercise.description}")
                    st.markdown(f"**효과:** {exercise.benefits}")
                    st.markdown(f"**목표 부위:** {', '.join(exercise.target_areas)}")
                    st.markdown(f"**주의사항:** {exercise.precautions}")

                with col2:
                    st.markdown(f"**난이도:** {exercise.difficulty}")
                    st.markdown(f"**소요 시간:** {exercise.duration_range}")
                    if st.button("▶️ 시작", key=f"browse_start_{exercise.name}"):
                        st.session_state.current_menu = "💪 실시간 AI 운동 코칭"
                        st.session_state.selected_exercise = exercise.name
                        st.rerun()

                st.markdown("---")


def render_youtube_videos() -> None:
    """유튜브 운동 영상 화면을 렌더링합니다."""
    st.title("📹 유튜브 운동 영상")
    st.subheader("운동별 유튜브 영상을 검색하고 시청합니다")

    searcher: YouTubeSearcher = st.session_state.youtube_searcher
    tracker: VideoWatchTracker = st.session_state.video_tracker

    # 운동 선택
    library = ExerciseLibrary()
    all_exercises = [ex.name for ex in library.get_all_exercises()]

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_exercise = st.selectbox("운동 선택", all_exercises, key="youtube_exercise_select")

    with col2:
        difficulty_filter = st.selectbox(
            "난이도 필터",
            ["모두", "초보자", "중급자", "고급자"],
            key="youtube_difficulty"
        )
    
    with col3:
        playback_method = st.selectbox(
            "재생 방식",
            ["앱 내 임베드", "유튜브 열기"],
            key="youtube_playback_method",
            help="앱 내에서 재생되지 않으면 '유튜브 열기'를 선택하세요"
        )

    if selected_exercise:
        st.markdown(f"### {selected_exercise} 관련 영상")
        
        # 운동 정보 표시
        exercise_info = library.get_exercise(selected_exercise)
        if exercise_info:
            st.info(f"**{selected_exercise}** - {exercise_info.description}")

        # 영상 검색
        difficulty_param = None if difficulty_filter == "모두" else difficulty_filter
        videos = searcher.search_videos(selected_exercise, difficulty_param, limit=6)

        if not videos:
            st.warning(f"{selected_exercise}의 추천 영상이 없습니다.")
        else:
            # 재생 가능한 영상과 불가능한 영상 분류
            playable_videos = [v for v in videos if v.get("is_playable", True)]
            unavailable_videos = [v for v in videos if not v.get("is_playable", True)]

            st.markdown(f"**찾은 영상:** {len(playable_videos)}개 (재생 가능) | {len(unavailable_videos)}개 (재생 불가)")

            # 영상 그리드로 표시
            cols = st.columns(2)
            for idx, video in enumerate(playable_videos):
                with cols[idx % 2]:
                    st.markdown(f"### {video.get('title', '제목 없음')}")
                    st.markdown(f"**채널:** {video.get('channel', '채널 정보 없음')}")
                    
                    # duration_text가 없으면 duration_seconds에서 계산
                    duration_text = video.get('duration_text')
                    if not duration_text and video.get('duration_seconds'):
                        mins = video['duration_seconds'] // 60
                        secs = video['duration_seconds'] % 60
                        duration_text = f"{mins}:{secs:02d}"
                    
                    duration_display = duration_text if duration_text else "정보 없음"
                    st.markdown(f"**길이:** {duration_display} | **난이도:** {video.get('difficulty', '정보 없음')}")

                    # 썸네일 표시 (Streamlit 1.19.0+ 호환)
                    try:
                        thumbnail_url = video.get('thumbnail_url')
                        if thumbnail_url:
                            # use_column_width는 deprecated → use_container_width로 변경
                            st.image(thumbnail_url, use_container_width=True)
                        else:
                            st.info("썸네일 정보 없음")
                    except Exception as e:
                        st.warning("썸네일을 불러올 수 없습니다.")

                    col_play, col_external = st.columns(2)
                    with col_play:
                        video_id = video.get('video_id', '')
                        if st.button("▶️ 재생", key=f"play_{video_id}", use_container_width=True):
                            st.session_state.selected_video = video_id
                            st.session_state.selected_video_title = video.get('title', '제목 없음')
                            st.session_state.selected_video_playability = video.get("playability", "playable")
                            st.session_state.selected_video_url = video.get('url', f"https://www.youtube.com/watch?v={video_id}")
                            st.rerun()

                    with col_external:
                        video_url = video.get('url', f"https://www.youtube.com/watch?v={video.get('video_id', '')}")
                        st.link_button(
                            "🔗 유튜브", 
                            video_url,
                            use_container_width=True
                        )

                    st.markdown("---")

            # 재생 불가능한 영상 표시
            if unavailable_videos:
                st.markdown("### ⚠️ 재생할 수 없는 영상")
                for video in unavailable_videos:
                    video_title = video.get('title', '제목 없음')
                    with st.expander(f"❌ {video_title}"):
                        reason = "재생할 수 없습니다"
                        if video.get("playability") == "unavailable":
                            reason = "🗑️ 이 영상은 삭제되었습니다."
                        elif video.get("playability") == "private":
                            reason = "🔒 이 영상은 비공개입니다."
                        elif video.get("playability") == "restricted":
                            reason = "⛔ 이 영상은 재생이 제한되어 있습니다."
                        elif video.get("playability") == "embed_disabled":
                            reason = "🚫 이 영상은 임베드가 허용되지 않습니다. 유튜브에서 직접 보세요."
                        
                        st.markdown(f"{reason}")
                        if video.get("restricted_message"):
                            st.info(f"상세 정보: {video.get('restricted_message')}")
                        
                        video_url = video.get('url', f"https://www.youtube.com/watch?v={video.get('video_id', '')}")
                        st.link_button("유튜브에서 보기", video_url, use_container_width=True)

        # 선택한 영상 재생
        if st.session_state.get("selected_video"):
            st.markdown("---")
            st.markdown("### 현재 재생 중")
            
            video_id = st.session_state.selected_video
            video_title = st.session_state.selected_video_title
            video_url = st.session_state.get("selected_video_url") or f"https://www.youtube.com/watch?v={video_id}"
            playability = st.session_state.get("selected_video_playability", "playable")
            
            if playability == "playable":
                col_title, col_clear = st.columns([4, 1])
                with col_title:
                    st.markdown(f"**{video_title}**")
                with col_clear:
                    if st.button("❌ 닫기", key="close_video"):
                        st.session_state.selected_video = None
                        st.rerun()
                
                # 재생 방식에 따라 다른 방법 사용
                if playback_method == "앱 내 임베드":
                    # HTML iframe 임베드 (개선된 버전)
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                    
                    # Streamlit에서 HTML iframe 렌더링
                    # 주의: 모든 YouTube 영상이 임베드를 허용하지는 않습니다
                    iframe_html = f"""
                    <div style="display:flex;justify-content:center;width:100%;margin:10px 0;">
                        <iframe 
                            width="100%" 
                            height="600" 
                            src="{embed_url}?rel=0&showinfo=0&modestbranding=1" 
                            title="{video_title}"
                            frameborder="0" 
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                            allowfullscreen
                            style="max-width:100%;border-radius:8px;border:1px solid #ddd;">
                        </iframe>
                    </div>
                    """
                    
                    st.markdown(iframe_html, unsafe_allow_html=True)
                    st.info("""
                    💡 팁: 위에서 비디오가 보이지 않으면 아래 버튼으로 유튜브에서 직접 보세요.
                    일부 영상은 외부 사이트에서의 임베드를 허용하지 않습니다.
                    """)
                
                else:  # 유튜브 열기
                    st.info("🔗 유튜브 페이지에서 영상을 재생합니다.")
                    st.link_button("🔗 유튜브에서 보기", video_url, use_container_width=True)
                
                col_complete, col_external = st.columns(2)
                with col_complete:
                    if st.button("✅ 시청 완료", key="video_watch_complete", use_container_width=True):
                        tracker.record_watch(st.session_state.selected_video, st.session_state.selected_video_title)
                        st.success("✅ 영상 시청이 기록되었습니다!")
                        st.session_state.selected_video = None
                        st.rerun()
                
                with col_external:
                    st.link_button("🔗 새 창에서 열기", video_url, use_container_width=True)
                    
            else:
                st.warning("🚫 이 영상은 재생할 수 없습니다.")
                st.markdown("**재생할 수 없는 이유:**")
                if playability == "unavailable":
                    st.info("🗑️ 이 영상은 삭제되었습니다.")
                elif playability == "private":
                    st.info("🔒 이 영상은 비공개입니다.")
                elif playability == "restricted":
                    st.info("⛔ 이 영상은 재생이 제한되어 있습니다.")
                elif playability == "embed_disabled":
                    st.info("🚫 이 영상은 임베드가 허용되지 않습니다.")
                
                st.link_button("유튜브에서 직접 보기", video_url, use_container_width=True)

        st.markdown("---")
        st.markdown("### 최근 시청 기록")
        recent = tracker.get_watch_history(5)
        if recent:
            for watch in recent:
                st.markdown(f"- **{watch['title']}** ({watch['watched_at'][:10]})")
        else:
            st.info("시청 기록이 없습니다.")



def render_realtime_coaching() -> None:
    """실시간 AI 운동 코칭 화면을 렌더링합니다."""
    st.title("💪 실시간 AI 운동 코칭")
    st.subheader("선택한 운동을 카메라로 실시간 분석합니다")

    # 기존 운동 메뉴 통합
    library = ExerciseLibrary()
    all_exercises = [ex.name for ex in library.get_all_exercises()]

    if "selected_exercise" not in st.session_state:
        selected_ex = st.selectbox("운동 선택", all_exercises, key="coaching_exercise")
        st.session_state.selected_exercise = selected_ex
    else:
        selected_ex = st.session_state.selected_exercise
        st.markdown(f"**선택한 운동:** {selected_ex}")

        if st.button("🔄 다른 운동 선택"):
            st.session_state.selected_exercise = None
            st.rerun()

    if selected_ex:
        exercise_info = library.get_exercise(selected_ex)
        
        with st.expander("📋 운동 상세 정보", expanded=False):
            st.markdown(f"**{exercise_info.name}**")
            st.markdown(f"**설명:** {exercise_info.description}")
            st.markdown(f"**효과:** {exercise_info.benefits}")
            st.markdown(f"**난이도:** {exercise_info.difficulty}")
            st.markdown(f"**목표 부위:** {', '.join(exercise_info.target_areas)}")
            st.markdown(f"**주의사항:** {exercise_info.precautions}")

        st.markdown("---")

        # 운동별 카메라 실행
        if selected_ex == "스쿼트":
            render_squat_coaching()
        elif selected_ex in ["걷기", "산책"]:
            render_walk_coaching()
        else:
            render_generic_coaching(selected_ex)


def render_squat_coaching() -> None:
    """스쿼트 운동 코칭을 렌더링합니다."""
    st.info("스쿼트 운동을 시작합니다. 카메라를 보고 천천히 움직여주세요.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎬 카메라 시작", key="squat_camera_start"):
            if not st.session_state.camera_running:
                try:
                    # 순환 임포트 방지를 위해 app 모듈 임포트
                    from app import start_camera
                    start_camera()
                except Exception as e:
                    st.error(f"카메라 시작 실패: {e}")
            else:
                st.info("카메라가 이미 실행 중입니다.")

    with col2:
        if st.button("🛑 카메라 중지", key="squat_camera_stop"):
            try:
                from app import stop_camera
                stop_camera()
                st.info("카메라가 중지되었습니다.")
            except Exception:
                pass

    if st.session_state.get("camera_running"):
        st.markdown("### 실시간 운동 분석")
        st.info("카메라에서 실시간 스쿼트를 분석합니다.")
        
        # 여기에 기존 스쿼트 분석 로직 통합
        col1, col2 = st.columns(2)
        with col1:
            st.metric("현재 반복 횟수", st.session_state.today_count)
        with col2:
            st.metric("운동 시간", f"{int(st.session_state.workout_seconds // 60)}분")


def render_walk_coaching() -> None:
    """보행 운동 코칭을 렌더링합니다."""
    st.info("보행 운동을 시작합니다. 카메라를 보고 걸어주세요.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎬 카메라 시작", key="walk_camera_start"):
            if not st.session_state.camera_running:
                try:
                    from app import start_camera
                    start_camera()
                except Exception as e:
                    st.error(f"카메라 시작 실패: {e}")
            else:
                st.info("카메라가 이미 실행 중입니다.")

    with col2:
        if st.button("🛑 카메라 중지", key="walk_camera_stop"):
            try:
                from app import stop_camera
                stop_camera()
                st.info("카메라가 중지되었습니다.")
            except Exception:
                pass

    if st.session_state.get("camera_running"):
        st.markdown("### 실시간 운동 분석")
        st.info("카메라에서 실시간 보행을 분석합니다.")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("걸음 수", st.session_state.today_steps)
        with col2:
            st.metric("운동 시간", f"{int(st.session_state.walk_seconds // 60)}분")


def render_generic_coaching(exercise_name: str) -> None:
    """일반 운동 코칭을 렌더링합니다."""
    st.info(f"{exercise_name} 운동을 위한 카메라 분석 기능을 준비 중입니다.")
    st.markdown("""
    현재 버전에서는 다음 운동들의 실시간 분석을 지원합니다:
    - 스쿼트
    - 걷기 / 산책
    
    다른 운동들은 위의 유튜브 영상 메뉴에서 영상을 보며 따라 할 수 있습니다.
    """)


def render_goal_management_new() -> None:
    """운동 목표 관리 화면을 렌더링합니다."""
    st.title("🎯 운동 목표 관리")
    st.subheader("개인별 운동 목표를 설정하고 진행도를 추적합니다")

    health_tracker: HealthTracker = st.session_state.health_tracker

    with st.expander("🎯 운동별 목표 설정", expanded=True):
        library = ExerciseLibrary()
        all_exercises = [ex.name for ex in library.get_all_exercises()]

        exercise_name = st.selectbox("운동 선택", all_exercises, key="goal_exercise")

        if exercise_name:
            current_goal = health_tracker.get_exercise_goal(exercise_name)

            col1, col2 = st.columns(2)

            with col1:
                target_frequency = st.slider(
                    "주간 목표 빈도 (회/주)",
                    1, 7,
                    current_goal["target_frequency_per_week"] if current_goal else 3,
                    key=f"freq_{exercise_name}"
                )

            with col2:
                target_duration = st.slider(
                    "목표 소요 시간 (분)",
                    5, 120,
                    current_goal["target_duration_minutes"] if current_goal else 30,
                    key=f"duration_{exercise_name}"
                )

            notes = st.text_area(
                "메모",
                current_goal["notes"] if current_goal else "",
                key=f"notes_{exercise_name}"
            )

            if st.button(f"💾 {exercise_name} 목표 저장"):
                health_tracker.set_exercise_goal(exercise_name, target_frequency, target_duration, notes)
                st.success(f"{exercise_name}의 목표가 저장되었습니다!")

    st.markdown("---")

    # 운동별 진행도 표시
    st.markdown("### 📊 목표 달성 현황")

    library = ExerciseLibrary()
    all_exercises = [ex.name for ex in library.get_all_exercises()]

    for exercise_name in all_exercises:
        goal = health_tracker.get_exercise_goal(exercise_name)
        if goal:
            progress = health_tracker.get_weekly_progress(exercise_name, days_back=7)

            with st.expander(f"{exercise_name}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("완료 세션", f"{progress['sessions_completed']}회")

                with col2:
                    achievement_rate = progress.get("session_achievement_rate", 0)
                    st.metric("달성률", f"{achievement_rate:.1f}%")

                with col3:
                    total_time = progress.get("total_duration_minutes", 0)
                    st.metric("총 시간", f"{total_time}분")

                st.progress(min(100, achievement_rate) / 100.0)

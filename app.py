import json
import math
import sqlite3
import time
from datetime import datetime
from pathlib import Path

import altair as alt
import cv2
import streamlit as st
import streamlit.components.v1 as components

from camera import CameraError, CameraManager
from pose_detection import PoseDetector
from squat_analysis import SquatAnalyzer
from walk_analysis import WalkAnalyzer
from goal_manager import GoalManager
from analytics import Analytics
from workout_recommendation import WorkoutRecommender, UserProfile
from health_tracker import HealthTracker
from youtube_integration import YouTubeSearcher, VideoWatchTracker
from home_dashboard_new import render_new_home_dashboard
from ui_renderers import (
    render_posture_analysis,
    render_workout_recommendations,
    render_exercise_browse,
    render_youtube_videos,
    render_realtime_coaching,
    render_goal_management_new,
)

MODEL_PATH = "pose_landmarker_lite.task"
DB_PATH = Path(__file__).with_name("workout_history.db")


st.set_page_config(
    page_title="AI 스마트 케어메이트",
    page_icon="🩺",
    layout="wide",
)


def ensure_session_state() -> None:
    """앱 전체에서 사용할 세션 상태를 초기화합니다."""
    defaults = {
        "camera": None,
        "camera_running": False,
        "pose_detector": None,
        "camera_error": "",
        "workout_running": False,
        "workout_paused": False,
        "workout_seconds": 0.0,
        "workout_started_ts": None,
        "workout_history": [],
        "today_count": 0,
        "goal_target": 20,
        "goal_rate": 0,
        "last_voice_message": "",
        "last_voice_ts": 0.0,
        "posture_monitoring": False,
        "posture_forward_started_ts": None,
        "posture_last_alert_ts": 0.0,
        "current_menu": "🏠 홈 대시보드",
        "walk_running": False,
        "walk_paused": False,
        "walk_seconds": 0.0,
        "walk_started_ts": None,
        "walk_history": [],
        "today_steps": 0,
        "walk_goal_target": 5000,
        "walk_goal_rate": 0,
        "settings": {
            "camera_index": 0,
            "detection_sensitivity": 0.55,
            "show_joint_labels": True,
            "show_guidance": True,
            "video_recording": False,
        },
        "health_settings": {
            "hydration_ml": 1000,
            "daily_steps": 8000,
            "sleep_hours": 7,
        },
        "safety_settings": {
            "camera_distance_ok": True,
            "lighting_ok": True,
            "floor_stable": True,
            "safety_note": "카메라와 바닥 상태를 점검해 주세요.",
        },
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "squat_analyzer" not in st.session_state:
        st.session_state.squat_analyzer = SquatAnalyzer()
    if "walk_analyzer" not in st.session_state:
        st.session_state.walk_analyzer = WalkAnalyzer()
    if "goal_manager" not in st.session_state:
        st.session_state.goal_manager = GoalManager()
    if "analytics" not in st.session_state:
        st.session_state.analytics = Analytics()
    if "workout_recommender" not in st.session_state:
        st.session_state.workout_recommender = WorkoutRecommender()
    if "health_tracker" not in st.session_state:
        st.session_state.health_tracker = HealthTracker()
    if "youtube_searcher" not in st.session_state:
        st.session_state.youtube_searcher = YouTubeSearcher()
    if "video_tracker" not in st.session_state:
        st.session_state.video_tracker = VideoWatchTracker()
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = UserProfile()

    # 초기화 시 목표 설정 (DB에 저장된 값이 있으면 로드)
    goal_mgr = st.session_state.goal_manager
    squat_goal = goal_mgr.get_goal("squat")
    walk_goal = goal_mgr.get_goal("walk")
    
    if squat_goal is not None:
        st.session_state.goal_target = squat_goal
    if walk_goal is not None:
        st.session_state.walk_goal_target = walk_goal



def stop_camera() -> None:
    """카메라를 종료하고 운동 상태를 정리합니다."""
    camera = st.session_state.get("camera")
    if camera is not None:
        camera.stop()
    st.session_state.camera = None
    st.session_state.camera_running = False
    st.session_state.workout_running = False
    st.session_state.workout_paused = False
    st.session_state.workout_started_ts = None


def start_camera() -> None:
    """웹캠을 열고 포즈 감지기를 준비합니다."""
    try:
        if st.session_state.pose_detector is None:
            st.session_state.pose_detector = PoseDetector(model_path=MODEL_PATH)

        camera = CameraManager(camera_index=int(st.session_state.settings["camera_index"]))
        camera.start()
        st.session_state.camera = camera
        st.session_state.camera_running = True
        st.session_state.camera_error = ""
    except FileNotFoundError as error:
        st.session_state.camera_error = str(error)
        st.session_state.camera_running = False
    except CameraError as error:
        st.session_state.camera_error = str(error)
        st.session_state.camera_running = False
    except RuntimeError as error:
        st.session_state.camera_error = str(error)
        st.session_state.camera_running = False


def update_workout_timer() -> None:
    """운동 중일 때 시간 누적을 계산합니다."""
    if st.session_state.get("workout_running") and not st.session_state.get("workout_paused"):
        if st.session_state.get("workout_started_ts") is None:
            st.session_state.workout_started_ts = time.time()
        else:
            elapsed = time.time() - st.session_state.workout_started_ts
            if elapsed > 0:
                st.session_state.workout_seconds += elapsed
                st.session_state.workout_started_ts = time.time()
    else:
        st.session_state.workout_started_ts = None


def update_walk_timer() -> None:
    """보행 중일 때 시간 누적을 계산합니다."""
    if st.session_state.get("walk_running") and not st.session_state.get("walk_paused"):
        if st.session_state.get("walk_started_ts") is None:
            st.session_state.walk_started_ts = time.time()
        else:
            elapsed = time.time() - st.session_state.walk_started_ts
            if elapsed > 0:
                st.session_state.walk_seconds += elapsed
                st.session_state.walk_started_ts = time.time()
    else:
        st.session_state.walk_started_ts = None


def init_workout_db() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workout_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_date TEXT NOT NULL,
                exercise_type TEXT NOT NULL,
                total_count INTEGER NOT NULL,
                workout_seconds REAL NOT NULL,
                avg_posture_accuracy REAL NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS walk_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                walk_date TEXT NOT NULL,
                duration_seconds REAL NOT NULL,
                total_steps INTEGER NOT NULL,
                cadence REAL NOT NULL,
                avg_left_right_balance REAL NOT NULL,
                gait_symmetry REAL NOT NULL,
                avg_posture_accuracy REAL NOT NULL
            )
            """
        )
        connection.commit()


def save_workout_record(
    workout_date: str,
    exercise_type: str,
    total_count: int,
    workout_seconds: float,
    avg_posture_accuracy: float,
) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO workout_records (
                workout_date, exercise_type, total_count, workout_seconds, avg_posture_accuracy
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                workout_date,
                exercise_type,
                int(total_count),
                float(workout_seconds),
                float(avg_posture_accuracy),
            ),
        )
        connection.commit()

    # 목표 달성 기록 저장
    goal_mgr = st.session_state.goal_manager
    squat_goal = goal_mgr.get_goal("squat")
    if squat_goal and int(total_count) > 0:
        # workout_date에서 날짜 부분만 추출 (YYYY-MM-DD)
        workout_date_only = workout_date.split(" ")[0] if " " in workout_date else workout_date
        goal_mgr.record_daily_goal(workout_date_only, "squat", squat_goal, int(total_count))


def load_recent_workout_records(limit: int = 5):
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT workout_date, exercise_type, total_count, workout_seconds, avg_posture_accuracy
            FROM workout_records
            ORDER BY workout_date DESC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()
    return [dict(row) for row in rows]


def load_daily_workout_trend(limit_days: int = 30):
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT substr(workout_date, 1, 10) AS workout_day, SUM(total_count) AS total_count
            FROM workout_records
            GROUP BY workout_day
            ORDER BY workout_day DESC
            LIMIT ?
            """,
            (int(limit_days),),
        ).fetchall()
    daily_rows = [dict(row) for row in rows]
    daily_rows.reverse()
    return daily_rows


def save_walk_record(
    walk_date: str,
    duration_seconds: float,
    total_steps: int,
    cadence: float,
    avg_left_right_balance: float,
    gait_symmetry: float,
    avg_posture_accuracy: float,
) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO walk_records (
                walk_date, duration_seconds, total_steps, cadence, avg_left_right_balance, gait_symmetry, avg_posture_accuracy
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                walk_date,
                float(duration_seconds),
                int(total_steps),
                float(cadence),
                float(avg_left_right_balance),
                float(gait_symmetry),
                float(avg_posture_accuracy),
            ),
        )
        connection.commit()

    # 목표 달성 기록 저장
    goal_mgr = st.session_state.goal_manager
    walk_goal = goal_mgr.get_goal("walk")
    if walk_goal and int(total_steps) > 0:
        # walk_date에서 날짜 부분만 추출 (YYYY-MM-DD)
        walk_date_only = walk_date.split(" ")[0] if " " in walk_date else walk_date
        goal_mgr.record_daily_goal(walk_date_only, "walk", walk_goal, int(total_steps))


def load_recent_walk_records(limit: int = 5):
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT walk_date, duration_seconds, total_steps, cadence, avg_left_right_balance, gait_symmetry, avg_posture_accuracy
            FROM walk_records
            ORDER BY walk_date DESC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()
    return [dict(row) for row in rows]


def load_daily_walk_trend(limit_days: int = 30):
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT substr(walk_date, 1, 10) AS walk_day, SUM(total_steps) AS total_steps
            FROM walk_records
            GROUP BY walk_day
            ORDER BY walk_day DESC
            LIMIT ?
            """,
            (int(limit_days),),
        ).fetchall()
    daily_rows = [dict(row) for row in rows]
    daily_rows.reverse()
    return daily_rows


def render_daily_trend_chart(chart_title: str) -> None:
    trend_rows = load_daily_workout_trend(limit_days=30)
    if not trend_rows:
        st.info("아직 저장된 운동 기록이 없습니다. 운동을 종료하면 날짜별 추이가 표시됩니다.")
        return
    chart_data = [{"날짜": row["workout_day"], "운동 횟수": int(row["total_count"])} for row in trend_rows]
    chart = (
        alt.Chart(alt.Data(values=chart_data))
        .mark_line(point=True, size=3)
        .encode(
            x=alt.X("날짜:N", sort=None, title="날짜"),
            y=alt.Y("운동 횟수:Q", title="운동 횟수(회)"),
            tooltip=["날짜:N", "운동 횟수:Q"],
        )
        .properties(height=280, title=chart_title)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)


def compute_posture_metrics(joint_data: dict):
    required = ["left_ear", "right_ear", "left_shoulder", "right_shoulder"]
    if any(name not in joint_data for name in required):
        return None

    for name in required:
        if float(joint_data[name]["confidence"]) < 0.5:
            return None

    left_ear = joint_data["left_ear"]["point"]
    right_ear = joint_data["right_ear"]["point"]
    left_shoulder = joint_data["left_shoulder"]["point"]
    right_shoulder = joint_data["right_shoulder"]["point"]

    ear_mid = ((left_ear[0] + right_ear[0]) / 2.0, (left_ear[1] + right_ear[1]) / 2.0)
    shoulder_mid = ((left_shoulder[0] + right_shoulder[0]) / 2.0, (left_shoulder[1] + right_shoulder[1]) / 2.0)

    dx = abs(ear_mid[0] - shoulder_mid[0])
    dy = max(1.0, abs(ear_mid[1] - shoulder_mid[1]))
    neck_forward_angle_deg = math.degrees(math.atan2(dx, dy))

    shoulder_dx = max(1.0, abs(right_shoulder[0] - left_shoulder[0]))
    shoulder_dy = abs(right_shoulder[1] - left_shoulder[1])
    shoulder_tilt_deg = math.degrees(math.atan2(shoulder_dy, shoulder_dx))

    return {
        "ear_mid": ear_mid,
        "shoulder_mid": shoulder_mid,
        "neck_forward_angle_deg": neck_forward_angle_deg,
        "shoulder_tilt_deg": shoulder_tilt_deg,
    }


def play_alert_beep(placeholder, message: str) -> None:
    escaped_message = json.dumps(message, ensure_ascii=False)
    with placeholder:
        components.html(
            f"""
            <script>
              (function() {{
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const o = ctx.createOscillator();
                const g = ctx.createGain();
                o.type = "sine";
                o.frequency.value = 880;
                g.gain.value = 0.08;
                o.connect(g);
                g.connect(ctx.destination);
                o.start();
                setTimeout(() => {{
                  o.stop();
                  ctx.close();
                }}, 220);
                if (window.speechSynthesis) {{
                  window.speechSynthesis.cancel();
                  const utterance = new SpeechSynthesisUtterance({escaped_message});
                  utterance.lang = "ko-KR";
                  utterance.rate = 1.0;
                  window.speechSynthesis.speak(utterance);
                }}
              }})();
            </script>
            """,
            height=0,
        )


ensure_session_state()
init_workout_db()

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f4f9ff 0%, #edf5ff 100%);
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .dashboard-card {
        background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
        border: 1px solid #dfeeff;
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 5px 16px rgba(17, 94, 191, 0.08);
    }
    .kpi-box {
        background: linear-gradient(135deg, #0a74ff 0%, #4da3ff 100%);
        color: white;
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 8px 18px rgba(10, 116, 255, 0.2);
    }
    .small-label {
        font-size: 0.8rem;
        color: #4f6a87;
        font-weight: 600;
    }
    .big-number {
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .accent-button > button {
        background: linear-gradient(135deg, #0a74ff 0%, #4ea2ff 100%);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 700;
        height: 48px;
    }
    .secondary-button > button {
        background: white;
        border: 1px solid #cfe3ff;
        color: #0d4fb8;
        border-radius: 12px;
        font-weight: 700;
        height: 48px;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #eff7ff 0%, #edf3ff 100%);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.sidebar.title("AI 스마트 케어메이트")
st.sidebar.caption("생활 속 건강 관리와 운동 보조")
menu_options = [
    "🏠 홈 대시보드",
    "🎥 AI 카메라 자세 분석",
    "🤖 AI 맞춤 운동 추천",
    "📚 운동 종류별 탐색",
    "📹 유튜브 운동 영상",
    "💪 실시간 AI 운동 코칭",
    "🎯 운동 목표 관리",
    "📊 운동 기록 및 통계",
    "📈 종합 건강 리포트",
    "⚙️ 환경 설정",
]
current_menu = st.session_state.get("current_menu", "🏠 홈 대시보드")
selected = st.sidebar.radio("메뉴", menu_options, index=menu_options.index(current_menu) if current_menu in menu_options else 0)
st.session_state.current_menu = selected

with st.sidebar:
    st.markdown("---")
    st.caption("현재 상태")
    st.info("실시간 카메라, 관절 인식, 스쿼트 분석 기능을 지원합니다.")


def render_home_dashboard() -> None:
    """새로운 맞춤형 홈 대시보드를 렌더링합니다."""
    render_new_home_dashboard()


def render_pose_page() -> None:
    st.title("실시간 AI 관절 인식")
    st.caption("웹캠을 실행하면 사람의 관절을 인식하고, 점과 선으로 표시합니다.")

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("카메라 시작", use_container_width=True, disabled=st.session_state.camera_running):
            start_camera()
    with col_stop:
        if st.button("카메라 종료", use_container_width=True, disabled=not st.session_state.camera_running):
            stop_camera()

    status_placeholder = st.empty()
    frame_placeholder = st.empty()

    if st.session_state.camera_error:
        status_placeholder.error(st.session_state.camera_error)

    if st.session_state.camera_running:
        camera = st.session_state.get("camera")
        detector = st.session_state.get("pose_detector")
        if camera is None or detector is None:
            status_placeholder.error("카메라 또는 포즈 감지기가 준비되지 않았습니다.")
            stop_camera()
        else:
            while st.session_state.get("camera_running", False):
                try:
                    frame = camera.read_frame()
                    annotated_frame, detected, _ = detector.detect_and_draw(frame, int(time.time() * 1000))
                    frame_placeholder.image(
                        cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB),
                        channels="RGB",
                        use_container_width=True,
                    )
                    if detected:
                        status_placeholder.success("관절 인식됨")
                    else:
                        status_placeholder.warning("사람이 화면 안에 없거나 관절이 가려져 인식이 불안정합니다.")
                    time.sleep(0.03)
                except CameraError as error:
                    status_placeholder.error(str(error))
                    stop_camera()
                    break
                except RuntimeError as error:
                    status_placeholder.error(str(error))
                    stop_camera()
                    break
    else:
        frame_placeholder.info("카메라가 꺼져 있습니다. 카메라를 시작하면 실시간 관절 인식 화면이 표시됩니다.")
        if not st.session_state.camera_error:
            status_placeholder.info("대기 중")


def render_squat_page() -> None:
    st.title("AI 스쿼트 자세 분석")
    st.caption("현재 버전은 2D 카메라 좌표 기반의 참고용 자세 분석 화면입니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("운동 시작", use_container_width=True, disabled=not st.session_state.camera_running):
            st.session_state.workout_running = True
            st.session_state.workout_paused = False
            st.session_state.workout_started_ts = time.time()
            st.session_state.squat_analyzer.reset()
            st.session_state.today_count = 0
            st.session_state.workout_seconds = 0.0
    with col2:
        if st.button("일시정지", use_container_width=True, disabled=(not st.session_state.camera_running) or (not st.session_state.workout_running)):
            st.session_state.workout_paused = not st.session_state.workout_paused
    with col3:
        if st.button("운동 종료", use_container_width=True, disabled=(not st.session_state.camera_running) or (not st.session_state.workout_running)):
            st.session_state.workout_running = False
            st.session_state.workout_paused = False
            st.session_state.workout_started_ts = None
            posture_accuracy = st.session_state.squat_analyzer.posture_accuracy_percent()
            workout_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_workout_record(
                workout_date=workout_date,
                exercise_type="스쿼트",
                total_count=int(st.session_state.today_count),
                workout_seconds=float(st.session_state.workout_seconds),
                avg_posture_accuracy=float(posture_accuracy),
            )
            st.session_state.workout_history.insert(
                0,
                {
                    "date": workout_date,
                    "count": int(st.session_state.today_count),
                    "minutes": int(st.session_state.workout_seconds // 60),
                    "accuracy": float(posture_accuracy),
                },
            )
            if len(st.session_state.workout_history) > 5:
                st.session_state.workout_history = st.session_state.workout_history[:5]
            st.session_state.squat_analyzer.reset()
            st.session_state.today_count = 0
            st.session_state.workout_seconds = 0.0

    status_placeholder = st.empty()
    frame_placeholder = st.empty()
    metrics_placeholder = st.empty()
    coach_placeholder = st.empty()
    feedback_placeholder = st.empty()
    summary_placeholder = st.empty()
    voice_placeholder = st.empty()

    if st.session_state.camera_error:
        status_placeholder.error(st.session_state.camera_error)

    if st.session_state.camera_running:
        camera = st.session_state.get("camera")
        detector = st.session_state.get("pose_detector")
        if camera is None or detector is None:
            status_placeholder.error("카메라 또는 포즈 감지기가 준비되지 않았습니다.")
            stop_camera()
        else:
            while st.session_state.get("camera_running", False):
                try:
                    frame = camera.read_frame()
                    timestamp_ms = int(time.time() * 1000)
                    annotated_frame, detected, joint_data = detector.detect_and_draw(frame, timestamp_ms)
                    frame_placeholder.image(
                        cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB),
                        channels="RGB",
                        use_container_width=True,
                    )

                    if detected:
                        status_placeholder.success("관절 인식됨")
                    else:
                        status_placeholder.warning("사람이 화면 안에 없거나 인식이 불안정합니다.")

                    analyze_enabled = st.session_state.workout_running and not st.session_state.workout_paused
                    if analyze_enabled:
                        update_workout_timer()
                    result = st.session_state.squat_analyzer.update(joint_data, timestamp_ms, analyze_enabled)
                    st.session_state.today_count = int(result["count"])

                    angle_text = "-" if result["angle"] is None else f"{result['angle']:.1f}°"
                    trunk_text = "-" if result["trunk_tilt_deg"] is None else f"{result['trunk_tilt_deg']:.1f}°"
                    speed_text = "-" if result["speed_deg_per_sec"] is None else f"{result['speed_deg_per_sec']:.1f}°/s"
                    paused_text = " (일시정지)" if st.session_state.workout_paused else ""
                    state_label = "진행 중" if st.session_state.workout_running else "대기"
                    
                    # 현재 단계 이름 가져오기
                    phase_name = st.session_state.squat_analyzer._get_phase_name(result['phase'])
                    
                    # 단계별 색상 코드 적용
                    phase_color = "#1f9d55"  # 기본값: 녹색
                    if not result["posture_ok"]:
                        phase_color = "#dc3545"  # 빨강: 주의 필요
                    elif result["posture_status"] == "양호":
                        phase_color = "#1f9d55"  # 녹색: 양호
                    else:
                        phase_color = "#ffc107"  # 노랑: 참고
                    
                    metrics_placeholder.markdown(
                        f"""
                        **운동 상태:** {state_label}{paused_text}  
                        **현재 단계:** <span style="color:{phase_color}; font-weight:bold; font-size:1.2rem;">{phase_name}</span>  
                        **무릎 각도:** <span style="font-weight:bold;">{angle_text}</span> (목표: 70°~110°)  
                        **상체 기울기:** <span style="font-weight:bold;">{trunk_text}</span> (목표: 20°~30°)  
                        **스쿼트 깊이:** {result['depth_level']}  
                        **동작 속도:** {speed_text}  
                        **자세 상태:** <span style="color:{phase_color}; font-weight:bold;">{result['posture_status']}</span>  
                        **스쿼트 횟수:** <span style="font-size:2rem; font-weight:bold; color:{phase_color};">{result['count']}회</span>  
                        **운동 시간:** {int(st.session_state.workout_seconds // 60)}분 {int(st.session_state.workout_seconds % 60)}초
                        """,
                        unsafe_allow_html=True,
                    )

                    coaching_message = str(result["coaching_message"])
                    if bool(result["posture_ok"]):
                        coach_placeholder.markdown(
                            f"""
                            <div style="background:#e8f7ee;border:2px solid #1f9d55;border-radius:14px;padding:18px 20px;">
                                <div style="color:#157347;font-size:2rem;font-weight:800;line-height:1.3;">✅ {coaching_message}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        coach_placeholder.markdown(
                            f"""
                            <div style="background:#feecec;border:2px solid #dc3545;border-radius:14px;padding:18px 20px;">
                                <div style="color:#b42318;font-size:2rem;font-weight:800;line-height:1.3;">⚠ {coaching_message}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if result["feedback"]:
                        feedback_text = ""
                        for idx, msg in enumerate(result["feedback"], 1):
                            feedback_text += f"{idx}. {msg}\n"
                        
                        feedback_placeholder.markdown(
                            f"""
                            <div style="background:#fff3cd;border:2px solid #ffc107;border-radius:10px;padding:15px;margin:10px 0;">
                            <div style="font-weight:bold;color:#856404;margin-bottom:10px;">📋 자세 개선 사항</div>
                            <div style="color:#856404;line-height:1.6;">{feedback_text.replace(chr(10), '<br>')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        feedback_placeholder.markdown(
                            """
                            <div style="background:#e8f7ee;border:2px solid #1f9d55;border-radius:10px;padding:15px;margin:10px 0;">
                            <div style="color:#157347;font-weight:bold;">✅ 훌륭한 자세입니다!</div>
                            <div style="color:#157347;">현재 동작을 계속 유지해 주세요.</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    voice_text = ""
                    now_ts = time.time()
                    if bool(result["counted_this_frame"]):
                        voice_text = f"{int(result['count'])}회"
                    elif (not bool(result["posture_ok"])) and coaching_message:
                        last_voice_ts = float(st.session_state.get("last_voice_ts", 0.0))
                        last_voice_message = str(st.session_state.get("last_voice_message", ""))
                        if coaching_message != last_voice_message and (now_ts - last_voice_ts) >= 1.5:
                            voice_text = coaching_message

                    if voice_text:
                        st.session_state.last_voice_message = voice_text
                        st.session_state.last_voice_ts = now_ts
                        voice_payload = json.dumps(voice_text, ensure_ascii=False)
                        with voice_placeholder:
                            components.html(
                                f"""
                                <script>
                                  (function() {{
                                    const text = {voice_payload};
                                    if (!window.speechSynthesis || !text) return;
                                    window.speechSynthesis.cancel();
                                    const utt = new SpeechSynthesisUtterance(text);
                                    utt.lang = "ko-KR";
                                    utt.rate = 1.0;
                                    utt.pitch = 1.0;
                                    window.speechSynthesis.speak(utt);
                                  }})();
                                </script>
                                """,
                                height=0,
                            )

                    summary = result["summary"]
                    summary_placeholder.info(
                        "운동 요약: "
                        f"총 {summary['count']}회 | "
                        f"평균 무릎 각도 {summary.get('avg_knee_angle', 0.0):.1f}° | "
                        f"최근 자세 상태 {result['posture_status']}"
                    )

                    time.sleep(0.03)
                except CameraError as error:
                    status_placeholder.error(str(error))
                    stop_camera()
                    break
                except RuntimeError as error:
                    status_placeholder.error(str(error))
                    stop_camera()
                    break
    else:
        frame_placeholder.info("카메라가 꺼져 있습니다. 먼저 카메라를 시작해 주세요.")
        metrics_placeholder.info("운동 상태: 대기 | 현재 단계: 서 있는 상태 | 무릎 각도: - | 자세 상태: 대기 | 스쿼트 횟수: 0회")
        coach_placeholder.info("자세 안내: 운동을 시작하면 자세 교정 피드백이 크게 표시됩니다.")
        feedback_placeholder.info("자세 안내: 카메라를 시작하면 분석이 표시됩니다.")
        summary_placeholder.info("운동 요약: 총 0회 | 평균 무릎 각도 0.0° | 최근 자세 상태 대기")


def render_walk_page() -> None:
    st.title("AI 보행 분석")
    st.caption("🚶 실시간 카메라를 통해 걷기 동작을 분석합니다. (참고용 건강 정보입니다.)")

    # 카메라 제어 버튼
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("▶ 카메라 시작", use_container_width=True, disabled=st.session_state.camera_running):
            start_camera()
    with col2:
        if st.button("⏹ 카메라 종료", use_container_width=True, disabled=not st.session_state.camera_running):
            stop_camera()
    with col3:
        if st.button("▶ 보행 시작", use_container_width=True, disabled=not st.session_state.camera_running):
            st.session_state.walk_running = True
            st.session_state.walk_paused = False
            st.session_state.walk_started_ts = time.time()
            st.session_state.walk_analyzer.reset()
            st.session_state.today_steps = 0
            st.session_state.walk_seconds = 0.0
    with col4:
        if st.button("⏸ 일시정지", use_container_width=True, disabled=(not st.session_state.camera_running) or (not st.session_state.walk_running)):
            st.session_state.walk_paused = not st.session_state.walk_paused
    with col5:
        if st.button("⏹ 보행 종료", use_container_width=True, disabled=(not st.session_state.camera_running) or (not st.session_state.walk_running)):
            st.session_state.walk_running = False
            st.session_state.walk_paused = False
            st.session_state.walk_started_ts = None
            posture_accuracy = st.session_state.walk_analyzer.posture_accuracy_percent()
            walk_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_walk_record(
                walk_date=walk_date,
                duration_seconds=float(st.session_state.walk_seconds),
                total_steps=int(st.session_state.today_steps),
                cadence=float(st.session_state.walk_analyzer.cadence),
                avg_left_right_balance=float(st.session_state.walk_analyzer.left_right_balance),
                gait_symmetry=float(st.session_state.walk_analyzer.gait_symmetry),
                avg_posture_accuracy=float(posture_accuracy),
            )
            st.session_state.walk_history.insert(
                0,
                {
                    "date": walk_date,
                    "steps": int(st.session_state.today_steps),
                    "minutes": int(st.session_state.walk_seconds // 60),
                    "cadence": float(st.session_state.walk_analyzer.cadence),
                    "accuracy": float(posture_accuracy),
                    "balance": float(st.session_state.walk_analyzer.left_right_balance),
                    "symmetry": float(st.session_state.walk_analyzer.gait_symmetry),
                },
            )
            if len(st.session_state.walk_history) > 5:
                st.session_state.walk_history = st.session_state.walk_history[:5]
            st.session_state.walk_analyzer.reset()
            st.session_state.today_steps = 0
            st.session_state.walk_seconds = 0.0
            st.success("✅ 보행 기록이 저장되었습니다.")

    st.markdown("---")

    # 플레이스홀더 생성
    status_placeholder = st.empty()
    frame_placeholder = st.empty()
    
    # 메인 메트릭 행
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    metrics_placeholder = st.empty()
    coach_placeholder = st.empty()
    feedback_placeholder = st.empty()
    
    # 고급 분석 섹션
    with st.expander("🔍 상세 보행 분석", expanded=False):
        advanced_col1, advanced_col2, advanced_col3, advanced_col4 = st.columns(4)
        body_sway_placeholder = st.empty()
        leg_symmetry_placeholder = st.empty()
        posture_consistency_placeholder = st.empty()
        step_frequency_placeholder = st.empty()

    summary_placeholder = st.empty()
    voice_placeholder = st.empty()

    if st.session_state.camera_error:
        status_placeholder.error(f"❌ 카메라 오류: {st.session_state.camera_error}")

    if st.session_state.camera_running:
        camera = st.session_state.get("camera")
        detector = st.session_state.get("pose_detector")
        if camera is None or detector is None:
            status_placeholder.error("❌ 카메라 또는 포즈 감지기가 준비되지 않았습니다.")
            stop_camera()
        else:
            while st.session_state.get("camera_running", False):
                try:
                    frame = camera.read_frame()
                    timestamp_ms = int(time.time() * 1000)
                    annotated_frame, detected, joint_data = detector.detect_and_draw(frame, timestamp_ms)
                    frame_placeholder.image(
                        cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB),
                        channels="RGB",
                        use_container_width=True,
                    )

                    if detected:
                        status_placeholder.success("✅ 관절 인식 완료")
                    else:
                        status_placeholder.warning("⚠️ 전신이 카메라에 보이도록 위치를 조정해 주세요.")

                    analyze_enabled = st.session_state.walk_running and not st.session_state.walk_paused
                    if analyze_enabled:
                        update_walk_timer()
                    
                    result = st.session_state.walk_analyzer.update(joint_data, timestamp_ms, analyze_enabled)
                    st.session_state.today_steps = int(result["step_count"])

                    # 텍스트 포맷팅
                    cadence_text = "-" if result.get("cadence", 0) is None else f"{result.get('cadence', 0):.1f}"
                    balance_text = "-" if result.get("left_right_balance", 50) is None else f"{result.get('left_right_balance', 50):.1f}%"
                    symmetry_text = "-" if result.get("gait_symmetry", 0) is None else f"{result.get('gait_symmetry', 0):.1f}"
                    sway_text = "-" if result.get("body_sway", 0) is None else f"{result.get('body_sway', 0):.1f}"
                    leg_sym_text = "-" if result.get("leg_lift_symmetry", 0) is None else f"{result.get('leg_lift_symmetry', 0):.1f}"
                    consistency_text = "-" if result.get("posture_consistency", 0) is None else f"{result.get('posture_consistency', 0):.1f}"
                    
                    paused_text = " (일시정지)" if st.session_state.walk_paused else ""
                    state_label = "진행 중" if st.session_state.walk_running else "대기"

                    # 주요 메트릭 표시
                    with metrics_col1:
                        st.metric(
                            "걸음 수",
                            f"{result['step_count']}걸음",
                            delta=None if result['step_count'] == 0 else "계속 중..."
                        )
                    with metrics_col2:
                        st.metric(
                            "보행 시간",
                            f"{int(st.session_state.walk_seconds // 60)}분 {int(st.session_state.walk_seconds % 60)}초"
                        )
                    with metrics_col3:
                        st.metric(
                            "분당 걸음 수",
                            cadence_text if cadence_text != "-" else "-",
                            delta="걸음/분"
                        )
                    with metrics_col4:
                        st.metric(
                            "자세 상태",
                            result['posture_status']
                        )

                    # 상세 정보
                    metrics_placeholder.markdown(
                        f"""
                        **상태:** {state_label}{paused_text}  
                        **좌우 균형:** {balance_text} (좌발 사용률)  
                        **보행 대칭성:** {symmetry_text}/100  
                        **신뢰도:** {float(result.get('avg_confidence', 0)):.1f}%
                        """
                    )

                    # 상세 분석 (확장 가능 섹션)
                    with st.expander("🔍 상세 보행 분석", expanded=False):
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            st.metric("신체 흔들림", sway_text if sway_text != "-" else "안정적")
                        with col_b:
                            st.metric("다리 들기 대칭성", leg_sym_text if leg_sym_text != "-" else "-")
                        with col_c:
                            st.metric("자세 일관성", consistency_text if consistency_text != "-" else "-")
                        with col_d:
                            st.metric("보행 속도", f"{result.get('walking_speed', 0):.2f}걸음/초")

                    # 코칭 메시지
                    coaching_message = str(result.get("coaching_message", "자연스럽게 걸어주세요."))
                    if bool(result.get("posture_ok", False)):
                        coach_placeholder.markdown(
                            f"""
                            <div style="background:#e8f7ee;border:2px solid #1f9d55;border-radius:14px;padding:18px 20px;">
                                <div style="color:#157347;font-size:1.3rem;font-weight:800;line-height:1.3;">✅ {coaching_message}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        coach_placeholder.markdown(
                            f"""
                            <div style="background:#feecec;border:2px solid #dc3545;border-radius:14px;padding:18px 20px;">
                                <div style="color:#b42318;font-size:1.3rem;font-weight:800;line-height:1.3;">⚠️ {coaching_message}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    # 피드백
                    if result.get("feedback"):
                        feedback_placeholder.error("\n".join(f"- {message}" for message in result.get("feedback", [])))
                    else:
                        feedback_placeholder.success("✅ 좋은 보행 자세입니다. 계속 걸어주세요.")

                    # 요약
                    summary_placeholder.info(
                        f"📊 보행 요약: {result['step_count']}걸음 | "
                        f"케이던스 {cadence_text}걸음/분 | "
                        f"좌우 균형 {balance_text} | "
                        f"대칭성 {symmetry_text}/100 | "
                        f"상태 {result['posture_status']}"
                    )

                    time.sleep(0.03)
                except CameraError as error:
                    status_placeholder.error(f"❌ 카메라 오류: {str(error)}")
                    stop_camera()
                    break
                except RuntimeError as error:
                    status_placeholder.error(f"❌ 오류: {str(error)}")
                    stop_camera()
                    break
    else:
        frame_placeholder.info("📷 카메라가 꺼져 있습니다. 먼저 카메라를 시작해 주세요.")
        metrics_placeholder.info("대기 중입니다. 카메라를 시작한 후 보행을 시작해 주세요.")
        coach_placeholder.info("💡 팁: 카메라에서 1.5m ~ 2m 떨어져서 전신이 보이도록 위치하세요.")
        feedback_placeholder.info("조명이 충분한지 확인하고 카메라를 시작해 주세요.")
        summary_placeholder.info("보행 분석: 대기 중 | 걸음 수: 0 | 케이던스: - | 상태: 준비")


def render_workout_stats() -> None:
    st.title("운동 기록 및 통계")
    st.caption("저장된 운동 이력과 날짜별 변화를 확인합니다.")

    # 탭으로 스쿼트와 보행 기록을 분리
    tab_squat, tab_walk, tab_combined = st.tabs(["스쿼트", "보행", "통합"])

    with tab_squat:
        st.markdown("### 오늘의 스쿼트 통계")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("오늘의 운동 횟수", int(st.session_state.today_count))
        with col2:
            st.metric("오늘의 운동 시간", f"{int(st.session_state.workout_seconds // 60)}분")
        with col3:
            st.metric("목표 달성률", f"{st.session_state.goal_rate}%")

        st.markdown("### 저장된 스쿼트 기록")
        recent_records = load_recent_workout_records(limit=20)
        if recent_records:
            for item in recent_records:
                st.markdown(
                    f"- {item['workout_date']} | {item['exercise_type']} | "
                    f"{int(item['total_count'])}회 / {int(float(item['workout_seconds']) // 60)}분 / "
                    f"평균 자세 정확도 {float(item['avg_posture_accuracy']):.1f}%"
                )
        else:
            st.info("아직 기록이 없습니다. 스쿼트 운동을 진행하고 종료하면 자동 저장됩니다.")

        st.markdown("### 날짜별 운동 횟수 변화 추이")
        render_daily_trend_chart("날짜별 운동 횟수 추이")

    with tab_walk:
        st.markdown("### 오늘의 보행 통계")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("오늘의 걸음 수", int(st.session_state.today_steps))
        with col2:
            st.metric("오늘의 보행 시간", f"{int(st.session_state.walk_seconds // 60)}분")
        with col3:
            walk_goal_rate = 0 if st.session_state.walk_goal_target == 0 else min(100, int((st.session_state.today_steps / st.session_state.walk_goal_target) * 100))
            st.metric("목표 달성률", f"{walk_goal_rate}%")

        st.markdown("### 저장된 보행 기록")
        recent_walk_records = load_recent_walk_records(limit=20)
        if recent_walk_records:
            for item in recent_walk_records:
                st.markdown(
                    f"- {item['walk_date']} | "
                    f"{int(item['total_steps'])}걸음 / {int(float(item['duration_seconds']) // 60)}분 / "
                    f"케이던스 {float(item['cadence']):.1f}걸음/분 / "
                    f"좌우 균형 {float(item['avg_left_right_balance']):.1f}% / "
                    f"자세 정확도 {float(item['avg_posture_accuracy']):.1f}%"
                )
        else:
            st.info("아직 기록이 없습니다. 보행 분석을 진행하고 종료하면 자동 저장됩니다.")

        st.markdown("### 날짜별 보행 걸음 수 변화 추이")
        walk_trend_rows = load_daily_walk_trend(limit_days=30)
        if not walk_trend_rows:
            st.info("아직 저장된 보행 기록이 없습니다. 보행을 종료하면 날짜별 추이가 표시됩니다.")
        else:
            chart_data = [{"날짜": row["walk_day"], "걸음 수": int(row["total_steps"])} for row in walk_trend_rows]
            chart = (
                alt.Chart(alt.Data(values=chart_data))
                .mark_line(point=True, size=3)
                .encode(
                    x=alt.X("날짜:N", sort=None, title="날짜"),
                    y=alt.Y("걸음 수:Q", title="걸음 수"),
                    tooltip=["날짜:N", "걸음 수:Q"],
                )
                .properties(height=280, title="날짜별 보행 걸음 수 추이")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

    with tab_combined:
        st.markdown("### 오늘의 통합 활동 통계")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**스쿼트**")
            st.metric("운동 횟수", int(st.session_state.today_count))
            st.metric("운동 시간", f"{int(st.session_state.workout_seconds // 60)}분")
        with col2:
            st.markdown("**보행**")
            st.metric("걸음 수", int(st.session_state.today_steps))
            st.metric("보행 시간", f"{int(st.session_state.walk_seconds // 60)}분")

        st.markdown("### 최근 운동 활동")
        if st.session_state.workout_history or st.session_state.walk_history:
            col_squat, col_walk = st.columns(2)
            with col_squat:
                st.markdown("**최근 스쿼트 세션**")
                if st.session_state.workout_history:
                    for record in st.session_state.workout_history[:3]:
                        st.write(f"- {record['date']}: {record['count']}회, {record['minutes']}분, 자세정확도 {record['accuracy']:.1f}%")
                else:
                    st.info("스쿼트 운동 기록이 없습니다.")
            with col_walk:
                st.markdown("**최근 보행 세션**")
                if st.session_state.walk_history:
                    for record in st.session_state.walk_history[:3]:
                        st.write(f"- {record['date']}: {record['steps']}걸음, {record['minutes']}분, 케이던스 {record['cadence']:.1f}")
                else:
                    st.info("보행 분석 기록이 없습니다.")
        else:
            st.info("아직 운동 활동 기록이 없습니다.")



def render_lifestyle() -> None:
    st.title("생활 습관 관리")
    st.caption("생활 습관 정보와 웹캠 기반 바른 자세(거북목) 모니터링을 함께 제공합니다.")

    monitor_col1, monitor_col2 = st.columns(2)
    with monitor_col1:
        if st.button("자세 모니터링 시작", use_container_width=True, disabled=st.session_state.posture_monitoring):
            st.session_state.posture_monitoring = True
            st.session_state.posture_forward_started_ts = None
            if not st.session_state.camera_running:
                start_camera()
            if not st.session_state.camera_running:
                st.session_state.posture_monitoring = False
    with monitor_col2:
        if st.button("자세 모니터링 종료", use_container_width=True, disabled=not st.session_state.posture_monitoring):
            st.session_state.posture_monitoring = False
            st.session_state.posture_forward_started_ts = None
            stop_camera()

    posture_banner_placeholder = st.empty()
    posture_frame_placeholder = st.empty()
    posture_metrics_placeholder = st.empty()
    posture_audio_placeholder = st.empty()

    if st.session_state.camera_error:
        posture_banner_placeholder.error(st.session_state.camera_error)

    if st.session_state.posture_monitoring and st.session_state.camera_running:
        camera = st.session_state.get("camera")
        detector = st.session_state.get("pose_detector")
        if camera is None or detector is None:
            posture_banner_placeholder.error("카메라 또는 포즈 감지기가 준비되지 않았습니다.")
            stop_camera()
            st.session_state.posture_monitoring = False
        else:
            neck_forward_threshold_deg = 18.0
            hold_seconds_for_alert = 4.0
            alert_interval_seconds = 6.0
            while st.session_state.get("posture_monitoring", False) and st.session_state.get("camera_running", False):
                try:
                    frame = camera.read_frame()
                    timestamp_ms = int(time.time() * 1000)
                    annotated_frame, detected, joint_data = detector.detect_and_draw(frame, timestamp_ms)

                    if not detected:
                        posture_banner_placeholder.warning("사람이 화면 안에 없습니다. 정면 상반신이 보이도록 위치를 맞춰주세요.")
                        posture_metrics_placeholder.info("자세 지표를 계산하는 중입니다.")
                        st.session_state.posture_forward_started_ts = None
                    else:
                        posture_metrics = compute_posture_metrics(joint_data)
                        if posture_metrics is None:
                            posture_banner_placeholder.warning("귀와 어깨가 충분히 인식되지 않았습니다. 조명과 거리를 조정해 주세요.")
                            posture_metrics_placeholder.info("귀·어깨 인식 품질을 확인 중입니다.")
                            st.session_state.posture_forward_started_ts = None
                        else:
                            ear_mid = posture_metrics["ear_mid"]
                            shoulder_mid = posture_metrics["shoulder_mid"]
                            neck_angle = float(posture_metrics["neck_forward_angle_deg"])
                            shoulder_tilt = float(posture_metrics["shoulder_tilt_deg"])

                            cv2.circle(annotated_frame, (int(ear_mid[0]), int(ear_mid[1])), 8, (0, 0, 255), -1)
                            cv2.circle(annotated_frame, (int(shoulder_mid[0]), int(shoulder_mid[1])), 8, (255, 0, 0), -1)
                            cv2.line(
                                annotated_frame,
                                (int(ear_mid[0]), int(ear_mid[1])),
                                (int(shoulder_mid[0]), int(shoulder_mid[1])),
                                (0, 255, 255),
                                3,
                            )

                            now_ts = time.time()
                            if neck_angle >= neck_forward_threshold_deg:
                                if st.session_state.posture_forward_started_ts is None:
                                    st.session_state.posture_forward_started_ts = now_ts
                            else:
                                st.session_state.posture_forward_started_ts = None

                            forward_elapsed = 0.0
                            if st.session_state.posture_forward_started_ts is not None:
                                forward_elapsed = now_ts - float(st.session_state.posture_forward_started_ts)
                            warning_active = forward_elapsed >= hold_seconds_for_alert

                            if warning_active:
                                posture_banner_placeholder.markdown(
                                    """
                                    <div style="background:#ffebee;border:2px solid #dc3545;border-radius:12px;padding:14px 16px;">
                                        <div style="font-size:1.25rem;font-weight:800;color:#b42318;">
                                            ⚠ 거북목 경고: 목이 앞으로 나온 자세가 오래 유지되고 있습니다. 턱을 당기고 상체를 세워주세요.
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                last_alert_ts = float(st.session_state.get("posture_last_alert_ts", 0.0))
                                if (now_ts - last_alert_ts) >= alert_interval_seconds:
                                    play_alert_beep(
                                        posture_audio_placeholder,
                                        "거북목 자세 경고입니다. 턱을 당기고 상체를 세워주세요.",
                                    )
                                    st.session_state.posture_last_alert_ts = now_ts
                            else:
                                posture_banner_placeholder.markdown(
                                    """
                                    <div style="background:#e8f7ee;border:2px solid #1f9d55;border-radius:12px;padding:14px 16px;">
                                        <div style="font-size:1.1rem;font-weight:700;color:#157347;">
                                            ✅ 바른 자세 유지 중입니다. 어깨 힘을 빼고 목을 길게 유지해 주세요.
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                            posture_metrics_placeholder.markdown(
                                f"""
                                **목 전방 기울기(수직 기준):** {neck_angle:.1f}°  
                                **어깨 수평 기울기:** {shoulder_tilt:.1f}°  
                                **경고 임계값:** {neck_forward_threshold_deg:.1f}° 이상이 {hold_seconds_for_alert:.0f}초 이상 지속
                                """
                            )

                    posture_frame_placeholder.image(
                        cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB),
                        channels="RGB",
                        use_container_width=True,
                    )
                    time.sleep(0.03)
                except CameraError as error:
                    posture_banner_placeholder.error(str(error))
                    stop_camera()
                    st.session_state.posture_monitoring = False
                    break
                except RuntimeError as error:
                    posture_banner_placeholder.error(str(error))
                    stop_camera()
                    st.session_state.posture_monitoring = False
                    break
    else:
        posture_banner_placeholder.info("자세 모니터링을 시작하면 거북목 위험을 실시간으로 안내합니다.")
        posture_frame_placeholder.info("웹캠 미리보기 대기 중입니다.")
        posture_metrics_placeholder.info("목 전방 기울기와 어깨 수평 기울기를 측정합니다.")

    with st.form("habit_form"):
        hydration_ml = st.slider("오늘 물 섭취량 (ml)", 0, 3000, int(st.session_state.health_settings["hydration_ml"]), step=100)
        daily_steps = st.slider("하루 목표 걸음 수", 0, 20000, int(st.session_state.health_settings["daily_steps"]), step=500)
        sleep_hours = st.slider("수면 시간 (시간)", 4, 12, int(st.session_state.health_settings["sleep_hours"]), step=1)
        if st.form_submit_button("저장"):
            st.session_state.health_settings["hydration_ml"] = hydration_ml
            st.session_state.health_settings["daily_steps"] = daily_steps
            st.session_state.health_settings["sleep_hours"] = sleep_hours
            st.success("생활 습관 정보가 저장되었습니다.")

    st.markdown("### 현재 설정값")
    st.json(st.session_state.health_settings)


def render_safety() -> None:
    st.title("안전 관리")
    st.caption("카메라와 주변 환경을 점검해 안전하게 운동할 수 있도록 도와줍니다.")

    with st.form("safety_form"):
        camera_distance_ok = st.checkbox("카메라와 사용자 간 거리가 적절합니다.", value=st.session_state.safety_settings["camera_distance_ok"])
        lighting_ok = st.checkbox("조명이 충분하고 눈부심이 없습니다.", value=st.session_state.safety_settings["lighting_ok"])
        floor_stable = st.checkbox("운동 바닥이 안정적이고 미끄럽지 않습니다.", value=st.session_state.safety_settings["floor_stable"])
        note = st.text_area("안전 메모", value=st.session_state.safety_settings["safety_note"])
        if st.form_submit_button("저장"):
            st.session_state.safety_settings = {
                "camera_distance_ok": camera_distance_ok,
                "lighting_ok": lighting_ok,
                "floor_stable": floor_stable,
                "safety_note": note,
            }
            st.success("안전 설정이 저장되었습니다.")

    st.markdown("### 현재 점검 상태")
    st.json(st.session_state.safety_settings)


def render_settings() -> None:
    st.title("환경 설정")
    st.caption("카메라와 포즈 인식 환경을 조정합니다.")

    with st.form("system_settings"):
        camera_index = st.number_input("카메라 인덱스", min_value=0, max_value=5, value=int(st.session_state.settings["camera_index"]))
        detection_sensitivity = st.slider("포즈 감지 민감도", 0.40, 0.90, float(st.session_state.settings["detection_sensitivity"]), step=0.01)
        show_joint_labels = st.checkbox("관절 라벨 표시", value=bool(st.session_state.settings["show_joint_labels"]))
        show_guidance = st.checkbox("자세 안내 표시", value=bool(st.session_state.settings["show_guidance"]))
        video_recording = st.checkbox("영상 저장 기능 사용", value=bool(st.session_state.settings["video_recording"]))
        if st.form_submit_button("저장"):
            st.session_state.settings = {
                "camera_index": int(camera_index),
                "detection_sensitivity": float(detection_sensitivity),
                "show_joint_labels": bool(show_joint_labels),
                "show_guidance": bool(show_guidance),
                "video_recording": bool(video_recording),
            }
            st.success("환경 설정이 저장되었습니다.")

    st.markdown("### 현재 설정")
    st.json(st.session_state.settings)


def render_goal_management() -> None:
    """개인 운동 및 보행 목표 관리 페이지를 렌더링합니다."""
    st.title("개인 목표 관리")
    st.caption("일일 운동 및 보행 목표를 설정하고 달성률을 확인합니다.")

    goal_mgr = st.session_state.goal_manager

    # 목표 설정 섹션
    st.markdown("### 목표 설정")
    
    col_squat, col_walk = st.columns(2)
    
    with col_squat:
        st.markdown("**스쿼트 목표**")
        squat_goal = st.number_input(
            "일일 스쿼트 목표 (회)",
            min_value=0,
            max_value=500,
            value=int(st.session_state.goal_target),
            step=1
        )
        if st.button("스쿼트 목표 저장", use_container_width=True):
            if goal_mgr.set_goal("squat", squat_goal):
                st.session_state.goal_target = squat_goal
                st.success(f"스쿼트 목표가 {squat_goal}회로 설정되었습니다.")
            else:
                st.error("목표 설정에 실패했습니다.")

    with col_walk:
        st.markdown("**보행 목표**")
        walk_goal = st.number_input(
            "일일 보행 목표 (걸음)",
            min_value=0,
            max_value=50000,
            value=int(st.session_state.walk_goal_target),
            step=100
        )
        if st.button("보행 목표 저장", use_container_width=True):
            if goal_mgr.set_goal("walk", walk_goal):
                st.session_state.walk_goal_target = walk_goal
                st.success(f"보행 목표가 {walk_goal:,}걸음으로 설정되었습니다.")
            else:
                st.error("목표 설정에 실패했습니다.")

    st.markdown("---")

    # 주간/월간 달성률 섹션
    st.markdown("### 목표 달성 현황")
    
    summary_col_squat, summary_col_walk = st.columns(2)
    
    with summary_col_squat:
        st.markdown("**스쿼트 주간 현황**")
        weekly_squat = goal_mgr.get_weekly_summary("squat")
        if weekly_squat and weekly_squat["days_recorded"] > 0:
            st.metric("달성 일수", f"{weekly_squat['days_recorded']}일")
            st.metric("총 운동 횟수", f"{weekly_squat['total_achieved']}회")
            st.metric("평균 달성률", f"{weekly_squat['avg_achievement_rate']:.1f}%")
            st.caption(f"최고: {weekly_squat['best_day']}회, 최저: {weekly_squat['worst_day']}회")
        else:
            st.info("아직 기록이 없습니다.")

    with summary_col_walk:
        st.markdown("**보행 주간 현황**")
        weekly_walk = goal_mgr.get_weekly_summary("walk")
        if weekly_walk and weekly_walk["days_recorded"] > 0:
            st.metric("달성 일수", f"{weekly_walk['days_recorded']}일")
            st.metric("총 걸음 수", f"{weekly_walk['total_achieved']:,}걸음")
            st.metric("평균 달성률", f"{weekly_walk['avg_achievement_rate']:.1f}%")
            st.caption(f"최고: {weekly_walk['best_day']:,}걸음, 최저: {weekly_walk['worst_day']:,}걸음")
        else:
            st.info("아직 기록이 없습니다.")

    st.markdown("---")

    # 월간 현황
    st.markdown("### 월간 목표 달성 현황")
    
    monthly_col_squat, monthly_col_walk = st.columns(2)
    
    with monthly_col_squat:
        st.markdown("**스쿼트 월간 현황**")
        monthly_squat = goal_mgr.get_monthly_summary("squat")
        if monthly_squat and monthly_squat["days_recorded"] > 0:
            st.metric("기록된 일수", f"{monthly_squat['days_recorded']}일")
            st.metric("총 운동 횟수", f"{monthly_squat['total_achieved']}회")
            st.metric("목표 달성 일수", f"{monthly_squat['goal_achieved_days']}일")
            st.metric("평균 달성률", f"{monthly_squat['avg_achievement_rate']:.1f}%")
        else:
            st.info("아직 기록이 없습니다.")

    with monthly_col_walk:
        st.markdown("**보행 월간 현황**")
        monthly_walk = goal_mgr.get_monthly_summary("walk")
        if monthly_walk and monthly_walk["days_recorded"] > 0:
            st.metric("기록된 일수", f"{monthly_walk['days_recorded']}일")
            st.metric("총 걸음 수", f"{monthly_walk['total_achieved']:,}걸음")
            st.metric("목표 달성 일수", f"{monthly_walk['goal_achieved_days']}일")
            st.metric("평균 달성률", f"{monthly_walk['avg_achievement_rate']:.1f}%")
        else:
            st.info("아직 기록이 없습니다.")

    st.markdown("---")

    # 최근 달성 기록
    st.markdown("### 최근 달성 기록 (최근 30일)")
    
    record_type = st.radio("기록 유형", ["스쿼트", "보행"], horizontal=True)
    
    if record_type == "스쿼트":
        records = goal_mgr.get_achievement_history("squat", limit_days=30)
        if records:
            for record in records:
                cols = st.columns([2, 1, 1, 1])
                with cols[0]:
                    st.caption(record["goal_date"])
                with cols[1]:
                    st.caption(f"{record['achieved_value']}/{record['target_value']}회")
                with cols[2]:
                    st.caption(f"{record['achievement_rate']:.1f}%")
                with cols[3]:
                    status = "✓" if record['achievement_rate'] >= 100 else "·"
                    st.caption(status)
        else:
            st.info("아직 기록이 없습니다.")
    else:
        records = goal_mgr.get_achievement_history("walk", limit_days=30)
        if records:
            for record in records:
                cols = st.columns([2, 1.5, 1, 1])
                with cols[0]:
                    st.caption(record["goal_date"])
                with cols[1]:
                    st.caption(f"{record['achieved_value']:,}/{record['target_value']:,}걸음")
                with cols[2]:
                    st.caption(f"{record['achievement_rate']:.1f}%")
                with cols[3]:
                    status = "✓" if record['achievement_rate'] >= 100 else "·"
                    st.caption(status)
        else:
            st.info("아직 기록이 없습니다.")


def render_integrated_report() -> None:
    """통합 운동 및 보행 리포트를 렌더링합니다."""
    st.title("통합 건강 리포트")
    st.caption("스쿼트와 보행의 통합 통계 및 분석을 제공합니다.")

    analytics = st.session_state.analytics

    # 오늘의 요약
    st.markdown("### 오늘의 활동 요약")
    today_summary = analytics.get_today_summary()
    
    summary_cols = st.columns(4)
    
    with summary_cols[0]:
        st.metric("스쿼트 횟수", f"{today_summary['squat']['count']}회")
    with summary_cols[1]:
        st.metric("운동 시간", f"{today_summary['squat']['minutes']}분")
    with summary_cols[2]:
        st.metric("보행 걸음 수", f"{today_summary['walk']['steps']:,}걸음")
    with summary_cols[3]:
        st.metric("보행 시간", f"{today_summary['walk']['minutes']}분")

    st.markdown("---")

    # 주간 비교
    st.markdown("### 주간 활동 현황")
    
    weekly_summary = analytics.get_weekly_summary(days_back=7)
    
    week_col_squat, week_col_walk = st.columns(2)
    
    with week_col_squat:
        st.markdown("**스쿼트 주간 통계**")
        squat_data = weekly_summary["squat"]
        st.metric("운동 일수", f"{squat_data['workout_days']}일")
        st.metric("총 운동 횟수", f"{squat_data['total_count']}회")
        st.metric("일평균", f"{squat_data['avg_count']:.1f}회")
        st.metric("최고 기록", f"{squat_data['max_count']}회")
        st.metric("평균 자세 정확도", f"{squat_data['avg_accuracy']:.1f}%")

    with week_col_walk:
        st.markdown("**보행 주간 통계**")
        walk_data = weekly_summary["walk"]
        st.metric("운동 일수", f"{walk_data['walk_days']}일")
        st.metric("총 걸음 수", f"{walk_data['total_steps']:,}걸음")
        st.metric("일평균", f"{walk_data['avg_steps']:.0f}걸음")
        st.metric("최고 기록", f"{walk_data['max_steps']:,}걸음")
        st.metric("평균 케이던스", f"{walk_data['avg_cadence']:.1f}걸음/분")

    st.markdown("---")

    # 월간 비교
    st.markdown("### 월간 활동 현황")
    
    monthly_summary = analytics.get_monthly_summary(month_offset=0)
    
    month_col_squat, month_col_walk = st.columns(2)
    
    with month_col_squat:
        st.markdown(f"**스쿼트 {monthly_summary['period']}**")
        squat_month = monthly_summary["squat"]
        st.metric("운동 일수", f"{squat_month['workout_days']}일")
        st.metric("총 운동 횟수", f"{squat_month['total_count']}회")
        st.metric("일평균", f"{squat_month['avg_count']:.1f}회")

    with month_col_walk:
        st.markdown(f"**보행 {monthly_summary['period']}**")
        walk_month = monthly_summary["walk"]
        st.metric("운동 일수", f"{walk_month['walk_days']}일")
        st.metric("총 걸음 수", f"{walk_month['total_steps']:,}걸음")
        st.metric("일평균", f"{walk_month['avg_steps']:.0f}걸음")

    st.markdown("---")

    # 개인 최고 기록
    st.markdown("### 개인 최고 기록 (PR)")
    
    pr_col_squat, pr_col_walk = st.columns(2)
    
    with pr_col_squat:
        st.markdown("**스쿼트 최고 기록**")
        squat_pr = analytics.get_personal_best("squat")
        if squat_pr:
            st.metric("기록", f"{squat_pr['count']}회")
            st.caption(f"날짜: {squat_pr['date']}")
            st.caption(f"자세 정확도: {squat_pr['accuracy']:.1f}%")
        else:
            st.info("아직 기록이 없습니다.")

    with pr_col_walk:
        st.markdown("**보행 최고 기록**")
        walk_pr = analytics.get_personal_best("walk")
        if walk_pr:
            st.metric("기록", f"{walk_pr['steps']:,}걸음")
            st.caption(f"날짜: {walk_pr['date']}")
            st.caption(f"케이던스: {walk_pr['cadence']:.1f}걸음/분")
        else:
            st.info("아직 기록이 없습니다.")

    st.markdown("---")

    # 이전 기간과의 비교
    st.markdown("### 이전 주와의 비교")
    
    comp_col_squat, comp_col_walk = st.columns(2)
    
    with comp_col_squat:
        st.markdown("**스쿼트 비교**")
        squat_comp = analytics.get_comparison_vs_previous_period("squat", days=7)
        if squat_comp:
            change = squat_comp["change"]
            change_rate = squat_comp["change_rate"]
            if change >= 0:
                st.metric(
                    "이번주 vs 지난주",
                    f"{squat_comp['current_total']}회",
                    delta=f"+{change}회 (+{change_rate:.1f}%)"
                )
            else:
                st.metric(
                    "이번주 vs 지난주",
                    f"{squat_comp['current_total']}회",
                    delta=f"{change}회 ({change_rate:.1f}%)"
                )

    with comp_col_walk:
        st.markdown("**보행 비교**")
        walk_comp = analytics.get_comparison_vs_previous_period("walk", days=7)
        if walk_comp:
            change = walk_comp["change"]
            change_rate = walk_comp["change_rate"]
            if change >= 0:
                st.metric(
                    "이번주 vs 지난주",
                    f"{walk_comp['current_total']:,}걸음",
                    delta=f"+{change:,}걸음 (+{change_rate:.1f}%)"
                )
            else:
                st.metric(
                    "이번주 vs 지난주",
                    f"{walk_comp['current_total']:,}걸음",
                    delta=f"{change:,}걸음 ({change_rate:.1f}%)"
                )

    st.markdown("---")

    # 일일 추이 차트
    st.markdown("### 활동 추이 (최근 30일)")
    
    chart_type = st.radio("차트 유형", ["스쿼트", "보행"], horizontal=True)
    
    if chart_type == "스쿼트":
        squat_trend = analytics.get_daily_trend("squat", limit_days=30)
        if squat_trend:
            chart_data = [{"날짜": item["date"], "운동 횟수": item["count"]} for item in squat_trend]
            chart = (
                alt.Chart(alt.Data(values=chart_data))
                .mark_line(point=True, size=2)
                .encode(
                    x=alt.X("날짜:N", sort=None, title="날짜"),
                    y=alt.Y("운동 횟수:Q", title="운동 횟수"),
                    tooltip=["날짜:N", "운동 횟수:Q"],
                )
                .properties(height=300, title="스쿼트 운동 횟수 추이")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("아직 데이터가 없습니다.")
    else:
        walk_trend = analytics.get_daily_trend("walk", limit_days=30)
        if walk_trend:
            chart_data = [{"날짜": item["date"], "걸음 수": item["steps"]} for item in walk_trend]
            chart = (
                alt.Chart(alt.Data(values=chart_data))
                .mark_line(point=True, size=2)
                .encode(
                    x=alt.X("날짜:N", sort=None, title="날짜"),
                    y=alt.Y("걸음 수:Q", title="걸음 수"),
                    tooltip=["날짜:N", "걸음 수:Q"],
                )
                .properties(height=300, title="보행 걸음 수 추이")
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("아직 데이터가 없습니다.")


if selected == "🏠 홈 대시보드":
    render_home_dashboard()
elif selected == "🎥 AI 카메라 자세 분석":
    render_posture_analysis()
elif selected == "🤖 AI 맞춤 운동 추천":
    render_workout_recommendations()
elif selected == "📚 운동 종류별 탐색":
    render_exercise_browse()
elif selected == "📹 유튜브 운동 영상":
    render_youtube_videos()
elif selected == "💪 실시간 AI 운동 코칭":
    render_realtime_coaching()
elif selected == "🎯 운동 목표 관리":
    render_goal_management_new()
elif selected == "📊 운동 기록 및 통계":
    render_workout_stats()
elif selected == "📈 종합 건강 리포트":
    render_integrated_report()
else:
    render_settings()

st.markdown("---")
if st.sidebar.button("홈 대시보드로 돌아가기"):
    st.session_state.current_menu = "🏠 홈 대시보드"
    st.rerun()

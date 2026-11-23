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
        "current_menu": "홈 대시보드",
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


def render_daily_trend_chart(chart_title: str) -> None:
    trend_rows = load_daily_workout_trend(limit_days=30)
    if not trend_rows:
        st.info("아직 저장된 운동 기록이 없습니다. 운동을 종료하면 날짜별 추이가 표시됩니다.")
        return
    chart_data = [{"날짜": row["workout_day"], "운동 횟수": int(row["total_count"])} for row in trend_rows]
    chart = (
        alt.Chart(alt.Data(values=chart_data))
        .mark_line(point=True, strokeWidth=3)
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
    "홈 대시보드",
    "실시간 AI 관절 인식",
    "AI 스쿼트 자세 분석",
    "운동 기록 및 통계",
    "생활 습관 관리",
    "안전 관리",
    "환경 설정",
]
current_menu = st.session_state.get("current_menu", "홈 대시보드")
selected = st.sidebar.radio("메뉴", menu_options, index=menu_options.index(current_menu))
st.session_state.current_menu = selected

with st.sidebar:
    st.markdown("---")
    st.caption("현재 상태")
    st.info("실시간 카메라, 관절 인식, 스쿼트 분석 기능을 지원합니다.")


def render_home_dashboard() -> None:
    st.title("AI 스마트 케어메이트")
    st.subheader("스마트한 생활 습관과 운동 관리를 위한 AI 대시보드")

    goal_target = int(st.session_state.goal_target)
    goal_rate = 0 if goal_target == 0 else min(100, int((st.session_state.today_count / goal_target) * 100))
    st.session_state.goal_rate = goal_rate

    elapsed_minutes = int(st.session_state.workout_seconds // 60)
    state_text = "진행 중" if st.session_state.workout_running else "대기"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="kpi-box">
                <div class="small-label" style="color: rgba(255,255,255,0.8);">오늘의 운동 횟수</div>
                <div class="big-number">{int(st.session_state.today_count)}회</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="kpi-box">
                <div class="small-label" style="color: rgba(255,255,255,0.8);">오늘의 운동 시간</div>
                <div class="big-number">{elapsed_minutes}분</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="kpi-box">
                <div class="small-label" style="color: rgba(255,255,255,0.8);">목표 달성률</div>
                <div class="big-number">{goal_rate}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="kpi-box">
                <div class="small-label" style="color: rgba(255,255,255,0.8);">최근 상태</div>
                <div class="big-number">{state_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    left_col, right_col = st.columns([1.5, 1])
    with left_col:
        st.markdown("### 최근 운동 기록")
        recent_records = load_recent_workout_records(limit=5)
        if recent_records:
            for item in recent_records:
                workout_minutes = int(float(item["workout_seconds"]) // 60)
                st.markdown(
                    f"- {item['workout_date']} | {item['exercise_type']} | "
                    f"{int(item['total_count'])}회 | {workout_minutes}분 | "
                    f"평균 자세 정확도 {float(item['avg_posture_accuracy']):.1f}%"
                )
        else:
            st.markdown(
                """
                <div class="dashboard-card">
                    <p>아직 저장된 운동 기록이 없습니다.</p>
                    <p>카메라를 시작해 스쿼트 동작을 진행하면 기록이 자동으로 누적됩니다.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("### 날짜별 운동 횟수 추이")
        render_daily_trend_chart("최근 30일 운동 횟수 변화")
    with right_col:
        st.markdown("### 주요 기능 바로가기")
        if st.button("실시간 AI 관절 인식", use_container_width=True):
            st.session_state.current_menu = "실시간 AI 관절 인식"
            st.rerun()
        if st.button("AI 스쿼트 자세 분석", use_container_width=True):
            st.session_state.current_menu = "AI 스쿼트 자세 분석"
            st.rerun()

    st.caption("참고: 운동 기록은 이 세션의 참고용 데이터이며, 의료 진단이나 전문 재활 평가는 아닙니다.")


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
                    metrics_placeholder.markdown(
                        f"""
                        **운동 상태:** {state_label}{paused_text}  
                        **현재 단계:** {result['phase']}  
                        **무릎 각도:** {angle_text}  
                        **상체 기울기:** {trunk_text}  
                        **스쿼트 깊이:** {result['depth_level']}  
                        **동작 속도:** {speed_text}  
                        **자세 상태:** {result['posture_status']}  
                        **스쿼트 횟수:** {result['count']}회  
                        **운동 시간:** {int(st.session_state.workout_seconds // 60)}분 {int(st.session_state.workout_seconds % 60)}초
                        """
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
                        feedback_placeholder.error("\n".join(f"- {message}" for message in result["feedback"]))
                    else:
                        feedback_placeholder.success("좋은 자세입니다. 현재 동작을 유지하세요.")

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


def render_workout_stats() -> None:
    st.title("운동 기록 및 통계")
    st.caption("저장된 운동 이력과 날짜별 변화를 확인합니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("오늘의 운동 횟수", int(st.session_state.today_count))
    with col2:
        st.metric("오늘의 운동 시간", f"{int(st.session_state.workout_seconds // 60)}분")
    with col3:
        st.metric("목표 달성률", f"{st.session_state.goal_rate}%")

    st.markdown("### 저장된 운동 기록")
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


if selected == "홈 대시보드":
    render_home_dashboard()
elif selected == "실시간 AI 관절 인식":
    render_pose_page()
elif selected == "AI 스쿼트 자세 분석":
    render_squat_page()
elif selected == "운동 기록 및 통계":
    render_workout_stats()
elif selected == "생활 습관 관리":
    render_lifestyle()
elif selected == "안전 관리":
    render_safety()
else:
    render_settings()

st.markdown("---")
if st.sidebar.button("홈 대시보드로 돌아가기"):
    st.session_state.current_menu = "홈 대시보드"
    st.rerun()

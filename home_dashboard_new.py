"""홈 대시보드 모듈 - 맞춤형 건강 관리 대시보드를 렌더링합니다."""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("workout_history.db")


def get_today_date() -> str:
    """오늘 날짜를 문자열로 반환합니다."""
    return datetime.now().strftime("%Y-%m-%d")


def get_today_workout_stats() -> Dict[str, Any]:
    """
    오늘의 운동 통계를 조회합니다.
    
    Returns:
        운동 횟수, 시간, 목표 달성률, 최근 운동 등을 포함한 딕셔너리
    """
    today = get_today_date()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    try:
        # 스쿼트 통계
        c.execute("""
            SELECT COUNT(*) as count, SUM(workout_seconds) as total_seconds
            FROM workout_records
            WHERE DATE(workout_date) = ?
        """, (today,))
        squat_row = c.fetchone()
        squat_count = squat_row[0] if squat_row else 0
        squat_seconds = squat_row[1] if squat_row and squat_row[1] else 0
        
        # 보행 통계
        c.execute("""
            SELECT COUNT(*) as count, SUM(duration_seconds) as total_seconds
            FROM walk_records
            WHERE DATE(walk_date) = ?
        """, (today,))
        walk_row = c.fetchone()
        walk_count = walk_row[0] if walk_row else 0
        walk_seconds = walk_row[1] if walk_row and walk_row[1] else 0
        
        # 최근 운동 기록 (최근 1개)
        c.execute("""
            SELECT exercise_type, total_count, workout_seconds, avg_posture_accuracy
            FROM workout_records
            WHERE DATE(workout_date) = ?
            ORDER BY workout_date DESC, id DESC
            LIMIT 1
        """, (today,))
        squat_record = c.fetchone()
        
        c.execute("""
            SELECT total_steps, duration_seconds, cadence, avg_posture_accuracy
            FROM walk_records
            WHERE DATE(walk_date) = ?
            ORDER BY walk_date DESC, id DESC
            LIMIT 1
        """, (today,))
        walk_record = c.fetchone()
        
        # 오늘 목표
        goal_target = st.session_state.get("goal_target", 20)
        walk_goal_target = st.session_state.get("walk_goal_target", 5000)
        
        squat_goal_rate = 0 if goal_target == 0 else min(100, int((squat_count / goal_target) * 100))
        walk_goal_rate = 0 if walk_goal_target == 0 else min(100, int((walk_count / walk_goal_target) * 100))
        
        return {
            "squat_count": squat_count,
            "squat_seconds": squat_seconds,
            "squat_minutes": int(squat_seconds // 60),
            "squat_goal_rate": squat_goal_rate,
            "walk_count": walk_count,
            "walk_steps": walk_count,  # 보행의 경우 count를 steps로 사용
            "walk_seconds": walk_seconds,
            "walk_minutes": int(walk_seconds // 60),
            "walk_goal_rate": walk_goal_rate,
            "total_minutes": int((squat_seconds + walk_seconds) // 60),
            "latest_squat": squat_record,
            "latest_walk": walk_record,
        }
    except Exception as e:
        import traceback
        st.warning(f"운동 통계 조회 오류: {str(e)}\n경로: {DB_PATH}\n{traceback.format_exc()}")
        return {
            "squat_count": 0,
            "squat_seconds": 0,
            "squat_minutes": 0,
            "squat_goal_rate": 0,
            "walk_count": 0,
            "walk_steps": 0,
            "walk_seconds": 0,
            "walk_minutes": 0,
            "walk_goal_rate": 0,
            "total_minutes": 0,
            "latest_squat": None,
            "latest_walk": None,
        }
    finally:
        conn.close()


def get_weekly_workout_summary() -> Dict[str, int]:
    """
    지난 7일간의 운동 요약을 조회합니다.
    
    Returns:
        날짜별 운동 횟수 딕셔너리
    """
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    try:
        weekly_data = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            
            c.execute("""
                SELECT COUNT(*) as count
                FROM workout_records
                WHERE DATE(workout_date) = ?
            """, (date,))
            squat_result = c.fetchone()
            squat_count = squat_result[0] if squat_result else 0
            
            c.execute("""
                SELECT COUNT(*) as count
                FROM walk_records
                WHERE DATE(walk_date) = ?
            """, (date,))
            walk_result = c.fetchone()
            walk_count = walk_result[0] if walk_result else 0
            
            weekly_data[date[:5]] = squat_count + walk_count
        
        return dict(reversed(weekly_data.items()))
    except Exception:
        return {}
    finally:
        conn.close()


def render_header_section() -> None:
    """대시보드 헤더 섹션을 렌더링합니다."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🩺 AI 스마트 케어메이트</h1>
        <h2 style="font-size: 1.5rem; color: #0a74ff; margin-bottom: 0.5rem;">🎯 오늘의 맞춤 운동</h2>
        <p style="font-size: 1.1rem; color: #666; margin-bottom: 0;">나에게 맞는 운동을 시작해 보세요!</p>
    </div>
    """, unsafe_allow_html=True)


def render_exercise_card(
    exercise_name: str,
    category: str,
    icon: str,
    difficulty: str,
    duration: str,
    description: str
) -> None:
    """
    운동 추천 카드를 렌더링합니다.
    
    Args:
        exercise_name: 운동 이름
        category: 운동 카테고리
        icon: 운동 아이콘
        difficulty: 난이도
        duration: 예상 시간
        description: 운동 설명
    """
    difficulty_emoji = {
        "초보자": "⭐",
        "중급자": "⭐⭐",
        "고급자": "⭐⭐⭐"
    }.get(difficulty, "⭐")
    
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        border: 1px solid #d0deff;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(10, 116, 255, 0.1);
    " class="exercise-card" onclick="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 16px rgba(10, 116, 255, 0.2)';">
        <div style="display: flex; align-items: flex-start; justify-content: space-between;">
            <div>
                <h3 style="font-size: 1.3rem; margin: 0 0 0.3rem 0; color: #0a74ff;">
                    {icon} {exercise_name}
                </h3>
                <p style="font-size: 0.85rem; color: #666; margin: 0.2rem 0;">
                    {category}
                </p>
                <p style="font-size: 0.9rem; color: #333; margin: 0.4rem 0 0 0; line-height: 1.4;">
                    {description}
                </p>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid #e0e8ff;">
            <div style="font-size: 0.85rem;">
                <span style="color: #666;">난이도: </span>
                <span style="color: #0a74ff; font-weight: 600;">{difficulty_emoji}</span>
            </div>
            <div style="font-size: 0.85rem; color: #666;">
                예상 시간: <strong>{duration}</strong>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_exercise_cards_section() -> None:
    """맞춤 운동 추천 카드 섹션을 렌더링합니다."""
    st.markdown("""
    <div style="margin: 2rem 0 1.5rem 0;">
        <h2 style="font-size: 1.3rem; color: #333; margin-bottom: 0.5rem;">💪 맞춤 운동 추천</h2>
        <p style="color: #666; margin: 0;">당신의 체력 수준과 목표에 맞는 최적의 운동들입니다</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 4개 운동 카드를 2x2 그리드로 표시
    col1, col2 = st.columns(2)
    
    exercises = [
        {
            "exercise_name": "스쿼트",
            "category": "하체 운동",
            "icon": "🏋️",
            "difficulty": "초보자",
            "duration": "10-20분",
            "description": "두 다리의 근력을 강화하는 기본 운동입니다."
        },
        {
            "exercise_name": "스트레칭",
            "category": "유연성 운동",
            "icon": "🧘",
            "difficulty": "초보자",
            "duration": "10-15분",
            "description": "근육의 경직을 완화하고 유연성을 높입니다."
        },
        {
            "exercise_name": "산책 & 걷기",
            "category": "보행 운동",
            "icon": "🚶",
            "difficulty": "초보자",
            "duration": "20-40분",
            "description": "관절에 부담 적은 유산소 운동입니다."
        },
        {
            "exercise_name": "홈트레이닝",
            "category": "전신 운동",
            "icon": "💪",
            "difficulty": "중급자",
            "duration": "15-30분",
            "description": "집에서 할 수 있는 다양한 전신 운동입니다."
        }
    ]
    
    for idx, exercise in enumerate(exercises):
        col = col1 if idx % 2 == 0 else col2
        with col:
            render_exercise_card(**exercise)


def render_youtube_video_card(
    title: str,
    thumbnail_url: str,
    channel: str,
    duration: str,
    difficulty: str,
    video_id: str
) -> None:
    """
    유튜브 영상 카드를 렌더링합니다.
    
    Args:
        title: 영상 제목
        thumbnail_url: 썸네일 URL
        channel: 채널명
        duration: 영상 길이
        difficulty: 난이도
        video_id: 유튜브 비디오 ID
    """
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    
    card_html = f"""
    <div style="
        background: white;
        border: 1px solid #d0deff;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(10, 116, 255, 0.1);
        transition: all 0.3s ease;
    " class="video-card">
        <div style="
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            background: #f0f0f0;
            overflow: hidden;
        ">
            <img src="{thumbnail_url}" alt="{title}" style="
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
            ">
            <div style="
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 2.5rem;
            ">
                ▶️
            </div>
        </div>
        <div style="padding: 1rem;">
            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.95rem; color: #333; line-height: 1.3;">
                {title}
            </h4>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #666; margin-bottom: 0.5rem;">
                <span>{channel}</span>
                <span>{duration}</span>
            </div>
            <div style="display: flex; gap: 0.5rem; margin-top: 0.8rem;">
                <a href="{watch_url}" target="_blank" style="
                    flex: 1;
                    display: inline-block;
                    background: #0a74ff;
                    color: white;
                    text-align: center;
                    padding: 0.5rem;
                    border-radius: 6px;
                    text-decoration: none;
                    font-size: 0.85rem;
                    font-weight: 600;
                    transition: background 0.3s;
                " onmouseover="this.style.background='#0657d8'" onmouseout="this.style.background='#0a74ff'">
                    유튜브에서 보기
                </a>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_youtube_videos_section() -> None:
    """추천 유튜브 영상 섹션을 렌더링합니다."""
    st.markdown("""
    <div style="margin: 2rem 0 1.5rem 0;">
        <h2 style="font-size: 1.3rem; color: #333; margin-bottom: 0.5rem;">📹 추천 운동 영상</h2>
        <p style="color: #666; margin: 0;">전문가의 가이드를 따라 올바르게 운동해 보세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 4개 영상을 2x2 그리드로 표시
    col1, col2 = st.columns(2)
    
    videos = [
        {
            "title": "올바른 스쿼트 자세 배우기 (초보자 가이드)",
            "thumbnail_url": "https://i.ytimg.com/vi/ZWUBHd6ysMU/hqdefault.jpg",
            "channel": "피지컬갤러리",
            "duration": "8분",
            "difficulty": "초보자",
            "video_id": "ZWUBHd6ysMU"
        },
        {
            "title": "일상적인 스트레칭 루틴 10분",
            "thumbnail_url": "https://i.ytimg.com/vi/0Feo-Bx_cJo/hqdefault.jpg",
            "channel": "핏투게더",
            "duration": "10분",
            "difficulty": "초보자",
            "video_id": "0Feo-Bx_cJo"
        },
        {
            "title": "올바른 걷기 운동법",
            "thumbnail_url": "https://i.ytimg.com/vi/V-1Yq8_1Hyk/hqdefault.jpg",
            "channel": "건강한생활",
            "duration": "5분",
            "difficulty": "초보자",
            "video_id": "V-1Yq8_1Hyk"
        },
        {
            "title": "초보자를 위한 홈 운동 15분",
            "thumbnail_url": "https://i.ytimg.com/vi/xHJdqKb-qVo/hqdefault.jpg",
            "channel": "홈트레이닝TV",
            "duration": "15분",
            "difficulty": "초보자",
            "video_id": "xHJdqKb-qVo"
        }
    ]
    
    for idx, video in enumerate(videos):
        col = col1 if idx % 2 == 0 else col2
        with col:
            render_youtube_video_card(**video)


def render_stats_section() -> None:
    """나의 운동 관리 통계 섹션을 렌더링합니다."""
    stats = get_today_workout_stats()
    
    st.markdown("""
    <div style="margin: 2rem 0 1.5rem 0;">
        <h2 style="font-size: 1.3rem; color: #333; margin-bottom: 1rem;">📊 나의 운동 관리</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 오늘의 운동 통계 (4개 KPI)
    col1, col2, col3, col4 = st.columns(4)
    
    kpis = [
        {
            "col": col1,
            "label": "오늘의 운동 횟수",
            "value": f"{stats['squat_count'] + stats['walk_count']}회",
            "icon": "🏃"
        },
        {
            "col": col2,
            "label": "누적 운동 시간",
            "value": f"{stats['total_minutes']}분",
            "icon": "⏱️"
        },
        {
            "col": col3,
            "label": "운동 목표 달성률",
            "value": f"{max(stats['squat_goal_rate'], stats['walk_goal_rate'])}%",
            "icon": "🎯"
        },
        {
            "col": col4,
            "label": "최근 운동",
            "value": "스쿼트" if stats['latest_squat'] else "없음",
            "icon": "✅"
        }
    ]
    
    for kpi in kpis:
        with kpi["col"]:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #0a74ff 0%, #4da3ff 100%);
                color: white;
                border-radius: 12px;
                padding: 1.2rem;
                text-align: center;
                box-shadow: 0 4px 12px rgba(10, 116, 255, 0.2);
            ">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{kpi['icon']}</div>
                <div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.9); margin-bottom: 0.5rem;">
                    {kpi['label']}
                </div>
                <div style="font-size: 1.8rem; font-weight: 700;">
                    {kpi['value']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 주간 운동 통계
    weekly_stats = get_weekly_workout_summary()
    
    st.markdown("""
    <div style="background: white; border: 1px solid #d0deff; border-radius: 12px; padding: 1.5rem;">
        <h3 style="margin-top: 0; font-size: 1rem; color: #333;">📅 주간 운동 통계</h3>
    """, unsafe_allow_html=True)
    
    # 주간 차트
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    days = ['월', '화', '수', '목', '금', '토', '일']
    dates_list = [(datetime.now() - timedelta(days=6-i)).strftime("%m-%d") for i in range(7)]
    
    for idx, (col, day, date) in enumerate(zip([col1, col2, col3, col4, col5, col6, col7], days, dates_list)):
        with col:
            count = weekly_stats.get(date, 0)
            fill_percent = min(100, (count / 10) * 100) if count > 0 else 0
            
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="
                    background: white;
                    border: 1px solid #d0deff;
                    border-radius: 8px;
                    padding: 0.8rem 0.4rem;
                    margin-bottom: 0.5rem;
                    min-height: 60px;
                    display: flex;
                    flex-direction: column;
                    justify-content: flex-end;
                    position: relative;
                    overflow: hidden;
                ">
                    <div style="
                        position: absolute;
                        bottom: 0;
                        left: 0;
                        width: 100%;
                        height: {fill_percent}%;
                        background: linear-gradient(180deg, #0a74ff 0%, #4da3ff 100%);
                        opacity: 0.3;
                    "></div>
                    <div style="position: relative; z-index: 1; font-weight: 700; color: #0a74ff;">
                        {count}
                    </div>
                </div>
                <div style="font-size: 0.75rem; color: #666; font-weight: 600;">{day}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 운동 목표
    st.markdown("""
    <div style="background: white; border: 1px solid #d0deff; border-radius: 12px; padding: 1.5rem;">
        <h3 style="margin-top: 0; font-size: 1rem; color: #333;">🎯 운동 목표</h3>
    """, unsafe_allow_html=True)
    
    goal_target = st.session_state.get("goal_target", 20)
    squat_count = stats['squat_count']
    squat_goal_rate = stats['squat_goal_rate']
    
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: #333; font-weight: 600;">스쿼트 목표</span>
            <span style="color: #0a74ff; font-weight: 700;">{squat_count} / {goal_target}회</span>
        </div>
        <div style="
            width: 100%;
            height: 8px;
            background: #e8f1ff;
            border-radius: 4px;
            overflow: hidden;
        ">
            <div style="
                width: {squat_goal_rate}%;
                height: 100%;
                background: linear-gradient(90deg, #0a74ff 0%, #4da3ff 100%);
                transition: width 0.3s ease;
            "></div>
        </div>
        <div style="text-align: right; font-size: 0.8rem; color: #666; margin-top: 0.3rem;">
            {squat_goal_rate}% 달성
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    walk_goal_target = st.session_state.get("walk_goal_target", 5000)
    walk_count = stats['walk_count']
    walk_goal_rate = stats['walk_goal_rate']
    
    st.markdown(f"""
    <div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: #333; font-weight: 600;">보행 목표</span>
            <span style="color: #0a74ff; font-weight: 700;">{walk_count} / {walk_goal_target}걸음</span>
        </div>
        <div style="
            width: 100%;
            height: 8px;
            background: #e8f1ff;
            border-radius: 4px;
            overflow: hidden;
        ">
            <div style="
                width: {walk_goal_rate}%;
                height: 100%;
                background: linear-gradient(90deg, #4da3ff 0%, #0a74ff 100%);
                transition: width 0.3s ease;
            "></div>
        </div>
        <div style="text-align: right; font-size: 0.8rem; color: #666; margin-top: 0.3rem;">
            {walk_goal_rate}% 달성
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_new_home_dashboard() -> None:
    """
    새로운 홈 대시보드를 렌더링합니다.
    맞춤 운동 추천, 유튜브 영상, 운동 통계를 한눈에 볼 수 있습니다.
    """
    # 헤더 섹션
    render_header_section()
    
    st.markdown("---")
    
    # 맞춤 운동 추천 카드 섹션
    render_exercise_cards_section()
    
    st.markdown("---")
    
    # 유튜브 영상 섹션
    render_youtube_videos_section()
    
    st.markdown("---")
    
    # 운동 관리 통계 섹션
    render_stats_section()
    
    st.markdown("""
    <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid #e0e8ff; text-align: center; color: #999; font-size: 0.85rem;">
        💡 팁: 왼쪽 사이드바 메뉴에서 운동별 상세 정보, 실시간 AI 코칭, 운동 기록을 확인할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

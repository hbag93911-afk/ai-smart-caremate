"""건강 추적 모듈 - 사용자의 운동 목표와 건강 지표를 추적합니다."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_PATH = Path(__file__).with_name("workout_history.db")


class HealthTracker:
    """사용자의 건강 지표와 운동 목표를 추적합니다."""

    def __init__(self):
        """HealthTracker를 초기화합니다."""
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """필요한 테이블을 생성합니다."""
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            # 운동별 세션 기록 테이블
            c.execute(
                """CREATE TABLE IF NOT EXISTS exercise_sessions (
                    id INTEGER PRIMARY KEY,
                    exercise_name TEXT,
                    session_date TIMESTAMP,
                    duration_seconds INTEGER,
                    repetitions INTEGER,
                    sets INTEGER,
                    posture_score FLOAT,
                    notes TEXT
                )"""
            )

            # 종합 건강 지표 테이블
            c.execute(
                """CREATE TABLE IF NOT EXISTS health_metrics (
                    id INTEGER PRIMARY KEY,
                    date DATE,
                    total_exercise_minutes INTEGER,
                    exercise_variety INTEGER,
                    consistency_score FLOAT,
                    overall_posture_score FLOAT
                )"""
            )

            # 개별 운동 목표 테이블
            c.execute(
                """CREATE TABLE IF NOT EXISTS exercise_goals (
                    id INTEGER PRIMARY KEY,
                    exercise_name TEXT UNIQUE,
                    target_frequency_per_week INTEGER,
                    target_duration_minutes INTEGER,
                    start_date DATE,
                    notes TEXT
                )"""
            )

            conn.commit()
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()

    def record_exercise_session(
        self,
        exercise_name: str,
        duration_seconds: int,
        repetitions: int = 0,
        sets: int = 0,
        posture_score: float = 0.0,
        notes: str = ""
    ) -> bool:
        """
        운동 세션을 기록합니다.
        
        Args:
            exercise_name: 운동 이름
            duration_seconds: 운동 시간 (초)
            repetitions: 반복 횟수
            sets: 세트 수
            posture_score: 자세 점수 (0-100)
            notes: 추가 메모
            
        Returns:
            성공 여부
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """INSERT INTO exercise_sessions
                   (exercise_name, session_date, duration_seconds, repetitions, sets, posture_score, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    exercise_name,
                    datetime.now(),
                    duration_seconds,
                    repetitions,
                    sets,
                    posture_score,
                    notes,
                )
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error recording exercise session: {e}")
            return False
        finally:
            conn.close()

    def get_exercise_history(
        self,
        exercise_name: str,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        특정 운동의 최근 기록을 조회합니다.
        
        Args:
            exercise_name: 운동 이름
            days_back: 최근 며칠간의 데이터
            
        Returns:
            운동 기록 목록
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        try:
            c.execute(
                """SELECT session_date, duration_seconds, repetitions, sets, posture_score, notes
                   FROM exercise_sessions
                   WHERE exercise_name = ? AND session_date >= ?
                   ORDER BY session_date DESC""",
                (exercise_name, cutoff_date)
            )
            rows = c.fetchall()
            return [
                {
                    "date": row[0],
                    "duration_seconds": row[1],
                    "repetitions": row[2],
                    "sets": row[3],
                    "posture_score": row[4],
                    "notes": row[5],
                }
                for row in rows
            ]
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()

    def set_exercise_goal(
        self,
        exercise_name: str,
        target_frequency_per_week: int,
        target_duration_minutes: int,
        notes: str = ""
    ) -> bool:
        """
        특정 운동의 목표를 설정합니다.
        
        Args:
            exercise_name: 운동 이름
            target_frequency_per_week: 주간 목표 빈도
            target_duration_minutes: 목표 소요 시간 (분)
            notes: 메모
            
        Returns:
            성공 여부
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """INSERT OR REPLACE INTO exercise_goals
                   (exercise_name, target_frequency_per_week, target_duration_minutes, start_date, notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    exercise_name,
                    target_frequency_per_week,
                    target_duration_minutes,
                    datetime.now().strftime("%Y-%m-%d"),
                    notes,
                )
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error setting exercise goal: {e}")
            return False
        finally:
            conn.close()

    def get_exercise_goal(self, exercise_name: str) -> Optional[Dict[str, Any]]:
        """
        특정 운동의 목표를 조회합니다.
        
        Args:
            exercise_name: 운동 이름
            
        Returns:
            목표 정보 또는 None
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """SELECT target_frequency_per_week, target_duration_minutes, start_date, notes
                   FROM exercise_goals
                   WHERE exercise_name = ?""",
                (exercise_name,)
            )
            row = c.fetchone()
            if row:
                return {
                    "exercise": exercise_name,
                    "target_frequency_per_week": row[0],
                    "target_duration_minutes": row[1],
                    "start_date": row[2],
                    "notes": row[3],
                }
            return None
        except sqlite3.OperationalError:
            return None
        finally:
            conn.close()

    def get_weekly_progress(
        self,
        exercise_name: str,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        특정 운동의 주간 진행도를 계산합니다.
        
        Args:
            exercise_name: 운동 이름
            days_back: 최근 며칠
            
        Returns:
            주간 진행도 정보
        """
        history = self.get_exercise_history(exercise_name, days_back)
        goal = self.get_exercise_goal(exercise_name)

        total_sessions = len(history)
        total_duration = sum(h["duration_seconds"] for h in history) / 60  # 분 단위
        total_repetitions = sum(h["repetitions"] for h in history)
        avg_posture = sum(h["posture_score"] for h in history) / len(history) if history else 0

        progress = {
            "exercise_name": exercise_name,
            "period_days": days_back,
            "sessions_completed": total_sessions,
            "total_duration_minutes": int(total_duration),
            "total_repetitions": total_repetitions,
            "avg_posture_score": round(avg_posture, 2),
        }

        if goal:
            target_sessions = goal["target_frequency_per_week"] * (days_back / 7)
            target_duration = goal["target_duration_minutes"] * (days_back / 7)
            
            progress["target_sessions"] = int(target_sessions)
            progress["session_achievement_rate"] = round(
                (total_sessions / target_sessions * 100) if target_sessions > 0 else 0, 1
            )
            progress["target_duration_minutes"] = int(target_duration)
            progress["duration_achievement_rate"] = round(
                (total_duration / target_duration * 100) if target_duration > 0 else 0, 1
            )

        return progress

    def get_overall_health_metrics(self, days_back: int = 30) -> Dict[str, Any]:
        """
        종합 건강 지표를 계산합니다.
        
        Args:
            days_back: 최근 며칠
            
        Returns:
            종합 건강 지표
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        try:
            # 전체 운동 시간
            c.execute(
                """SELECT SUM(duration_seconds)
                   FROM exercise_sessions
                   WHERE session_date >= ?""",
                (cutoff_date,)
            )
            total_seconds = c.fetchone()[0] or 0
            total_minutes = int(total_seconds / 60)

            # 운동 종류 수
            c.execute(
                """SELECT COUNT(DISTINCT exercise_name)
                   FROM exercise_sessions
                   WHERE session_date >= ?""",
                (cutoff_date,)
            )
            exercise_variety = c.fetchone()[0] or 0

            # 평균 자세 점수
            c.execute(
                """SELECT AVG(posture_score)
                   FROM exercise_sessions
                   WHERE session_date >= ? AND posture_score > 0""",
                (cutoff_date,)
            )
            avg_posture = c.fetchone()[0] or 0

            # 운동 일수 (스쿼트 + 보행)
            c.execute(
                """SELECT COUNT(DISTINCT DATE(workout_date))
                   FROM workout_records
                   WHERE workout_date >= ?""",
                (cutoff_date,)
            )
            squat_days = c.fetchone()[0] or 0

            c.execute(
                """SELECT COUNT(DISTINCT DATE(walk_date))
                   FROM walk_records
                   WHERE walk_date >= ?""",
                (cutoff_date,)
            )
            walk_days = c.fetchone()[0] or 0

            total_exercise_days = squat_days + walk_days

            # 일관성 점수 (기존 운동 기록 기반)
            consistency_score = min(100, (total_exercise_days / days_back * 100))

            return {
                "period_days": days_back,
                "total_exercise_minutes": total_minutes,
                "exercise_variety": exercise_variety,
                "avg_posture_score": round(avg_posture, 2),
                "total_exercise_days": total_exercise_days,
                "consistency_score": round(consistency_score, 1),
            }
        except sqlite3.OperationalError:
            return {
                "period_days": days_back,
                "total_exercise_minutes": 0,
                "exercise_variety": 0,
                "avg_posture_score": 0,
                "total_exercise_days": 0,
                "consistency_score": 0,
            }
        finally:
            conn.close()

    def get_exercise_trends(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        각 운동별 최근 추세를 계산합니다.
        
        Args:
            days_back: 최근 며칠
            
        Returns:
            운동별 추세 정보 목록
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        try:
            c.execute(
                """SELECT exercise_name, COUNT(*) as sessions, 
                          SUM(duration_seconds) as total_seconds,
                          SUM(repetitions) as total_reps,
                          AVG(posture_score) as avg_score
                   FROM exercise_sessions
                   WHERE session_date >= ?
                   GROUP BY exercise_name
                   ORDER BY sessions DESC""",
                (cutoff_date,)
            )
            rows = c.fetchall()
            return [
                {
                    "exercise_name": row[0],
                    "sessions": row[1],
                    "total_minutes": int((row[2] or 0) / 60),
                    "total_repetitions": row[3] or 0,
                    "avg_posture_score": round(row[4] or 0, 2),
                }
                for row in rows
            ]
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()

    def save_health_metrics(self, date: str) -> bool:
        """
        특정 날짜의 종합 건강 지표를 저장합니다.
        
        Args:
            date: YYYY-MM-DD 형식의 날짜
            
        Returns:
            성공 여부
        """
        metrics = self.get_overall_health_metrics(days_back=1)
        
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """INSERT OR REPLACE INTO health_metrics
                   (date, total_exercise_minutes, exercise_variety, consistency_score, overall_posture_score)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    date,
                    metrics["total_exercise_minutes"],
                    metrics["exercise_variety"],
                    metrics["consistency_score"],
                    metrics["avg_posture_score"],
                )
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving health metrics: {e}")
            return False
        finally:
            conn.close()

    def get_improvement_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """
        사용자의 개선 요약을 생성합니다.
        
        Args:
            days_back: 최근 며칠
            
        Returns:
            개선 요약 정보
        """
        metrics = self.get_overall_health_metrics(days_back)
        trends = self.get_exercise_trends(days_back)
        
        # 최근 절반 vs 이전 절반 비교
        first_half = self.get_overall_health_metrics(days_back // 2)
        second_half = self.get_overall_health_metrics(days_back // 4)

        improvements = {
            "period_days": days_back,
            "total_minutes_improved": second_half["total_exercise_minutes"] - first_half["total_exercise_minutes"],
            "posture_improvement": second_half["avg_posture_score"] - first_half["avg_posture_score"],
            "consistency_improvement": second_half["consistency_score"] - first_half["consistency_score"],
            "top_exercises": trends[:3],
            "recommendations": []
        }

        # 추천 메시지 생성
        if improvements["total_minutes_improved"] > 0:
            improvements["recommendations"].append(
                f"최근 {improvements['total_minutes_improved']}분 더 운동했습니다! 꾸준함을 유지하세요."
            )
        
        if improvements["posture_improvement"] > 0:
            improvements["recommendations"].append(
                f"자세 점수가 {round(improvements['posture_improvement'], 1)}점 향상되었습니다!"
            )
        
        if metrics["exercise_variety"] > 3:
            improvements["recommendations"].append(
                f"{metrics['exercise_variety']}가지 운동을 하고 있습니다. 훌륭합니다!"
            )
        else:
            improvements["recommendations"].append(
                "다양한 운동을 시도해보세요. 전체 신체의 균형을 맞출 수 있습니다."
            )

        return improvements

"""통합 분석 모듈 - 스쿼트와 보행 데이터의 통합 통계를 계산합니다."""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = Path(__file__).with_name("workout_history.db")


class Analytics:
    """운동 및 보행 데이터의 통합 분석을 제공하는 클래스입니다."""

    def __init__(self):
        """Analytics를 초기화합니다."""
        pass

    def get_today_summary(self) -> Dict[str, Any]:
        """
        오늘의 통합 운동 및 보행 요약을 반환합니다.
        
        Returns:
            오늘의 통계 딕셔너리
        """
        today = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            # 스쿼트 데이터
            c.execute(
                """SELECT SUM(total_count), SUM(workout_seconds)
                   FROM workout_records
                   WHERE workout_date = ?""",
                (today,)
            )
            squat_result = c.fetchone()
            squat_count = int(squat_result[0]) if squat_result[0] else 0
            squat_seconds = float(squat_result[1]) if squat_result[1] else 0.0

            # 보행 데이터
            c.execute(
                """SELECT SUM(total_steps), SUM(duration_seconds)
                   FROM walk_records
                   WHERE walk_date = ?""",
                (today,)
            )
            walk_result = c.fetchone()
            walk_steps = int(walk_result[0]) if walk_result[0] else 0
            walk_seconds = float(walk_result[1]) if walk_result[1] else 0.0

            return {
                "date": today,
                "squat": {
                    "count": squat_count,
                    "seconds": squat_seconds,
                    "minutes": int(squat_seconds // 60),
                },
                "walk": {
                    "steps": walk_steps,
                    "seconds": walk_seconds,
                    "minutes": int(walk_seconds // 60),
                },
            }
        finally:
            conn.close()

    def get_weekly_summary(self, days_back: int = 7) -> Dict[str, Any]:
        """
        주간 통합 요약을 반환합니다.
        
        Args:
            days_back: 최근 며칠간의 데이터를 조회할지 (기본값 7일)
            
        Returns:
            주간 요약 딕셔너리
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            # 계산 날짜 범위
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back - 1)
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            # 스쿼트 주간 통계
            c.execute(
                """SELECT 
                     COUNT(DISTINCT workout_date) as workout_days,
                     SUM(total_count) as total_count,
                     SUM(workout_seconds) as total_seconds,
                     AVG(total_count) as avg_count,
                     MAX(total_count) as max_count,
                     MIN(total_count) as min_count,
                     AVG(avg_posture_accuracy) as avg_accuracy
                   FROM workout_records
                   WHERE workout_date >= ? AND workout_date <= ?""",
                (start_str, end_str)
            )
            squat = c.fetchone()

            # 보행 주간 통계
            c.execute(
                """SELECT 
                     COUNT(DISTINCT walk_date) as walk_days,
                     SUM(total_steps) as total_steps,
                     SUM(duration_seconds) as total_seconds,
                     AVG(total_steps) as avg_steps,
                     MAX(total_steps) as max_steps,
                     MIN(total_steps) as min_steps,
                     AVG(cadence) as avg_cadence,
                     AVG(avg_posture_accuracy) as avg_accuracy
                   FROM walk_records
                   WHERE walk_date >= ? AND walk_date <= ?""",
                (start_str, end_str)
            )
            walk = c.fetchone()

            return {
                "period": f"{days_back}일간",
                "start_date": start_str,
                "end_date": end_str,
                "squat": {
                    "workout_days": int(squat[0]) if squat[0] else 0,
                    "total_count": int(squat[1]) if squat[1] else 0,
                    "total_seconds": float(squat[2]) if squat[2] else 0.0,
                    "avg_count": float(squat[3]) if squat[3] else 0.0,
                    "max_count": int(squat[4]) if squat[4] else 0,
                    "min_count": int(squat[5]) if squat[5] else 0,
                    "avg_accuracy": float(squat[6]) if squat[6] else 0.0,
                },
                "walk": {
                    "walk_days": int(walk[0]) if walk[0] else 0,
                    "total_steps": int(walk[1]) if walk[1] else 0,
                    "total_seconds": float(walk[2]) if walk[2] else 0.0,
                    "avg_steps": float(walk[3]) if walk[3] else 0.0,
                    "max_steps": int(walk[4]) if walk[4] else 0,
                    "min_steps": int(walk[5]) if walk[5] else 0,
                    "avg_cadence": float(walk[6]) if walk[6] else 0.0,
                    "avg_accuracy": float(walk[7]) if walk[7] else 0.0,
                },
            }
        finally:
            conn.close()

    def get_monthly_summary(self, month_offset: int = 0) -> Dict[str, Any]:
        """
        월간 통합 요약을 반환합니다.
        
        Args:
            month_offset: 0=이번달, -1=지난달 등
            
        Returns:
            월간 요약 딕셔너리
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            # 월 계산 (SQLite에서 month offset 처리)
            if month_offset == 0:
                start_expr = "'now', 'start of month'"
                end_expr = "'now', 'start of month', '+1 month'"
            elif month_offset == -1:
                start_expr = "'now', 'start of month', '-1 month'"
                end_expr = "'now', 'start of month'"
            else:
                start_expr = "'now', 'start of month', '+{} month'".format(month_offset)
                end_expr = "'now', 'start of month', '+{} month'".format(month_offset + 1)

            # 스쿼트 월간 통계
            c.execute(
                f"""SELECT 
                     COUNT(DISTINCT workout_date) as workout_days,
                     SUM(total_count) as total_count,
                     SUM(workout_seconds) as total_seconds,
                     AVG(total_count) as avg_count,
                     MAX(total_count) as max_count,
                     AVG(avg_posture_accuracy) as avg_accuracy
                   FROM workout_records
                   WHERE workout_date >= date({start_expr})
                   AND workout_date < date({end_expr})"""
            )
            squat = c.fetchone()

            # 보행 월간 통계
            c.execute(
                f"""SELECT 
                     COUNT(DISTINCT walk_date) as walk_days,
                     SUM(total_steps) as total_steps,
                     SUM(duration_seconds) as total_seconds,
                     AVG(total_steps) as avg_steps,
                     MAX(total_steps) as max_steps,
                     AVG(cadence) as avg_cadence,
                     AVG(avg_posture_accuracy) as avg_accuracy
                   FROM walk_records
                   WHERE walk_date >= date({start_expr})
                   AND walk_date < date({end_expr})"""
            )
            walk = c.fetchone()

            month_label = self._get_month_label(month_offset)

            return {
                "period": month_label,
                "squat": {
                    "workout_days": int(squat[0]) if squat and squat[0] else 0,
                    "total_count": int(squat[1]) if squat and squat[1] else 0,
                    "total_seconds": float(squat[2]) if squat and squat[2] else 0.0,
                    "avg_count": float(squat[3]) if squat and squat[3] else 0.0,
                    "max_count": int(squat[4]) if squat and squat[4] else 0,
                    "avg_accuracy": float(squat[5]) if squat and squat[5] else 0.0,
                },
                "walk": {
                    "walk_days": int(walk[0]) if walk and walk[0] else 0,
                    "total_steps": int(walk[1]) if walk and walk[1] else 0,
                    "total_seconds": float(walk[2]) if walk and walk[2] else 0.0,
                    "avg_steps": float(walk[3]) if walk and walk[3] else 0.0,
                    "max_steps": int(walk[4]) if walk and walk[4] else 0,
                    "avg_cadence": float(walk[6]) if walk and len(walk) > 6 else 0.0,
                    "avg_accuracy": float(walk[6] if len(walk) > 6 else walk[5]) if walk else 0.0,
                },
            }
        finally:
            conn.close()

    def get_daily_trend(self, activity_type: str, limit_days: int = 30) -> List[Dict[str, Any]]:
        """
        일일 활동 추이를 반환합니다.
        
        Args:
            activity_type: 'squat' 또는 'walk'
            limit_days: 최근 며칠간의 데이터
            
        Returns:
            일일 데이터 리스트
        """
        if activity_type not in ["squat", "walk"]:
            return []

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            if activity_type == "squat":
                c.execute(
                    """SELECT workout_date, total_count, workout_seconds, avg_posture_accuracy
                       FROM workout_records
                       ORDER BY workout_date DESC
                       LIMIT ?""",
                    (limit_days,)
                )
                results = []
                for row in c.fetchall():
                    results.append({
                        "date": row[0],
                        "count": int(row[1]),
                        "seconds": float(row[2]),
                        "accuracy": float(row[3]),
                    })
            else:  # walk
                c.execute(
                    """SELECT walk_date, total_steps, duration_seconds, cadence, avg_posture_accuracy
                       FROM walk_records
                       ORDER BY walk_date DESC
                       LIMIT ?""",
                    (limit_days,)
                )
                results = []
                for row in c.fetchall():
                    results.append({
                        "date": row[0],
                        "steps": int(row[1]),
                        "seconds": float(row[2]),
                        "cadence": float(row[3]),
                        "accuracy": float(row[4]),
                    })

            return list(reversed(results))  # 오래된 것부터
        finally:
            conn.close()

    def get_comparison_vs_previous_period(
        self, activity_type: str, days: int = 7
    ) -> Dict[str, Any]:
        """
        이전 기간과의 비교를 반환합니다.
        
        Args:
            activity_type: 'squat' 또는 'walk'
            days: 기간 (기본값 7일)
            
        Returns:
            비교 데이터
        """
        if activity_type not in ["squat", "walk"]:
            return {}

        # 현재 기간
        current = self.get_weekly_summary(days_back=days)

        # 이전 기간 (동일한 길이)
        end_date = datetime.now() - timedelta(days=days)
        start_date = end_date - timedelta(days=days)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            if activity_type == "squat":
                c.execute(
                    """SELECT 
                         COUNT(DISTINCT workout_date) as workout_days,
                         SUM(total_count) as total_count,
                         SUM(workout_seconds) as total_seconds,
                         AVG(total_count) as avg_count
                       FROM workout_records
                       WHERE workout_date >= ? AND workout_date <= ?""",
                    (start_str, end_str)
                )
                prev = c.fetchone()
                current_data = current["squat"]
                prev_total = int(prev[1]) if prev and prev[1] else 0
                current_total = current_data["total_count"]
            else:  # walk
                c.execute(
                    """SELECT 
                         COUNT(DISTINCT walk_date) as walk_days,
                         SUM(total_steps) as total_steps,
                         SUM(duration_seconds) as total_seconds,
                         AVG(total_steps) as avg_steps
                       FROM walk_records
                       WHERE walk_date >= ? AND walk_date <= ?""",
                    (start_str, end_str)
                )
                prev = c.fetchone()
                current_data = current["walk"]
                prev_total = int(prev[1]) if prev and prev[1] else 0
                current_total = current_data["total_steps"]

            # 증감률 계산
            if prev_total > 0:
                change_rate = ((current_total - prev_total) / prev_total) * 100.0
            else:
                change_rate = 100.0 if current_total > 0 else 0.0

            return {
                "activity_type": activity_type,
                "period_days": days,
                "current_total": current_total,
                "previous_total": prev_total,
                "change": current_total - prev_total,
                "change_rate": change_rate,
                "is_improvement": change_rate >= 0,
            }
        finally:
            conn.close()

    def get_personal_best(self, activity_type: str) -> Optional[Dict[str, Any]]:
        """
        개인 최고 기록(PR)을 반환합니다.
        
        Args:
            activity_type: 'squat' 또는 'walk'
            
        Returns:
            PR 데이터 또는 None
        """
        if activity_type not in ["squat", "walk"]:
            return None

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            if activity_type == "squat":
                c.execute(
                    """SELECT workout_date, total_count, workout_seconds, avg_posture_accuracy
                       FROM workout_records
                       ORDER BY total_count DESC
                       LIMIT 1"""
                )
                result = c.fetchone()
                if result:
                    return {
                        "activity_type": "squat",
                        "date": result[0],
                        "count": int(result[1]),
                        "seconds": float(result[2]),
                        "accuracy": float(result[3]),
                    }
            else:  # walk
                c.execute(
                    """SELECT walk_date, total_steps, duration_seconds, cadence, avg_posture_accuracy
                       FROM walk_records
                       ORDER BY total_steps DESC
                       LIMIT 1"""
                )
                result = c.fetchone()
                if result:
                    return {
                        "activity_type": "walk",
                        "date": result[0],
                        "steps": int(result[1]),
                        "seconds": float(result[2]),
                        "cadence": float(result[3]),
                        "accuracy": float(result[4]),
                    }
            return None
        finally:
            conn.close()

    def _get_month_label(self, month_offset: int) -> str:
        """월 오프셋을 문자열로 변환합니다."""
        now = datetime.now()
        if month_offset == 0:
            return now.strftime("%Y년 %m월 (이번달)")
        elif month_offset == -1:
            prev = now - timedelta(days=30)
            return prev.strftime("%Y년 %m월 (지난달)")
        else:
            target = now + timedelta(days=30 * month_offset)
            return target.strftime("%Y년 %m월")

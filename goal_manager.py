"""목표 관리 모듈 - 스쿼트와 보행의 개인 목표를 관리합니다."""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

DB_PATH = Path(__file__).with_name("workout_history.db")


class GoalManager:
    """사용자의 운동 및 보행 목표를 관리하는 클래스입니다."""

    SQUAT = "squat"
    WALK = "walk"

    def __init__(self):
        """GoalManager를 초기화합니다."""
        self._ensure_tables_exist()

    def _ensure_tables_exist(self) -> None:
        """필요한 테이블이 존재하는지 확인합니다."""
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type TEXT NOT NULL,
                target_value INTEGER NOT NULL,
                created_date TEXT NOT NULL,
                updated_date TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS daily_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_date TEXT NOT NULL,
                goal_type TEXT NOT NULL,
                target_value INTEGER NOT NULL,
                achieved_value INTEGER NOT NULL,
                achievement_rate REAL NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()

    def set_goal(self, goal_type: str, target_value: int) -> bool:
        """
        목표를 설정 또는 업데이트합니다.
        
        Args:
            goal_type: 'squat' 또는 'walk'
            target_value: 목표값 (회수 또는 걸음)
            
        Returns:
            성공 여부
        """
        if goal_type not in [self.SQUAT, self.WALK]:
            return False
        
        if target_value < 0:
            return False

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        now = datetime.now().isoformat()

        try:
            # 기존 활성 목표가 있는지 확인
            c.execute("SELECT id FROM goals WHERE goal_type = ? AND is_active = 1", (goal_type,))
            existing = c.fetchone()

            if existing:
                # 기존 목표 업데이트
                c.execute(
                    "UPDATE goals SET target_value = ?, updated_date = ? WHERE id = ?",
                    (target_value, now, existing[0])
                )
            else:
                # 새 목표 삽입
                c.execute(
                    "INSERT INTO goals (goal_type, target_value, created_date, is_active) VALUES (?, ?, ?, 1)",
                    (goal_type, target_value, now)
                )

            conn.commit()
            return True
        finally:
            conn.close()

    def get_goal(self, goal_type: str) -> Optional[int]:
        """
        현재 활성 목표를 조회합니다.
        
        Args:
            goal_type: 'squat' 또는 'walk'
            
        Returns:
            목표값 또는 None
        """
        if goal_type not in [self.SQUAT, self.WALK]:
            return None

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                "SELECT target_value FROM goals WHERE goal_type = ? AND is_active = 1",
                (goal_type,)
            )
            result = c.fetchone()
            return result[0] if result else None
        finally:
            conn.close()

    def record_daily_goal(
        self, goal_date: str, goal_type: str, target_value: int, achieved_value: int
    ) -> bool:
        """
        일일 목표 달성 기록을 저장합니다.
        
        Args:
            goal_date: 기록 날짜 (YYYY-MM-DD)
            goal_type: 'squat' 또는 'walk'
            target_value: 목표값
            achieved_value: 달성값
            
        Returns:
            성공 여부
        """
        if goal_type not in [self.SQUAT, self.WALK]:
            return False

        if target_value <= 0 or achieved_value < 0:
            return False

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            achievement_rate = (achieved_value / target_value) * 100.0 if target_value > 0 else 0.0
            achievement_rate = min(100.0, achievement_rate)  # 100% 초과 제한

            c.execute(
                """INSERT INTO daily_goals 
                   (goal_date, goal_type, target_value, achieved_value, achievement_rate)
                   VALUES (?, ?, ?, ?, ?)""",
                (goal_date, goal_type, target_value, achieved_value, achievement_rate)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def get_daily_goal_record(self, goal_date: str, goal_type: str) -> Optional[Dict[str, Any]]:
        """
        특정 날짜의 목표 기록을 조회합니다.
        
        Args:
            goal_date: 기록 날짜 (YYYY-MM-DD)
            goal_type: 'squat' 또는 'walk'
            
        Returns:
            기록 딕셔너리 또는 None
        """
        if goal_type not in [self.SQUAT, self.WALK]:
            return None

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """SELECT goal_date, goal_type, target_value, achieved_value, achievement_rate
                   FROM daily_goals
                   WHERE goal_date = ? AND goal_type = ?""",
                (goal_date, goal_type)
            )
            result = c.fetchone()
            if result:
                return {
                    "goal_date": result[0],
                    "goal_type": result[1],
                    "target_value": result[2],
                    "achieved_value": result[3],
                    "achievement_rate": result[4],
                }
            return None
        finally:
            conn.close()

    def get_daily_goals_by_type(
        self, goal_type: str, limit_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        특정 타입의 최근 일일 목표 기록을 조회합니다.
        
        Args:
            goal_type: 'squat' 또는 'walk'
            limit_days: 조회할 최근 일수
            
        Returns:
            기록 딕셔너리 리스트 (최신순)
        """
        if goal_type not in [self.SQUAT, self.WALK]:
            return []

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """SELECT goal_date, goal_type, target_value, achieved_value, achievement_rate
                   FROM daily_goals
                   WHERE goal_type = ?
                   ORDER BY goal_date DESC
                   LIMIT ?""",
                (goal_type, limit_days)
            )
            results = c.fetchall()
            return [
                {
                    "goal_date": row[0],
                    "goal_type": row[1],
                    "target_value": row[2],
                    "achieved_value": row[3],
                    "achievement_rate": row[4],
                }
                for row in results
            ]
        finally:
            conn.close()

    def get_weekly_summary(self, goal_type: str, week_offset: int = 0) -> Dict[str, Any]:
        """
        주간 목표 달성 요약을 반환합니다.
        
        Args:
            goal_type: 'squat' 또는 'walk'
            week_offset: 0=이번주, -1=지난주, 1=다음주
            
        Returns:
            주간 요약 딕셔너리
        """
        if goal_type not in [self.SQUAT, self.WALK]:
            return {}

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            # SQLite에서 주별 집계
            # strftime은 SQLite 함수
            c.execute(
                """SELECT 
                     COUNT(*) as days_recorded,
                     SUM(achieved_value) as total_achieved,
                     AVG(achievement_rate) as avg_rate,
                     MAX(achieved_value) as best_day,
                     MIN(achieved_value) as worst_day
                   FROM daily_goals
                   WHERE goal_type = ?
                   AND goal_date >= date('now', 'weekday 1', '-7 days')
                   AND goal_date < date('now', 'weekday 1')""",
                (goal_type,)
            )
            result = c.fetchone()
            
            if result and result[0] > 0:
                return {
                    "goal_type": goal_type,
                    "days_recorded": result[0],
                    "total_achieved": int(result[1]) if result[1] else 0,
                    "avg_achievement_rate": float(result[2]) if result[2] else 0.0,
                    "best_day": int(result[3]) if result[3] else 0,
                    "worst_day": int(result[4]) if result[4] else 0,
                }
            return {
                "goal_type": goal_type,
                "days_recorded": 0,
                "total_achieved": 0,
                "avg_achievement_rate": 0.0,
                "best_day": 0,
                "worst_day": 0,
            }
        finally:
            conn.close()

    def get_monthly_summary(self, goal_type: str, month_offset: int = 0) -> Dict[str, Any]:
        """
        월간 목표 달성 요약을 반환합니다.
        
        Args:
            goal_type: 'squat' 또는 'walk'
            month_offset: 0=이번달, -1=지난달, 1=다음달
            
        Returns:
            월간 요약 딕셔너리
        """
        if goal_type not in [self.SQUAT, self.WALK]:
            return {}

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """SELECT 
                     COUNT(*) as days_recorded,
                     SUM(achieved_value) as total_achieved,
                     AVG(achievement_rate) as avg_rate,
                     MAX(achieved_value) as best_day,
                     MIN(achieved_value) as worst_day,
                     SUM(CASE WHEN achievement_rate >= 100 THEN 1 ELSE 0 END) as goal_achieved_days
                   FROM daily_goals
                   WHERE goal_type = ?
                   AND goal_date >= date('now', 'start of month')
                   AND goal_date < date('now', 'start of month', '+1 month')""",
                (goal_type,)
            )
            result = c.fetchone()
            
            if result and result[0] > 0:
                return {
                    "goal_type": goal_type,
                    "days_recorded": result[0],
                    "total_achieved": int(result[1]) if result[1] else 0,
                    "avg_achievement_rate": float(result[2]) if result[2] else 0.0,
                    "best_day": int(result[3]) if result[3] else 0,
                    "worst_day": int(result[4]) if result[4] else 0,
                    "goal_achieved_days": int(result[5]) if result[5] else 0,
                }
            return {
                "goal_type": goal_type,
                "days_recorded": 0,
                "total_achieved": 0,
                "avg_achievement_rate": 0.0,
                "best_day": 0,
                "worst_day": 0,
                "goal_achieved_days": 0,
            }
        finally:
            conn.close()

    def get_achievement_history(
        self, goal_type: str, limit_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        달성 기록을 반환합니다 (최신순).
        
        Args:
            goal_type: 'squat' 또는 'walk'
            limit_days: 최근 일수
            
        Returns:
            기록 리스트
        """
        if goal_type not in [self.SQUAT, self.WALK]:
            return []

        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute(
                """SELECT goal_date, target_value, achieved_value, achievement_rate
                   FROM daily_goals
                   WHERE goal_type = ?
                   ORDER BY goal_date DESC
                   LIMIT ?""",
                (goal_type, limit_days)
            )
            results = c.fetchall()
            return [
                {
                    "goal_date": row[0],
                    "target_value": row[1],
                    "achieved_value": row[2],
                    "achievement_rate": row[3],
                }
                for row in results
            ]
        finally:
            conn.close()

    def delete_goal_record(self, record_id: int) -> bool:
        """
        특정 일일 목표 기록을 삭제합니다.
        
        Args:
            record_id: 기록 ID
            
        Returns:
            성공 여부
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute("DELETE FROM daily_goals WHERE id = ?", (record_id,))
            conn.commit()
            return c.rowcount > 0
        finally:
            conn.close()

    def clear_all_goals(self) -> bool:
        """
        모든 목표 기록을 삭제합니다 (테스트 용도).
        
        Returns:
            성공 여부
        """
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()

        try:
            c.execute("DELETE FROM daily_goals")
            c.execute("DELETE FROM goals")
            conn.commit()
            return True
        finally:
            conn.close()

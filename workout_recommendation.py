"""AI 맞춤형 운동 추천 엔진 - 사용자 프로필과 운동 기록을 기반으로 운동을 추천합니다."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

DB_PATH = Path(__file__).with_name("workout_history.db")


@dataclass
class Exercise:
    """운동 정보 클래스"""
    name: str
    category: str
    description: str
    benefits: str
    difficulty: str
    duration_range: str
    target_areas: List[str]
    precautions: str
    video_keywords: List[str]


class ExerciseLibrary:
    """운동 라이브러리 - 모든 운동 정보를 관리합니다."""
    
    EXERCISES = {
        "스쿼트": Exercise(
            name="스쿼트",
            category="하체",
            description="두 다리로 서서 무릎을 굽혔다 펴는 운동입니다. 가장 기본적인 하체 운동입니다.",
            benefits="대퇴사두근, 엉덩이, 종아리 강화. 하체 근력과 안정성 향상.",
            difficulty="초보자",
            duration_range="10-20분",
            target_areas=["무릎", "엉덩이", "허리"],
            precautions="무릎이 발끝보다 앞으로 나가지 않도록 주의. 허리를 곧게 유지하세요.",
            video_keywords=["스쿼트", "squat", "초보자 스쿼트"]
        ),
        "걷기": Exercise(
            name="걷기",
            category="유산소",
            description="일반적인 속도로 계속 걷는 유산소 운동입니다.",
            benefits="심폐 지구력 향상, 칼로리 소모, 관절에 무리 적음.",
            difficulty="초보자",
            duration_range="20-40분",
            target_areas=["다리", "심장"],
            precautions="편한 신발을 착용하고, 무리하지 않은 속도로 진행하세요.",
            video_keywords=["걷기", "walking", "산책"]
        ),
        "산책": Exercise(
            name="산책",
            category="유산소",
            description="천천히 여유 있게 걷는 가벼운 운동입니다.",
            benefits="스트레스 해소, 기초 대사량 증가, 관절 유연성 향상.",
            difficulty="초보자",
            duration_range="20-60분",
            target_areas=["다리", "심장"],
            precautions="안전한 경로를 선택하고 필요시 지팡이를 사용하세요.",
            video_keywords=["산책", "casual walk"]
        ),
        "스트레칭": Exercise(
            name="스트레칭",
            category="유연성",
            description="근육을 천천히 늘려 유연성을 향상시키는 운동입니다.",
            benefits="근육 경직 완화, 운동 범위 증대, 부상 예방.",
            difficulty="초보자",
            duration_range="10-15분",
            target_areas=["전신"],
            precautions="반동을 주지 말고 천천히 진행하세요. 통증은 금지입니다.",
            video_keywords=["스트레칭", "stretching", "flexibility"]
        ),
        "팔 굽혀펴기": Exercise(
            name="팔 굽혀펴기",
            category="상체",
            description="팔의 힘으로 몸을 들었다 내리는 상체 운동입니다.",
            benefits="팔, 가슴, 어깨, 코어 근력 강화.",
            difficulty="중급자",
            duration_range="10-20분",
            target_areas=["팔", "가슴", "어깨"],
            precautions="무릎으로 한 후 점진적으로 발끝으로 이동하세요.",
            video_keywords=["팔굽혀펴기", "push-ups", "pushup"]
        ),
        "플랭크": Exercise(
            name="플랭크",
            category="코어",
            description="엎드린 상태에서 팔꿈치로 버티는 운동입니다.",
            benefits="코어, 복근, 등 근력 강화. 자세 개선.",
            difficulty="초보자",
            duration_range="5-15분",
            target_areas=["복근", "허리", "등"],
            precautions="몸이 일직선을 유지하도록 주의하세요.",
            video_keywords=["플랭크", "plank", "core"]
        ),
        "런지": Exercise(
            name="런지",
            category="하체",
            description="한 발씩 앞으로 내딛으며 무릎을 굽히는 운동입니다.",
            benefits="대퇴사두근, 엉덩이, 종아리 강화. 한쪽 다리 근력 개선.",
            difficulty="중급자",
            duration_range="10-20분",
            target_areas=["다리", "엉덩이"],
            precautions="무릎이 발끝보다 앞으로 나가지 않도록 주의하세요.",
            video_keywords=["런지", "lunge", "다리 운동"]
        ),
        "상체 근력": Exercise(
            name="상체 근력",
            category="상체",
            description="팔, 어깨, 가슴을 강화하는 종합 상체 운동입니다.",
            benefits="상체 근력 증대, 자세 개선.",
            difficulty="중급자",
            duration_range="15-25분",
            target_areas=["팔", "어깨", "가슴"],
            precautions="관절에 무리가 없도록 천천히 진행하세요.",
            video_keywords=["상체 운동", "upper body"]
        ),
        "하체 근력": Exercise(
            name="하체 근력",
            category="하체",
            description="다리와 엉덩이를 강화하는 종합 하체 운동입니다.",
            benefits="하체 근력 증대, 안정성 향상.",
            difficulty="중급자",
            duration_range="15-25분",
            target_areas=["다리", "엉덩이", "무릎"],
            precautions="무릎과 허리에 과부하가 없도록 주의하세요.",
            video_keywords=["하체 운동", "lower body"]
        ),
        "코어 운동": Exercise(
            name="코어 운동",
            category="코어",
            description="복근, 등, 옆구리를 강화하는 운동입니다.",
            benefits="코어 근력 증진, 자세 개선, 허리 건강.",
            difficulty="초보자",
            duration_range="10-15분",
            target_areas=["복근", "허리", "옆구리"],
            precautions="항상 허리를 보호하면서 진행하세요.",
            video_keywords=["코어", "core", "복근"]
        ),
        "균형 운동": Exercise(
            name="균형 운동",
            category="균형",
            description="한 발 서기, 걷기 등으로 신체 균형을 개선하는 운동입니다.",
            benefits="전정기관 개선, 낙상 예방, 신경계 발달.",
            difficulty="초보자",
            duration_range="10-20분",
            target_areas=["다리", "코어"],
            precautions="안전한 장소에서 하고 필요시 지지대를 사용하세요.",
            video_keywords=["균형", "balance", "stability"]
        ),
        "홈트레이닝": Exercise(
            name="홈트레이닝",
            category="종합",
            description="집에서 간단한 도구로 할 수 있는 가벼운 운동 조합입니다.",
            benefits="전신 운동, 편의성, 비용 절감.",
            difficulty="초보자",
            duration_range="20-30분",
            target_areas=["전신"],
            precautions="충분한 공간을 확보하고 안전하게 진행하세요.",
            video_keywords=["홈트", "home workout"]
        ),
        "요가": Exercise(
            name="요가",
            category="유연성",
            description="신체와 정신을 함께 단련하는 운동입니다.",
            benefits="유연성 향상, 스트레스 완화, 균형감각 개선.",
            difficulty="초보자",
            duration_range="20-30분",
            target_areas=["전신"],
            precautions="개인의 능력에 맞게 천천히 진행하세요.",
            video_keywords=["요가", "yoga", "초보자 요가"]
        ),
        "근력 운동": Exercise(
            name="근력 운동",
            category="근력",
            description="전신 근육을 강화하는 종합 근력 운동입니다.",
            benefits="전신 근력 증강, 신진대사 촉진, 뼈 건강 개선.",
            difficulty="초보자",
            duration_range="20-30분",
            target_areas=["전신"],
            precautions="올바른 자세를 유지하고 개인 능력에 맞게 진행하세요.",
            video_keywords=["근력 운동", "strength training", "근트"]
        ),
    }

    @classmethod
    def get_exercise(cls, name: str) -> Optional[Exercise]:
        """운동 정보 조회"""
        return cls.EXERCISES.get(name)

    @classmethod
    def get_all_exercises(cls) -> List[Exercise]:
        """모든 운동 조회"""
        return list(cls.EXERCISES.values())

    @classmethod
    def get_exercises_by_category(cls, category: str) -> List[Exercise]:
        """카테고리별 운동 조회"""
        return [ex for ex in cls.EXERCISES.values() if ex.category == category]

    @classmethod
    def get_exercises_by_difficulty(cls, difficulty: str) -> List[Exercise]:
        """난이도별 운동 조회"""
        return [ex for ex in cls.EXERCISES.values() if ex.difficulty == difficulty]


class UserProfile:
    """사용자 프로필 - 사용자의 체력 정보와 목표를 관리합니다."""

    def __init__(self):
        """사용자 프로필을 초기화합니다."""
        self.age: Optional[int] = None
        self.gender: Optional[str] = None  # male, female, other
        self.fitness_level: str = "초보자"  # 초보자, 중급자, 고급자
        self.goals: List[str] = []  # 체중 관리, 근력 향상, 유연성, 체력 증진
        self.available_time_minutes: int = 30  # 하루 운동 가능 시간
        self.physical_limitations: List[str] = []  # 무릎 통증, 허리 통증 등
        self.recent_performance: Dict[str, Any] = {}

    def set_fitness_level(self, level: str) -> None:
        """체력 수준 설정"""
        if level in ["초보자", "중급자", "고급자"]:
            self.fitness_level = level

    def add_goal(self, goal: str) -> None:
        """운동 목표 추가"""
        if goal not in self.goals:
            self.goals.append(goal)

    def add_limitation(self, limitation: str) -> None:
        """신체적 제한사항 추가"""
        if limitation not in self.physical_limitations:
            self.physical_limitations.append(limitation)

    def has_limitation(self, keyword: str) -> bool:
        """특정 제한사항이 있는지 확인"""
        return any(keyword.lower() in lim.lower() for lim in self.physical_limitations)


class WorkoutRecommender:
    """운동 추천 엔진 - 사용자 프로필과 운동 성능을 기반으로 운동을 추천합니다."""

    def __init__(self):
        """추천 엔진을 초기화합니다."""
        self.library = ExerciseLibrary()

    def get_recommended_exercises(
        self,
        profile: UserProfile,
        squat_performance: Optional[Dict[str, Any]] = None,
        walk_performance: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        사용자 프로필에 맞는 운동을 추천합니다.
        
        Args:
            profile: 사용자 프로필
            squat_performance: 스쿼트 성능 (optional)
            walk_performance: 보행 성능 (optional)
            limit: 추천할 운동 개수
            
        Returns:
            추천 운동 목록 (각 운동에 추천 이유 포함)
        """
        recommendations = []

        # 현재 운동 능력 분석
        fitness_assessment = self._assess_fitness_from_performance(
            squat_performance, walk_performance
        )

        # 체력 수준에 맞는 운동 필터링
        candidates = self._filter_by_fitness_level(profile.fitness_level)

        # 제한사항에 맞는 운동 필터링
        candidates = self._filter_by_limitations(candidates, profile.physical_limitations)

        # 목표에 맞는 운동 선택
        candidates = self._rank_by_goals(candidates, profile.goals, fitness_assessment)

        # 추천
        for exercise in candidates[:limit]:
            recommendation = {
                "exercise": exercise,
                "reason": self._generate_recommendation_reason(
                    exercise, profile, fitness_assessment
                ),
                "difficulty": exercise.difficulty,
                "duration": exercise.duration_range,
                "benefits": exercise.benefits,
                "tips": self._generate_tips(exercise, profile),
            }
            recommendations.append(recommendation)

        return recommendations

    def get_exercise_details(self, exercise_name: str) -> Optional[Dict[str, Any]]:
        """
        특정 운동의 상세 정보를 조회합니다.
        
        Args:
            exercise_name: 운동 이름
            
        Returns:
            운동 상세 정보
        """
        exercise = self.library.get_exercise(exercise_name)
        if not exercise:
            return None

        return {
            "name": exercise.name,
            "category": exercise.category,
            "description": exercise.description,
            "benefits": exercise.benefits,
            "difficulty": exercise.difficulty,
            "duration_range": exercise.duration_range,
            "target_areas": exercise.target_areas,
            "precautions": exercise.precautions,
            "video_keywords": exercise.video_keywords,
        }

    def get_category_exercises(self, category: str) -> List[Dict[str, Any]]:
        """
        카테고리별 운동을 조회합니다.
        
        Args:
            category: 운동 카테고리 (상체, 하체, 유산소 등)
            
        Returns:
            카테고리 운동 목록
        """
        exercises = self.library.get_exercises_by_category(category)
        return [
            {
                "name": ex.name,
                "description": ex.description,
                "difficulty": ex.difficulty,
                "duration_range": ex.duration_range,
                "target_areas": ex.target_areas,
            }
            for ex in exercises
        ]

    def _assess_fitness_from_performance(
        self,
        squat_performance: Optional[Dict[str, Any]],
        walk_performance: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """운동 성능으로부터 체력을 평가합니다."""
        assessment = {
            "lower_body_strength": "미측정",
            "cardio_fitness": "미측정",
            "flexibility": "미측정",
            "weakness_areas": []
        }

        if squat_performance:
            count = squat_performance.get("count", 0)
            avg_score = squat_performance.get("average_score", 0)
            
            if count < 10:
                assessment["lower_body_strength"] = "약함"
                assessment["weakness_areas"].append("하체 근력")
            elif count < 20:
                assessment["lower_body_strength"] = "보통"
            else:
                assessment["lower_body_strength"] = "좋음"

        if walk_performance:
            steps = walk_performance.get("steps", 0)
            
            if steps < 2000:
                assessment["cardio_fitness"] = "약함"
                assessment["weakness_areas"].append("심폐 지구력")
            elif steps < 5000:
                assessment["cardio_fitness"] = "보통"
            else:
                assessment["cardio_fitness"] = "좋음"

        return assessment

    def _filter_by_fitness_level(self, fitness_level: str) -> List[Exercise]:
        """체력 수준에 맞는 운동을 필터링합니다."""
        all_exercises = self.library.get_all_exercises()

        if fitness_level == "초보자":
            # 초보자: 초보자 운동만
            return [ex for ex in all_exercises if ex.difficulty == "초보자"]
        elif fitness_level == "중급자":
            # 중급자: 초보자 + 중급자
            return [ex for ex in all_exercises if ex.difficulty in ["초보자", "중급자"]]
        else:
            # 고급자: 모든 운동
            return all_exercises

    def _filter_by_limitations(
        self,
        candidates: List[Exercise],
        limitations: List[str]
    ) -> List[Exercise]:
        """제한사항에 맞는 운동을 필터링합니다."""
        if not limitations:
            return candidates

        filtered = []
        for exercise in candidates:
            is_safe = True
            
            for limitation in limitations:
                if limitation.lower() in ["무릎", "무릎 통증"]:
                    if "무릎" in exercise.target_areas:
                        is_safe = False
                        break
                elif limitation.lower() in ["허리", "허리 통증"]:
                    if "허리" in exercise.target_areas:
                        is_safe = False
                        break
                elif limitation.lower() in ["어깨", "어깨 통증"]:
                    if "어깨" in exercise.target_areas:
                        is_safe = False
                        break

            if is_safe:
                filtered.append(exercise)

        return filtered if filtered else candidates

    def _rank_by_goals(
        self,
        candidates: List[Exercise],
        goals: List[str],
        fitness_assessment: Dict[str, Any]
    ) -> List[Exercise]:
        """목표에 맞게 운동을 우선순위로 정렬합니다."""
        scored = []

        for exercise in candidates:
            score = 0

            # 목표 점수
            if "근력 향상" in goals:
                if exercise.category in ["상체", "하체", "코어"]:
                    score += 3
            if "체력 증진" in goals:
                if exercise.category == "유산소":
                    score += 3
            if "유연성" in goals:
                if exercise.category == "유연성":
                    score += 3
            if "체중 관리" in goals:
                if exercise.category in ["유산소", "종합"]:
                    score += 2

            # 약점 보완
            if "하체 근력" in fitness_assessment.get("weakness_areas", []):
                if exercise.category == "하체":
                    score += 2
            if "심폐 지구력" in fitness_assessment.get("weakness_areas", []):
                if exercise.category == "유산소":
                    score += 2

            # 운동 다양성 (최근에 한 운동을 덜 추천)
            score += 1

            scored.append((exercise, score))

        # 점수로 정렬 (높을수록 먼저)
        scored.sort(key=lambda x: x[1], reverse=True)
        return [exercise for exercise, _ in scored]

    def _generate_recommendation_reason(
        self,
        exercise: Exercise,
        profile: UserProfile,
        fitness_assessment: Dict[str, Any]
    ) -> str:
        """추천 이유를 생성합니다."""
        reasons = []

        if exercise.category == "하체":
            reasons.append("하체 근력 강화")
        elif exercise.category == "상체":
            reasons.append("상체 근력 강화")
        elif exercise.category == "유산소":
            reasons.append("심폐 지구력 향상")
        elif exercise.category == "유연성":
            reasons.append("유연성 개선")
        elif exercise.category == "코어":
            reasons.append("코어 근력 강화")

        if "근력 향상" in profile.goals:
            reasons.append("목표: 근력 향상")
        if "체력 증진" in profile.goals:
            reasons.append("목표: 체력 증진")

        if "하체 근력" in fitness_assessment.get("weakness_areas", []):
            if exercise.category == "하체":
                reasons.append("약점 보완")
        if "심폐 지구력" in fitness_assessment.get("weakness_areas", []):
            if exercise.category == "유산소":
                reasons.append("약점 보완")

        return ", ".join(reasons) if reasons else "건강한 생활 유지"

    def _generate_tips(self, exercise: Exercise, profile: UserProfile) -> List[str]:
        """운동 팁을 생성합니다."""
        tips = []

        if exercise.difficulty == "초보자":
            tips.append("초보자도 쉽게 할 수 있습니다.")
        elif exercise.difficulty == "중급자":
            tips.append("기초 운동을 한 후에 시작하는 것이 좋습니다.")

        if profile.available_time_minutes < 20:
            tips.append("짧은 시간에 완료할 수 있습니다.")
        else:
            tips.append("여유 있게 진행할 수 있습니다.")

        if profile.fitness_level == "초보자":
            tips.append("천천히 시작하고 점진적으로 강도를 높이세요.")

        tips.append(exercise.precautions)

        return tips


def save_recommendation_to_db(
    exercise_name: str,
    reason: str,
    difficulty: str,
    duration_minutes: int
) -> None:
    """추천한 운동을 데이터베이스에 저장합니다."""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    try:
        c.execute(
            """INSERT INTO exercise_recommendations 
               (user_id, recommendation_date, exercise_type, reason, difficulty, duration_minutes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            ("default", datetime.now().strftime("%Y-%m-%d"), exercise_name, reason, difficulty, duration_minutes)
        )
        conn.commit()
    except sqlite3.OperationalError:
        # 테이블이 없으면 무시
        pass
    finally:
        conn.close()


def get_recent_recommendations(limit: int = 10) -> List[Dict[str, Any]]:
    """최근 추천 운동을 조회합니다."""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    try:
        c.execute(
            """SELECT exercise_type, reason, difficulty, duration_minutes, recommendation_date
               FROM exercise_recommendations
               ORDER BY recommendation_date DESC
               LIMIT ?""",
            (limit,)
        )
        rows = c.fetchall()
        return [
            {
                "exercise": row[0],
                "reason": row[1],
                "difficulty": row[2],
                "duration_minutes": row[3],
                "date": row[4],
            }
            for row in rows
        ]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()

import math
from typing import Dict, List, Optional, Tuple, Any
from collections import deque

Point = Tuple[int, int]
JointData = Dict[str, Any]


class WalkAnalyzer:
    """보행 분석 엔진: 걸음 수, 케이던스, 좌우 균형을 분석합니다."""

    WALK_IDLE = "준비"
    WALK_ACTIVE = "보행 중"

    def __init__(self) -> None:
        self.step_count = 0
        self.walk_phase = self.WALK_IDLE
        self.cadence = 0.0  # 분당 걸음 수
        self.walk_time_seconds = 0.0
        self.left_right_balance = 50.0  # 좌발 사용률 (0-100)
        self.gait_symmetry = 0.0  # 보행 대칭성 점수 (0-100)
        self.posture_status = "준비"
        self.feedback_messages: List[str] = []
        self.walking_speed = 0.0  # 보행 속도 (걸음/초)
        self.stride_length = 0.0  # 보행 길이 (추정)
        self.body_sway = 0.0  # 신체 흔들림 정도 (0-100)
        self.leg_lift_symmetry = 0.0  # 다리 들기 대칭성 (0-100)
        self.posture_consistency = 0.0  # 자세 일관성 (0-100)

        self._left_foot_down_frames: List[int] = []
        self._right_foot_down_frames: List[int] = []
        self._previous_left_ankle_y: Optional[float] = None
        self._previous_right_ankle_y: Optional[float] = None
        self._previous_left_knee_y: Optional[float] = None
        self._previous_right_knee_y: Optional[float] = None
        self._left_foot_rising = False
        self._right_foot_rising = False
        self._last_left_step_ms: Optional[int] = None
        self._last_right_step_ms: Optional[int] = None
        self._start_time_ms: Optional[int] = None
        self._analyzed_frames = 0
        self._posture_ok_frames = 0
        self._completed_steps: List[Dict[str, Any]] = []
        
        # 보행 감지 개선: 슬라이딩 윈도우로 노이즈 필터링
        self._ankle_y_buffer_left: deque = deque(maxlen=5)
        self._ankle_y_buffer_right: deque = deque(maxlen=5)
        self._knee_height_buffer_left: deque = deque(maxlen=5)
        self._knee_height_buffer_right: deque = deque(maxlen=5)
        
        # 보행 분석 데이터
        self._left_knee_lift_heights: List[float] = []
        self._right_knee_lift_heights: List[float] = []
        self._trunk_tilt_history: List[float] = []
        self._shoulder_symmetry_history: List[float] = []
        
        # 단계별 분석
        self._step_details: List[Dict[str, Any]] = []

    def reset(self) -> None:
        """보행 분석 상태를 초기화합니다."""
        self.step_count = 0
        self.walk_phase = self.WALK_IDLE
        self.cadence = 0.0
        self.walk_time_seconds = 0.0
        self.left_right_balance = 50.0
        self.gait_symmetry = 0.0
        self.posture_status = "준비"
        self.feedback_messages = []
        self.walking_speed = 0.0
        self.stride_length = 0.0
        self.body_sway = 0.0
        self.leg_lift_symmetry = 0.0
        self.posture_consistency = 0.0

        self._left_foot_down_frames = []
        self._right_foot_down_frames = []
        self._previous_left_ankle_y = None
        self._previous_right_ankle_y = None
        self._previous_left_knee_y = None
        self._previous_right_knee_y = None
        self._left_foot_rising = False
        self._right_foot_rising = False
        self._last_left_step_ms = None
        self._last_right_step_ms = None
        self._start_time_ms = None
        self._analyzed_frames = 0
        self._posture_ok_frames = 0
        self._completed_steps = []
        
        self._ankle_y_buffer_left.clear()
        self._ankle_y_buffer_right.clear()
        self._knee_height_buffer_left.clear()
        self._knee_height_buffer_right.clear()
        
        self._left_knee_lift_heights = []
        self._right_knee_lift_heights = []
        self._trunk_tilt_history = []
        self._shoulder_symmetry_history = []
        
        self._step_details = []

    def posture_accuracy_percent(self) -> float:
        """자세 정확도를 반환합니다 (0-100%)."""
        if self._analyzed_frames == 0:
            return 0.0
        return (self._posture_ok_frames / self._analyzed_frames) * 100.0

    @staticmethod
    def _calculate_trunk_tilt_deg(joints: Dict[str, JointData]) -> float:
        """상체 기울기를 계산합니다."""
        left_shoulder = joints["left_shoulder"]["point"]
        right_shoulder = joints["right_shoulder"]["point"]
        left_hip = joints["left_hip"]["point"]
        right_hip = joints["right_hip"]["point"]

        shoulder_mid = (
            (left_shoulder[0] + right_shoulder[0]) / 2.0,
            (left_shoulder[1] + right_shoulder[1]) / 2.0,
        )
        hip_mid = (
            (left_hip[0] + right_hip[0]) / 2.0,
            (left_hip[1] + right_hip[1]) / 2.0,
        )

        dx = shoulder_mid[0] - hip_mid[0]
        dy = shoulder_mid[1] - hip_mid[1]

        if dx == 0 and dy == 0:
            return 0.0
        return abs(math.degrees(math.atan2(abs(dx), abs(dy))))

    @staticmethod
    def _calculate_shoulder_symmetry(joints: Dict[str, JointData]) -> float:
        """어깨 수평 대칭성을 계산합니다 (0-100)."""
        left_shoulder = joints["left_shoulder"]["point"]
        right_shoulder = joints["right_shoulder"]["point"]
        
        offset = abs(left_shoulder[1] - right_shoulder[1])
        
        # 50픽셀 이상 차이 = 0점, 차이 없음 = 100점
        if offset > 50:
            return 0.0
        return max(0.0, 100.0 - (offset * 2.0))

    @staticmethod
    def _calculate_body_sway(joints: Dict[str, JointData], previous_hip_x: Optional[float]) -> Tuple[float, float]:
        """신체 흔들림 정도를 계산합니다."""
        left_hip = joints["left_hip"]["point"]
        right_hip = joints["right_hip"]["point"]
        
        hip_mid_x = (left_hip[0] + right_hip[0]) / 2.0
        
        if previous_hip_x is None:
            return 0.0, hip_mid_x
        
        # 프레임 간 엉덩이 위치 변화
        sway_px = abs(hip_mid_x - previous_hip_x)
        
        # 정상 보행: 5픽셀 이하, 흔들림: 20픽셀 이상
        if sway_px > 20:
            sway_score = min(100.0, (sway_px - 20) * 5.0)
        else:
            sway_score = 0.0
        
        return sway_score, hip_mid_x

    @staticmethod
    def _avg_confidence(joints: Dict[str, JointData], names: List[str]) -> float:
        """지정된 관절의 평균 신뢰도를 반환합니다."""
        values = [joints[name]["confidence"] for name in names if name in joints]
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _is_joint_ready(self, joints: Dict[str, JointData], names: List[str], threshold: float) -> bool:
        """필요한 관절이 모두 감지되고 신뢰도가 충분한지 확인합니다."""
        for name in names:
            if name not in joints:
                return False
            if joints[name]["confidence"] < threshold:
                return False
        return True

    def _make_feedback(
        self,
        joints: Dict[str, JointData],
        trunk_tilt_deg: float,
        body_sway: float,
        shoulder_symmetry: float,
    ) -> List[str]:
        """보행 중 자세에 대한 피드백을 생성합니다."""
        messages: List[str] = []

        # 상체 기울기 체크
        if trunk_tilt_deg > 20:
            messages.append("상체를 펴고 걸어주세요.")

        # 어깨 대칭성 체크
        if shoulder_symmetry < 50:
            messages.append("어깨 높이를 맞춰주세요.")

        # 신체 흔들림 체크
        if body_sway > 50:
            messages.append("안정적으로 걸어주세요.")

        return messages

    def _smooth_ankle_position(self, ankle_y: float, buffer: deque) -> float:
        """슬라이딩 윈도우 필터로 발목 위치를 평활화합니다."""
        buffer.append(ankle_y)
        if len(buffer) == 0:
            return ankle_y
        return sum(buffer) / len(buffer)

    def _detect_step_v2(
        self,
        left_ankle_y: float,
        right_ankle_y: float,
        left_knee_y: float,
        right_knee_y: float,
        now_ms: int,
    ) -> int:
        """
        개선된 발 감지: 발목뿐만 아니라 무릎도 고려하여
        더 정확한 걸음 감지를 수행합니다.
        """
        new_steps = 0

        # 발목 위치 평활화 (노이즈 제거)
        smooth_left_ankle = self._smooth_ankle_position(left_ankle_y, self._ankle_y_buffer_left)
        smooth_right_ankle = self._smooth_ankle_position(right_ankle_y, self._ankle_y_buffer_right)
        smooth_left_knee = self._smooth_ankle_position(left_knee_y, self._knee_height_buffer_left)
        smooth_right_knee = self._smooth_ankle_position(right_knee_y, self._knee_height_buffer_right)

        # 왼발 걸음 감지
        if self._previous_left_ankle_y is not None and self._previous_left_knee_y is not None:
            prev_ankle_y = self._previous_left_ankle_y
            curr_ankle_y = smooth_left_ankle
            prev_knee_y = self._previous_left_knee_y
            curr_knee_y = smooth_left_knee

            # 발목이 올라오고 무릎도 올라오면: 발이 든 상태
            if curr_ankle_y < prev_ankle_y - 15 and curr_knee_y < prev_knee_y - 10:
                if not self._left_foot_rising:
                    self._left_foot_rising = True
            
            # 발목이 내려오고 무릎도 내려오면: 발이 내려온 상태 (발자국)
            elif curr_ankle_y > prev_ankle_y + 15 and curr_knee_y > prev_knee_y + 10 and self._left_foot_rising:
                self._left_foot_rising = False
                # 최소 400ms 간격 (보행 케이던스 ~150/min 이상)
                if self._last_left_step_ms is None or (now_ms - self._last_left_step_ms) > 400:
                    new_steps += 1
                    self._last_left_step_ms = now_ms
                    self._left_foot_down_frames.append(now_ms)
                    self._left_knee_lift_heights.append(prev_knee_y - curr_knee_y)

        # 오른발 걸음 감지 (동일 로직)
        if self._previous_right_ankle_y is not None and self._previous_right_knee_y is not None:
            prev_ankle_y = self._previous_right_ankle_y
            curr_ankle_y = smooth_right_ankle
            prev_knee_y = self._previous_right_knee_y
            curr_knee_y = smooth_right_knee

            if curr_ankle_y < prev_ankle_y - 15 and curr_knee_y < prev_knee_y - 10:
                if not self._right_foot_rising:
                    self._right_foot_rising = True
            
            elif curr_ankle_y > prev_ankle_y + 15 and curr_knee_y > prev_knee_y + 10 and self._right_foot_rising:
                self._right_foot_rising = False
                if self._last_right_step_ms is None or (now_ms - self._last_right_step_ms) > 400:
                    new_steps += 1
                    self._last_right_step_ms = now_ms
                    self._right_foot_down_frames.append(now_ms)
                    self._right_knee_lift_heights.append(prev_knee_y - curr_knee_y)

        self._previous_left_ankle_y = smooth_left_ankle
        self._previous_right_ankle_y = smooth_right_ankle
        self._previous_left_knee_y = smooth_left_knee
        self._previous_right_knee_y = smooth_right_knee

        return new_steps

    def _calculate_left_right_balance(self) -> float:
        """좌발과 우발의 사용 비율을 계산합니다."""
        total_frames = len(self._left_foot_down_frames) + len(self._right_foot_down_frames)
        if total_frames == 0:
            return 50.0
        left_percent = (len(self._left_foot_down_frames) / total_frames) * 100.0
        return max(0.0, min(100.0, left_percent))

    def _calculate_gait_symmetry(self) -> float:
        """보행 대칭성을 평가합니다 (0-100)."""
        if len(self._left_foot_down_frames) < 3 or len(self._right_foot_down_frames) < 3:
            return 0.0

        def calculate_intervals(frames: List[int]) -> List[float]:
            if len(frames) < 2:
                return []
            intervals = [
                (frames[i] - frames[i - 1]) / 1000.0 for i in range(1, len(frames))
            ]
            return intervals

        left_intervals = calculate_intervals(self._left_foot_down_frames)
        right_intervals = calculate_intervals(self._right_foot_down_frames)

        if not left_intervals or not right_intervals:
            return 0.0

        # 평균 간격
        left_avg = sum(left_intervals) / len(left_intervals)
        right_avg = sum(right_intervals) / len(right_intervals)

        if left_avg == 0 or right_avg == 0:
            return 0.0

        # 편차 계산
        left_variance = sum((x - left_avg) ** 2 for x in left_intervals) / len(left_intervals)
        right_variance = sum((x - right_avg) ** 2 for x in right_intervals) / len(right_intervals)
        
        # 이상적인 보행: 양쪽 간격이 같고 편차가 작음
        interval_diff = abs(left_avg - right_avg) / max(left_avg, right_avg)
        variance_score = math.sqrt((left_variance + right_variance) / 2.0)
        
        # 대칭성 점수 계산
        symmetry = 100.0 - (interval_diff * 50.0) - (variance_score * 10.0)
        return max(0.0, min(100.0, symmetry))

    def _calculate_leg_lift_symmetry(self) -> float:
        """좌우 다리 들기 높이의 대칭성을 계산합니다 (0-100)."""
        if len(self._left_knee_lift_heights) < 2 or len(self._right_knee_lift_heights) < 2:
            return 0.0
        
        left_avg = sum(self._left_knee_lift_heights) / len(self._left_knee_lift_heights)
        right_avg = sum(self._right_knee_lift_heights) / len(self._right_knee_lift_heights)
        
        if left_avg == 0 or right_avg == 0:
            return 0.0
        
        # 무릎 들기 높이 차이
        height_diff = abs(left_avg - right_avg) / max(left_avg, right_avg)
        symmetry = max(0.0, 100.0 - (height_diff * 100.0))
        return symmetry

    def _calculate_posture_consistency(self) -> float:
        """보행 중 자세 일관성을 계산합니다 (0-100)."""
        if len(self._trunk_tilt_history) < 5:
            return 0.0
        
        avg_tilt = sum(self._trunk_tilt_history) / len(self._trunk_tilt_history)
        variance = sum((x - avg_tilt) ** 2 for x in self._trunk_tilt_history) / len(self._trunk_tilt_history)
        std_dev = math.sqrt(variance)
        
        # 표준편차가 작을수록 일관성이 높음
        # 5도 이상 편차 = 0점, 편차 없음 = 100점
        consistency = max(0.0, 100.0 - (std_dev * 10.0))
        return min(100.0, consistency)

    def _calculate_walking_speed(self) -> float:
        """보행 속도를 계산합니다 (걸음/초)."""
        if self.walk_time_seconds <= 0 or self.step_count == 0:
            return 0.0
        return self.step_count / self.walk_time_seconds

    def get_step_frequency_analysis(self) -> Dict[str, float]:
        """걸음 주기 분석을 반환합니다."""
        result = {
            "left_step_count": len(self._left_foot_down_frames),
            "right_step_count": len(self._right_foot_down_frames),
            "left_avg_interval_sec": 0.0,
            "right_avg_interval_sec": 0.0,
        }
        
        def get_avg_interval(frames: List[int]) -> float:
            if len(frames) < 2:
                return 0.0
            intervals = [(frames[i] - frames[i-1]) / 1000.0 for i in range(1, len(frames))]
            return sum(intervals) / len(intervals) if intervals else 0.0
        
        result["left_avg_interval_sec"] = get_avg_interval(self._left_foot_down_frames)
        result["right_avg_interval_sec"] = get_avg_interval(self._right_foot_down_frames)
        
        return result

    def update(
        self,
        joints: Dict[str, JointData],
        now_ms: int,
        analyze_enabled: bool,
    ) -> Dict[str, object]:
        """각 프레임마다 호출되어 보행 상태를 업데이트합니다."""
        required = [
            "left_shoulder",
            "right_shoulder",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle",
        ]
        conf_threshold = 0.55

        joints_ready = self._is_joint_ready(joints, required, conf_threshold)

        if not joints_ready:
            self.posture_status = "관절 인식 대기"
            self.feedback_messages = [
                "관절 인식이 불안정합니다. 카메라와 조명을 조정하세요."
            ]
            return {
                "step_count": self.step_count,
                "cadence": self.cadence,
                "walk_time_seconds": self.walk_time_seconds,
                "left_right_balance": self.left_right_balance,
                "gait_symmetry": self.gait_symmetry,
                "posture_status": self.posture_status,
                "feedback": self.feedback_messages,
                "coaching_message": self.feedback_messages[0] if self.feedback_messages else "관절을 인식 중입니다.",
                "posture_ok": False,
                "confidence_ok": False,
                "avg_confidence": 0.0,
                "walking_speed": self.walking_speed,
                "body_sway": self.body_sway,
                "leg_lift_symmetry": self.leg_lift_symmetry,
                "posture_consistency": self.posture_consistency,
                "posture_accuracy_percent": 0.0,
            }

        # 초기화
        if self._start_time_ms is None and analyze_enabled:
            self._start_time_ms = now_ms

        # 관절 좌표 추출
        left_ankle_y = float(joints["left_ankle"]["point"][1])
        right_ankle_y = float(joints["right_ankle"]["point"][1])
        left_knee_y = float(joints["left_knee"]["point"][1])
        right_knee_y = float(joints["right_knee"]["point"][1])

        # 개선된 발 감지 (무릎도 고려)
        new_steps = self._detect_step_v2(left_ankle_y, right_ankle_y, left_knee_y, right_knee_y, now_ms)
        self.step_count += new_steps

        # 상체 기울기 계산
        trunk_tilt_deg = self._calculate_trunk_tilt_deg(joints)
        self._trunk_tilt_history.append(trunk_tilt_deg)
        if len(self._trunk_tilt_history) > 100:
            self._trunk_tilt_history.pop(0)

        # 어깨 대칭성
        shoulder_symmetry = self._calculate_shoulder_symmetry(joints)
        self._shoulder_symmetry_history.append(shoulder_symmetry)
        if len(self._shoulder_symmetry_history) > 100:
            self._shoulder_symmetry_history.pop(0)

        # 신체 흔들림 계산
        hip_mid_x = (joints["left_hip"]["point"][0] + joints["right_hip"]["point"][0]) / 2.0
        self.body_sway, _ = self._calculate_body_sway(joints, getattr(self, "_prev_hip_x", None))
        self._prev_hip_x = hip_mid_x

        # 자세 피드백
        self.feedback_messages = self._make_feedback(joints, trunk_tilt_deg, self.body_sway, shoulder_symmetry)
        posture_ok = len(self.feedback_messages) == 0

        # 분석 프레임 카운트
        if analyze_enabled:
            self._analyzed_frames += 1
            if posture_ok:
                self._posture_ok_frames += 1

        # 보행 시간 계산
        if analyze_enabled and self._start_time_ms is not None:
            self.walk_time_seconds = (now_ms - self._start_time_ms) / 1000.0

        # 케이던스 계산 (분당 걸음 수)
        if self.walk_time_seconds > 0:
            walk_minutes = self.walk_time_seconds / 60.0
            if walk_minutes > 0:
                self.cadence = self.step_count / walk_minutes
        else:
            self.cadence = 0.0

        # 보행 속도
        self.walking_speed = self._calculate_walking_speed()

        # 좌우 균형
        self.left_right_balance = self._calculate_left_right_balance()

        # 보행 대칭성
        self.gait_symmetry = self._calculate_gait_symmetry()

        # 다리 들기 대칭성
        self.leg_lift_symmetry = self._calculate_leg_lift_symmetry()

        # 자세 일관성
        self.posture_consistency = self._calculate_posture_consistency()

        # 보행 상태 판정
        if self.step_count > 0:
            self.walk_phase = self.WALK_ACTIVE
        else:
            self.walk_phase = self.WALK_IDLE

        # 자세 상태
        if not posture_ok:
            self.posture_status = "주의 필요"
        elif self.step_count > 0:
            self.posture_status = "양호"
        else:
            self.posture_status = "준비"

        coaching_message = "자연스럽게 걸어주세요."
        if self.step_count > 0:
            coaching_message = f"좋은 자세입니다. 계속 걸어주세요. ({self.step_count}걸음)"
        if not posture_ok and self.feedback_messages:
            coaching_message = self.feedback_messages[0]

        avg_confidence = self._avg_confidence(joints, required)

        return {
            "step_count": self.step_count,
            "cadence": self.cadence,
            "walk_time_seconds": self.walk_time_seconds,
            "left_right_balance": self.left_right_balance,
            "gait_symmetry": self.gait_symmetry,
            "posture_status": self.posture_status,
            "feedback": self.feedback_messages,
            "coaching_message": coaching_message,
            "posture_ok": posture_ok,
            "confidence_ok": True,
            "avg_confidence": avg_confidence,
            "posture_accuracy_percent": self.posture_accuracy_percent(),
            "walking_speed": self.walking_speed,
            "body_sway": self.body_sway,
            "leg_lift_symmetry": self.leg_lift_symmetry,
            "posture_consistency": self.posture_consistency,
        }

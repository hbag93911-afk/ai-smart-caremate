import math
from typing import Dict, List, Optional, Tuple, Any


Point = Tuple[int, int]
JointData = Dict[str, Any]


class SquatAnalyzer:
    STANDING = "서 있는 상태"
    DESCENDING = "내려가는 상태"
    BOTTOM = "앉은 상태"
    ASCENDING = "올라오는 상태"

    def __init__(self) -> None:
        self.squat_count = 0
        self.phase = self.STANDING
        self.last_knee_angle: Optional[float] = None
        self.low_confidence = True
        self.feedback_messages: List[str] = []
        self.knee_angle = 180.0
        self.trunk_tilt_deg = 0.0
        self.depth_level = "낮음"
        self.speed_deg_per_sec = 0.0
        self.posture_status = "관절 인식 대기"
        self.session_summary: Dict[str, Any] = {
            "count": 0,
            "avg_knee_angle": 0.0,
            "avg_trunk_tilt_deg": 0.0,
            "avg_speed_deg_per_sec": 0.0,
            "best_depth": "낮음",
        }

        self._did_reach_bottom = False
        self._last_phase_change_ms: Optional[int] = None
        self._squat_start_ms: Optional[int] = None
        self._left_knee_angle: Optional[float] = None
        self._right_knee_angle: Optional[float] = None
        self._previous_angle: Optional[float] = None
        self._previous_time_ms: Optional[int] = None
        self._completed_summary: List[Dict[str, Any]] = []
        self._rep_has_warning = False
        self._rep_min_knee_angle: Optional[float] = None
        self._rep_max_trunk_tilt: float = 0.0
        self._posture_ok_frames = 0
        self._analyzed_frames = 0

    def reset(self) -> None:
        self.squat_count = 0
        self.phase = self.STANDING
        self.last_knee_angle = None
        self.low_confidence = True
        self.feedback_messages = []
        self.knee_angle = 180.0
        self.trunk_tilt_deg = 0.0
        self.depth_level = "낮음"
        self.speed_deg_per_sec = 0.0
        self.posture_status = "관절 인식 대기"
        self.session_summary = {
            "count": 0,
            "avg_knee_angle": 0.0,
            "avg_trunk_tilt_deg": 0.0,
            "avg_speed_deg_per_sec": 0.0,
            "best_depth": "낮음",
        }
        self._did_reach_bottom = False
        self._last_phase_change_ms = None
        self._squat_start_ms = None
        self._left_knee_angle = None
        self._right_knee_angle = None
        self._previous_angle = None
        self._previous_time_ms = None
        self._completed_summary = []
        self._rep_has_warning = False
        self._rep_min_knee_angle = None
        self._rep_max_trunk_tilt = 0.0
        self._posture_ok_frames = 0
        self._analyzed_frames = 0

    def posture_accuracy_percent(self) -> float:
        if self._analyzed_frames == 0:
            return 0.0
        return (self._posture_ok_frames / self._analyzed_frames) * 100.0

    @staticmethod
    def _calculate_angle(a: Point, b: Point, c: Point) -> float:
        ab = (a[0] - b[0], a[1] - b[1])
        cb = (c[0] - b[0], c[1] - b[1])

        dot = ab[0] * cb[0] + ab[1] * cb[1]
        mag_ab = math.sqrt(ab[0] ** 2 + ab[1] ** 2)
        mag_cb = math.sqrt(cb[0] ** 2 + cb[1] ** 2)
        if mag_ab == 0 or mag_cb == 0:
            return 180.0

        cos_value = max(-1.0, min(1.0, dot / (mag_ab * mag_cb)))
        return math.degrees(math.acos(cos_value))

    @staticmethod
    def _calculate_trunk_tilt_deg(joints: Dict[str, JointData]) -> float:
        left_shoulder = joints["left_shoulder"]["point"]
        right_shoulder = joints["right_shoulder"]["point"]
        left_hip = joints["left_hip"]["point"]
        right_hip = joints["right_hip"]["point"]
        shoulder_mid = ((left_shoulder[0] + right_shoulder[0]) / 2.0, (left_shoulder[1] + right_shoulder[1]) / 2.0)
        hip_mid = ((left_hip[0] + right_hip[0]) / 2.0, (left_hip[1] + right_hip[1]) / 2.0)
        dx = shoulder_mid[0] - hip_mid[0]
        dy = shoulder_mid[1] - hip_mid[1]
        if dx == 0 and dy == 0:
            return 0.0
        return abs(math.degrees(math.atan2(abs(dx), abs(dy))))

    @staticmethod
    def _avg_confidence(joints: Dict[str, JointData], names: List[str]) -> float:
        values = [joints[name]["confidence"] for name in names if name in joints]
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _is_joint_ready(self, joints: Dict[str, JointData], names: List[str], threshold: float) -> bool:
        for name in names:
            if name not in joints:
                return False
            if joints[name]["confidence"] < threshold:
                return False
        return True

    @staticmethod
    def _classify_depth(knee_angle: float) -> str:
        if knee_angle <= 85:
            return "깊음"
        if knee_angle <= 110:
            return "보통"
        return "얕음"

    @staticmethod
    def _movement_speed_deg_per_sec(prev_angle: Optional[float], curr_angle: Optional[float], prev_ms: Optional[int], curr_ms: int) -> float:
        if prev_angle is None or prev_ms is None or curr_ms <= prev_ms:
            return 0.0
        delta_angle = abs(curr_angle - prev_angle)
        elapsed_sec = (curr_ms - prev_ms) / 1000.0
        if elapsed_sec <= 0:
            return 0.0
        return delta_angle / elapsed_sec

    def _is_rep_stable(self) -> bool:
        if self._rep_min_knee_angle is None:
            return False
        enough_depth = self._rep_min_knee_angle <= 110.0
        stable_trunk = self._rep_max_trunk_tilt <= 30.0
        return enough_depth and stable_trunk and (not self._rep_has_warning)

    def _update_phase(self, angle: float, now_ms: int) -> bool:
        standing_angle = 165.0
        bottom_angle = 105.0
        descending_trigger = 150.0
        ascending_trigger = 125.0
        counted_this_frame = False

        if self.phase == self.STANDING:
            if angle < descending_trigger:
                self.phase = self.DESCENDING
                self._squat_start_ms = now_ms
                self._last_phase_change_ms = now_ms
                self._rep_has_warning = False
                self._rep_min_knee_angle = angle
                self._rep_max_trunk_tilt = 0.0

        elif self.phase == self.DESCENDING:
            if angle <= bottom_angle:
                self.phase = self.BOTTOM
                self._did_reach_bottom = True
                self._last_phase_change_ms = now_ms
            elif angle >= standing_angle:
                self.phase = self.STANDING
                self._did_reach_bottom = False
                self._squat_start_ms = None
                self._last_phase_change_ms = now_ms

        elif self.phase == self.BOTTOM:
            if angle > ascending_trigger:
                self.phase = self.ASCENDING
                self._last_phase_change_ms = now_ms

        elif self.phase == self.ASCENDING:
            if angle >= standing_angle and self._did_reach_bottom:
                if self._is_rep_stable():
                    self.squat_count += 1
                    counted_this_frame = True
                self.phase = self.STANDING
                self._did_reach_bottom = False
                self._last_phase_change_ms = now_ms
                self._completed_summary.append({
                    "count": self.squat_count,
                    "knee_angle": angle,
                    "timestamp_ms": now_ms,
                })
            elif angle < ascending_trigger:
                self.phase = self.BOTTOM
                self._last_phase_change_ms = now_ms
        return counted_this_frame

    def _make_feedback(self, joints: Dict[str, JointData], knee_angle: float, trunk_tilt_deg: float, speed_deg_per_sec: float) -> List[str]:
        messages: List[str] = []

        left_knee = joints["left_knee"]["point"]
        left_ankle = joints["left_ankle"]["point"]
        right_knee = joints["right_knee"]["point"]
        right_ankle = joints["right_ankle"]["point"]

        knee_ankle_offset_left = abs(left_knee[0] - left_ankle[0])
        knee_ankle_offset_right = abs(right_knee[0] - right_ankle[0])
        if knee_ankle_offset_left > 55 or knee_ankle_offset_right > 55:
            messages.append("무릎 방향을 발끝 방향과 맞춰주세요.")

        if trunk_tilt_deg > 35:
            messages.append("상체를 세워주세요.")

        if speed_deg_per_sec > 60:
            messages.append("동작 속도를 조금 늦춰주세요.")

        if knee_angle > 110 and self.phase in (self.DESCENDING, self.BOTTOM):
            messages.append("무릎을 조금 더 굽혀주세요.")
        elif knee_angle < 70:
            messages.append("너무 깊게 앉고 있어요. 무릎 각도를 조금 펴주세요.")

        return messages

    def _build_summary(self) -> Dict[str, Any]:
        count = self.squat_count
        if not self._completed_summary:
            return {
                "count": count,
                "avg_knee_angle": 0.0,
                "avg_trunk_tilt_deg": 0.0,
                "avg_speed_deg_per_sec": 0.0,
                "best_depth": "낮음",
            }
        knee_values = [item["knee_angle"] for item in self._completed_summary]
        avg_knee = sum(knee_values) / len(knee_values)
        best_depth = self._classify_depth(min(knee_values))
        return {
            "count": count,
            "avg_knee_angle": avg_knee,
            "avg_trunk_tilt_deg": 0.0,
            "avg_speed_deg_per_sec": 0.0,
            "best_depth": best_depth,
        }

    def update(
        self,
        joints: Dict[str, JointData],
        now_ms: int,
        analyze_enabled: bool,
    ) -> Dict[str, object]:
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
            self.low_confidence = True
            self.last_knee_angle = None
            self.feedback_messages = ["관절 인식 신뢰도가 낮습니다. 카메라 위치, 거리, 조명을 조정해 주세요."]
            self.posture_status = "주의 필요"
            if not analyze_enabled:
                self.phase = self.STANDING
                self._did_reach_bottom = False
                self._squat_start_ms = None
            return {
                "angle": None,
                "count": self.squat_count,
                "phase": self.phase,
                "confidence_ok": False,
                "feedback": self.feedback_messages,
                "coaching_message": self.feedback_messages[0],
                "posture_ok": False,
                "counted_this_frame": False,
                "trunk_tilt_deg": 0.0,
                "depth_level": "분석 대기",
                "speed_deg_per_sec": 0.0,
                "posture_status": self.posture_status,
                "summary": self._build_summary(),
            }

        left_hip = joints["left_hip"]["point"]
        left_knee = joints["left_knee"]["point"]
        left_ankle = joints["left_ankle"]["point"]
        right_hip = joints["right_hip"]["point"]
        right_knee = joints["right_knee"]["point"]
        right_ankle = joints["right_ankle"]["point"]

        self._left_knee_angle = self._calculate_angle(left_hip, left_knee, left_ankle)
        self._right_knee_angle = self._calculate_angle(right_hip, right_knee, right_ankle)
        knee_angle = (self._left_knee_angle + self._right_knee_angle) / 2.0
        self.last_knee_angle = knee_angle
        self.knee_angle = knee_angle

        trunk_tilt_deg = self._calculate_trunk_tilt_deg(joints)
        self.trunk_tilt_deg = trunk_tilt_deg

        self.speed_deg_per_sec = self._movement_speed_deg_per_sec(
            self._previous_angle,
            knee_angle,
            self._previous_time_ms,
            now_ms,
        )
        self._previous_angle = knee_angle
        self._previous_time_ms = now_ms

        self.depth_level = self._classify_depth(knee_angle)
        self.feedback_messages = self._make_feedback(joints, knee_angle, trunk_tilt_deg, self.speed_deg_per_sec)
        posture_ok = len(self.feedback_messages) == 0
        counted_this_frame = False

        if analyze_enabled and self.phase in (self.DESCENDING, self.BOTTOM, self.ASCENDING):
            if self._rep_min_knee_angle is None:
                self._rep_min_knee_angle = knee_angle
            self._rep_min_knee_angle = min(self._rep_min_knee_angle, knee_angle)
            self._rep_max_trunk_tilt = max(self._rep_max_trunk_tilt, trunk_tilt_deg)
            if not posture_ok:
                self._rep_has_warning = True

        if analyze_enabled:
            self._analyzed_frames += 1
            if posture_ok:
                self._posture_ok_frames += 1
            counted_this_frame = self._update_phase(knee_angle, now_ms)

        if not posture_ok:
            self.posture_status = "주의 필요"
        elif self.depth_level == "보통" or self.depth_level == "깊음":
            self.posture_status = "양호"
        else:
            self.posture_status = "참고용 분석"

        coaching_message = "좋은 자세입니다. 현재 자세를 유지하세요."
        if counted_this_frame:
            coaching_message = f"좋은 자세입니다! {self.squat_count}회 성공"
        elif not posture_ok:
            coaching_message = self.feedback_messages[0]

        self.session_summary = self._build_summary()
        self.session_summary["avg_trunk_tilt_deg"] = trunk_tilt_deg
        self.session_summary["avg_speed_deg_per_sec"] = self.speed_deg_per_sec
        self.session_summary["best_depth"] = self.depth_level

        return {
            "angle": knee_angle,
            "count": self.squat_count,
            "phase": self.phase,
            "confidence_ok": True,
            "feedback": self.feedback_messages,
            "coaching_message": coaching_message,
            "posture_ok": posture_ok,
            "counted_this_frame": counted_this_frame,
            "avg_confidence": self._avg_confidence(joints, required),
            "trunk_tilt_deg": trunk_tilt_deg,
            "depth_level": self.depth_level,
            "speed_deg_per_sec": self.speed_deg_per_sec,
            "posture_status": self.posture_status,
            "posture_accuracy_percent": self.posture_accuracy_percent(),
            "summary": self.session_summary,
        }

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
        
        # 향상된 자세 피드백을 위한 추가 추적 변수
        self._posture_history: List[Dict[str, Any]] = []  # 현재 반복의 자세 기록
        self._phase_start_time: Optional[int] = None
        self._frame_count_in_phase = 0
        self._posture_warnings_in_rep: List[Dict[str, Any]] = []  # 현재 반복의 경고 목록
        self._knee_stability_history: List[float] = []  # 무릎 각도 안정성 추적
        self._trunk_stability_history: List[float] = []  # 상체 안정성 추적

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
        
        # 향상된 자세 피드백 리셋
        self._posture_history = []
        self._phase_start_time = None
        self._frame_count_in_phase = 0
        self._posture_warnings_in_rep = []
        self._knee_stability_history = []
        self._trunk_stability_history = []

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
        """향상된 자세 피드백 생성"""
        messages: List[str] = []

        left_knee = joints["left_knee"]["point"]
        left_ankle = joints["left_ankle"]["point"]
        right_knee = joints["right_knee"]["point"]
        right_ankle = joints["right_ankle"]["point"]
        left_hip = joints["left_hip"]["point"]
        right_hip = joints["right_hip"]["point"]
        left_shoulder = joints["left_shoulder"]["point"]
        right_shoulder = joints["right_shoulder"]["point"]

        # 1. 무릎 정렬 확인 (무릎과 발끝이 같은 방향인지)
        knee_ankle_offset_left = abs(left_knee[0] - left_ankle[0])
        knee_ankle_offset_right = abs(right_knee[0] - right_ankle[0])
        if knee_ankle_offset_left > 55 or knee_ankle_offset_right > 55:
            messages.append("[무릎] 무릎 방향을 발끝 방향과 맞춰주세요.")
            self._posture_warnings_in_rep.append({"type": "knee_alignment", "phase": self.phase})

        # 2. 상체 기울기 확인
        if trunk_tilt_deg > 40:
            messages.append("[상체] 상체를 세워주세요. 너무 앞으로 기울어졌습니다.")
            self._posture_warnings_in_rep.append({"type": "trunk_forward", "phase": self.phase})
        elif trunk_tilt_deg > 25:
            messages.append("[상체] 약간 상체가 기울어졌습니다. 더 세워주세요.")
            self._posture_warnings_in_rep.append({"type": "trunk_tilt_slight", "phase": self.phase})

        # 3. 동작 속도 확인
        if speed_deg_per_sec > 70:
            messages.append("[속도] 동작 속도를 조금 늦춰주세요.")
            self._posture_warnings_in_rep.append({"type": "speed_too_fast", "phase": self.phase})

        # 4. 무릎 각도 확인 (단계별로 다르게)
        if self.phase == self.DESCENDING:
            if knee_angle > 130:
                messages.append("[무릎] 무릎을 더 굽혀주세요 (목표: 110도 이하).")
                self._posture_warnings_in_rep.append({"type": "knees_not_bent", "phase": self.phase})
        elif self.phase == self.BOTTOM:
            if knee_angle > 115:
                messages.append("[무릎] 최저점에서 무릎을 더 굽혀주세요 (목표: 100도).")
                self._posture_warnings_in_rep.append({"type": "bottom_too_shallow", "phase": self.phase})
            elif knee_angle < 60:
                messages.append("[무릎] 너무 깊게 앉고 있습니다. 무릎 각도를 조금 펴주세요.")
                self._posture_warnings_in_rep.append({"type": "bottom_too_deep", "phase": self.phase})
        elif self.phase == self.ASCENDING:
            if knee_angle < 90 and self.last_knee_angle and self.last_knee_angle < knee_angle:
                # 올라오는 중에 아직 충분히 펴지지 않음
                pass  # 정상적인 올라오는 과정

        # 5. 왼쪽/오른쪽 균형 확인
        left_knee_y = left_knee[1]
        right_knee_y = right_knee[1]
        knee_height_diff = abs(left_knee_y - right_knee_y)
        
        if knee_height_diff > 40:  # 무릎 높이 차이가 큼 (왼쪽 무릎이 올라가 있거나 내려가 있음)
            if left_knee_y < right_knee_y:
                messages.append("[좌우균형] 오른쪽 무릎이 더 높습니다. 왼쪽 무릎을 더 올려주세요.")
            else:
                messages.append("[좌우균형] 왼쪽 무릎이 더 높습니다. 오른쪽 무릎을 더 올려주세요.")
            self._posture_warnings_in_rep.append({"type": "knee_imbalance", "phase": self.phase})

        # 6. 엉덩이 위치 확인 (무릎과 비교)
        hip_mid_y = (left_hip[1] + right_hip[1]) / 2.0
        knee_mid_y = (left_knee[1] + right_knee[1]) / 2.0
        
        if self.phase in (self.DESCENDING, self.BOTTOM):
            if hip_mid_y < knee_mid_y - 20:  # 엉덩이가 무릎보다 훨씬 올라가 있음
                messages.append("[엉덩이] 엉덩이를 더 내려주세요. 무릎과 엉덩이가 같은 높이가 되도록 해주세요.")
                self._posture_warnings_in_rep.append({"type": "hips_too_high", "phase": self.phase})

        # 7. 어깨 위치 확인
        shoulder_level_diff = abs(left_shoulder[1] - right_shoulder[1])
        if shoulder_level_diff > 50:
            if left_shoulder[1] < right_shoulder[1]:
                messages.append("[어깨] 오른쪽 어깨가 더 내려갔습니다. 양쪽 어깨를 같은 높이로 유지해주세요.")
            else:
                messages.append("[어깨] 왼쪽 어깨가 더 내려갔습니다. 양쪽 어깨를 같은 높이로 유지해주세요.")
            self._posture_warnings_in_rep.append({"type": "shoulder_uneven", "phase": self.phase})

        # 현재 프레임 자세 기록
        self._posture_history.append({
            "phase": self.phase,
            "knee_angle": knee_angle,
            "trunk_tilt": trunk_tilt_deg,
            "speed": speed_deg_per_sec,
            "warnings": len(messages),
        })

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

    def get_posture_feedback_by_phase(self) -> Dict[str, Any]:
        """현재 반복에 대한 단계별 자세 피드백 반환"""
        return {
            "phase": self.phase,
            "phase_name": self._get_phase_name(self.phase),
            "knee_angle": round(self.knee_angle, 1),
            "trunk_tilt": round(self.trunk_tilt_deg, 1),
            "speed": round(self.speed_deg_per_sec, 1),
            "warnings": self._posture_warnings_in_rep.copy(),
            "posture_history": self._posture_history[-10:] if len(self._posture_history) > 10 else self._posture_history.copy(),
        }

    def get_rep_assessment(self) -> Dict[str, Any]:
        """완료된 반복에 대한 전체 평가"""
        if not self._posture_history:
            return {
                "assessment": "분석 대기 중",
                "score": 0,
                "warnings": [],
                "recommendations": [],
            }
        
        total_warnings = sum(1 for frame in self._posture_history if frame["warnings"] > 0)
        frame_count = len(self._posture_history)
        warning_rate = total_warnings / frame_count if frame_count > 0 else 0
        
        # 자세 점수 계산 (0-100)
        posture_score = max(0, 100 - int(warning_rate * 100))
        
        # 단계별 경고 분석
        assessment = self._assess_posture_quality(warning_rate)
        recommendations = self._get_improvement_tips()
        
        return {
            "assessment": assessment,
            "score": posture_score,
            "warning_rate": round(warning_rate, 2),
            "warnings": list(set([w["type"] for w in self._posture_warnings_in_rep])),
            "recommendations": recommendations,
        }

    def _get_phase_name(self, phase: int) -> str:
        """단계 번호를 한글 이름으로 변환"""
        phases = {
            self.STANDING: "서있는 상태",
            self.DESCENDING: "내려가기",
            self.BOTTOM: "최저점",
            self.ASCENDING: "올라오기",
        }
        return phases.get(phase, "알 수 없음")

    def _assess_posture_quality(self, warning_rate: float) -> str:
        """자세 품질 평가"""
        if warning_rate == 0:
            return "✅ 완벽한 자세"
        elif warning_rate < 0.1:
            return "⭐ 훌륭한 자세"
        elif warning_rate < 0.3:
            return "🟢 좋은 자세"
        elif warning_rate < 0.5:
            return "🟡 개선 필요"
        else:
            return "🔴 주의 필요"

    def _get_improvement_tips(self) -> List[str]:
        """자세 개선 팁"""
        tips = []
        
        # 경고 종류별 팁
        warning_types = set([w["type"] for w in self._posture_warnings_in_rep])
        
        if "knee_alignment" in warning_types:
            tips.append("💡 무릎과 발끝을 같은 방향으로 유지하면 무릎 부상을 예방할 수 있습니다.")
        if "trunk_forward" in warning_types or "trunk_tilt_slight" in warning_types:
            tips.append("💡 상체를 세우면 더 많은 근력을 사용하고 안정성이 향상됩니다.")
        if "speed_too_fast" in warning_types:
            tips.append("💡 느린 동작은 근육 활동을 증대시키고 안전성을 높입니다.")
        if "knees_not_bent" in warning_types or "bottom_too_shallow" in warning_types:
            tips.append("💡 더 깊은 스쿼트는 다리 근육을 더 효과적으로 단련합니다.")
        if "bottom_too_deep" in warning_types:
            tips.append("💡 무릎 각도가 너무 작으면 관절에 부담이 갈 수 있습니다.")
        if "knee_imbalance" in warning_types:
            tips.append("💡 양쪽 다리의 균형을 맞추면 근력 차이를 줄일 수 있습니다.")
        if "hips_too_high" in warning_types:
            tips.append("💡 엉덩이를 충분히 내려야 완전한 운동 범위를 활용할 수 있습니다.")
        if "shoulder_uneven" in warning_types:
            tips.append("💡 양쪽 어깨를 같은 높이로 유지하면 척추 정렬이 개선됩니다.")
        
        return tips[:3]  # 상위 3개만 반환

    def _reset_rep_data(self) -> None:
        """반복별 데이터 리셋"""
        self._posture_history = []
        self._posture_warnings_in_rep = []
        self._phase_start_time = None
        self._frame_count_in_phase = 0
        self._knee_stability_history = []
        self._trunk_stability_history = []

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
            
            # 반복이 완료될 때 (STANDING 상태로 돌아왔을 때) 반복 데이터 리셋
            if counted_this_frame and self.phase == self.STANDING:
                self._reset_rep_data()

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

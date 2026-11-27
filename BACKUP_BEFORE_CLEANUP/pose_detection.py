from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class PoseDetector:
    JOINT_INDEX = {
        "left_ear": 7,
        "right_ear": 8,
        "left_shoulder": 11,
        "right_shoulder": 12,
        "left_elbow": 13,
        "right_elbow": 14,
        "left_wrist": 15,
        "right_wrist": 16,
        "left_hip": 23,
        "right_hip": 24,
        "left_knee": 25,
        "right_knee": 26,
        "left_ankle": 27,
        "right_ankle": 28,
    }

    JOINT_CONNECTIONS = (
        ("left_ear", "left_shoulder"),
        ("right_ear", "right_shoulder"),
        ("left_shoulder", "left_elbow"),
        ("left_elbow", "left_wrist"),
        ("right_shoulder", "right_elbow"),
        ("right_elbow", "right_wrist"),
        ("left_shoulder", "left_hip"),
        ("right_shoulder", "right_hip"),
        ("left_hip", "left_knee"),
        ("left_knee", "left_ankle"),
        ("right_hip", "right_knee"),
        ("right_knee", "right_ankle"),
    )

    def __init__(self, model_path: str) -> None:
        model_file = Path(model_path)
        if not model_file.exists():
            raise FileNotFoundError(
                "pose_landmarker_lite.task 파일이 필요합니다. "
                "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task "
                "에서 다운로드하여 app.py와 같은 폴더에 두세요."
            )

        options = vision.PoseLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(model_file)),
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def detect_and_draw(self, frame_bgr, timestamp_ms: int):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection_result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        annotated = frame_bgr.copy()
        if not detection_result.pose_landmarks:
            return annotated, False, {}

        landmarks = detection_result.pose_landmarks[0]
        frame_h, frame_w = annotated.shape[:2]
        points = {}
        joint_data = {}

        for name, index in self.JOINT_INDEX.items():
            landmark = landmarks[index]
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            visibility = float(getattr(landmark, "visibility", 1.0))
            presence = float(getattr(landmark, "presence", 1.0))
            confidence = min(1.0, max(0.0, (visibility + presence) / 2.0))
            if 0 <= x < frame_w and 0 <= y < frame_h:
                points[name] = (x, y)
                joint_data[name] = {
                    "x": x,
                    "y": y,
                    "point": (x, y),
                    "confidence": confidence,
                }
                cv2.circle(annotated, (x, y), 6, (0, 255, 0), -1)

        for start_name, end_name in self.JOINT_CONNECTIONS:
            if start_name in points and end_name in points:
                cv2.line(annotated, points[start_name], points[end_name], (255, 200, 0), 3)

        return annotated, len(points) > 0, joint_data

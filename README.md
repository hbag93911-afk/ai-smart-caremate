# AI 스마트 케어메이트 (AI Smart Caremate)

스마트한 생활 습관과 운동 관리를 위한 **실시간 AI 자세 분석 및 운동 기록 대시보드** 웹 애플리케이션입니다.

## 주요 기능
- **실시간 자세 인식 및 분석**: 카메라 영상과 MediaPipe Pose 모델(`pose_landmark_lite.task`)을 활용해 관절 좌표를 추적하고 자세를 판별합니다.
- **스쿼트 카운팅 및 피드백**: 관절 각도와 움직임을 분석하여 스쿼트 횟수를 자동으로 집계하고 자세 교정 알림을 제공합니다.
- **운동 기록 대시보드**: 일별 운동 횟수, 총 운동 시간, 목표 달성률, 날짜별 운동 추이를 한눈에 확인할 수 있습니다.

## 기술 스택
- **Frontend / Web App**: Python, Streamlit, Altair
- **AI / Computer Vision**: OpenCV (`cv2`), MediaPipe (`pose_landmark_lite.task`)
- **Database**: SQLite (`workout_history.db`)

## 프로젝트 구조
```text
AI 스마트 케어메이트/
├── app.py                     # 메인 Streamlit 대시보드 및 UI 실행 파일
├── camera.py                  # 웹캠 제어 및 영상 스트리밍 모듈
├── pose_detection.py          # 관절 좌표 검출 모듈
├── squat_analysis.py          # 스쿼트 자세 및 횟수 분석 로직
└── pose_landmark_lite.task    # 자세 추정 AI 모델 파일
# 1. 저장소 클론
git clone [https://github.com/hbag93911-afk/ai-smart-caremate.git](https://github.com/hbag93911-afk/ai-smart-caremate.git)
cd ai-smart-caremate

# 2. 필수 패키지 설치
pip install streamlit opencv-python mediapipe altair

# 3. 앱 실행
streamlit run app.py

# AI 스마트 케어메이트 개편 계획서

## 1. 현재 프로젝트 분석

### 1.1 기존 구현된 기능
- ✅ **실시간 카메라 자세 분석** (MediaPipe Pose)
  - 웹캠으로 사용자 촬영
  - 14개 주요 관절(어깨, 팔, 허리, 골반, 무릎, 발목) 인식
  - 관절 좌표와 신뢰도 계산
  - 실시간 스켈레톤 오버레이

- ✅ **스쿼트 분석** (squat_analysis.py)
  - 무릎 각도 계산으로 스쿼트 카운팅
  - 자세 평가 및 피드백
  - 운동 기록 저장

- ✅ **보행 분석** (walk_analysis.py)
  - 걸음 수 카운팅
  - 케이던스(분당 걸음 수) 측정
  - 좌우 균형 분석
  - 보행 속도 및 대칭성 평가

- ✅ **운동 기록 및 통계** (analytics.py)
  - SQLite 데이터베이스로 운동 기록 저장
  - 일일/주간/월간 통계
  - 목표 대비 달성률 계산

- ✅ **목표 관리** (goal_manager.py)
  - 사용자 목표 설정 및 저장
  - 목표 달성률 추적

- ✅ **Streamlit UI**
  - 메인 대시보드
  - 카메라 운동 화면
  - 운동 기록 조회

### 1.2 현재 메뉴 구조
1. 홈 대시보드 - 오늘 운동 요약, 목표 진행률
2. 🎥 카메라 운동 - 스쿼트, 보행 분석
3. 📊 운동 기록 - 일일/주간/월간 통계
4. ⚙️ 환경 설정 - 카메라 설정, 목표 설정

### 1.3 기술 스택
- **Frontend**: Streamlit (Python 웹 프레임워크)
- **CV/AI**: MediaPipe Pose + OpenCV
- **Database**: SQLite
- **Dependencies**: streamlit, opencv-python-headless, mediapipe, altair

---

## 2. 새로 추가할 기능

### 2.1 AI 맞춤형 운동 추천 (신규)
**파일**: `workout_recommendation.py` (신규)
- 사용자 프로필 정보 수집:
  - 현재 체력 수준 (스쿼트 성능, 보행 속도로 추정)
  - 운동 목표 (체중 관리, 근력 향상, 유연성, 체력 증진)
  - 운동 경험 (초보자, 중급자, 고급자)
  - 운동 가능 시간
  - 신체적 제한사항 (무릎 통증, 허리 통증 등)
  - 나이대, 성별 (선택)

- 추천 알고리즘:
  - 현재 자세 분석 결과 기반 약점 파악
  - 사용자 목표와 제한사항 반영
  - 체력 수준별 운동 난이도 조정
  - 운동 조합 제안 (상체, 하체, 코어 균형)

- 추천 운동 타입:
  - 스쿼트 (하체)
  - 걷기/산책 (유산소)
  - 스트레칭 (유연성)
  - 가벼운 홈트레이닝
  - 상체 운동
  - 하체 운동
  - 코어 운동
  - 균형 운동

### 2.2 유튜브 운동 영상 연동 (신규)
**파일**: `youtube_integration.py` (신규)
- YouTube Data API 연동 또는 웹 스크래핑
- 운동별 영상 검색:
  - 초보자/중급자/고급자 별 필터링
  - 영상 길이 필터링 (5분, 10분, 20분 등)
  - 채널 평판 필터링 (구독자 수 등)

- 영상 정보 표시:
  - 제목, 썸네일, 채널명
  - 영상 길이, 조회수
  - 영상 링크 (유튜브 직접 or 임베디드)

- 기능:
  - Streamlit에서 유튜브 영상 임베드 (iframe)
  - 영상 시청 기록 저장
  - 즐겨찾기 기능

### 2.3 실시간 AI 운동 코칭 (기존 확장)
**파일**: `realtime_coaching.py` (신규), `squat_analysis.py` / `walk_analysis.py` (확장)
- 선택한 운동의 카메라 실행
- 실시간 동작 인식 및 카운팅
- 자세 교정 메시지:
  - "무릎이 발끝보다 앞으로 나왔습니다" 같은 구체적 피드백
  - 텍스트 및 음성 알림

- 운동 진행 상황:
  - 현재 반복 횟수 / 목표
  - 세트 진행률
  - 휴식 시간 카운트다운

- 운동 완료 후:
  - 자세 점수 (평균 정확도)
  - 개선 팁
  - 운동 기록 자동 저장

### 2.4 개인별 운동 목표 및 건강 관리 (기존 확장)
**파일**: `goal_manager.py` (확장), `health_tracker.py` (신규)
- 운동별 목표 설정:
  - 주간 운동 시간
  - 주간 운동 횟수
  - 월간 운동 목표

- 건강 지표 추적:
  - 일일 운동 시간 / 목표
  - 주간 운동 로그
  - 월간 운동 통계
  - 운동 종류별 통계

- 개인별 리포트:
  - 최근 1주일/1개월 추세
  - 목표 달성률
  - 가장 자주 한 운동
  - 개선된 운동 성능
  - 건강 개선 지표

### 2.5 메뉴 및 UI 개편
**파일**: `app.py` (대규모 수정)
- 새 메뉴 구조:
  1. 🏠 홈 대시보드 - 오늘 운동 요약, 운동 추천
  2. 🎥 AI 카메라 자세 분석 - 현재 자세 평가
  3. 🤖 AI 맞춤 운동 추천 - 운동 추천 및 상세 정보
  4. 📚 운동 종류별 탐색 - 운동 카테고리 별 조회
  5. 📹 유튜브 운동 영상 - 영상 검색 및 시청
  6. 💪 실시간 AI 운동 코칭 - 운동 선택 후 실시간 분석
  7. 🎯 운동 목표 관리 - 목표 설정 및 추적
  8. 📊 운동 기록 및 통계 - 기존 기능 유지
  9. 📈 종합 건강 리포트 - 통합 분석 보고서
  10. ⚙️ 환경 설정 - 기존 기능 유지

---

## 3. 개발 우선순위 및 단계

### Phase 1: 기초 구조 (우선순위: 높음)
1. ✅ 운동 추천 엔진 (`workout_recommendation.py`)
   - 운동 데이터베이스 (운동 정보, 난이도, 시간)
   - 추천 알고리즘
   - UI 화면

2. ✅ 메뉴 구조 개편 (`app.py`)
   - 기존 메뉴 유지
   - 새 메뉴 추가

3. ✅ 건강 추적 모듈 (`health_tracker.py`)
   - 운동별 목표 설정
   - 통계 계산

### Phase 2: 유튜브 연동 (우선순위: 높음)
1. ✅ YouTube 영상 검색 (`youtube_integration.py`)
   - API 연동 또는 웹 스크래핑
   - 영상 정보 조회

2. ✅ 영상 임베드 및 재생
   - Streamlit iframe 임베드
   - 영상 시청 기록

### Phase 3: 실시간 코칭 (우선순위: 중간)
1. ✅ 실시간 코칭 UI (`realtime_coaching.py`)
   - 운동 선택 후 카메라 실행
   - 동작 카운팅 및 피드백
   - 자세 교정 메시지

2. ✅ 기존 분석기 확장
   - 더 자세한 피드백 메시지
   - 자세 점수 계산

### Phase 4: 종합 리포트 (우선순위: 중간)
1. ✅ 통합 분석 대시보드 (`analytics.py` 확장)
   - 개인별 추이 분석
   - 종합 건강 리포트

---

## 4. 데이터베이스 스키마 (기존 + 신규)

### 기존 테이블
- `workout_records` - 스쿼트 기록
- `walk_records` - 보행 기록
- `goals` - 사용자 목표

### 신규 테이블
```sql
-- 운동 추천 이력
CREATE TABLE IF NOT EXISTS exercise_recommendations (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    recommendation_date DATE,
    exercise_type TEXT,
    reason TEXT,
    difficulty TEXT,
    duration_minutes INTEGER
);

-- 운동 카테고리 및 정보
CREATE TABLE IF NOT EXISTS exercise_library (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    category TEXT,
    description TEXT,
    difficulty TEXT,
    duration_range TEXT,
    benefits TEXT,
    precautions TEXT,
    target_areas TEXT
);

-- 유튜브 영상 캐시
CREATE TABLE IF NOT EXISTS youtube_videos (
    id INTEGER PRIMARY KEY,
    exercise_name TEXT,
    video_id TEXT UNIQUE,
    title TEXT,
    channel TEXT,
    duration INTEGER,
    difficulty TEXT,
    url TEXT,
    thumbnail_url TEXT,
    cached_at TIMESTAMP
);

-- 운동별 세션 기록
CREATE TABLE IF NOT EXISTS exercise_sessions (
    id INTEGER PRIMARY KEY,
    exercise_name TEXT,
    session_date TIMESTAMP,
    duration_seconds INTEGER,
    repetitions INTEGER,
    sets INTEGER,
    posture_score FLOAT,
    notes TEXT
);

-- 종합 건강 지표
CREATE TABLE IF NOT EXISTS health_metrics (
    id INTEGER PRIMARY KEY,
    date DATE,
    total_exercise_minutes INTEGER,
    exercise_variety INTEGER,
    consistency_score FLOAT,
    overall_posture_score FLOAT
);
```

---

## 5. 개발 순서 및 예상 소요 시간

| 단계 | 작업 | 소요시간 | 상태 |
|------|------|---------|------|
| 1 | 메뉴 구조 개편 | 30분 | 준비 |
| 2 | 운동 추천 엔진 구현 | 2시간 | 준비 |
| 3 | 운동 라이브러리 DB 초기화 | 1시간 | 준비 |
| 4 | 유튜브 연동 (영상 검색) | 1.5시간 | 준비 |
| 5 | 유튜브 임베드 UI | 1시간 | 준비 |
| 6 | 건강 추적 모듈 | 1시간 | 준비 |
| 7 | 실시간 코칭 UI | 1시간 | 준비 |
| 8 | 종합 건강 리포트 | 1시간 | 준비 |
| 9 | 테스트 및 버그 수정 | 2시간 | 준비 |
| **총합** | | **약 11시간** | |

---

## 6. 주의사항

### ✅ 지켜야 할 사항
- 기존 `app.py`, `camera.py`, `pose_detection.py`, `squat_analysis.py`, `walk_analysis.py`, `analytics.py`, `goal_manager.py` 파일 유지
- 기존 카메라 및 관절 인식 기능 최대 재사용
- 기존 운동 기록 및 데이터베이스 보존
- 메뉴 추가만 아니라 실제 작동하는 기능 구현
- 유튜브 영상은 공식 API 또는 실제 검색 결과 사용
- 질병 진단 금지 (건강 보조 목적)
- 신체적 제한사항이 있으면 무리한 운동 추천 금지

### ⚠️ 기술적 고려사항
- **카메라 성능**: 실시간 처리 최적화 필요
- **API 제한**: YouTube Data API는 quota 제한 있음
  - 대체 옵션: 웹 스크래핑 또는 사전 영상 데이터베이스
- **데이터베이스**: SQLite의 성능 한계 (대량 데이터 시 고려)
- **메모리**: Streamlit의 세션 상태 관리

---

## 7. 최종 검증 체크리스트

- [ ] 모든 기존 기능이 여전히 작동하는가?
- [ ] 새 메뉴가 모두 표시되는가?
- [ ] 운동 추천이 사용자 프로필에 따라 다르게 나타나는가?
- [ ] 유튜브 영상이 로드되고 재생되는가?
- [ ] 실시간 코칭 중 자세 피드백이 나타나는가?
- [ ] 운동 기록이 정확하게 저장되는가?
- [ ] 종합 건강 리포트가 올바른 데이터를 표시하는가?


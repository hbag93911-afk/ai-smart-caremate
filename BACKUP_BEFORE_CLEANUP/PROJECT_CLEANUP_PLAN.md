## 프로젝트 파일 정리 계획 - 종합 분석 보고서

**작성 일시**: 2026-11-26
**프로젝트**: AI 스마트 케어메이트 (Python + Streamlit)

---

## 1. 현재 프로젝트 상태 분석

### 프로젝트 디렉토리 구조
```
AI 스마트 케어메이트/
├── .venv/                          (Python 가상 환경 - 보존)
├── __pycache__/                    (Python 캐시 - 자동 생성)
├── 핵심 애플리케이션 파일 (10개)
├── 보조 모듈 파일 (11개)
├── 테스트 파일 (5개)
├── 보고서/문서 파일 (27개)
├── 데이터베이스 파일 (2개)
├── 모델 파일 (1개)
└── 구성 파일 (3개)
```

### 전체 파일 통계
- **Python 소스 코드**: 21개 파일
- **문서/보고서**: 27개 파일 (약 310KB)
- **데이터베이스**: 2개 파일 (약 50KB)
- **모델 파일**: 1개 (5.51MB)
- **구성 파일**: 3개

---

## 2. 파일 분류 및 분석

### ① 반드시 필요한 파일 (핵심 애플리케이션)

**A. 메인 애플리케이션**
- `app.py` (약 2000+ 줄)
  - **용도**: 메인 Streamlit 애플리케이션 진입점
  - **상태**: 현재 실행 중 ✓
  - **import 관계**: 11개 모듈 import 함
  - **보존 필요**: ✅ 반드시

**B. 카메라 및 자세 분석 (1순위 필수 기능)**
- `camera.py`
  - **용도**: 카메라 캡처 및 프레임 처리
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: CameraManager, CameraError
  - **보존 필요**: ✅ 반드시

- `pose_detection.py`
  - **용도**: 실시간 관절 인식 (MediaPipe Pose)
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: PoseDetector 클래스
  - **보존 필요**: ✅ 반드시

- `pose_landmarker_lite.task` (5.51MB)
  - **용도**: Google MediaPipe 사전학습 모델
  - **상태**: pose_detection.py에서 사용 중 ✓
  - **보존 필요**: ✅ 반드시

**C. 운동 분석 모듈 (2순위 핵심 기능)**
- `squat_analysis.py`
  - **용도**: 스쿼트 자세 분석
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: SquatAnalyzer 클래스
  - **보존 필요**: ✅ 반드시

- `walk_analysis.py`
  - **용도**: 보행 분석
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: WalkAnalyzer 클래스
  - **보존 필요**: ✅ 반드시

**D. 사용자 맞춤화 및 추천 (3순위 핵심 기능)**
- `workout_recommendation.py`
  - **용도**: AI 맞춤 운동 추천
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: WorkoutRecommender, UserProfile
  - **보존 필요**: ✅ 반드시

- `goal_manager.py`
  - **용도**: 운동 목표 관리
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: GoalManager 클래스
  - **보존 필요**: ✅ 반드시

- `health_tracker.py`
  - **용도**: 건강 메트릭 추적 및 종합 리포트
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: HealthTracker 클래스
  - **보존 필요**: ✅ 반드시

**E. 운동 기록 및 분석**
- `analytics.py`
  - **용도**: 운동 통계 및 분석
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: Analytics 클래스
  - **보존 필요**: ✅ 반드시

**F. UI 및 대시보드**
- `ui_renderers.py`
  - **용도**: 각 페이지별 UI 렌더링
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: 다양한 render_* 함수
  - **보존 필요**: ✅ 반드시

- `home_dashboard_new.py`
  - **용도**: 홈 대시보드 렌더링
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: render_new_home_dashboard()
  - **보존 필요**: ✅ 반드시

**G. 외부 서비스 연동**
- `youtube_integration.py`
  - **용도**: 유튜브 운동 영상 검색 및 추적
  - **상태**: app.py에서 사용 중 ✓
  - **기능**: YouTubeSearcher, VideoWatchTracker
  - **보존 필요**: ✅ 반드시

**H. 데이터베이스**
- `workout_history.db`
  - **용도**: 운동 기록, 목표, 유튜브 영상 메타데이터 저장
  - **상태**: 현재 사용 중 (테이블 10개 이상) ✓
  - **데이터 크기**: 약 50KB
  - **보존 필요**: ✅ 반드시

- `health_data.db`
  - **용도**: 건강 메트릭 추가 저장소 (현재 미사용)
  - **상태**: 테스트용 (내용 중복 가능)
  - **보존 필요**: ⚠️ 보류 (검토 필요)

**I. 프로젝트 구성 파일**
- `requirements.txt`
  - **용도**: 의존성 패키지 목록
  - **상태**: 필수
  - **보존 필요**: ✅ 반드시

- `.gitignore`
  - **용도**: Git 무시 파일 목록
  - **상태**: 필수
  - **보존 필요**: ✅ 반드시

- `README.md`
  - **용도**: 프로젝트 소개 및 사용법
  - **상태**: 필수 (내용 보완 권장)
  - **보존 필요**: ✅ 반드시

---

### ② 현재 사용하지 않지만 보관할 가치가 있는 파일

**A. 개발 과정의 주요 문서 (보관 권장)**
1. `IMPLEMENTATION_SUMMARY.txt` (21.52KB)
   - **내용**: 최종 구현 요약
   - **가치**: 개발 역사 기록
   - **추천**: `docs/archive/` 폴더로 이동

2. `USER_GUIDE.md` (11.13KB)
   - **내용**: 사용자 가이드
   - **가치**: 중간 가치 (업데이트 필요)
   - **추천**: `docs/` 폴더로 이동, 내용 보완

3. `HOME_DASHBOARD_SUMMARY.md` (20.17KB)
   - **내용**: 홈 대시보드 구현 요약
   - **가치**: 개발 참고용
   - **추천**: `docs/implementation/` 폴더로 이동

4. `WALKMATE_IMPLEMENTATION_REPORT.md` (16.84KB)
   - **내용**: 보행 분석 모듈 구현 보고서
   - **가치**: 개발 참고용
   - **추천**: `docs/implementation/` 폴더로 이동

5. `PHASE_1_COMPLETION_REPORT.md` (7.89KB)
   - **내용**: Phase 1 완료 보고서
   - **가치**: 프로젝트 이정표
   - **추천**: `docs/archive/` 폴더로 이동

---

### ③ 중복되거나 불필요하여 삭제를 검토할 파일

**A. 중복 보고서 파일 (동일 또는 유사 내용)**

다음 파일들은 내용이 거의 동일하거나 중복되어 있습니다:

1. **완료 보고서 중복** (5개 - 하나만 선택 보관)
   - `FINAL_COMPLETION_REPORT.txt` (15.64KB)
   - `DEVELOPMENT_COMPLETION.md` (13.57KB)
   - `DEVELOPMENT_COMPLETION_REPORT.md` (13.22KB)
   - `FINAL_PROJECT_STATUS.md` (13.38KB)
   - `FINAL_REPORT.md` (11.71KB)
   - **상태**: 대부분 비슷한 내용, 최신본 1개만 보관
   - **추천 삭제**: 4개 (최신 1개만 보관)
   - **보관**: `FINAL_COMPLETION_REPORT.txt` (가장 최신)

2. **최종 요약 중복** (3개)
   - `FINAL_SUMMARY.md` (10.29KB)
   - `FINAL_VALIDATION_REPORT.md` (11.3KB)
   - `COMPREHENSIVE_AUDIT_REPORT.txt` (12.74KB)
   - **상태**: 거의 동일한 내용
   - **추천 삭제**: 2개 (1개만 보관)
   - **보관**: `FINAL_VALIDATION_REPORT.md`

3. **분석 및 계획 중복** (3개)
   - `ANALYSIS_AND_PLAN.md` (13.08KB)
   - `PROJECT_ANALYSIS_AND_PLAN.md` (9.73KB)
   - `COMPREHENSIVE_PROJECT_ANALYSIS.md` (9.77KB)
   - **상태**: 프로젝트 분석 문서, 대부분 오래된 내용
   - **추천 삭제**: 2개 (1개만 보관)
   - **보관**: `COMPREHENSIVE_PROJECT_ANALYSIS.md`

4. **홈 대시보드 보고서 중복** (5개)
   - `HOME_DASHBOARD_REDESIGN_PLAN.md` (6.25KB)
   - `HOME_DASHBOARD_COMPLETION_REPORT.md` (14.72KB)
   - `HOME_DASHBOARD_FINAL_GUIDE.md` (15.87KB)
   - `HOME_DASHBOARD_SUMMARY.md` (20.17KB)
   - **상태**: 최근 작업, 세부 가이드 포함
   - **추천**: 모두 보관 (최근 작업) - `docs/implementation/` 이동

5. **개선 보고서 중복** (2개)
   - `ENHANCEMENT_REPORT.md` (13.36KB)
   - `POSTURE_FEEDBACK_ENHANCEMENT.md` (13.16KB)
   - **상태**: 비슷한 개선 내용
   - **추천 삭제**: 1개
   - **보관**: `POSTURE_FEEDBACK_ENHANCEMENT.md` (더 구체적)

**삭제 대상 요약:**
- **총 11개 보고서 파일** 중복/구식
- **보관 공간 절약**: 약 150KB

---

### ④ 테스트 파일 (기능 검증용, 필요시에만 사용)

**A. 테스트 파일 목록**
1. `test_full_flow.py` - 전체 흐름 테스트
2. `test_walk_analysis.py` - 보행 분석 테스트
3. `test_posture_feedback.py` - 자세 피드백 테스트
4. `test_compatibility.py` - 호환성 테스트
5. `final_test.py` - 최종 테스트
6. `validation_test.py` - 검증 테스트

**상태**: 개발 완료, 현재 미사용
**추천**: `tests/` 폴더로 이동 (실행 환경 분리)

---

### ⑤ 데이터 확인 스크립트 (유틸리티)

1. `check_db.py` - health_data.db 확인
2. `check_db_history.py` - workout_history.db 확인
3. `check_features.py` - 기능 확인

**상태**: 개발 중 사용, 현재 미사용
**추천**: `utils/` 폴더로 이동 또는 필요 없으면 삭제

---

## 3. 재무 분류 및 추천

### 카테고리별 정리

```
📂 프로젝트 루트 (정리 후)
│
├── 📄 핵심 애플리케이션 (11개 - 보존)
│   ├── app.py ✓
│   ├── camera.py ✓
│   ├── pose_detection.py ✓
│   ├── squat_analysis.py ✓
│   ├── walk_analysis.py ✓
│   ├── analytics.py ✓
│   ├── goal_manager.py ✓
│   ├── health_tracker.py ✓
│   ├── workout_recommendation.py ✓
│   ├── youtube_integration.py ✓
│   ├── ui_renderers.py ✓
│   └── home_dashboard_new.py ✓
│
├── 📄 구성 파일 (3개 - 보존)
│   ├── requirements.txt ✓
│   ├── .gitignore ✓
│   └── README.md ✓
│
├── 🗄️ 데이터베이스 (1개 - 보존)
│   └── workout_history.db ✓
│
├── 🤖 모델 파일 (1개 - 보존)
│   └── pose_landmarker_lite.task ✓
│
├── 📂 docs/ (문서 정리 - 새로 생성)
│   ├── README.md (프로젝트 소개)
│   ├── USER_GUIDE.md (사용자 가이드)
│   ├── FEATURES.md (기능 설명)
│   ├── implementation/
│   │   ├── HOME_DASHBOARD_SUMMARY.md
│   │   ├── WALKMATE_IMPLEMENTATION_REPORT.md
│   │   └── POSTURE_FEEDBACK_ENHANCEMENT.md
│   └── archive/
│       ├── FINAL_COMPLETION_REPORT.txt
│       ├── COMPREHENSIVE_PROJECT_ANALYSIS.md
│       ├── PHASE_1_COMPLETION_REPORT.md
│       └── IMPLEMENTATION_SUMMARY.txt
│
├── 📂 tests/ (테스트 파일 - 새로 생성)
│   ├── test_full_flow.py
│   ├── test_walk_analysis.py
│   ├── test_posture_feedback.py
│   ├── test_compatibility.py
│   ├── final_test.py
│   └── validation_test.py
│
├── 📂 utils/ (유틸리티 - 새로 생성)
│   ├── check_db.py
│   ├── check_db_history.py
│   └── check_features.py
│
└── 📂 .venv/ (가상 환경 - 보존)
```

---

## 4. 삭제 대상 파일 목록 (최종 검토 필요)

### 반드시 삭제할 파일 (11개 - 중복/구식 보고서)

1. ❌ `DEVELOPMENT_COMPLETION.md` (13.57KB) - `DEVELOPMENT_COMPLETION_REPORT.md`와 중복
2. ❌ `FINAL_REPORT.md` (11.71KB) - `FINAL_COMPLETION_REPORT.txt`와 중복
3. ❌ `FINAL_SUMMARY.md` (10.29KB) - 구식 요약본
4. ❌ `FINAL_PROJECT_STATUS.md` (13.38KB) - `FINAL_COMPLETION_REPORT.txt`와 중복
5. ❌ `ANALYSIS_AND_PLAN.md` (13.08KB) - 구식 계획, `COMPREHENSIVE_PROJECT_ANALYSIS.md` 추천
6. ❌ `PROJECT_ANALYSIS_AND_PLAN.md` (9.73KB) - 구식 계획
7. ❌ `COMPREHENSIVE_AUDIT_REPORT.txt` (12.74KB) - 오래된 감사 보고서
8. ❌ `ENHANCEMENT_REPORT.md` (13.36KB) - `POSTURE_FEEDBACK_ENHANCEMENT.md`와 중복
9. ❌ `ACTUAL_IMPLEMENTATION_REPORT.md` (15.48KB) - 중간 보고서
10. ❌ `DEVELOPMENT_PLAN_SUMMARY.md` (4.37KB) - 구식 계획
11. ❌ `HOME_DASHBOARD_REDESIGN_PLAN.md` (6.25KB) - 완료된 계획, 더 이상 필요 없음

**절감 공간**: 약 142KB

### 검토 필요한 파일 (1개)

1. ⚠️ `health_data.db` (0.05MB)
   - **현재 상태**: 사용하지 않음 (workout_history.db 사용)
   - **선택 사항**:
     - **A) 삭제**: 불필요 시 공간 절약
     - **B) 보관**: 혹시 모를 백업용
   - **추천**: 삭제 (workout_history.db만 충분)

---

## 5. 보존해야 할 최소 필수 파일

### 애플리케이션 실행에 필수 (11개)
✅ `app.py`
✅ `camera.py`
✅ `pose_detection.py`
✅ `squat_analysis.py`
✅ `walk_analysis.py`
✅ `analytics.py`
✅ `goal_manager.py`
✅ `health_tracker.py`
✅ `workout_recommendation.py`
✅ `youtube_integration.py`
✅ `ui_renderers.py`
✅ `home_dashboard_new.py`

### 리소스 파일
✅ `pose_landmarker_lite.task` (모델)
✅ `workout_history.db` (데이터)

### 프로젝트 구성
✅ `requirements.txt`
✅ `.gitignore`
✅ `README.md`

### 개발 환경
✅ `.venv/` (가상 환경)

---

## 6. 안전성 검사 사항

### A. 코드 종속성 검증

```
✓ app.py imports:
  - camera.py ✓
  - pose_detection.py ✓
  - squat_analysis.py ✓
  - walk_analysis.py ✓
  - goal_manager.py ✓
  - analytics.py ✓
  - workout_recommendation.py ✓
  - health_tracker.py ✓
  - youtube_integration.py ✓
  - home_dashboard_new.py ✓
  - ui_renderers.py ✓

✓ home_dashboard_new.py imports:
  - sqlite3 (표준 라이브러리)
  - streamlit
  - datetime, pathlib (표준 라이브러리)

✓ 테스트 파일들은 별도의 검증용 (삭제 가능)
✓ 체크 스크립트들은 유틸리티용 (이동 가능)
```

### B. 데이터베이스 검증

현재 `workout_history.db` 사용:
```
✓ workout_records 테이블 (운동 기록)
✓ walk_records 테이블 (보행 기록)
✓ goals 테이블 (운동 목표)
✓ daily_goals 테이블 (일일 목표)
✓ exercise_sessions 테이블
✓ health_metrics 테이블
✓ exercise_goals 테이블
✓ youtube_videos 테이블 (영상 메타데이터)
✓ video_watch_history 테이블
```

**health_data.db**는 사용하지 않음 (삭제 가능)

### C. 버전 관리 검증

```
✓ .git/ 폴더 존재 (Git 저장소)
✓ .gitignore 파일 존재
✓ 주요 변경 사항은 커밋됨
```

---

## 7. 최종 정리 계획

### Phase 1: 문서 정리 (안전함)
1. `docs/` 폴더 생성
2. `docs/README.md` - 프로젝트 소개 (기존 README.md 활용)
3. `docs/USER_GUIDE.md` - 사용자 가이드
4. `docs/FEATURES.md` - 기능 명세
5. `docs/implementation/` - 구현 보고서 이동
6. `docs/archive/` - 보관 문서 이동

### Phase 2: 테스트 파일 정리
1. `tests/` 폴더 생성
2. 모든 test_*.py 파일 이동
3. `tests/README.md` - 테스트 실행 가이드

### Phase 3: 유틸리티 정리
1. `utils/` 폴더 생성
2. `check_db.py`, `check_db_history.py`, `check_features.py` 이동
3. `utils/README.md` - 유틸리티 사용 가이드

### Phase 4: 불필요한 파일 삭제
1. 11개 중복/구식 보고서 파일 삭제
2. `health_data.db` 삭제 검토

---

## 8. 정리 후 프로젝트 크기 비교

### 현재 상태
- 루트 디렉토리: 약 60개 파일
- 문서/보고서: 약 310KB
- 전체 크기: 약 5.5MB (모델 포함)

### 정리 후
- 루트 디렉토리: 약 30개 파일 (-50%)
- 보고서: 약 150KB (-50%)
- 더 명확한 폴더 구조
- 실행 속도 변화 없음 (코드만 보존)

---

## 9. 추천 사항 및 주의사항

### ✅ 최종 추천
1. **문서 정리**: `docs/` 폴더 생성 및 정리 (안전함)
2. **테스트 분리**: `tests/` 폴더 생성 (안전함)
3. **유틸리티 분리**: `utils/` 폴더 생성 (안전함)
4. **중복 삭제**: 11개 중복 보고서 삭제
5. **DB 정리**: `health_data.db` 삭제 (workout_history.db만 사용)

### ⚠️ 주의사항
1. **app.py import 변경 금지**: 현재 파일 위치 변경 불가
2. **모델 파일 삭제 금지**: `pose_landmarker_lite.task` 필수
3. **데이터베이스 백업**: workout_history.db는 반드시 보존
4. **.venv 폴더 삭제 금지**: 가상 환경 필수
5. **Git 커밋**: 정리 후 'Cleanup project structure' 커밋 추천

### 🔍 검증 항목
- [ ] 모든 import 구문 확인
- [ ] 각 함수의 호출 관계 재확인
- [ ] 데이터베이스 테이블 무결성 검증
- [ ] Git 상태 확인
- [ ] 앱 실행 테스트
- [ ] 모든 메뉴 기능 테스트

---

## 10. 사용자 승인 필요 사항

### 삭제 승인 대기 (다음 파일들)
1. DEVELOPMENT_COMPLETION.md
2. FINAL_REPORT.md
3. FINAL_SUMMARY.md
4. FINAL_PROJECT_STATUS.md
5. ANALYSIS_AND_PLAN.md
6. PROJECT_ANALYSIS_AND_PLAN.md
7. COMPREHENSIVE_AUDIT_REPORT.txt
8. ENHANCEMENT_REPORT.md
9. ACTUAL_IMPLEMENTATION_REPORT.md
10. DEVELOPMENT_PLAN_SUMMARY.md
11. HOME_DASHBOARD_REDESIGN_PLAN.md
12. ⚠️ health_data.db (선택 사항)

### 이동 승인 대기
- 모든 테스트 파일 → `tests/` 폴더
- 모든 유틸리티 → `utils/` 폴더
- 보관 문서 → `docs/` 폴더

---

## 계획 요약

**총 작업 항목**: 25개
- **삭제**: 11-12개 파일
- **이동**: 13개 파일
- **신규 생성**: 3개 폴더 (`docs/`, `tests/`, `utils/`)
- **수정/검토**: 3-5개 파일

**예상 작업 시간**: 20-30분
**예상 공간 절약**: 약 150KB
**안전성**: ★★★★★ (코드 변경 없음, 문서만 정리)

---

**승인 대기 중입니다.**

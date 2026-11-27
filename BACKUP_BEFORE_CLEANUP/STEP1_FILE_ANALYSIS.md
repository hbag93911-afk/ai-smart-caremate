# 프로젝트 파일 정리 - 1단계: 전체 파일 분석

**작성일**: 2026-11-26  
**상태**: 사용자 승인 대기 중

---

## 📊 전체 파일 현황

| 항목 | 개수 | 크기 | 비고 |
|------|------|------|------|
| 루트 디렉토리 파일 | 54개 | ~5.6MB | .venv, .git 제외 |
| Python 소스 코드 | 12개 | 198KB | 필수 모듈 |
| 문서/보고서 | 25개 | 374KB | 개발 기록 |
| 테스트 파일 | 5개 | 36KB | 테스트 코드 |
| 유틸리티 파일 | 3개 | 8KB | 검사 도구 |
| 데이터베이스 | 2개 | 53KB | 운동 기록 |
| 모델 파일 | 1개 | 5.5MB | AI 모델 |
| 프로젝트 설정 | 3개 | 2KB | 구성 파일 |
| 캐시/컴파일 | 2개 | 460KB | __pycache__, .pyc |

---

## 🎯 카테고리 1: 반드시 필요한 파일 (보존 100%)

### A. 핵심 애플리케이션 모듈 (12개)

| 파일명 | 크기 | 역할 | 삭제 불가 |
|--------|------|------|----------|
| **app.py** | 76,922B | 메인 Streamlit 애플리케이션, 모든 메뉴 관리 | ✅ 필수 |
| **camera.py** | 1,101B | 카메라 캡처 기능 | ✅ 필수 |
| **pose_detection.py** | 3,603B | MediaPipe 관절 인식 | ✅ 필수 |
| **squat_analysis.py** | 24,769B | 스쿼트 자세 분석 엔진 | ✅ 필수 |
| **walk_analysis.py** | 22,494B | 보행 자세 분석 엔진 | ✅ 필수 |
| **analytics.py** | 16,940B | 운동 통계 및 데이터 분석 | ✅ 필수 |
| **goal_manager.py** | 14,145B | 운동 목표 관리 | ✅ 필수 |
| **health_tracker.py** | 17,178B | 개인별 건강 추적 | ✅ 필수 |
| **workout_recommendation.py** | 22,897B | AI 맞춤 운동 추천 | ✅ 필수 |
| **youtube_integration.py** | 19,575B | 유튜브 운동 영상 연동 | ✅ 필수 |
| **ui_renderers.py** | 18,609B | UI 화면 렌더링 | ✅ 필수 |
| **home_dashboard_new.py** | 22,953B | 홈 대시보드 렌더링 | ✅ 필수 |

**선택 이유**:
- 모두 app.py에서 직접 import됨
- 각각 하나의 기능을 담당
- 중복 없음

---

### B. 데이터베이스 (1개)

| 파일명 | 크기 | 역할 | 삭제 불가 |
|--------|------|------|----------|
| **workout_history.db** | 53,248B | 모든 운동 기록, 목표, 사용자 데이터 저장 | ✅ 필수 |

**테이블 목록**:
- workout_records: 스쿼트, 걷기 등 운동 기록
- walk_records: 보행 분석 데이터
- goals: 사용자 운동 목표
- daily_goals: 일일 목표
- youtube_videos: 유튜브 메타데이터
- 기타 7개 테이블

**선택 이유**:
- 사용자의 모든 데이터 포함
- 앱 실행 시 자동으로 로드
- 절대 삭제 금지

---

### C. AI 모델 파일 (1개)

| 파일명 | 크기 | 역할 | 삭제 불가 |
|--------|------|------|----------|
| **pose_landmarker_lite.task** | 5,777,746B | Google MediaPipe 사전학습 모델 | ✅ 필수 |

**사용처**:
- pose_detection.py에서 로드
- 실시간 관절 인식에 필수
- 프로젝트 용량의 95% 차지

**선택 이유**:
- 카메라 기능의 핵심
- 대체 불가능

---

### D. 프로젝트 구성 파일 (3개)

| 파일명 | 크기 | 역할 | 삭제 불가 |
|--------|------|------|----------|
| **requirements.txt** | 52B | Python 의존성 패키지 목록 | ✅ 필수 |
| **.gitignore** | 32B | Git 무시 파일 목록 | ✅ 필수 |
| **README.md** | 1,699B | 프로젝트 설명 | ✅ 필수 |

**선택 이유**:
- 프로젝트 기본 설정
- 개발 환경 구성에 필수

---

## ⚠️ 카테고리 2: 보관 가치 있는 문서 (보관 권장)

이 문서들은 `docs/` 폴더로 이동하여 보관합니다.

### 사용자 가이드 (1개)

| 파일명 | 크기 | 내용 | 조치 |
|--------|------|------|------|
| **USER_GUIDE.md** | 11,402B | 사용자 사용 설명서 | 📂 docs/ 이동 |

---

### 구현 상세 가이드 (3개)

| 파일명 | 크기 | 내용 | 조치 |
|--------|------|------|------|
| **HOME_DASHBOARD_SUMMARY.md** | 20,652B | 홈 대시보드 구현 가이드 | 📂 docs/implementation/ 이동 |
| **WALKMATE_IMPLEMENTATION_REPORT.md** | 17,248B | 보행 분석 모듈 상세 설명 | 📂 docs/implementation/ 이동 |
| **POSTURE_FEEDBACK_ENHANCEMENT.md** | 13,471B | 자세 피드백 기능 설명 | 📂 docs/implementation/ 이동 |

---

### 최종 보고서 (3개)

| 파일명 | 크기 | 내용 | 조치 |
|--------|------|------|------|
| **FINAL_COMPLETION_REPORT.txt** | 16,020B | 최종 완료 보고서 (최신) | 📂 docs/archive/ 이동 |
| **COMPREHENSIVE_PROJECT_ANALYSIS.md** | 10,001B | 프로젝트 종합 분석 | 📂 docs/archive/ 이동 |
| **PHASE_1_COMPLETION_REPORT.md** | 8,080B | Phase 1 완료 기록 | 📂 docs/archive/ 이동 |
| **IMPLEMENTATION_SUMMARY.txt** | 22,033B | 최종 구현 요약 | 📂 docs/archive/ 이동 |

**이동 이유**:
- 개발 기록으로 보관 가치 있음
- 루트 디렉토리의 혼잡 완화
- 필요시 참고 가능

---

## ❌ 카테고리 3: 삭제 대상 (중복 또는 구식)

### 삭제할 보고서 파일 (11개)

| 파일명 | 크기 | 삭제 이유 | 대체 | 삭제 |
|--------|------|----------|------|------|
| **DEVELOPMENT_COMPLETION.md** | 13,898B | 중복: DEVELOPMENT_COMPLETION_REPORT.md와 동일 내용 | DEVELOPMENT_COMPLETION_REPORT.md 사용 | ❌ |
| **FINAL_REPORT.md** | 11,993B | 중복: FINAL_COMPLETION_REPORT.txt와 거의 동일 | FINAL_COMPLETION_REPORT.txt 사용 | ❌ |
| **FINAL_SUMMARY.md** | 10,532B | 구식: IMPLEMENTATION_SUMMARY.txt가 더 최신 | IMPLEMENTATION_SUMMARY.txt 사용 | ❌ |
| **FINAL_PROJECT_STATUS.md** | 13,705B | 중복: FINAL_COMPLETION_REPORT.txt와 동일 | FINAL_COMPLETION_REPORT.txt 사용 | ❌ |
| **ANALYSIS_AND_PLAN.md** | 13,398B | 구식: 오래된 계획, COMPREHENSIVE_PROJECT_ANALYSIS.md 추천 | COMPREHENSIVE_PROJECT_ANALYSIS.md 사용 | ❌ |
| **PROJECT_ANALYSIS_AND_PLAN.md** | 9,962B | 중복: ANALYSIS_AND_PLAN.md와 중복 | 삭제 | ❌ |
| **COMPREHENSIVE_AUDIT_REPORT.txt** | 13,044B | 구식: 감사 보고서 (더 이상 필요 없음) | 없음 | ❌ |
| **ENHANCEMENT_REPORT.md** | 13,685B | 중복: POSTURE_FEEDBACK_ENHANCEMENT.md와 중복 | POSTURE_FEEDBACK_ENHANCEMENT.md 사용 | ❌ |
| **ACTUAL_IMPLEMENTATION_REPORT.md** | 15,849B | 중복: 중간 버전 (최종만 보관 필요) | IMPLEMENTATION_SUMMARY.txt 사용 | ❌ |
| **DEVELOPMENT_PLAN_SUMMARY.md** | 4,479B | 구식: 개발 완료되어 계획 불필요 | 없음 | ❌ |
| **HOME_DASHBOARD_REDESIGN_PLAN.md** | 6,400B | 구식: 완료된 계획 (더 이상 필요 없음) | 없음 | ❌ |

**총 삭제 용량**: ~142,945B (약 143KB 절감)

**삭제 사유 분류**:
- **중복 (7개)**: FINAL, DEVELOPMENT, ANALYSIS 등 거의 동일한 내용
- **구식 (4개)**: 개발 완료되어 계획, 감사 보고서 등은 더 이상 불필요

---

### 추가 삭제 검토: health_data.db

| 파일명 | 크기 | 상태 | 삭제 | 비고 |
|--------|------|------|------|------|
| **health_data.db** | 0B (빈 파일) | 사용 안 함 | ⚠️ 선택사항 | 초기 개발 단계에서 생성, 현재 미사용 |

**검토**:
- 비어있는 파일
- workout_history.db만 사용 중
- 삭제해도 안전

**결정**: 사용자 승인 후 삭제

---

## 📦 카테고리 4: 테스트 및 유틸리티 (폴더로 이동)

### 테스트 파일 (5개) → `tests/` 폴더로 이동

| 파일명 | 크기 | 목적 | 조치 |
|--------|------|------|------|
| **test_full_flow.py** | 4,019B | 전체 흐름 테스트 | 📂 tests/ 이동 |
| **test_walk_analysis.py** | 10,528B | 보행 분석 테스트 | 📂 tests/ 이동 |
| **test_posture_feedback.py** | 9,171B | 자세 피드백 테스트 | 📂 tests/ 이동 |
| **test_compatibility.py** | 3,086B | 호환성 테스트 | 📂 tests/ 이동 |
| **validation_test.py** | 9,045B | 검증 테스트 | 📂 tests/ 이동 |

**이동 이유**:
- 테스트 파일을 별도 폴더에 정리
- 루트 디렉토리 혼잡 완화
- 테스트 관리 용이

---

### 유틸리티 파일 (3개) → `utils/` 폴더로 이동

| 파일명 | 크기 | 목적 | 조치 |
|--------|------|------|------|
| **check_db_history.py** | 610B | workout_history.db 확인 | 📂 utils/ 이동 |
| **check_features.py** | 5,851B | 기능 확인 | 📂 utils/ 이동 |
| **check_db.py** | 1,475B | health_data.db 확인 (또는 삭제) | 📂 utils/ 이동 |

**이동 이유**:
- 유틸리티를 별도 폴더에 정리
- 필요시 접근 용이

---

## 📝 최종 정리 계획

### Phase 1: 문서 정리 (폴더 생성 및 이동)
```
Step 1: docs/ 폴더 생성
Step 2: docs/implementation/ 폴더 생성
Step 3: docs/archive/ 폴더 생성
Step 4: 보관할 6개 문서 이동
```

### Phase 2: 테스트 및 유틸리티 정리 (폴더 생성 및 이동)
```
Step 1: tests/ 폴더 생성
Step 2: utils/ 폴더 생성
Step 3: 테스트 파일 5개 이동
Step 4: 유틸리티 파일 3개 이동
```

### Phase 3: 불필요한 파일 삭제
```
Step 1: 중복 보고서 7개 삭제
Step 2: 구식 보고서 4개 삭제
Step 3: health_data.db 삭제 (선택)
```

### Phase 4: 최종 검증
```
Step 1: 모든 import 경로 확인 (변경 불필요)
Step 2: 앱 실행 테스트
Step 3: 모든 기능 테스트
Step 4: Git 커밋 (사용자 선택)
```

---

## ✅ 정리 후 프로젝트 구조

```
AI 스마트 케어메이트/
│
├── 🎯 핵심 애플리케이션 (12개 파일)
│   ├── app.py ✅
│   ├── camera.py ✅
│   ├── pose_detection.py ✅
│   ├── squat_analysis.py ✅
│   ├── walk_analysis.py ✅
│   ├── analytics.py ✅
│   ├── goal_manager.py ✅
│   ├── health_tracker.py ✅
│   ├── workout_recommendation.py ✅
│   ├── youtube_integration.py ✅
│   ├── ui_renderers.py ✅
│   └── home_dashboard_new.py ✅
│
├── 📚 문서 & 가이드 (새로 생성)
│   ├── README.md ✅
│   ├── requirements.txt ✅
│   ├── .gitignore ✅
│   └── docs/ (새로 생성)
│       ├── USER_GUIDE.md
│       ├── implementation/
│       │   ├── HOME_DASHBOARD_SUMMARY.md
│       │   ├── WALKMATE_IMPLEMENTATION_REPORT.md
│       │   └── POSTURE_FEEDBACK_ENHANCEMENT.md
│       └── archive/
│           ├── FINAL_COMPLETION_REPORT.txt
│           ├── COMPREHENSIVE_PROJECT_ANALYSIS.md
│           ├── PHASE_1_COMPLETION_REPORT.md
│           └── IMPLEMENTATION_SUMMARY.txt
│
├── 🧪 테스트 (새로 생성)
│   └── tests/
│       ├── test_full_flow.py
│       ├── test_walk_analysis.py
│       ├── test_posture_feedback.py
│       ├── test_compatibility.py
│       ├── validation_test.py
│       └── README.md
│
├── 🛠️ 유틸리티 (새로 생성)
│   └── utils/
│       ├── check_db_history.py
│       ├── check_features.py
│       └── README.md
│
├── 🗄️ 데이터
│   └── workout_history.db ✅
│
├── 🤖 모델
│   └── pose_landmarker_lite.task ✅
│
├── 🐍 개발 환경
│   └── .venv/ ✅
│
└── 🔧 Git 버전 관리
    ├── .git/ ✅
    ├── .gitignore ✅
    └── __pycache__/ (캐시, 자동 생성)
```

---

## 📊 정리 효과

| 항목 | 현재 | 정리 후 | 절감 |
|------|------|--------|------|
| 루트 파일 (보고서 제외) | 54개 | 약 30개 | -44% |
| 루트 파일 (보고서 포함) | 54개 | 약 19개 | -65% |
| 문서 파일 | 25개 | 10개 (docs 이동) | -60% |
| 디렉토리 | 2개 | 5개 | +3개 |
| 저장공간 | ~5.6MB | ~5.4MB | 약 200KB |

---

## 🔒 안전성 보장

### ✅ 보존 사항
- **12개 핵심 애플리케이션 모듈** (app.py 등)
- **workout_history.db** (모든 사용자 운동 기록)
- **pose_landmarker_lite.task** (AI 모델)
- **requirements.txt, .gitignore, README.md**
- **.git, .venv** (버전 관리, 개발 환경)

### ✅ 기능 보존
- 카메라 및 실시간 관절 인식 ✅
- 스쿼트 분석, 보행 분석 ✅
- AI 맞춤 운동 추천 ✅
- 유튜브 운동 영상 ✅
- 운동 기록 및 통계 ✅
- 종합 건강 리포트 ✅

### ✅ import 경로 무변경
- 모든 모듈이 같은 디렉토리에 위치
- Python import 문 수정 불필요
- 테스트 파일만 `tests/` 폴더로 이동 (독립 실행용)

### ✅ Git 버전 관리 유지
- .git 폴더 보존
- 정리 후 'Cleanup project structure' 커밋 추천

---

## 🎯 다음 단계

**이 분석 보고서를 검토한 후 다음 중 하나를 선택하여 알려주세요:**

### 선택지 1: 계획 승인 (권장)
> "파일 정리를 진행해 주세요"
- 11개 보고서 삭제
- 6개 문서를 docs/ 이동
- 8개 파일을 tests/, utils/ 이동
- 최종 테스트

### 선택지 2: 추가 검토
> "다시 한 번 확인해 주세요"
- 특정 파일에 대한 추가 분석
- 삭제 대상 재검토
- 구조 개선 제안

### 선택지 3: 계획 수정
> "다음을 변경해 주세요: ..."
- 파일 보관/삭제 기준 변경
- 폴더 구조 조정
- 보관 문서 선택 변경

---

**📌 중요: 아래 항목을 확인해 주세요:**

1. ✅ 11개 삭제 대상 파일에 동의하시나요?
2. ✅ 6개 보관 문서 선택에 동의하시나요?
3. ✅ health_data.db를 삭제해도 되나요?
4. ✅ 테스트 파일을 tests/ 폴더로 옮겨도 되나요?
5. ✅ 유틸리티 파일을 utils/ 폴더로 옮겨도 되나요?

---

**지금 바로 말씀해 주세요!** 👇

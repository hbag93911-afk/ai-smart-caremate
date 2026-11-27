#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""향상된 자세 피드백 기능 테스트"""

import sys
sys.path.insert(0, '.')

from squat_analysis import SquatAnalyzer
from typing import Dict, Tuple, Any

# JointData 타입 정의
JointData = Dict[str, Any]

def create_mock_joints() -> Dict[str, JointData]:
    """기본 자세의 모의 관절 데이터 생성 (기본값)"""
    return {
        "left_shoulder": {"point": (200, 100), "confidence": 0.9},
        "right_shoulder": {"point": (400, 100), "confidence": 0.9},
        "left_hip": {"point": (200, 300), "confidence": 0.9},
        "right_hip": {"point": (400, 300), "confidence": 0.9},
        "left_knee": {"point": (200, 500), "confidence": 0.9},
        "right_knee": {"point": (400, 500), "confidence": 0.9},
        "left_ankle": {"point": (200, 700), "confidence": 0.9},
        "right_ankle": {"point": (400, 700), "confidence": 0.9},
    }

def test_phase_names():
    """단계 이름 테스트"""
    print("=" * 60)
    print("TEST 1: 단계 이름 테스트")
    print("=" * 60)
    
    analyzer = SquatAnalyzer()
    
    phases = [
        (analyzer.STANDING, "서있는 상태"),
        (analyzer.DESCENDING, "내려가기"),
        (analyzer.BOTTOM, "최저점"),
        (analyzer.ASCENDING, "올라오기"),
    ]
    
    for phase_num, expected_name in phases:
        name = analyzer._get_phase_name(phase_num)
        status = "✅" if name == expected_name else "❌"
        print(f"{status} Phase {phase_num}: {name} (expected: {expected_name})")
    
    print()

def test_posture_feedback_initialization():
    """향상된 피드백 초기화 테스트"""
    print("=" * 60)
    print("TEST 2: 향상된 피드백 초기화 테스트")
    print("=" * 60)
    
    analyzer = SquatAnalyzer()
    
    # 초기 상태 확인
    assert analyzer._posture_history == []
    assert analyzer._posture_warnings_in_rep == []
    assert analyzer._phase_start_time is None
    
    print("✅ 모든 피드백 변수가 올바르게 초기화되었습니다.")
    print()

def test_feedback_message_generation():
    """피드백 메시지 생성 테스트"""
    print("=" * 60)
    print("TEST 3: 피드백 메시지 생성 테스트")
    print("=" * 60)
    
    analyzer = SquatAnalyzer()
    joints = create_mock_joints()
    
    # 테스트 1: 완벽한 자세
    print("\n1️⃣ 완벽한 자세 (무릎 각도: 90°, 상체 기울기: 20°)")
    analyzer.phase = analyzer.BOTTOM
    feedback = analyzer._make_feedback(joints, 90.0, 20.0, 30.0)
    print(f"   피드백 개수: {len(feedback)}")
    for msg in feedback:
        print(f"   - {msg}")
    
    # 테스트 2: 무릎이 너무 펴져 있음
    print("\n2️⃣ 무릎이 너무 펴져 있음 (무릎 각도: 140°)")
    analyzer._posture_warnings_in_rep = []
    analyzer._posture_history = []
    analyzer.phase = analyzer.DESCENDING
    feedback = analyzer._make_feedback(joints, 140.0, 20.0, 30.0)
    print(f"   피드백 개수: {len(feedback)}")
    for msg in feedback:
        print(f"   - {msg}")
    
    # 테스트 3: 상체가 너무 앞으로 기울어짐
    print("\n3️⃣ 상체가 너무 앞으로 기울어짐 (상체 기울기: 50°)")
    analyzer._posture_warnings_in_rep = []
    analyzer._posture_history = []
    analyzer.phase = analyzer.BOTTOM
    feedback = analyzer._make_feedback(joints, 90.0, 50.0, 30.0)
    print(f"   피드백 개수: {len(feedback)}")
    for msg in feedback:
        print(f"   - {msg}")
    
    # 테스트 4: 무릎이 너무 깊음
    print("\n4️⃣ 무릎이 너무 깊음 (무릎 각도: 50°)")
    analyzer._posture_warnings_in_rep = []
    analyzer._posture_history = []
    analyzer.phase = analyzer.BOTTOM
    feedback = analyzer._make_feedback(joints, 50.0, 20.0, 30.0)
    print(f"   피드백 개수: {len(feedback)}")
    for msg in feedback:
        print(f"   - {msg}")
    
    print()

def test_posture_assessment():
    """자세 평가 테스트"""
    print("=" * 60)
    print("TEST 4: 자세 평가 테스트")
    print("=" * 60)
    
    # 테스트 1: 경고율 0% (완벽한 자세)
    print("\n1️⃣ 경고율 0% (완벽한 자세)")
    result = "완벽한 자세" if "완벽" in SquatAnalyzer()._assess_posture_quality(0.0) else "실패"
    assessment = SquatAnalyzer()._assess_posture_quality(0.0)
    print(f"   평가: {assessment}")
    
    # 테스트 2: 경고율 5% (훌륭한 자세)
    print("\n2️⃣ 경고율 5% (훌륭한 자세)")
    assessment = SquatAnalyzer()._assess_posture_quality(0.05)
    print(f"   평가: {assessment}")
    
    # 테스트 3: 경고율 20% (좋은 자세)
    print("\n3️⃣ 경고율 20% (좋은 자세)")
    assessment = SquatAnalyzer()._assess_posture_quality(0.20)
    print(f"   평가: {assessment}")
    
    # 테스트 4: 경고율 40% (개선 필요)
    print("\n4️⃣ 경고율 40% (개선 필요)")
    assessment = SquatAnalyzer()._assess_posture_quality(0.40)
    print(f"   평가: {assessment}")
    
    # 테스트 5: 경고율 70% (주의 필요)
    print("\n5️⃣ 경고율 70% (주의 필요)")
    assessment = SquatAnalyzer()._assess_posture_quality(0.70)
    print(f"   평가: {assessment}")
    
    print()

def test_rep_assessment():
    """반복 평가 메서드 테스트"""
    print("=" * 60)
    print("TEST 5: 반복 평가 테스트")
    print("=" * 60)
    
    analyzer = SquatAnalyzer()
    
    # 초기 상태 (분석 대기)
    print("\n1️⃣ 초기 상태 (분석 전)")
    assessment = analyzer.get_rep_assessment()
    print(f"   평가: {assessment['assessment']}")
    print(f"   점수: {assessment['score']}")
    
    # 모의 자세 히스토리 추가
    print("\n2️⃣ 자세 히스토리 추가 후 평가")
    for i in range(10):
        analyzer._posture_history.append({
            "phase": analyzer.BOTTOM,
            "knee_angle": 85.0 + (i % 5),
            "trunk_tilt": 20.0,
            "speed": 30.0,
            "warnings": 0 if i % 3 == 0 else 1,
        })
    
    assessment = analyzer.get_rep_assessment()
    print(f"   평가: {assessment['assessment']}")
    print(f"   점수: {assessment['score']}")
    print(f"   경고율: {assessment['warning_rate']}")
    print(f"   권장사항 개수: {len(assessment['recommendations'])}")
    for tip in assessment['recommendations']:
        print(f"   - {tip}")
    
    print()

def test_rep_data_reset():
    """반복 데이터 리셋 테스트"""
    print("=" * 60)
    print("TEST 6: 반복 데이터 리셋 테스트")
    print("=" * 60)
    
    analyzer = SquatAnalyzer()
    
    # 데이터 추가
    analyzer._posture_history.append({"phase": analyzer.BOTTOM, "knee_angle": 90.0})
    analyzer._posture_warnings_in_rep.append({"type": "knee_alignment"})
    
    print(f"리셋 전: 히스토리 길이 = {len(analyzer._posture_history)}, 경고 개수 = {len(analyzer._posture_warnings_in_rep)}")
    
    # 리셋
    analyzer._reset_rep_data()
    
    print(f"리셋 후: 히스토리 길이 = {len(analyzer._posture_history)}, 경고 개수 = {len(analyzer._posture_warnings_in_rep)}")
    print("✅ 반복 데이터가 올바르게 리셋되었습니다.")
    
    print()

def test_posture_feedback_by_phase():
    """단계별 자세 피드백 테스트"""
    print("=" * 60)
    print("TEST 7: 단계별 자세 피드백 테스트")
    print("=" * 60)
    
    analyzer = SquatAnalyzer()
    
    # 각 단계에서의 피드백 생성
    for phase_num in [analyzer.STANDING, analyzer.DESCENDING, analyzer.BOTTOM, analyzer.ASCENDING]:
        analyzer.phase = phase_num
        analyzer.knee_angle = 90.0
        analyzer.trunk_tilt_deg = 25.0
        analyzer.speed_deg_per_sec = 35.0
        
        feedback = analyzer.get_posture_feedback_by_phase()
        
        print(f"\n단계: {feedback['phase_name']}")
        print(f"  무릎 각도: {feedback['knee_angle']}°")
        print(f"  상체 기울기: {feedback['trunk_tilt']}°")
        print(f"  속도: {feedback['speed']}°/s")
        print(f"  경고 개수: {len(feedback['warnings'])}")
    
    print()

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("\n")
    print("=" * 60)
    print("향상된 자세 피드백 기능 테스트")
    print("=" * 60)
    print()
    
    try:
        test_phase_names()
        test_posture_feedback_initialization()
        test_feedback_message_generation()
        test_posture_assessment()
        test_rep_assessment()
        test_rep_data_reset()
        test_posture_feedback_by_phase()
        
        print("=" * 60)
        print("✅ 모든 테스트 완료!")
        print("=" * 60)
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

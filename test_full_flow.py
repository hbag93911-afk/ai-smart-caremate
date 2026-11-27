#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""app.py 함수 호출 테스트 (카메라 없이)"""

import sys
import os
sys.path.insert(0, '.')

# Streamlit 테스트 모드 설정
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'error'

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from squat_analysis import SquatAnalyzer
import time

def test_squat_analysis_full_flow():
    """스쿼트 분석 전체 흐름 테스트 (카메라 없이)"""
    
    print("=" * 60)
    print("스쿼트 분석 전체 흐름 테스트")
    print("=" * 60)
    
    analyzer = SquatAnalyzer()
    
    # 모의 관절 데이터
    def create_joints(knee_angle_deg: float) -> dict:
        """주어진 무릎 각도를 가진 모의 관절 데이터"""
        # 무릎 각도를 사용하여 관절 위치 계산
        angle_rad = (180 - knee_angle_deg) * 3.14159 / 180
        
        left_knee_x = 200
        left_knee_y = 400
        
        # 엉덩이에서 무릎까지 거리: 200픽셀, 각도: angle_rad
        left_hip_x = left_knee_x - 200 * (1 - 0.3)
        left_hip_y = left_knee_y - 200 * (1 - 0.3)
        
        # 무릎에서 발목까지 거리: 200픽셀, 같은 각도
        left_ankle_x = left_knee_x + 200 * 0.3
        left_ankle_y = left_knee_y + 200 * 0.3
        
        return {
            "left_shoulder": {"point": (200, 100), "confidence": 0.95},
            "right_shoulder": {"point": (600, 100), "confidence": 0.95},
            "left_hip": {"point": (220, 350), "confidence": 0.95},
            "right_hip": {"point": (580, 350), "confidence": 0.95},
            "left_knee": {"point": (220, 550), "confidence": 0.95},
            "right_knee": {"point": (580, 550), "confidence": 0.95},
            "left_ankle": {"point": (220, 750), "confidence": 0.95},
            "right_ankle": {"point": (580, 750), "confidence": 0.95},
        }
    
    # 시뮬레이션: 1회 반복 (서있기 -> 내려가기 -> 최저점 -> 올라오기 -> 서있기)
    knee_angles = [
        # 서있기
        170, 170, 170,
        # 내려가기
        150, 130, 110,
        # 최저점
        100, 95, 90, 95,
        # 올라오기
        110, 130, 150,
        # 서있기
        170, 170, 170
    ]
    
    print(f"\n시뮬레이션: {len(knee_angles)}프레임 처리")
    print("-" * 60)
    
    for frame_idx, knee_angle in enumerate(knee_angles):
        joints = create_joints(knee_angle)
        timestamp_ms = int((frame_idx * 33))  # 약 30fps
        
        result = analyzer.update(joints, timestamp_ms, analyze_enabled=True)
        
        phase_name = analyzer._get_phase_name(result['phase'])
        posture_ok = "OK" if result['posture_ok'] else "주의"
        
        print(f"Frame {frame_idx + 1:2d}: "
              f"무릎={result['angle']:5.1f}° | "
              f"단계={phase_name:8s} | "
              f"자세={posture_ok:4s} | "
              f"횟수={result['count']}회 | "
              f"개선사항={len(result['feedback'])}개")
    
    print("-" * 60)
    print(f"\n최종 결과:")
    print(f"  총 스쿼트 횟수: {analyzer.squat_count}회")
    print(f"  현재 단계: {analyzer._get_phase_name(analyzer.phase)}")
    print(f"  자세 정확도: {analyzer.posture_accuracy_percent():.1f}%")
    
    summary = analyzer._build_summary()
    print(f"\n세션 요약:")
    print(f"  총 횟수: {summary['count']}회")
    print(f"  평균 무릎 각도: {summary['avg_knee_angle']:.1f}°")
    print(f"  최고 깊이: {summary['best_depth']}")
    
    # 평가 테스트
    assessment = analyzer.get_rep_assessment()
    print(f"\n마지막 반복 평가:")
    print(f"  평가: {assessment['assessment']}")
    print(f"  점수: {assessment['score']}")
    
    print("\n✅ 테스트 완료!")
    print()

if __name__ == "__main__":
    test_squat_analysis_full_flow()

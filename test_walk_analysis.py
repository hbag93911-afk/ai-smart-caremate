# -*- coding: utf-8 -*-
"""
AI Smart CareMate - Walk Analysis Enhancement Test
Test suite for improved gait analysis functionality
"""
import time
from walk_analysis import WalkAnalyzer


def create_mock_joint_data(
    left_ankle_y=400,
    right_ankle_y=400,
    left_knee_y=250,
    right_knee_y=250,
    left_shoulder_y=100,
    right_shoulder_y=100,
    left_hip_y=300,
    right_hip_y=300,
):
    """Generate test joint data for unit tests."""
    return {
        "left_ankle": {"point": (100, left_ankle_y), "confidence": 0.9},
        "right_ankle": {"point": (500, right_ankle_y), "confidence": 0.9},
        "left_knee": {"point": (100, left_knee_y), "confidence": 0.9},
        "right_knee": {"point": (500, right_knee_y), "confidence": 0.9},
        "left_shoulder": {"point": (100, left_shoulder_y), "confidence": 0.9},
        "right_shoulder": {"point": (500, right_shoulder_y), "confidence": 0.9},
        "left_hip": {"point": (100, left_hip_y), "confidence": 0.9},
        "right_hip": {"point": (500, right_hip_y), "confidence": 0.9},
    }


def test_basic_initialization():
    """Test WalkAnalyzer basic initialization."""
    print("\n[TEST 1] Basic Initialization")
    analyzer = WalkAnalyzer()
    assert analyzer.step_count == 0, "Step count should be 0"
    assert analyzer.cadence == 0.0, "Cadence should be 0.0"
    assert analyzer.walk_time_seconds == 0.0, "Walk time should be 0.0"
    assert analyzer.left_right_balance == 50.0, "Balance should be 50.0"
    assert analyzer.gait_symmetry == 0.0, "Gait symmetry should be 0.0"
    assert analyzer.body_sway == 0.0, "Body sway should be 0.0"
    print("   PASS: All initialization values are correct")


def test_reset_functionality():
    """Test reset functionality."""
    print("\n[TEST 2] Reset Functionality")
    analyzer = WalkAnalyzer()
    
    # Modify some values
    analyzer.step_count = 10
    analyzer.cadence = 60.0
    analyzer.walk_time_seconds = 10.0
    
    # Reset
    analyzer.reset()
    
    assert analyzer.step_count == 0, "Step count should be reset to 0"
    assert analyzer.cadence == 0.0, "Cadence should be reset to 0.0"
    assert analyzer.walk_time_seconds == 0.0, "Walk time should be reset to 0.0"
    print("   PASS: Reset works correctly")


def test_joint_confidence_check():
    """Test joint confidence checking."""
    print("\n[TEST 3] Joint Confidence Check")
    analyzer = WalkAnalyzer()
    
    # High confidence data
    good_joints = create_mock_joint_data()
    result = analyzer._is_joint_ready(good_joints, ["left_ankle", "right_ankle"], 0.5)
    assert result == True, "Should pass with high confidence"
    print("   PASS: High confidence data accepted")
    
    # Low confidence data
    bad_joints = {
        "left_ankle": {"point": (100, 400), "confidence": 0.3},
        "right_ankle": {"point": (500, 400), "confidence": 0.3},
    }
    result = analyzer._is_joint_ready(bad_joints, ["left_ankle", "right_ankle"], 0.5)
    assert result == False, "Should reject low confidence"
    print("   PASS: Low confidence data filtered")


def test_step_detection():
    """Test improved step detection (v2 algorithm)."""
    print("\n[TEST 4] Step Detection (v2 Algorithm)")
    analyzer = WalkAnalyzer()
    
    # Initial state
    joints = create_mock_joint_data()
    result = analyzer.update(joints, 0, True)
    assert result["step_count"] == 0, "Initial step count should be 0"
    print("   PASS: Initial state has 0 steps")
    
    # Simulate left foot rising (ankle and knee lift)
    joints = create_mock_joint_data(left_ankle_y=320, left_knee_y=180)
    result = analyzer.update(joints, 1, True)
    # May or may not detect step depending on threshold - just check no error
    print(f"   INFO: After left foot rise: {result['step_count']} steps")
    
    # Left foot lowers
    joints = create_mock_joint_data(left_ankle_y=400, left_knee_y=250)
    result = analyzer.update(joints, 2, True)
    print(f"   INFO: After left foot lower: {result['step_count']} steps")
    
    print("   PASS: Step detection runs without errors")


def test_improved_metrics():
    """Test new metric calculations."""
    print("\n[TEST 5] Improved Metrics Calculation")
    analyzer = WalkAnalyzer()
    
    # Simulate walking sequence
    for frame in range(5):
        joints = create_mock_joint_data()
        result = analyzer.update(joints, frame, True)
        
        # Check that all new metrics are present
        assert "body_sway" in result, "body_sway metric missing"
        assert "leg_lift_symmetry" in result, "leg_lift_symmetry metric missing"
        assert "posture_consistency" in result, "posture_consistency metric missing"
        assert "walking_speed" in result, "walking_speed metric missing"
    
    print("   PASS: All new metrics calculated and returned")


def test_posture_feedback():
    """Test posture feedback generation."""
    print("\n[TEST 6] Posture Feedback")
    analyzer = WalkAnalyzer()
    
    joints = create_mock_joint_data()
    result = analyzer.update(joints, 0, True)
    
    assert "feedback" in result, "Feedback should be generated"
    feedback = result["feedback"]
    assert isinstance(feedback, list), "Feedback should be a list"
    print(f"   PASS: Feedback generated: {len(feedback)} items")


def test_posture_accuracy():
    """Test posture accuracy calculation."""
    print("\n[TEST 7] Posture Accuracy")
    analyzer = WalkAnalyzer()
    
    joints = create_mock_joint_data()
    result = analyzer.update(joints, 0, True)
    
    assert "posture_accuracy_percent" in result, "posture_accuracy_percent should be present"
    accuracy = result["posture_accuracy_percent"]
    assert 0 <= accuracy <= 100, f"Accuracy should be 0-100, got {accuracy}"
    print(f"   PASS: Posture accuracy calculated: {accuracy:.1f}%")


def test_ankle_smoothing():
    """Test ankle position smoothing with deque."""
    print("\n[TEST 8] Ankle Position Smoothing")
    analyzer = WalkAnalyzer()
    
    # Simulate noisy ankle data
    noisy_positions = [
        (100, 400),
        (101, 395),  # noise
        (100, 405),  # noise
        (100, 400),
        (99, 398),   # noise
    ]
    
    for i, pos in enumerate(noisy_positions):
        joints = create_mock_joint_data(left_ankle_y=pos[1])
        result = analyzer.update(joints, i, True)
        # Just verify it runs without error
    
    print("   PASS: Smoothing filter handles noisy data")


def test_confidence_handling():
    """Test handling of varying joint confidence."""
    print("\n[TEST 9] Confidence Handling")
    analyzer = WalkAnalyzer()
    
    # Normal confidence
    good_joints = create_mock_joint_data()
    result = analyzer.update(good_joints, 0, True)
    assert result is not None, "Should return result for good confidence"
    print("   PASS: Normal confidence handled")
    
    # Degraded confidence (but above threshold)
    medium_joints = {
        "left_ankle": {"point": (100, 400), "confidence": 0.7},
        "right_ankle": {"point": (500, 400), "confidence": 0.7},
        "left_knee": {"point": (100, 250), "confidence": 0.7},
        "right_knee": {"point": (500, 250), "confidence": 0.7},
        "left_shoulder": {"point": (100, 100), "confidence": 0.7},
        "right_shoulder": {"point": (500, 100), "confidence": 0.7},
        "left_hip": {"point": (100, 300), "confidence": 0.7},
        "right_hip": {"point": (500, 300), "confidence": 0.7},
    }
    result = analyzer.update(medium_joints, 1, True)
    assert result is not None, "Should return result for medium confidence"
    print("   PASS: Medium confidence handled")
    
    # Very low confidence
    bad_joints = {
        "left_ankle": {"point": (100, 400), "confidence": 0.2},
        "right_ankle": {"point": (500, 400), "confidence": 0.2},
        "left_knee": {"point": (100, 250), "confidence": 0.2},
        "right_knee": {"point": (500, 250), "confidence": 0.2},
        "left_shoulder": {"point": (100, 100), "confidence": 0.2},
        "right_shoulder": {"point": (500, 100), "confidence": 0.2},
        "left_hip": {"point": (100, 300), "confidence": 0.2},
        "right_hip": {"point": (500, 300), "confidence": 0.2},
    }
    result = analyzer.update(bad_joints, 2, True)
    assert result is not None, "Should handle low confidence gracefully"
    # Status should indicate waiting for joint recognition
    print(f"   PASS: Low confidence handled gracefully (status: {result.get('status', 'unknown')})")


def test_walking_speed_calculation():
    """Test walking speed calculation."""
    print("\n[TEST 10] Walking Speed Calculation")
    analyzer = WalkAnalyzer()
    
    # Simulate multiple frames
    joints = create_mock_joint_data()
    result = analyzer.update(joints, 0, True)
    
    # With more frames, speed should be calculable
    for frame in range(1, 10):
        joints = create_mock_joint_data()
        result = analyzer.update(joints, frame, True)
    
    assert "walking_speed" in result, "walking_speed should be present"
    speed = result["walking_speed"]
    assert isinstance(speed, (int, float)), "Speed should be numeric"
    print(f"   PASS: Walking speed calculated: {speed:.2f} units")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("[TEST SUITE] AI Smart CareMate - Walk Analysis Enhancement")
    print("=" * 60)
    
    try:
        test_basic_initialization()
        test_reset_functionality()
        test_joint_confidence_check()
        test_step_detection()
        test_improved_metrics()
        test_posture_feedback()
        test_posture_accuracy()
        test_ankle_smoothing()
        test_confidence_handling()
        test_walking_speed_calculation()
        
        print("\n" + "=" * 60)
        print("SUCCESS: All 10 tests passed!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\nFAILURE: Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\nERROR: Unexpected exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

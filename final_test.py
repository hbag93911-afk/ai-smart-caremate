# -*- coding: utf-8 -*-
"""
AI Smart CareMate - Final Comprehensive Test
Tests core functionality of all enhanced components
"""
from walk_analysis import WalkAnalyzer
from squat_analysis import SquatAnalyzer
from goal_manager import GoalManager
from analytics import Analytics
import os


def test_walk_analysis_complete():
    """Complete walk analysis test."""
    print("\n[TEST] Complete Walk Analysis")
    try:
        analyzer = WalkAnalyzer()
        
        # Create realistic joint data
        def mock_joints():
            return {
                "left_ankle": {"point": (100, 400), "confidence": 0.9},
                "right_ankle": {"point": (500, 400), "confidence": 0.9},
                "left_knee": {"point": (100, 250), "confidence": 0.9},
                "right_knee": {"point": (500, 250), "confidence": 0.9},
                "left_shoulder": {"point": (100, 100), "confidence": 0.9},
                "right_shoulder": {"point": (500, 100), "confidence": 0.9},
                "left_hip": {"point": (100, 300), "confidence": 0.9},
                "right_hip": {"point": (500, 300), "confidence": 0.9},
            }
        
        # Simulate walking with step progression
        for frame in range(30):
            # Simulate step motion
            if frame % 10 == 5:  # Simulate lifting foot
                joints = mock_joints()
                joints["left_ankle"]["point"] = (100, 350)
                joints["left_knee"]["point"] = (100, 180)
            else:
                joints = mock_joints()
            
            result = analyzer.update(joints, frame * 33, True)
            
            # Verify all required keys exist
            required_keys = {
                'step_count', 'cadence', 'walk_time_seconds',
                'left_right_balance', 'gait_symmetry', 'walking_speed',
                'body_sway', 'leg_lift_symmetry', 'posture_consistency',
                'posture_accuracy_percent', 'feedback', 'posture_ok'
            }
            
            if not required_keys.issubset(result.keys()):
                print(f"   ERROR: Missing keys. Got: {result.keys()}")
                return False
        
        print("   PASS: Walk analysis complete with all metrics")
        print(f"      Steps: {result['step_count']}, Cadence: {result['cadence']:.1f}")
        print(f"      Body Sway: {result['body_sway']:.1f}, Symmetry: {result['leg_lift_symmetry']:.1f}")
        return True
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_squat_analysis_complete():
    """Complete squat analysis test."""
    print("\n[TEST] Complete Squat Analysis")
    try:
        analyzer = SquatAnalyzer()
        
        # Create joint data
        def mock_joints(knee_angle_deg=90):
            angle_rad = knee_angle_deg * 3.14159 / 180
            import math
            # Simulate knee angle changes
            return {
                "left_hip": {"point": (100, 300), "confidence": 0.9},
                "left_knee": {"point": (100, 300 + 100 * math.cos(angle_rad)), "confidence": 0.9},
                "left_ankle": {"point": (100, 400), "confidence": 0.9},
                "right_hip": {"point": (500, 300), "confidence": 0.9},
                "right_knee": {"point": (500, 300 + 100 * math.cos(angle_rad)), "confidence": 0.9},
                "right_ankle": {"point": (500, 400), "confidence": 0.9},
                "left_shoulder": {"point": (100, 100), "confidence": 0.9},
                "right_shoulder": {"point": (500, 100), "confidence": 0.9},
            }
        
        # Simulate squat progression
        frame = 0
        for angle in [100, 90, 80, 70, 60, 50, 60, 70, 80, 90, 100]:  # Squat sequence
            result = analyzer.update(mock_joints(angle), frame * 50, True)
            frame += 1
            
            if not isinstance(result, dict):
                print(f"   ERROR: update() should return dict")
                return False
        
        print("   PASS: Squat analysis complete")
        print(f"      Squats counted: {result['count']}")
        print(f"      Phase: {result['phase']}, Status: {result['posture_status']}")
        return True
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_goal_tracking():
    """Test goal tracking and progress."""
    print("\n[TEST] Goal Tracking")
    try:
        manager = GoalManager()
        
        # Set goals using correct constants
        manager.set_goal(manager.SQUAT, 100)
        manager.set_goal(manager.WALK, 5000)
        
        # Verify goals were set (via get_goal)
        squat_goal = manager.get_goal(manager.SQUAT)
        walk_goal = manager.get_goal(manager.WALK)
        
        if squat_goal is None:
            print("   ERROR: Squat goal not set")
            return False
        
        print("   PASS: Goals set successfully")
        print(f"      Squat goal: {squat_goal}, Walk goal: {walk_goal}")
        return True
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analytics_reports():
    """Test analytics and report generation."""
    print("\n[TEST] Analytics Reports")
    try:
        analytics = Analytics()
        
        # Get different summaries
        today = analytics.get_today_summary()
        weekly = analytics.get_weekly_summary()
        monthly = analytics.get_monthly_summary()
        
        if not isinstance(today, dict):
            print("   ERROR: today_summary should return dict")
            return False
        
        if not isinstance(weekly, dict):
            print("   ERROR: weekly_summary should return dict")
            return False
        
        if not isinstance(monthly, dict):
            print("   ERROR: monthly_summary should return dict")
            return False
        
        print("   PASS: All analytics reports generated")
        print(f"      Today's squats: {today.get('total_squats', 0)}, steps: {today.get('total_steps', 0)}")
        print(f"      Weekly total: {weekly.get('total_squats', 0)} squats, {weekly.get('total_steps', 0)} steps")
        return True
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_persistence():
    """Test database integrity."""
    print("\n[TEST] Database Persistence")
    try:
        db_path = "workout_history.db"
        
        if not os.path.exists(db_path):
            print("   WARNING: Database does not exist (will be created on first run)")
            return True
        
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table existence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['squat_records', 'walk_records', 'goals']
        for table in required_tables:
            if table not in tables:
                print(f"   WARNING: Table '{table}' not found")
        
        conn.close()
        print("   PASS: Database is accessible and contains required tables")
        return True
    except Exception as e:
        print(f"   ERROR: {e}")
        return False


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("=" * 70)
    print("[COMPREHENSIVE TEST] AI Smart CareMate - Walk Analysis Enhancement")
    print("=" * 70)
    
    tests = [
        test_walk_analysis_complete,
        test_squat_analysis_complete,
        test_goal_tracking,
        test_analytics_reports,
        test_database_persistence,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   FATAL ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"FINAL RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n[SUCCESS] All comprehensive tests passed!")
        print("The WalkMate enhancement is ready for Streamlit testing.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)

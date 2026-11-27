# -*- coding: utf-8 -*-
"""
AI Smart CareMate - Comprehensive Validation Test
Validates all components and their integration
"""
import os
import sqlite3
from walk_analysis import WalkAnalyzer
from squat_analysis import SquatAnalyzer
from goal_manager import GoalManager
from analytics import Analytics


def test_database_schema():
    """Test database structure and compatibility."""
    print("\n[TEST] Database Schema Validation")
    
    db_path = "workout_history.db"
    if not os.path.exists(db_path):
        print("   INFO: Database does not exist (will be created on first run)")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check squat_records table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='squat_records'")
        if cursor.fetchone():
            print("   PASS: squat_records table exists")
        
        # Check walk_records table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='walk_records'")
        if cursor.fetchone():
            print("   PASS: walk_records table exists")
        
        # Check goals table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='goals'")
        if cursor.fetchone():
            print("   PASS: goals table exists")
        
        conn.close()
        return True
    except Exception as e:
        print(f"   ERROR: Database error: {e}")
        return False


def test_walk_analyzer_initialization():
    """Test WalkAnalyzer initialization."""
    print("\n[TEST] WalkAnalyzer Initialization")
    try:
        analyzer = WalkAnalyzer()
        
        # Check all required attributes
        required_attrs = [
            'step_count', 'cadence', 'walk_time_seconds', 'left_right_balance',
            'gait_symmetry', 'body_sway', 'leg_lift_symmetry', 'posture_consistency',
            'walking_speed', 'posture_status', 'feedback_messages'
        ]
        
        for attr in required_attrs:
            if not hasattr(analyzer, attr):
                print(f"   ERROR: Missing attribute: {attr}")
                return False
        
        print("   PASS: All required attributes initialized")
        
        # Check methods
        required_methods = [
            'update', 'reset', '_detect_step_v2',
            '_calculate_body_sway', '_calculate_leg_lift_symmetry',
            '_calculate_posture_consistency', '_calculate_walking_speed'
        ]
        
        for method in required_methods:
            if not hasattr(analyzer, method):
                print(f"   ERROR: Missing method: {method}")
                return False
        
        print("   PASS: All required methods present")
        return True
    except Exception as e:
        print(f"   ERROR: Initialization failed: {e}")
        return False


def test_squat_analyzer_initialization():
    """Test SquatAnalyzer initialization."""
    print("\n[TEST] SquatAnalyzer Initialization")
    try:
        analyzer = SquatAnalyzer()
        
        required_attrs = [
            'squat_count', 'squat_phase', 'posture_feedback', 'is_analyzing'
        ]
        
        for attr in required_attrs:
            if not hasattr(analyzer, attr):
                print(f"   ERROR: Missing attribute: {attr}")
                return False
        
        print("   PASS: All required attributes initialized")
        
        required_methods = ['update', 'reset']
        for method in required_methods:
            if not hasattr(analyzer, method):
                print(f"   ERROR: Missing method: {method}")
                return False
        
        print("   PASS: All required methods present")
        return True
    except Exception as e:
        print(f"   ERROR: Initialization failed: {e}")
        return False


def test_goal_manager_initialization():
    """Test GoalManager initialization."""
    print("\n[TEST] GoalManager Initialization")
    try:
        manager = GoalManager()
        
        required_methods = [
            'get_goal', 'set_goal', 'record_daily_goal',
            'get_daily_goal_record', 'get_achievement_history'
        ]
        
        for method in required_methods:
            if not hasattr(manager, method):
                print(f"   ERROR: Missing method: {method}")
                return False
        
        print("   PASS: All required methods present")
        
        # Test basic functionality
        manager.set_goal('squats', 100)
        goal = manager.get_goal('squats')
        
        if goal != 100:
            print("   ERROR: Goal not stored properly")
            return False
        
        print("   PASS: Basic functionality works")
        return True
    except Exception as e:
        print(f"   ERROR: Initialization failed: {e}")
        return False


def test_analytics_initialization():
    """Test Analytics initialization."""
    print("\n[TEST] Analytics Initialization")
    try:
        analytics = Analytics()
        
        required_methods = [
            'get_today_summary', 'get_weekly_summary', 'get_monthly_summary',
            'get_daily_trend', 'get_comparison_vs_previous_period'
        ]
        
        for method in required_methods:
            if not hasattr(analytics, method):
                print(f"   ERROR: Missing method: {method}")
                return False
        
        print("   PASS: All required methods present")
        
        # Test basic functionality
        today = analytics.get_today_summary()
        
        if not isinstance(today, dict):
            print("   ERROR: get_today_summary should return dict")
            return False
        
        print("   PASS: Basic functionality works")
        return True
    except Exception as e:
        print(f"   ERROR: Initialization failed: {e}")
        return False


def test_walk_analysis_full_cycle():
    """Test complete walk analysis cycle."""
    print("\n[TEST] Walk Analysis Full Cycle")
    try:
        analyzer = WalkAnalyzer()
        
        # Create mock joint data
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
        
        # Simulate walking
        for frame in range(10):
            result = analyzer.update(mock_joints(), frame * 33, True)
            
            if not isinstance(result, dict):
                print(f"   ERROR: update() should return dict, got {type(result)}")
                return False
            
            # Check required keys
            required_keys = [
                'step_count', 'cadence', 'walk_time_seconds',
                'left_right_balance', 'gait_symmetry', 'walking_speed',
                'body_sway', 'leg_lift_symmetry', 'posture_consistency'
            ]
            
            for key in required_keys:
                if key not in result:
                    print(f"   ERROR: Missing key in update() result: {key}")
                    return False
        
        print("   PASS: Walk analysis cycle completed successfully")
        return True
    except Exception as e:
        print(f"   ERROR: Full cycle failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_validation_tests():
    """Run all validation tests."""
    print("=" * 60)
    print("[VALIDATION] AI Smart CareMate - Component Tests")
    print("=" * 60)
    
    tests = [
        test_database_schema,
        test_walk_analyzer_initialization,
        test_squat_analyzer_initialization,
        test_goal_manager_initialization,
        test_analytics_initialization,
        test_walk_analysis_full_cycle,
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
            print(f"   ERROR: Test exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_validation_tests()
    exit(0 if success else 1)

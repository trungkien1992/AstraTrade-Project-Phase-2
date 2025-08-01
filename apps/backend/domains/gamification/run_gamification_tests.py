#!/usr/bin/env python3
"""
Test runner for Gamification Domain tests
"""
import sys
import os
import unittest
import asyncio
from pathlib import Path

# Add the parent directory to Python path to import domain modules
current_dir = Path(__file__).parent
domain_dir = current_dir.parent.parent
sys.path.insert(0, str(domain_dir))

def run_tests():
    """Run all gamification domain tests"""
    
    # Discover and run tests
    loader = unittest.TestLoader()
    
    # Load test modules
    test_modules = [
        'domains.gamification.tests.test_value_objects',
        'domains.gamification.tests.test_entities', 
        'domains.gamification.tests.test_services'
    ]
    
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            tests = loader.loadTestsFromName(module_name)
            suite.addTests(tests)
            print(f"✓ Loaded tests from {module_name}")
        except Exception as e:
            print(f"✗ Failed to load {module_name}: {e}")
            return False
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"GAMIFICATION DOMAIN TEST RESULTS")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n🎉 ALL TESTS PASSED! 🎉")
        print(f"Gamification Domain implementation is ready for production.")
    else:
        print(f"\n❌ Some tests failed. Please fix issues before proceeding.")
    
    return success

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
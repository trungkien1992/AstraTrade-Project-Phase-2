#!/usr/bin/env python3
"""
User Domain Test Runner

Run all tests for the User Domain and generate comprehensive test report.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_tests():
    """Run all User Domain tests"""
    
    # Get the domain directory
    domain_dir = Path(__file__).parent
    test_dir = domain_dir / "tests"
    
    print("🧪 Running User Domain Tests")
    print("=" * 50)
    
    # Test files to run
    test_files = [
        "test_value_objects.py",
        "test_entities.py", 
        "test_services.py"
    ]
    
    total_tests_run = 0
    total_tests_passed = 0
    total_tests_failed = 0
    
    for test_file in test_files:
        test_path = test_dir / test_file
        
        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            continue
        
        print(f"\n📋 Running {test_file}")
        print("-" * 30)
        
        try:
            # Run pytest with verbose output
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                str(test_path), 
                "-v", 
                "--tb=short",
                "--no-header"
            ], capture_output=True, text=True, cwd=str(domain_dir))
            
            print(result.stdout)
            
            if result.stderr:
                print("Errors/Warnings:")
                print(result.stderr)
            
            # Parse results
            lines = result.stdout.split('\n')
            for line in lines:
                if "passed" in line and "failed" in line:
                    # Extract test counts
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            passed = int(parts[i-1])
                            total_tests_passed += passed
                        elif part == "failed":
                            failed = int(parts[i-1])
                            total_tests_failed += failed
                elif line.strip().endswith("passed"):
                    # Only passed tests
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            passed = int(parts[i-1])
                            total_tests_passed += passed
                            
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            continue
    
    total_tests_run = total_tests_passed + total_tests_failed
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 USER DOMAIN TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests Run: {total_tests_run}")
    print(f"✅ Tests Passed: {total_tests_passed}")
    print(f"❌ Tests Failed: {total_tests_failed}")
    
    if total_tests_run > 0:
        success_rate = (total_tests_passed / total_tests_run) * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if total_tests_failed == 0 and total_tests_run > 0:
        print("\n🎉 ALL TESTS PASSED! User Domain implementation is ready for production.")
    elif total_tests_failed > 0:
        print(f"\n⚠️  {total_tests_failed} tests failed. Review and fix before proceeding.")
    else:
        print("\n❓ No tests were executed. Check test file paths and dependencies.")
    
    return total_tests_failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
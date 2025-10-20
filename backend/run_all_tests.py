"""Run all tests with detailed output."""
import sys
import pytest

if __name__ == "__main__":
    args = [
        "-v",
        "-m", "not slow",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html"
    ]
    
    print("🧪 Running ALL Chess Insight AI Tests (excluding slow tests)")
    print(f"Arguments: {' '.join(args)}\n")
    
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Some tests failed (exit code: {exit_code})")
    
    sys.exit(exit_code)

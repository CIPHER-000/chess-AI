"""Test runner script for Chess Insight AI."""
import sys
import pytest

if __name__ == "__main__":
    # Run fast tests only (skip Stockfish tests)
    args = [
        "-v",  # Verbose
        "-m", "not slow",  # Skip slow tests
        "--tb=short",  # Short traceback
    ]
    
    # Add additional arguments if provided
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    
    print("🧪 Running Chess Insight AI Tests")
    print(f"Arguments: {' '.join(args)}\n")
    
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    sys.exit(exit_code)

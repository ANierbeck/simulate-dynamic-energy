#!/usr/bin/env python3
"""
Simple test runner script for the dynamic energy analysis application
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with coverage"""
    print("🧪 Running tests for Dynamic Energy Analysis Application...")
    print("=" * 60)
    
    # Install test dependencies if not already installed
    try:
        import pytest
        import pytest_cov
    except ImportError:
        print("⏳ Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"], check=True)
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=core",
        "--cov-report=term",
        "--cov-report=html",
        "-v"
    ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    print("-" * 60)
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/ directory")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
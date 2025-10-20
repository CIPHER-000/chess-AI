#!/usr/bin/env python3
"""
Chess Insight AI Deployment Readiness Test
Tests all configurations before deploying to Render
"""

import os
import sys
import json
from pathlib import Path

def test_file_exists(filepath, description):
    """Test if a required file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - MISSING")
        return False

def test_directory_exists(dirpath, description):
    """Test if a required directory exists."""
    if Path(dirpath).exists():
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} - MISSING")
        return False

def test_render_yaml():
    """Test render.yaml configuration."""
    print("\\n🔍 Testing render.yaml configuration...")
    
    if not test_file_exists("render.yaml", "Render configuration file"):
        return False
    
    try:
        with open("render.yaml", "r") as f:
            content = f.read()
            
        # Check for essential components
        required_sections = [
            "services:",
            "type: web",
            "type: pserv", 
            "type: redis",
            "buildCommand:",
            "startCommand:",
            "envVars:"
        ]
        
        missing = []
        for section in required_sections:
            if section not in content:
                missing.append(section)
        
        if missing:
            print(f"❌ render.yaml missing sections: {missing}")
            return False
        else:
            print("✅ render.yaml contains all required sections")
            return True
            
    except Exception as e:
        print(f"❌ Error reading render.yaml: {e}")
        return False

def test_backend_structure():
    """Test backend directory structure."""
    print("\\n🔍 Testing backend directory structure...")
    
    checks = [
        ("backend/", "Backend directory"),
        ("backend/app/", "App directory"),
        ("backend/app/main.py", "Main application file"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/alembic.ini", "Alembic configuration"),
        ("backend/alembic/", "Alembic directory"),
        ("backend/alembic/env.py", "Alembic environment"),
        ("backend/alembic/versions/", "Migration versions directory"),
        ("backend/alembic/versions/0001_initial_tables.py", "Initial migration"),
    ]
    
    passed = 0
    for filepath, description in checks:
        if test_file_exists(filepath, description) or test_directory_exists(filepath, description):
            passed += 1
    
    return passed == len(checks)

def test_requirements():
    """Test requirements.txt for essential packages."""
    print("\\n🔍 Testing Python requirements...")
    
    if not test_file_exists("backend/requirements.txt", "Requirements file"):
        return False
    
    try:
        with open("backend/requirements.txt", "r") as f:
            requirements = f.read()
        
        essential_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy", 
            "alembic",
            "psycopg2-binary",
            "redis",
            "python-chess",
            "stockfish",
            "httpx",
            "pydantic",
            "loguru"
        ]
        
        missing = []
        for package in essential_packages:
            if package not in requirements.lower():
                missing.append(package)
        
        if missing:
            print(f"❌ Missing essential packages: {missing}")
            return False
        else:
            print("✅ All essential packages present in requirements.txt")
            return True
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def test_health_endpoint():
    """Test if health endpoint is configured."""
    print("\\n🔍 Testing health endpoint configuration...")
    
    if not test_file_exists("backend/app/main.py", "Main application file"):
        return False
    
    try:
        with open("backend/app/main.py", "r") as f:
            main_content = f.read()
        
        if "/health" in main_content and "/api/v1/health" in main_content:
            print("✅ Health endpoints configured")
            return True
        else:
            print("❌ Health endpoints not found in main.py")
            return False
            
    except Exception as e:
        print(f"❌ Error reading main.py: {e}")
        return False

def test_cors_configuration():
    """Test CORS configuration."""
    print("\\n🔍 Testing CORS configuration...")
    
    try:
        with open("backend/app/main.py", "r") as f:
            main_content = f.read()
        
        if "CORSMiddleware" in main_content:
            print("✅ CORS middleware configured")
            return True
        else:
            print("❌ CORS middleware not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking CORS configuration: {e}")
        return False

def test_environment_variables():
    """Test environment variable handling."""
    print("\\n🔍 Testing environment variable configuration...")
    
    if not test_file_exists("backend/app/core/config.py", "Configuration file"):
        return False
    
    try:
        with open("backend/app/core/config.py", "r") as f:
            config_content = f.read()
        
        required_env_vars = [
            "POSTGRES_SERVER",
            "POSTGRES_USER", 
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
            "REDIS_HOST",
            "SECRET_KEY"
        ]
        
        missing = []
        for var in required_env_vars:
            if var not in config_content:
                missing.append(var)
        
        if missing:
            print(f"❌ Missing environment variables in config: {missing}")
            return False
        else:
            print("✅ All required environment variables configured")
            return True
            
    except Exception as e:
        print(f"❌ Error checking environment variables: {e}")
        return False

def main():
    """Run all deployment readiness tests."""
    print("🚀 Chess Insight AI - Deployment Readiness Test")
    print("=" * 50)
    
    tests = [
        ("Render Configuration", test_render_yaml),
        ("Backend Structure", test_backend_structure),
        ("Python Requirements", test_requirements),
        ("Health Endpoints", test_health_endpoint),
        ("CORS Configuration", test_cors_configuration),
        ("Environment Variables", test_environment_variables),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\\n⚠️  {test_name} test failed")
        except Exception as e:
            print(f"\\n💥 {test_name} test crashed: {e}")
    
    print("\\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ✅ ALL TESTS PASSED - Ready for deployment!")
        print("\\n🚀 Next steps:")
        print("1. Push code to GitHub/GitLab")
        print("2. Deploy to Render using render.yaml")
        print("3. Monitor deployment logs")
        print("4. Test live API endpoints")
        return True
    else:
        print(f"❌ {total - passed} tests failed - Fix issues before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

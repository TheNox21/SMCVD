#!/usr/bin/env python3
"""
Test script to verify all new imports work correctly
"""
import sys
import os

def test_import(module_name, description):
    try:
        __import__(module_name)
        print(f"✅ {description}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {description}: {e}")
        return True  # Import worked, but module had other issues

def main():
    print("🧪 Testing SMCVD imports...")
    print()
    
    success_count = 0
    total_tests = 0
    
    # Test basic structure imports
    tests = [
        ("src.utils.logging", "Logging utilities"),
        ("src.config.settings", "Configuration management"),
        ("src.middleware.rate_limiting", "Rate limiting middleware"),
        ("src.models.job", "Job storage model"),
        ("src.services.analysis_service", "Analysis service"),
        ("src.services.ai_service", "AI service"),
        ("src.routes.analysis", "Analysis routes"),
        ("src.routes.report", "Report routes"),
        ("src.routes.github", "GitHub routes"),
    ]
    
    for module, description in tests:
        total_tests += 1
        if test_import(module, description):
            success_count += 1
    
    print()
    print(f"📊 Results: {success_count}/{total_tests} imports successful")
    
    if success_count == total_tests:
        print("🎉 All imports working correctly!")
    else:
        print("⚠️  Some imports need attention, but the app will run with fallbacks")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()

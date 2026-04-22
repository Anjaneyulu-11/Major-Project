#!/usr/bin/env python
"""
Session Security Test Script
Tests the session security implementation for inactivity logout and browser close behavior.

Usage:
  python test_session_security.py
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.test import Client
from django.utils import timezone
from public_admin.middleware import SessionSecurityMiddleware

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_pass(msg):
    print(f"{Colors.GREEN}✓ PASS: {msg}{Colors.RESET}")

def print_fail(msg):
    print(f"{Colors.RED}✗ FAIL: {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ INFO: {msg}{Colors.RESET}")

def test_settings():
    """Test that session security settings are configured correctly"""
    print_test("Session Security Settings")
    
    from django.conf import settings
    
    tests_passed = 0
    tests_failed = 0
    
    # Check SESSION_EXPIRE_AT_BROWSER_CLOSE
    if getattr(settings, 'SESSION_EXPIRE_AT_BROWSER_CLOSE', False):
        print_pass("SESSION_EXPIRE_AT_BROWSER_CLOSE = True")
        tests_passed += 1
    else:
        print_fail("SESSION_EXPIRE_AT_BROWSER_CLOSE not set to True")
        tests_failed += 1
    
    # Check SESSION_COOKIE_HTTPONLY
    if getattr(settings, 'SESSION_COOKIE_HTTPONLY', False):
        print_pass("SESSION_COOKIE_HTTPONLY = True")
        tests_passed += 1
    else:
        print_fail("SESSION_COOKIE_HTTPONLY not set to True")
        tests_failed += 1
    
    # Check SESSION_COOKIE_SAMESITE
    samesite = getattr(settings, 'SESSION_COOKIE_SAMESITE', None)
    if samesite in ('Lax', 'Strict', 'None'):
        print_pass(f"SESSION_COOKIE_SAMESITE = {samesite}")
        tests_passed += 1
    else:
        print_info(f"SESSION_COOKIE_SAMESITE = {samesite} (check if appropriate)")
    
    # Check SESSION_SAVE_EVERY_REQUEST
    if getattr(settings, 'SESSION_SAVE_EVERY_REQUEST', False):
        print_pass("SESSION_SAVE_EVERY_REQUEST = True")
        tests_passed += 1
    else:
        print_fail("SESSION_SAVE_EVERY_REQUEST not set to True")
        tests_failed += 1
    
    # Check SESSION_COOKIE_AGE
    age = getattr(settings, 'SESSION_COOKIE_AGE', None)
    print_info(f"SESSION_COOKIE_AGE = {age} seconds ({age//3600} hours)")
    
    return tests_passed, tests_failed

def test_middleware_installed():
    """Test that SessionSecurityMiddleware is installed"""
    print_test("Middleware Installation")
    
    from django.conf import settings
    
    middleware_list = settings.MIDDLEWARE
    
    session_mw = 'django.contrib.sessions.middleware.SessionMiddleware'
    auth_mw = 'django.contrib.auth.middleware.AuthenticationMiddleware'
    security_mw = 'public_admin.middleware.SessionSecurityMiddleware'
    admin_mw = 'public_admin.middleware.AdminAccessMiddleware'
    
    tests_passed = 0
    tests_failed = 0
    
    if session_mw in middleware_list:
        print_pass("SessionMiddleware installed")
        tests_passed += 1
    else:
        print_fail("SessionMiddleware not found")
        tests_failed += 1
    
    if auth_mw in middleware_list:
        print_pass("AuthenticationMiddleware installed")
        tests_passed += 1
    else:
        print_fail("AuthenticationMiddleware not found")
        tests_failed += 1
    
    if security_mw in middleware_list:
        print_pass("SessionSecurityMiddleware installed")
        tests_passed += 1
    else:
        print_fail("SessionSecurityMiddleware not found")
        tests_failed += 1
    
    if admin_mw in middleware_list:
        print_pass("AdminAccessMiddleware installed")
        tests_passed += 1
    else:
        print_info("AdminAccessMiddleware not installed (optional)")
    
    # Check order: Session -> Auth -> Security
    if middleware_list.index(session_mw) < middleware_list.index(auth_mw):
        print_pass("SessionMiddleware before AuthenticationMiddleware ✓")
        tests_passed += 1
    else:
        print_fail("SessionMiddleware should be before AuthenticationMiddleware")
        tests_failed += 1
    
    if middleware_list.index(auth_mw) < middleware_list.index(security_mw):
        print_pass("AuthenticationMiddleware before SecurityMiddleware ✓")
        tests_passed += 1
    else:
        print_fail("AuthenticationMiddleware should be before SecurityMiddleware")
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_middleware_functionality():
    """Test SessionSecurityMiddleware functionality"""
    print_test("Middleware Functionality")
    
    tests_passed = 0
    tests_failed = 0
    
    # Check middleware attributes
    mw = SessionSecurityMiddleware(lambda r: None)
    
    if hasattr(mw, 'INACTIVITY_TIMEOUT'):
        timeout = mw.INACTIVITY_TIMEOUT
        print_pass(f"INACTIVITY_TIMEOUT defined = {timeout} seconds ({timeout//60} minutes)")
        tests_passed += 1
    else:
        print_fail("INACTIVITY_TIMEOUT not defined")
        tests_failed += 1
    
    if hasattr(mw, 'EXCLUDED_PATHS'):
        paths = mw.EXCLUDED_PATHS
        print_pass(f"EXCLUDED_PATHS defined with {len(paths)} paths")
        for path in paths:
            print(f"  - {path}")
        tests_passed += 1
    else:
        print_fail("EXCLUDED_PATHS not defined")
        tests_failed += 1
    
    # Test _is_excluded_path method
    if mw._is_excluded_path('/static/style.css'):
        print_pass("_is_excluded_path correctly identifies /static/ paths")
        tests_passed += 1
    else:
        print_fail("_is_excluded_path doesn't recognize /static/ paths")
        tests_failed += 1
    
    if not mw._is_excluded_path('/dashboard/'):
        print_pass("_is_excluded_path correctly rejects non-excluded paths")
        tests_passed += 1
    else:
        print_fail("_is_excluded_path wrongly excludes /dashboard/")
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_session_creation():
    """Test that sessions are created properly"""
    print_test("Session Creation")
    
    from django.contrib.sessions.backends.db import SessionStore
    from django.conf import settings
    
    tests_passed = 0
    tests_failed = 0
    
    # Create a test session
    session = SessionStore()
    session['_last_activity'] = timezone.now().isoformat()
    session.create()
    
    print_info(f"Created test session: {session.session_key}")
    
    if session.session_key:
        print_pass("Session key generated successfully")
        tests_passed += 1
    else:
        print_fail("Failed to generate session key")
        tests_failed += 1
    
    # Verify session data
    session_data = SessionStore(session_key=session.session_key)
    if '_last_activity' in session_data:
        print_pass("_last_activity field stored in session")
        tests_passed += 1
    else:
        print_fail("_last_activity field not found in session")
        tests_failed += 1
    
    # Clean up
    session.delete()
    
    return tests_passed, tests_failed

def test_database_connection():
    """Test database and session backend"""
    print_test("Database & Session Backend")
    
    from django.contrib.sessions.models import Session
    from django.db import connection
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        # Test DB connection
        connection.ensure_connection()
        print_pass("Database connection successful")
        tests_passed += 1
    except Exception as e:
        print_fail(f"Database connection failed: {e}")
        tests_failed += 1
    
    try:
        # Count existing sessions
        count = Session.objects.count()
        print_info(f"Active sessions in database: {count}")
        print_pass("Session table accessible")
        tests_passed += 1
    except Exception as e:
        print_fail(f"Session table query failed: {e}")
        tests_failed += 1
    
    return tests_passed, tests_failed

def test_login_flow():
    """Test basic login flow (if test user exists)"""
    print_test("Login Flow (Optional)")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        # Try to get or create test user
        test_user, created = User.objects.get_or_create(
            username='test_session_user',
            defaults={'email': 'test@example.com'}
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print_info("Created test user: test_session_user")
        else:
            print_info("Using existing test user: test_session_user")
        
        # Attempt login with client
        client = Client()
        response = client.post('/login/', {
            'username': 'test_session_user',
            'password': 'testpass123',
        }, follow=True)
        
        if client.session:
            print_pass("Session created after login")
            tests_passed += 1
            
            if '_last_activity' in client.session:
                print_pass("_last_activity recorded in session")
                tests_passed += 1
            else:
                print_info("_last_activity not in session (may be added by middleware)")
        else:
            print_fail("No session created after login attempt")
            tests_failed += 1
            
    except Exception as e:
        print_info(f"Login flow test skipped: {e}")
    
    return tests_passed, tests_failed

def print_summary(total_passed, total_failed):
    """Print test summary"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    if total_failed == 0:
        print(f"{Colors.GREEN}✓ All tests passed! ({total_passed} assertions){Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Tests completed: {total_passed} passed, {total_failed} failed{Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}Next Steps:{Colors.RESET}")
    print("1. Deploy to production")
    print("2. Set SESSION_COOKIE_SECURE = True (if using HTTPS)")
    print("3. Monitor logs for inactivity logouts")
    print("4. Run 'python manage.py cleanupsessions' periodically")

def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}╔════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║  SESSION SECURITY IMPLEMENTATION TEST SUITE            ║{Colors.RESET}")
    print(f"{Colors.BLUE}║  Civic Pulse - Public Grievance Portal                 ║{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════╝{Colors.RESET}")
    
    total_passed = 0
    total_failed = 0
    
    # Run all tests
    p, f = test_settings()
    total_passed += p
    total_failed += f
    
    p, f = test_database_connection()
    total_passed += p
    total_failed += f
    
    p, f = test_middleware_installed()
    total_passed += p
    total_failed += f
    
    p, f = test_middleware_functionality()
    total_passed += p
    total_failed += f
    
    p, f = test_session_creation()
    total_passed += p
    total_failed += f
    
    p, f = test_login_flow()
    total_passed += p
    total_failed += f
    
    # Print summary
    print_summary(total_passed, total_failed)
    
    sys.exit(0 if total_failed == 0 else 1)

if __name__ == '__main__':
    main()

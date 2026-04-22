# Session Security Implementation - Civic Pulse

## Overview

This document describes the session security enhancements implemented for the Civic Pulse public grievance portal. The implementation ensures:

✅ **Browser Close Logout**: Sessions expire when the browser is closed
✅ **Inactivity Auto-Logout**: Users are logged out after 30 minutes of inactivity
✅ **Session Fixation Prevention**: No previous user sessions after server restart
✅ **Production-Safe**: Designed for public portal environments
✅ **Non-Breaking**: Preserves authentication, admin access, and language switching

---

## What Was Changed

### 1. **Enhanced Middleware** ([pulse_admin/middleware.py](pulse_admin/middleware.py))

#### New: `SessionSecurityMiddleware`
- Tracks last user activity timestamp in session
- Automatically logs out users after 30 minutes of inactivity
- Excludes certain paths (static files, language switching, logout)
- Implements graceful session cleanup
- Logs inactivity logout events for security audit

**Key Features:**
```python
INACTIVITY_TIMEOUT = 30 * 60  # 30 minutes in seconds
EXCLUDED_PATHS = ['/static/', '/media/', '/logout/', '/set_language/', ...]
```

### 2. **Session Configuration** (public_pulse/settings.py)

#### Session Security Settings Added:
```python
# Browser Close Logout
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Session Timeout (4 hours - backup to middleware check)
SESSION_COOKIE_AGE = 4 * 60 * 60

# Always update session to track inactivity
SESSION_SAVE_EVERY_REQUEST = True

# Security: JavaScript cannot access session cookie
SESSION_COOKIE_HTTPONLY = True

# Security: Only sent over HTTPS (development: False, production: True)
SESSION_COOKIE_SECURE = False

# Security: Prevent CSRF attacks via cookie
SESSION_COOKIE_SAMESITE = 'Lax'

# Session serialization format
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
```

### 3. **Middleware Ordering** (public_pulse/settings.py)

**Correct middleware order (critical for functionality):**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',      # 1st: Load session
    'public_pulse.safe_i18n_middleware.SafeI18nMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',   # 2nd: Load user
    'pulse_admin.middleware.SessionSecurityMiddleware',          # 3rd: Check activity
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pulse_admin.middleware.AdminAccessMiddleware',
]
```

**Why this order matters:**
1. SessionMiddleware loads first (creates session object)
2. AuthenticationMiddleware loads user into request
3. SessionSecurityMiddleware checks inactivity (needs both session + user)
4. AdminAccessMiddleware checks permissions (needs user + messages)

---

## How It Works

### Flow 1: Browser Tab Closure
```
User closes browser tab
  ↓
Browser clears cookies (including sessionid)
  ↓
Django session destroyed (SESSION_EXPIRE_AT_BROWSER_CLOSE = True)
  ↓
Next visit requires login
```

### Flow 2: 30-Minute Inactivity
```
User clicks on page
  ↓
SessionSecurityMiddleware.check_session_activity() runs
  ↓
Calculate: now - request.session['_last_activity']
  ↓
If > 30 minutes:
  ├─ logout(request) called
  ├─ Log inactivity event
  └─ User redirected to login
Else:
  ├─ Update _last_activity timestamp
  └─ Request proceeds normally
```

### Flow 3: Server Restart
```
Server restarts
  ↓
Django session backend reset
  ↓
Old sessionids still in database (if using DB backend)
  ↓
But Django load balancer/new process doesn't have them in memory
  ↓
When user makes request:
  ├─ SessionMiddleware tries to load old session
  ├─ If expired: new session created
  └─ User redirected to login (not authenticated)
```

### Flow 4: Logout Button Click
```
User clicks logout (/logout/)
  ↓
View calls logout(request)
  ├─ Clears session data
  ├─ Removes user from request
  └─ Deletes 'django_session' record
  ↓
SessionSecurityMiddleware.delete_cookie() runs
  └─ Removes sessionid cookie
  ↓
Redirects to LOGOUT_REDIRECT_URL = '/'
```

---

## Security Benefits

### 1. **Protection Against Unattended Sessions**
- Public portal users won't leave active sessions on shared/public computers
- 30-minute timeout catches forgotten logins

### 2. **Prevention of Session Fixation**
- New session ID generated on each login (Django default)
- No stored session cookies after browser close
- Server restart clears old session IDs

### 3. **Reduced Attack Surface**
- SessionSecurityMiddleware logs inactivity logouts (audit trail)
- SESSION_COOKIE_HTTPONLY prevents JavaScript theft
- SESSION_COOKIE_SAMESITE prevents CSRF attacks

### 4. **Compliance**
- Meets public portal security requirements
- GDPR-friendly (automatic logout deletes session data)
- Government standards for citizen portals

---

## Excluded Paths (No Activity Update)

The following paths don't trigger activity updates:
- `/static/` - Static files (CSS, JS, images)
- `/media/` - Media files (uploads)
- `/logout/` - Logout action itself
- `/set_language/` - Language switching
- `/health/`, `/status/` - Health checks

**Why?** These aren't "real" user activity - they're infrastructure requests.

---

## Testing Guide

### Test 1: Browser Close Logout
1. Login to the portal
2. Note your session ID: Open DevTools → Application → Cookies → sessionid
3. Close the browser tab/window
4. Open a new tab
5. **Expected:** Portal shows login page (session expired)

### Test 2: 30-Minute Inactivity
1. Login to the portal
2. Don't click anything for 31 minutes
3. Make any request (click any link)
4. **Expected:** User is logged out, redirected to login page
5. Check Django logs: Should see "User X logged out due to inactivity (31 minutes)"

### Test 3: Activity Update
1. Login to the portal
2. After 15 minutes, click on a page
3. After another 20 minutes, click again
4. **Expected:** Still logged in (activity reset timer)
5. Wait 31 minutes without clicking
6. **Expected:** Then receive logout

### Test 4: Language Switching (No Logout)
1. Login to the portal
2. Switch language (e.g., English → Hindi)
3. **Expected:** Still logged in (language switching excluded from inactivity)
4. Check: `/set_language/` request in Network tab doesn't log activity

### Test 5: Admin Access
1. Login with non-staff user
2. Try accessing `/admin/`
3. **Expected:** Redirected with permission error
4. Login with staff/admin user
5. Try accessing `/admin/`
6. **Expected:** Access granted (username in Django admin)

### Test 6: Session Renewal on Activity
1. Login
2. Make multiple requests within 30 minutes
3. **Expected:** Session persists (not logged out)
4. Check DevTools: sessionid cookie still valid

### Test 7: Server Restart (Development)
1. Login to portal
2. Stop Django dev server (Ctrl+C)
3. Start Django dev server again
4. Try accessing portal with same browser
5. **Expected:** Redirected to login (old session ID invalid)

---

## Production Deployment Checklist

### Before Going to Production

- [ ] Set `SESSION_COOKIE_SECURE = True` (requires HTTPS)
- [ ] Set `DEBUG = False` in settings.py
- [ ] Generate new `SECRET_KEY` (don't use development one)
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up HTTPS certificate (Let's Encrypt recommended)
- [ ] Use database-backed sessions instead of cache:
  ```bash
  python manage.py migrate  # Creates django_session table
  ```
- [ ] Review and adjust INACTIVITY_TIMEOUT if needed
- [ ] Set up log aggregation (monitor inactivity logouts)

### Session Backend (Production Recommended)

**Current (Default - File-based):**
```python
# Django default - sessions stored in file system
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

**Recommended for Production (Database-backed):**
```python
# Sessions stored in database (more reliable)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

To migrate to database sessions:
```bash
# In production environment
python manage.py migrate
python manage.py cleanupsessions  # Run periodically
```

---

## Customization

### Adjust Inactivity Timeout

**Default:** 30 minutes

**To change, edit** [pulse_admin/middleware.py](pulse_admin/middleware.py):
```python
class SessionSecurityMiddleware:
    INACTIVITY_TIMEOUT = 15 * 60  # Change to 15 minutes
```

### Exclude More Paths

**To exclude additional paths** (e.g., API endpoints), edit:
```python
EXCLUDED_PATHS = [
    '/static/',
    '/media/',
    '/logout/',
    '/set_language/',
    '/api/health/',  # Add this
    '/api/status/',  # Add this
]
```

### Disable for Specific Paths

**To require login but NOT track inactivity** (e.g., admin):
```python
def _check_session_activity(self, request):
    # Skip admin paths
    if request.path.startswith('/admin/'):
        return
    # ... rest of code
```

---

## Troubleshooting

### "User logged out unexpectedly after 5 minutes"

**Cause:** SESSION_COOKIE_AGE conflict with middleware

**Solution:** Ensure INACTIVITY_TIMEOUT < SESSION_COOKIE_AGE in the same units

### "Language switching breaks translation"

**Cause:** `/set_language/` was removed from EXCLUDED_PATHS

**Solution:** Add it back to EXCLUDED_PATHS

### "Admin can't login"

**Cause:** SessionSecurityMiddleware running before admin auth completes

**Solution:** Check middleware order (SessionSecurityMiddleware must be AFTER AuthenticationMiddleware)

### "Sessions persist after browser close"

**Cause:** SESSION_EXPIRE_AT_BROWSER_CLOSE = False

**Solution:** 
```python
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Must be True
```

### "Lots of inactivity logout messages in logs"

**Cause:** INACTIVITY_TIMEOUT is too aggressive

**Solution:** Increase timeout:
```python
INACTIVITY_TIMEOUT = 60 * 60  # 60 minutes instead of 30
```

---

## Monitoring & Maintenance

### View Session Count
```bash
python manage.py shell
from django.contrib.sessions.models import Session
print(f"Active sessions: {Session.objects.count()}")
```

### Clear Expired Sessions
```bash
# Django includes this command
python manage.py cleanupsessions

# Or add to cron (weekly)
0 2 * * 0 /path/to/venv/bin/python /path/to/manage.py cleanupsessions
```

### Monitor Logs for Inactivity Logouts
```bash
# Search Django logs for inactivity events
grep "logged out due to inactivity" /var/log/django.log

# Count inactivity logouts per user
grep "logged out due to inactivity" /var/log/django.log | cut -d' ' -f3 | sort | uniq -c
```

---

## Backward Compatibility

✅ **No Breaking Changes:**
- Existing authentication system unchanged
- Admin interface fully functional
- Language switching works normally
- Existing views don't need modification
- API endpoints can exclude themselves via EXCLUDED_PATHS

⚠️ **User Experience Changes:**
- Sessions expire on browser close (new)
- Auto-logout after 30 min inactivity (new)
- Users need to login more frequently (by design)

---

## Files Modified

1. **[pulse_admin/middleware.py](pulse_admin/middleware.py)**
   - Added: `SessionSecurityMiddleware` class
   - Kept: `AdminAccessMiddleware` class

2. **[public_pulse/settings.py](public_pulse/settings.py)**
   - Updated: SESSION_* configuration
   - Updated: MIDDLEWARE list with new ordering

---

## References

- [Django Session Security (Official Docs)](https://docs.djangoproject.com/en/4.2/topics/http/sessions/)
- [OWASP Session Security](https://owasp.org/www-community/attacks/Session_fixation)
- [PCI-DSS Inactivity Timeout](https://www.pcisecuritystandards.org/)

---

## Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Review Django session documentation
3. Check middleware order in settings.py
4. Verify SESSION_* settings are correct
5. Check Django debug logs: `tail -f logs/debug.log`

---

**Last Updated:** February 2026
**Django Version:** 4.x
**Python Version:** 3.8+

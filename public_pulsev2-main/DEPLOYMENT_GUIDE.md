# Session Security - Quick Deployment Guide

## For Development Testing

### 1. Run the Test Suite
```bash
cd /path/to/public-pulse
python manage.py shell < test_session_security.py
```

Or directly:
```bash
python test_session_security.py
```

### 2. Manual Testing in Development

**Test 1: Browser Close Logout**
```
1. Login to http://127.0.0.1:8000/login/
2. Note the sessionid cookie (DevTools → Application → Cookies)
3. Close browser completely
4. Reopen browser and visit portal
5. ✓ Should see login page (session expired)
```

**Test 2: Inactivity Timeout (30 minutes)**
```
1. Login to portal
2. Wait 31 minutes without making any requests
3. Make any request (click a link)
4. ✓ Should see login page (auto-logout)
5. Check Django logs for: "User X logged out due to inactivity"
```

**Test 3: Verify Activity Tracking**
```
1. Login
2. Click around for 15 minutes
3. ✓ Session persists
4. Check: request.session['_last_activity'] updated each request
```

### 3. Quick Local Test Script

```python
# Quick test in Django shell
python manage.py shell

>>> from django.contrib.sessions.models import Session
>>> from django.contrib.sessions.backends.db import SessionStore
>>> from django.utils import timezone
>>> 
>>> # Create test session
>>> s = SessionStore()
>>> s['_last_activity'] = timezone.now().isoformat()
>>> s.create()
>>> print(f"Created session: {s.session_key}")
>>> 
>>> # Verify
>>> s2 = SessionStore(session_key=s.session_key)
>>> print(s2['_last_activity'])
>>> 
>>> # Cleanup
>>> s.delete()
```

---

## For Production Deployment

### Pre-Deployment Checklist

- [ ] Back up database
- [ ] Update settings.py:
  ```python
  SESSION_COOKIE_SECURE = True      # HTTPS required
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SAMESITE = 'Strict'
  DEBUG = False
  ```

- [ ] Verify HTTPS certificate is valid
- [ ] Run migrations (if needed):
  ```bash
  python manage.py migrate
  ```

- [ ] Test in staging environment first

### Deployment Steps

**1. Update Settings**
```bash
# In production server
nano public_pulse/settings.py

# Change:
SESSION_COOKIE_SECURE = True  # Only over HTTPS
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

**2. Run Migrations**
```bash
python manage.py migrate
```

**3. Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

**4. Restart Production Server**
```bash
# If using systemd
sudo systemctl restart django_app

# If using gunicorn
pkill -f gunicorn
gunicorn public_pulse.wsgi:application --bind 0.0.0.0:8000
```

**5. Verify Deployment**
```bash
# Check settings applied correctly
python manage.py shell
>>> from django.conf import settings
>>> settings.SESSION_COOKIE_SECURE
True
>>> settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
True
```

### Monitor After Deployment

**Check for inactivity logouts:**
```bash
tail -f /var/log/django.log | grep "logged out due to inactivity"
```

**Monitor session count:**
```bash
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> print(f"Active sessions: {Session.objects.count()}")
```

**Clean up old sessions:**
```bash
# Run on schedule (weekly)
python manage.py cleanupsessions

# Or add to crontab:
# 0 2 * * 0 /path/to/venv/bin/python /path/to/manage.py cleanupsessions
```

---

## Configuration in Production

### Recommended Settings for Production

```python
# public_pulse/settings.py

# ========== SESSION SECURITY (PRODUCTION) ==========
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 4 * 60 * 60          # 4 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True              # ← PRODUCTION ONLY (HTTPS required)
SESSION_COOKIE_SAMESITE = 'Strict'        # Stricter than Lax
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# Database-backed sessions (more reliable)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

### Inactivity Timeout Customization

To change from 30 minutes to a different value:

```python
# pulse_admin/middleware.py
class SessionSecurityMiddleware:
    INACTIVITY_TIMEOUT = 60 * 60  # 60 minutes instead of 30
```

### For High-Traffic Sites

If you have many concurrent users, consider:

1. **Cache-backed sessions** (faster than DB):
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'  # Must have Redis/Memcached configured
```

2. **Session cleanup in background task**:
```python
# Use Celery to run cleanupsessions periodically
python manage.py cleanupsessions --every-hour
```

---

## Troubleshooting Production Issues

### Issue: "Users logged out too quickly"
**Solution:** Increase inactivity timeout
```python
INACTIVITY_TIMEOUT = 60 * 60  # 60 minutes
```

### Issue: "SESSION_COOKIE_SECURE requires HTTPS"
**Solution:** Ensure SSL certificate is configured
```bash
# Check if port 443 is listening
netstat -tlnp | grep 443

# Restart web server with SSL
sudo systemctl restart nginx  # or apache2
```

### Issue: "Old sessions causing problems"
**Solution:** Clean up manually
```bash
python manage.py cleanupsessions
```

### Issue: "Admin users getting logged out"
**Solution:** Add admin exclusion in middleware
```python
# pulse_admin/middleware.py
if request.path.startswith('/admin/'):
    self._update_last_activity(request)
    return  # Don't check inactivity for admin
```

---

## Rollback Plan (If Needed)

If issues occur, quickly revert:

```bash
# 1. Restore previous settings.py
git checkout public_pulse/settings.py

# 2. Restore previous middleware.py
git checkout pulse_admin/middleware.py

# 3. Restart application
sudo systemctl restart django_app

# 4. Verify reversal
python manage.py shell
>>> from django.conf import settings
>>> settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
False  # Back to default
```

---

## Monitoring & Maintenance

### Weekly Tasks
```bash
# Clean old sessions
python manage.py cleanupsessions

# Check for errors
grep -i "error\|warning" /var/log/django.log | tail -20

# Verify active sessions
python manage.py shell -c "from django.contrib.sessions.models import Session; print(f'Active: {Session.objects.count()}')"
```

### Monthly Tasks
```bash
# Review security logs
grep "inactivity" /var/log/django.log | wc -l

# Check database size
python manage.py manage.py dbshell -c "SELECT COUNT(*) FROM django_session;"

# Verify no orphaned sessions
python manage.py cleanupsessions --dry-run
```

---

## Support & Additional Resources

- Django Session Documentation: https://docs.djangoproject.com/en/4.2/topics/http/sessions/
- Security Best Practices: https://docs.djangoproject.com/en/4.2/topics/security/
- Production Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/

---

**Created:** February 2026
**Django Version:** 4.x
**Last Updated:** February 2026

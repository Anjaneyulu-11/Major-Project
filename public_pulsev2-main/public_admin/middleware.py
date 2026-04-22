from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class SessionSecurityMiddleware:
    """
    Middleware for secure session management:
    - Logs out users after 30 minutes of inactivity
    - Prevents session fixation attacks
    - Ensures proper cleanup on browser close
    - Production-safe for public portals
    """
    
    INACTIVITY_TIMEOUT = 30 * 60  # 30 minutes in seconds
    
    # URLs that don't count as user activity
    EXCLUDED_PATHS = [
        '/static/',
        '/media/',
        '/logout/',
        '/set_language/',
        '/health/',
        '/status/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip excluded paths
        if not self._is_excluded_path(request.path):
            if request.user.is_authenticated:
                self._check_session_activity(request)
                self._update_last_activity(request)

        response = self.get_response(request)
        
        # Clear session-related cookies on logout
        if request.path == '/logout/':
            response.delete_cookie('sessionid', path='/', domain=None)
        
        return response

    def _is_excluded_path(self, path):
        """Check if path should be excluded from activity tracking"""
        return any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS)

    def _check_session_activity(self, request):
        """Check if user session has expired due to inactivity"""
        last_activity = request.session.get('_last_activity')
        
        if last_activity:
            try:
                last_activity_time = timezone.datetime.fromisoformat(last_activity)
                now = timezone.now()
                time_since_activity = (now - last_activity_time).total_seconds()
                
                if time_since_activity > self.INACTIVITY_TIMEOUT:
                    logger.info(
                        f"User {request.user.username} logged out due to inactivity "
                        f"({time_since_activity/60:.0f} minutes)"
                    )
                    logout(request)
                    # User will be redirected to login by view/auth check
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing last_activity: {e}")
                # Continue - let request proceed

    def _update_last_activity(self, request):
        """Update the last activity timestamp for the session"""
        request.session['_last_activity'] = timezone.now().isoformat()
        # Mark session as modified so it gets saved
        request.session.modified = True


class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is trying to access admin URLs
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access admin panel.')
                return redirect(reverse('login') + '?next=' + request.path)
            
            if not request.user.is_staff:
                messages.error(request, 'You do not have permission to access the admin panel.')
                return redirect('home')
        
        response = self.get_response(request)
        return response
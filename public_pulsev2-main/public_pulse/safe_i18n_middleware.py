"""
Safe i18n middleware for Civic Pulse.
Catches translation loading errors and provides graceful fallback.

This prevents "unpack requires a buffer of 8 bytes" crashes when .mo files
are corrupted or improperly formatted, while still allowing language selection
and template {% trans %} tags to function via Django's translation system.
"""

import logging
from django.utils.translation import activate, get_language
from django.http import HttpRequest

logger = logging.getLogger(__name__)


class SafeI18nMiddleware:
    """
    Wraps Django's locale middleware with error handling.
    - Prevents crashes from corrupted .mo files
    - Maintains language preference in session
    - Falls back to English if translation loading fails
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest):
        """Process request with safe translation handling."""
        try:
            # Get the requested language from session, cookie, or Accept-Language
            language = self._get_language_for_request(request)
            
            # Try to activate the language
            try:
                activate(language)
            except Exception as e:
                # Translation loading failed - fall back to English
                logger.warning(f"Failed to activate language '{language}': {e}")
                logger.info("Falling back to English")
                activate('en')
            
            # Store current language in request for templates
            request.LANGUAGE_CODE = get_language()
        
        except Exception as e:
            logger.error(f"i18n middleware error: {e}", exc_info=True)
            # Continue anyway - don't break the site
        
        response = self.get_response(request)
        return response
    
    def _get_language_for_request(self, request: HttpRequest) -> str:
        """Extract language preference from session, cookie, or browser."""
        from django.conf import settings
        
        # 1. Check Django session
        if hasattr(request, 'session') and 'django_language' in request.session:
            lang = request.session.get('django_language')
            if lang in [code for code, _ in settings.LANGUAGES]:
                return lang
        
        # 2. Check cookie (set by set_language view)
        lang_cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if lang_cookie and lang_cookie in [code for code, _ in settings.LANGUAGES]:
            return lang_cookie
        
        # 3. Check HTTP Accept-Language header
        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        if accept_language:
            lang = self._parse_accept_language(accept_language, settings.LANGUAGES)
            if lang:
                return lang
        
        # 4. Default to configured language
        return settings.LANGUAGE_CODE
    
    def _parse_accept_language(self, accept_language: str, supported_languages):
        """Parse Accept-Language header and find best match."""
        try:
            # Parse Accept-Language like: "en-US,en;q=0.9,hi;q=0.8"
            supported_codes = [code for code, _ in supported_languages]
            
            for part in accept_language.split(','):
                part = part.strip().split(';')[0].strip()
                
                # Exact match
                if part in supported_codes:
                    return part
                
                # Language only match (e.g., "en" from "en-US")
                lang = part.split('-')[0].lower()
                if lang in supported_codes:
                    return lang
            
            return None
        except Exception:
            return None

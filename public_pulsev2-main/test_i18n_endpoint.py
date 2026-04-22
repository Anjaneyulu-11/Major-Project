#!/usr/bin/env python
"""
Test Django i18n language switching endpoint.
Verifies that /i18n/setlang/ works without errors.

Run from project root:
    python test_i18n_endpoint.py
"""

import os
import sys
import django
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')

try:
    django.setup()
except Exception as e:
    print("✗ Django setup failed:", str(e))
    sys.exit(1)

from django.conf import settings

def test_language_switching():
    """Test language switching via /i18n/setlang/ endpoint."""
    setup_test_environment()
    client = Client()
    
    print("Testing Django i18n language switching")
    print("-" * 60)
    print(f"Configured languages: {[code for code, _ in settings.LANGUAGES]}")
    print()
    
    languages_to_test = ['hi', 'te', 'ta', 'kn', 'ml', 'mr', 'bn']
    
    for lang_code in languages_to_test:
        try:
            # Test switching to this language (POST to /i18n/setlang/)
            response = client.post(
                '/i18n/setlang/',
                {'language': lang_code, 'next': '/'},
                follow=True
            )
            
            if response.status_code == 200:
                print(f"✓ Language '{lang_code}': POST /i18n/setlang/ → 200 OK")
                # Check if session cookie was set
                if 'django_language' in client.cookies:
                    print(f"  ✓ Session cookie set: django_language={client.cookies.get('django_language').value}")
            else:
                print(f"✗ Language '{lang_code}': Status {response.status_code}")
        
        except Exception as e:
            print(f"✗ Language '{lang_code}': ERROR - {str(e)}")
    
    teardown_test_environment()
    print("-" * 60)
    print("✅ Language switching tests complete!")
    print("If all languages show '200 OK', language switching is working.")

if __name__ == '__main__':
    test_language_switching()

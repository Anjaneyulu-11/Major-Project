#!/usr/bin/env python
"""
Minimal gettext translation loading test.
Directly test if translations can be loaded without Django setup.
"""

import gettext
from pathlib import Path

def test_translation_loading():
    """Test if gettext can load .mo files directly."""
    locale_dir = Path('locale')
    languages = ['en', 'hi', 'te', 'ta', 'kn', 'ml', 'mr', 'bn']
    
    print("Testing gettext translation loading")
    print("-" * 60)
    
    for lang in languages:
        mo_path = locale_dir / lang / 'LC_MESSAGES' / 'django.mo'
        
        if not mo_path.exists():
            print(f"✗ {lang}: .mo file not found at {mo_path}")
            continue
        
        try:
            # Try to load the .mo file using gettext
            trans = gettext.GNUTranslations(open(mo_path, 'rb'))
            num_msgs = len(trans._catalog) if hasattr(trans, '_catalog') else 'unknown'
            print(f"✓ {lang}: Loaded {mo_path.name} ({num_msgs} messages)")
        
        except Exception as e:
            print(f"✗ {lang}: Failed to load - {type(e).__name__}: {e}")
    
    print("-" * 60)

if __name__ == '__main__':
    test_translation_loading()

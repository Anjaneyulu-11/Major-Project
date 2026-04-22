#!/usr/bin/env python
"""
Validate and clean locale files for Django i18n.
- Ensures .po files are valid UTF-8 (attempts safe re-encoding from latin-1 if necessary)
- Removes corrupted or empty .mo files that cause gettext crashes
- Uses Django settings for LOCALE_PATHS and LANGUAGES

Run from project root:
    python validate_and_clean_locales.py

This script is safe: it only deletes .mo files that appear invalid and rewrites .po files when encoding fixes are applied.
"""

import os
import sys
import struct
from pathlib import Path
import shutil

# Bootstrap Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')
try:
    import django
    django.setup()
    from django.conf import settings
except Exception as e:
    print("✗ Could not import Django settings. Make sure you're in project root and Django is installed.")
    print(str(e))
    sys.exit(1)


def is_valid_mo(path: Path) -> bool:
    """Quick validation for a .mo file based on size and magic number."""
    try:
        size = path.stat().st_size
        if size < 32:
            return False
        with open(path, 'rb') as f:
            data = f.read(8)
            if len(data) < 8:
                return False
            # Read first 4 bytes as unsigned int (little-endian)
            magic = struct.unpack('<I', data[0:4])[0]
            # Accept both common endianness values
            # Standard magic: 0x950412de
            # Alternate: 0xDE120495
            if magic in (0x950412de, 0xDE120495):
                return True
            return False
    except Exception:
        return False


def ensure_po_utf8(po_path: Path) -> bool:
    """Ensure .po is UTF-8. If not, try reading as latin-1 and re-save as UTF-8.
    Returns True if file is valid UTF-8 after this function.
    """
    try:
        with open(po_path, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except UnicodeDecodeError:
        # Attempt to recover by reading latin-1 and rewriting as utf-8
        try:
            with open(po_path, 'r', encoding='latin-1') as f:
                data = f.read()
            backup = po_path.with_suffix('.po.bak')
            shutil.copy2(po_path, backup)
            with open(po_path, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"⚠ Converted {po_path} from latin-1 → UTF-8 (backup: {backup.name})")
            return True
        except Exception as e:
            print(f"✗ Failed to re-encode {po_path}: {e}")
            return False
    except Exception as e:
        print(f"✗ Error reading {po_path}: {e}")
        return False


def main():
    locale_paths = list(getattr(settings, 'LOCALE_PATHS', []))
    # Also check project root locale
    project_locale = Path(settings.BASE_DIR) / 'locale'
    if project_locale.exists() and str(project_locale) not in locale_paths:
        locale_paths.insert(0, str(project_locale))

    languages = [code for code, name in getattr(settings, 'LANGUAGES', [])]
    print("i18n validation using settings:")
    print("  LOCALE_PATHS:")
    for p in locale_paths:
        print(f"    - {p}")
    print("  LANGUAGES:")
    print(f"    - {languages}")

    removed_mo = []
    fixed_pos = []
    missing_lang_dirs = []

    for lp in locale_paths:
        base = Path(lp)
        if not base.exists():
            continue
        for lang in languages:
            lang_dir = base / lang / 'LC_MESSAGES'
            if not lang_dir.exists():
                missing_lang_dirs.append(str(lang_dir))
                continue
            po_path = lang_dir / 'django.po'
            mo_path = lang_dir / 'django.mo'
            if po_path.exists():
                ok = ensure_po_utf8(po_path)
                if ok:
                    fixed_pos.append(str(po_path))
            else:
                print(f"✗ Missing .po file: {po_path}")
            if mo_path.exists():
                if not is_valid_mo(mo_path):
                    try:
                        mo_backup = mo_path.with_suffix('.mo.bak')
                        shutil.move(str(mo_path), str(mo_backup))
                        removed_mo.append(str(mo_path))
                        print(f"⚠ Removed invalid .mo file (backed up): {mo_backup}")
                    except Exception as e:
                        print(f"✗ Failed to remove corrupted {mo_path}: {e}")
                else:
                    print(f"✓ Valid .mo: {mo_path}")
            else:
                print(f"- .mo not present (will be generated): {mo_path}")

    print("\nSummary:")
    print(f"  Removed/backspped .mo files: {len(removed_mo)}")
    print(f"  Verified/converted .po files: {len(fixed_pos)}")
    if missing_lang_dirs:
        print("  Missing language directories:")
        for m in missing_lang_dirs:
            print(f"    - {m}")

    if removed_mo:
        print("\nNext: run Django's compilemessages to regenerate .mo files using system gettext:")
        print("  python manage.py compilemessages")
        print("If that fails with msgfmt/missing gettext, install GNU gettext (see README instructions).")
    else:
        print("\nNo invalid .mo files found. If you still see crashes, try running compilemessages anyway to refresh .mo files.")

if __name__ == '__main__':
    main()

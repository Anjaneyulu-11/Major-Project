#!/usr/bin/env python
"""
Corrected pure-Python .po -> .mo compiler.
Uses the exact gettext .mo binary format spec.

Reference: https://www.gnu.org/software/gettext/manual/gettext.html#MO-Files
"""

import os
import sys
import struct
from pathlib import Path
from collections import OrderedDict

# Bootstrap Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')
try:
    import django
    django.setup()
    from django.conf import settings
except Exception as e:
    print("✗ Could not import Django settings.")
    print(str(e))
    sys.exit(1)


class POParser:
    """Parse .po files into a dictionary of translations."""
    
    def __init__(self, po_path):
        self.po_path = po_path
        self.messages = OrderedDict()
    
    def parse(self):
        """Parse .po file and extract msgid/msgstr pairs."""
        with open(self.po_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        msgid = None
        msgstr = None
        
        for line in lines:
            line = line.rstrip('\n')
            
            # Skip comments and blank lines
            if not line or line.startswith('#'):
                continue
            
            # Parse msgid
            if line.startswith('msgid '):
                if msgid is not None and msgstr is not None and msgid != '':
                    self.messages[msgid] = msgstr
                
                msgid = self._extract_string(line)
                msgstr = None
            
            # Parse msgstr
            elif line.startswith('msgstr '):
                msgstr = self._extract_string(line)
            
            # Handle multi-line strings
            elif line.startswith('"') and msgid is not None:
                if msgstr is not None:
                    msgstr += self._extract_string(line)
                else:
                    msgid += self._extract_string(line)
        
        # Don't forget last pair
        if msgid is not None and msgstr is not None and msgid != '':
            self.messages[msgid] = msgstr
        
        return self.messages
    
    def _extract_string(self, line):
        """Extract quoted string from msgid/msgstr line."""
        start = line.find('"') + 1
        end = line.rfind('"')
        if start > 0 and end > start:
            return line[start:end]
        return ''


class MOWriter:
    """Write translations to .mo (Machine Object) format using gettext spec."""
    
    def __init__(self, messages):
        self.messages = messages
    
    def generate(self):
        """
        Generate .mo file binary content.
        
        Format:
        - Header (28 bytes)
        - Master (msgid) offset table (8 bytes per entry)
        - Translation (msgstr) offset table (8 bytes per entry)
        - Keys (msgid strings)
        - Values (msgstr strings)
        """
        
        # Empty set: just header
        if not self.messages:
            return self._make_header(0, 28, 28)
        
        # Sort messages by key for deterministic output
        keys = sorted(self.messages.keys())
        
        # Collect key-value pairs as bytes
        ids_data = []    # List of (key_bytes, value_bytes)
        for key in keys:
            key_bytes = key.encode('utf-8')
            val_bytes = self.messages[key].encode('utf-8')
            ids_data.append((key_bytes, val_bytes))
        
        num_entries = len(ids_data)
        
        # Calculate file layout
        # Header: 28 bytes + 0x1c alignment
        header_offset = 0
        
        # Master offset table: starts at byte 28
        master_offset_start = 28
        master_offset_size = num_entries * 8
        
        # Translation offset table: after master table
        trans_offset_start = master_offset_start + master_offset_size
        trans_offset_size = num_entries * 8
        
        # Keys and values start after both offset tables
        data_start = trans_offset_start + trans_offset_size
        
        # Build master and translation offset tables
        master_offsets = []
        trans_offsets = []
        
        keys_pos = data_start
        vals_pos = data_start + sum(len(k[0]) + 1 for k in ids_data)
        
        for key_bytes, val_bytes in ids_data:
            key_len = len(key_bytes)
            val_len = len(val_bytes)
            
            master_offsets.append((key_len, keys_pos))
            trans_offsets.append((val_len, vals_pos))
            
            keys_pos += key_len + 1  # +1 for null terminator
            vals_pos += val_len + 1
        
        # Build the file
        output = self._make_header(num_entries, master_offset_start, trans_offset_start)
        
        # Write master offset table
        for key_len, key_pos in master_offsets:
            output += struct.pack('<ii', key_len, key_pos)
        
        # Write translation offset table
        for val_len, val_pos in trans_offsets:
            output += struct.pack('<ii', val_len, val_pos)
        
        # Write keys
        for key_bytes, _ in ids_data:
            output += key_bytes + b'\x00'
        
        # Write values
        for _, val_bytes in ids_data:
            output += val_bytes + b'\x00'
        
        return output
    
    def _make_header(self, num_entries, master_offset, trans_offset):
        """Create .mo file header (28 bytes)."""
        return struct.pack(
            '<I I I I I I I',
            0xDE120495,      # Magic (little-endian)
            0,               # Version
            num_entries,     # Number of entries
            master_offset,   # Offset of master offset table
            trans_offset,    # Offset of translation offset table
            0,               # Hash table size (0 = unused)
            0                # Hash table offset (0 = unused)
        )


def compile_po_to_mo(po_path, mo_path):
    """Parse .po and write .mo."""
    try:
        parser = POParser(po_path)
        messages = parser.parse()
        
        writer = MOWriter(messages)
        mo_content = writer.generate()
        
        with open(mo_path, 'wb') as f:
            f.write(mo_content)
        
        return True, len(messages)
    except Exception as e:
        return False, str(e)


def main():
    locale_paths = list(getattr(settings, 'LOCALE_PATHS', []))
    project_locale = Path(settings.BASE_DIR) / 'locale'
    if project_locale.exists() and str(project_locale) not in locale_paths:
        locale_paths.insert(0, str(project_locale))
    
    languages = [code for code, name in getattr(settings, 'LANGUAGES', [])]
    
    print("Compiling .po → .mo (FIXED format)")
    print("-" * 60)
    
    compiled_count = 0
    failed_count = 0
    
    for lp in locale_paths:
        base = Path(lp)
        if not base.exists():
            continue
        
        for lang in languages:
            po_path = base / lang / 'LC_MESSAGES' / 'django.po'
            mo_path = base / lang / 'LC_MESSAGES' / 'django.mo'
            
            if po_path.exists():
                success, result = compile_po_to_mo(po_path, mo_path)
                if success:
                    print(f"✓ {lang}: compiled {result} messages → {mo_path.name}")
                    compiled_count += 1
                else:
                    print(f"✗ {lang}: {result}")
                    failed_count += 1
            else:
                print(f"- {lang}: .po file not found (skipped)")
    
    print("-" * 60)
    print(f"Summary: {compiled_count} compiled, {failed_count} failed")
    
    if failed_count == 0:
        print("\n✅ All .mo files compiled (fixed format)!")
        print("Testing with gettext in 5 seconds...")
        import time
        time.sleep(5)  # Give user a moment
        
        # Quick verification
        import gettext
        test_lang = [lang for lang in languages if lang != 'en'][0] if len(languages) > 1 else 'en'
        mo_path = project_locale / test_lang / 'LC_MESSAGES' / 'django.mo'
        try:
            trans = gettext.GNUTranslations(open(mo_path, 'rb'))
            print(f"✓ gettext can load {test_lang} translations!")
        except Exception as e:
            print(f"✗ gettext still fails for {test_lang}: {e}")
    
    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

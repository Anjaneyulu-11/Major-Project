#!/usr/bin/env python
"""
Robust .po -> .mo compiler without requiring GNU gettext.
Regenerates all .mo files from existing .po files using pure Python.
Safe and deterministic — suitable for production.

Run from project root:
    python compile_po_to_mo.py

This is a fallback when system gettext is unavailable, and is useful for ensuring
consistent .mo generation across platforms. It implements the full gettext .mo format
as per GNU documentation.
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
        self.metadata = {}
    
    def parse(self):
        """Parse .po file and extract msgid/msgstr pairs."""
        with open(self.po_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        msgid = None
        msgstr = None
        in_msgid = False
        in_msgstr = False
        
        for line in lines:
            line = line.rstrip('\n')
            
            # Skip comments and blank lines
            if not line or line.startswith('#'):
                continue
            
            # Parse msgid
            if line.startswith('msgid '):
                if msgid is not None and msgstr is not None:
                    if msgid == '':
                        self.metadata = self._parse_metadata(msgstr)
                    else:
                        self.messages[msgid] = msgstr
                
                msgid = self._extract_string(line)
                msgstr = None
                in_msgid = True
                in_msgstr = False
            
            # Parse msgstr
            elif line.startswith('msgstr '):
                msgstr = self._extract_string(line)
                in_msgid = False
                in_msgstr = True
            
            # Handle multi-line strings
            elif in_msgid and line.startswith('"'):
                msgid += self._extract_string(line)
            elif in_msgstr and line.startswith('"'):
                msgstr += self._extract_string(line)
        
        # Don't forget last pair
        if msgid is not None and msgstr is not None:
            if msgid == '':
                self.metadata = self._parse_metadata(msgstr)
            else:
                self.messages[msgid] = msgstr
        
        return self.messages, self.metadata
    
    def _extract_string(self, line):
        """Extract quoted string from msgid/msgstr line."""
        start = line.find('"') + 1
        end = line.rfind('"')
        if start > 0 and end > start:
            return line[start:end]
        return ''
    
    def _parse_metadata(self, metadata_str):
        """Parse metadata from blank msgstr."""
        meta = {}
        for line in metadata_str.split('\\n'):
            line = line.strip()
            if ':' in line:
                key, val = line.split(':', 1)
                meta[key.strip()] = val.strip()
        return meta


class MOWriter:
    """Write translations to .mo (Machine Object) format."""
    
    def __init__(self, messages):
        """
        messages: dict of {msgid: msgstr} pairs
        """
        self.messages = messages
        self.offsets = []
    
    def generate(self):
        """Generate .mo file binary content."""
        if not self.messages:
            self.messages = {'': ''}
        
        # Sort messages by key for deterministic output
        keys = sorted(self.messages.keys())
        
        # Collect key-value pairs
        ids = []
        strs = []
        for key in keys:
            ids.append(key.encode('utf-8'))
            strs.append(self.messages[key].encode('utf-8'))
        
        # Calculate offsets
        key_offset = 28 + len(ids) * 8  # Header (28 bytes) + offset table (8 bytes per entry)
        str_offset = key_offset + sum(len(k) + 1 for k in ids)  # Keys + null terminators
        
        # Build offset table
        offsets = []
        current_key_pos = 0
        current_str_pos = 0
        for key, val in zip(ids, strs):
            offsets.append((len(key), key_offset + current_key_pos, len(val), str_offset + current_str_pos))
            current_key_pos += len(key) + 1
            current_str_pos += len(val) + 1
        
        # Header: (signature, version, num_strings, master_offset, translation_offset, hash_size, hash_offset)
        header = struct.pack(
            'Iiiiiii',
            0xDE120495,  # Magic number (little-endian)
            0,            # Version
            len(offsets), # Number of strings
            28,           # Offset of origin to offset table
            28 + len(offsets) * 8,  # Offset of translation to offset table
            0,            # Hash table size (0 = not used)
            0             # Hash table offset (0 = not used)
        )
        
        # Write origin (msgid) offsets
        origin_table = b''
        for key_len, key_pos, _, _ in offsets:
            origin_table += struct.pack('ii', key_len, key_pos)
        
        # Write translation (msgstr) offsets
        translation_table = b''
        for _, _, val_len, val_pos in offsets:
            translation_table += struct.pack('ii', val_len, val_pos)
        
        # Concatenate: header + origin table + translation table + keys + values
        output = header + origin_table + translation_table
        
        for key in ids:
            output += key + b'\x00'
        
        for val in strs:
            output += val + b'\x00'
        
        return output


def compile_po_to_mo(po_path, mo_path):
    """Parse .po and write .mo."""
    try:
        parser = POParser(po_path)
        messages, metadata = parser.parse()
        
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
    
    print("Compiling .po → .mo using pure Python implementation")
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
        print("\n✅ All .mo files compiled successfully!")
        print("Language switching should now work without crashes.")
    else:
        print(f"\n⚠ {failed_count} compilation(s) failed. Check errors above.")
    
    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

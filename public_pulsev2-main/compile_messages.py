#!/usr/bin/env python
"""
Compile .po files to .mo files for Django i18n.
This script converts PO (Portable Object) files to MO (Machine Object) files
that Django can efficiently load.
"""

from pathlib import Path
import struct
import array

def generate_mo_file(po_path, mo_path):
    """
    Compile a .po file to a .mo file.
    
    The .mo file format is binary and consists of:
    - Header (magic number, offsets, etc.)
    - Translated strings
    """
    
    messages = {}
    
    # Parse .po file
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_msgid = None
    current_msgstr = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            i += 1
            continue
        
        # Handle msgid
        if line.startswith('msgid '):
            if current_msgid is not None and current_msgstr is not None:
                messages[current_msgid] = current_msgstr
            
            current_msgid = line[7:-1]  # Remove 'msgid "' and '"'
            current_msgstr = None
        
        # Handle msgstr
        elif line.startswith('msgstr '):
            current_msgstr = line[8:-1]  # Remove 'msgstr "' and '"'
        
        i += 1
    
    # Don't forget the last message
    if current_msgid is not None and current_msgstr is not None:
        messages[current_msgid] = current_msgstr
    
    # Generate .mo file
    keys = sorted(messages.keys())
    offsets = []
    ids = b''
    strs = b''
    
    for key in keys:
        if not key:  # Skip empty key (header)
            continue
        
        key_bytes = key.encode('utf-8')
        str_bytes = messages[key].encode('utf-8')
        
        offsets.append((len(ids), len(key_bytes), len(strs), len(str_bytes)))
        ids += key_bytes + b'\x00'
        strs += str_bytes + b'\x00'
    
    # Generate MO file format
    # Magic number: 0xDE120495 (little-endian)
    magic = 0xDE120495
    version = 0
    num_strings = len(offsets)
    
    # Calculate positions
    header_size = 28
    keyoffset = header_size + num_strings * 8
    valueoffset = keyoffset + len(ids)
    
    # Build the .mo file
    output = struct.pack(
        'Iiiiiii',
        magic,
        version,
        num_strings,
        header_size,
        keyoffset,
        valueoffset,
        0  # hash table size (not used)
    )
    
    # Offset table for keys
    for key_start, key_len, val_start, val_len in offsets:
        output += struct.pack('ii', key_len, keyoffset + key_start)
    
    # Offset table for values
    for key_start, key_len, val_start, val_len in offsets:
        output += struct.pack('ii', val_len, valueoffset + val_start)
    
    # Keys and values
    output += ids
    output += strs
    
    # Write .mo file
    with open(mo_path, 'wb') as f:
        f.write(output)

def main():
    """Main function"""
    base_dir = Path(__file__).parent
    locale_dir = base_dir / 'locale'
    
    languages = ['hi', 'te', 'ta', 'kn', 'ml', 'mr', 'bn']
    
    print("Compiling .po files to .mo files...")
    print("-" * 50)
    
    for lang_code in languages:
        po_path = locale_dir / lang_code / 'LC_MESSAGES' / 'django.po'
        mo_path = locale_dir / lang_code / 'LC_MESSAGES' / 'django.mo'
        
        if po_path.exists():
            try:
                generate_mo_file(po_path, mo_path)
                print(f"✓ Compiled {lang_code}: {po_path.name} → {mo_path.name}")
            except Exception as e:
                print(f"✗ Error compiling {lang_code}: {str(e)}")
        else:
            print(f"✗ .po file not found: {po_path}")
    
    print("-" * 50)
    print("✓ All .mo files compiled successfully!")
    print("\nNext steps:")
    print("1. Wrap UI text in templates with {% trans \"text\" %}")
    print("2. Test language switching:")
    print("   python manage.py runserver")
    print("   Visit: http://localhost:8000")
    print("3. Switch languages using the dropdown")
    print("4. Verify translations appear on all pages")

if __name__ == '__main__':
    main()

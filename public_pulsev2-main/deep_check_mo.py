#!/usr/bin/env python
"""
Deep validation of .mo files to find the exact problem.
"""

import struct
from pathlib import Path

def deep_check_mo(mo_path: Path):
    """Very detailed .mo file validation."""
    print(f"\nValidating: {mo_path.name}")
    print(f"  Size: {mo_path.stat().st_size} bytes")
    
    try:
        with open(mo_path, 'rb') as f:
            data = f.read()
        
        # Check minimum size
        if len(data) < 28:
            print(f"  ✗ TOO SMALL (< 28 bytes for header)")
            return False
        
        # Try to unpack header
        try:
            magic, version, num_strings, master_offset, trans_offset, hash_size, hash_offset = struct.unpack(
                'Iiiiiii', data[:28]
            )
            print(f"  Magic: 0x{magic:08x}")
            print(f"  Version: {version}")
            print(f"  Num strings: {num_strings}")
            print(f"  Master offset: {master_offset}")
            print(f"  Trans offset: {trans_offset}")
            
            # Validate magic
            if magic not in (0xDE120495, 0x950412de):
                print(f"  ✗ INVALID MAGIC")
                return False
            
            # Check if offsets are within file bounds
            if master_offset + num_strings * 8 > len(data):
                print(f"  ✗ Master offset table out of bounds")
                return False
            
            if trans_offset + num_strings * 8 > len(data):
                print(f"  ✗ Translation offset table out of bounds")
                return False
            
            print(f"  ✓ Header valid")
            return True
        
        except struct.error as e:
            print(f"  ✗ Failed to unpack header: {e}")
            return False
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    locale_base = Path('locale')
    if not locale_base.exists():
        print("✗ locale/ directory not found")
        return
    
    languages = ['en', 'hi', 'te', 'ta', 'kn', 'ml', 'mr', 'bn']
    print("Deep scanning .mo files for errors")
    print("=" * 60)
    
    all_valid = True
    for lang in languages:
        mo_path = locale_base / lang / 'LC_MESSAGES' / 'django.mo'
        if mo_path.exists():
            valid = deep_check_mo(mo_path)
            if not valid:
                all_valid = False
        else:
            print(f"\n{lang}: .mo not found")
    
    print("\n" + "=" * 60)
    if all_valid:
        print("✅ All .mo files appear valid")
    else:
        print("✗ Some .mo files have issues")

if __name__ == '__main__':
    main()

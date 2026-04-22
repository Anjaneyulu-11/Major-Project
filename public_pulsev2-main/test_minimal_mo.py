#!/usr/bin/env python
"""
Create a minimalist test .mo file and verify gettext can read it.
This helps us understand the exact requirements of the format.
"""

import struct
import gettext
from pathlib import Path

def create_minimal_mo():
    """Create a minimal .mo file with just the header and one string."""
    
    # One translation: Hello → Hola
    key = b'Hello'
    val = b'Hola'
    
    # Calculate the layout:
    # - Header: 0-27 (28 bytes)
    # - Master table: 28-35 (1 entry = 8 bytes) 
    # - Trans table: 36-43 (1 entry = 8 bytes)
    # - Keys data: 44-48 (5 bytes key + 1 null)
    # - Values data: 49-52 (4 bytes val + 1 null)
    
    header_size = 28
    num_entries = 1
    master_offset = 28
    trans_offset = 36
    
    # Key position and length
    key_len = len(key)
    key_pos = 44
    
    # Value position and length
    val_len = len(val)
    val_pos = 49
    
    # Build the file carefully
    data = struct.pack(
        '<7I',
        0xDE120495,      # Magic (little-endian signed)
        0,               # Version
        num_entries,     # Number of entries
        master_offset,   # Offset of master table
        trans_offset,    # Offset of trans table
        0,               # Hash table size
        0                # Hash table offset
    )
    
    # Master table: (key_len, key_pos)
    data += struct.pack('<2i', key_len, key_pos)
    
    # Trans table: (val_len, val_pos)
    data += struct.pack('<2i', val_len, val_pos)
    
    # Keys data
    data += key + b'\x00'
    
    # Values data
    data += val + b'\x00'
    
    return data

def test_minimal():
    """Test if gettext can read our minimal .mo."""
    print("Creating minimal test .mo file...")
    mo_data = create_minimal_mo()
    
    test_path = Path('test_minimal.mo')
    with open(test_path, 'wb') as f:
        f.write(mo_data)
    
    print(f"Created {test_path} ({len(mo_data)} bytes)")
    print("\nTrying to load with gettext...")
    
    try:
        with open(test_path, 'rb') as f:
            trans = gettext.GNUTranslations(f)
        print(f"✓ gettext loaded successfully!")
        print(f"  Translation: 'Hello' → '{trans.gettext('Hello')}'")
        return True
    except Exception as e:
        print(f"✗ gettext failed: {type(e).__name__}: {e}")
        
        # Debug: print raw file contents
        print(f"\nFile hex dump (first 100 bytes):")
        hex_str = mo_data[:100].hex()
        for i in range(0, len(hex_str), 32):
            print(f"  {hex_str[i:i+32]}")
        
        return False
    finally:
        test_path.unlink(missing_ok=True)

if __name__ == '__main__':
    success = test_minimal()
    if success:
        print("\n✅ Minimal .mo format works!")
    else:
        print("\n✗ Minimal test failed - need to diagnose format")

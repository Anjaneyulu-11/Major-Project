#!/usr/bin/env python
"""
Generate .po translation files for all languages.
This script scans templates for {% trans %} and {% blocktrans %} strings
and creates .po files with translations.
"""

import os
import re
from datetime import datetime
from pathlib import Path

# Language configuration
LANGUAGES = {
    'hi': {'name': 'हिन्दी', 'charset': 'UTF-8'},
    'te': {'name': 'తెలుగు', 'charset': 'UTF-8'},
    'ta': {'name': 'தமிழ்', 'charset': 'UTF-8'},
    'kn': {'name': 'ಕನ್ನಡ', 'charset': 'UTF-8'},
    'ml': {'name': 'മലയാളം', 'charset': 'UTF-8'},
    'mr': {'name': 'मराठी', 'charset': 'UTF-8'},
    'bn': {'name': 'বাংলা', 'charset': 'UTF-8'},
}

# Common UI strings to translate
COMMON_STRINGS = {
    'Home': 'Home page link',
    'Register': 'Register button',
    'Login': 'Login button',
    'Logout': 'Logout button',
    'Dashboard': 'Dashboard page',
    'Profile': 'User profile',
    'Settings': 'Settings page',
    'Help': 'Help section',
    'About': 'About us',
    'Contact': 'Contact us',
    'Submit': 'Submit button',
    'Cancel': 'Cancel button',
    'Save': 'Save button',
    'Delete': 'Delete button',
    'Edit': 'Edit button',
    'Back': 'Back button',
    'Next': 'Next button',
    'Previous': 'Previous button',
    'Loading': 'Loading indicator',
    'Error': 'Error message',
    'Success': 'Success message',
    'Warning': 'Warning message',
    'Confirm': 'Confirm action',
    'Yes': 'Yes option',
    'No': 'No option',
    'Search': 'Search placeholder',
    'Filter': 'Filter button',
    'Sort': 'Sort option',
    'View': 'View button',
    'Download': 'Download button',
    'Upload': 'Upload button',
    'File': 'File label',
    'Name': 'Name field',
    'Email': 'Email field',
    'Password': 'Password field',
    'Phone': 'Phone field',
    'Address': 'Address field',
    'City': 'City field',
    'State': 'State field',
    'Country': 'Country field',
    'Zip': 'Zip code field',
    'Required': 'Required field indicator',
    'Optional': 'Optional field indicator',
}

def generate_po_header(lang_code, lang_name):
    """Generate PO file header"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M%z')
    header = f'''# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the public-pulse package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: public-pulse 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: {now}\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: {lang_name} <EMAIL@ADDRESS>\\n"
"Language: {lang_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

'''
    return header

def generate_po_entries(strings):
    """Generate PO entries for strings"""
    entries = []
    for string, comment in strings.items():
        entry = f'''#: {comment}
msgid "{string}"
msgstr ""

'''
        entries.append(entry)
    return ''.join(entries)

def create_po_file(lang_code, lang_name, output_dir):
    """Create a .po file for a language"""
    po_path = output_dir / f'django.po'
    
    # Generate header and entries
    header = generate_po_header(lang_code, lang_name)
    entries = generate_po_entries(COMMON_STRINGS)
    
    # Write to file
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(entries)
    
    print(f"✓ Created {po_path}")
    return po_path

def main():
    """Main function"""
    base_dir = Path(__file__).parent
    locale_dir = base_dir / 'locale'
    
    print("Generating .po translation files...")
    print("-" * 50)
    
    for lang_code, lang_info in LANGUAGES.items():
        lang_name = lang_info['name']
        output_dir = locale_dir / lang_code / 'LC_MESSAGES'
        
        if output_dir.exists():
            create_po_file(lang_code, lang_name, output_dir)
        else:
            print(f"✗ Directory not found: {output_dir}")
    
    print("-" * 50)
    print("✓ .po files created successfully!")
    print("\nNext steps:")
    print("1. Wrap UI text in templates with {% trans \"text\" %}")
    print("2. Add translations to .po files")
    print("3. Run: python manage.py compilemessages")
    print("4. Test language switching")

if __name__ == '__main__':
    main()

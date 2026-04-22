#!/usr/bin/env python
"""
Add sample translations to .po files for all languages.
Provides a starting point for real translations.
"""

import os
from pathlib import Path

# Translations for key UI strings
TRANSLATIONS = {
    'hi': {  # Hindi
        'Home': 'मुख्य पृष्ठ',
        'Register': 'पंजीकरण करें',
        'Login': 'लॉगिन',
        'Logout': 'लॉगआउट',
        'Dashboard': 'डैशबोर्ड',
        'Profile': 'प्रोफ़ाइल',
        'Settings': 'सेटिंग्स',
        'Help': 'मदद',
        'About': 'हमारे बारे में',
        'Contact': 'संपर्क करें',
        'Submit': 'सबमिट करें',
        'Cancel': 'रद्द करें',
        'Save': 'सहेजें',
        'Delete': 'हटाएं',
        'Edit': 'संपादित करें',
        'Back': 'वापस',
        'Next': 'आगे',
        'Previous': 'पिछला',
        'Loading': 'लोड हो रहा है',
        'Error': 'त्रुटि',
        'Success': 'सफल',
        'Warning': 'चेतावनी',
        'View': 'देखें',
        'Download': 'डाउनलोड',
        'Upload': 'अपलोड',
        'Search': 'खोज',
        'Filter': 'फ़िल्टर',
        'Email': 'ईमेल',
        'Password': 'पासवर्ड',
        'Phone': 'फोन',
        'Name': 'नाम',
    },
    'te': {  # Telugu
        'Home': 'హోమ్',
        'Register': 'నమోదు చేయండి',
        'Login': 'లాగిన్',
        'Logout': 'లాగআউట్',
        'Dashboard': 'డ్యాషబోర్డ్',
        'Profile': 'ప్రొఫైల్',
        'Settings': 'సెట్టింగ్‌లు',
        'Help': 'సహాయం',
        'About': 'గురించి',
        'Contact': 'సంప్రదించండి',
        'Submit': 'సమర్పించండి',
        'Cancel': 'రద్దు చేయండి',
        'Save': 'సేవ్ చేయండి',
        'Delete': 'తొలగించండి',
        'Edit': 'సవరించండి',
        'Back': 'వెనుకకు',
        'Next': 'తర్వాత',
        'Previous': 'మునుపటి',
        'Loading': 'లోడ్ చేస్తున్నాం',
        'Error': 'ఎర్రర్',
        'Success': 'విజయం',
        'Warning': 'హెచ్చరిక',
        'View': 'వీక్షించండి',
        'Download': 'డౌన్‌లోడ్',
        'Upload': 'అపలోడ్',
        'Search': 'శోధించండి',
        'Filter': 'ఫిల్టర్',
        'Email': 'ఇమెయిల్',
        'Password': 'పాస్‌వర్డ్',
        'Phone': 'ఫోన్',
        'Name': 'పేరు',
    },
    'ta': {  # Tamil
        'Home': 'முகப்பு',
        'Register': 'பதிவுசெய்க',
        'Login': 'உள்நுழைக',
        'Logout': 'வெளியேறுக',
        'Dashboard': 'பDashboard',
        'Profile': 'சுயவிவரம்',
        'Settings': 'அமைப்புகள்',
        'Help': 'உதவி',
        'About': 'பற்றி',
        'Contact': 'தொடர்பு கொள்ளுக',
        'Submit': 'சமர்ப்பிக்க',
        'Cancel': 'ரத்து செய்க',
        'Save': 'சேமிக்க',
        'Delete': 'அழிக்க',
        'Edit': 'திருத்துக',
        'Back': 'பின்னுக்குப்',
        'Next': 'அடுத்து',
        'Previous': 'முந்தைய',
        'Loading': 'ஏற்றுகிறது',
        'Error': 'பிழை',
        'Success': 'வெற்றி',
        'Warning': 'எச்சரிக்கை',
        'View': 'பார்க்க',
        'Download': 'பதிவிறக்க',
        'Upload': 'பதிவேற்ற',
        'Search': 'தேடுக',
        'Filter': 'வடிப்பி',
        'Email': 'மின்னஞ்சல்',
        'Password': 'கடவுச்சொல்',
        'Phone': 'தொலைபேசி',
        'Name': 'பெயர்',
    },
    'kn': {  # Kannada
        'Home': 'ಮುಖ್ಯ ಪುಟ',
        'Register': 'ನೊಂದಾಯಿಸಲು',
        'Login': 'ಲಾಗಿನ್',
        'Logout': 'ಲಾಗ್ ಔಟ್',
        'Dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
        'Profile': 'ಪ್ರೊಫೈಲ್',
        'Settings': 'ಸೆಟ್ಟಿಂಗ್‌ಗಳು',
        'Help': 'ಸಹಾಯ',
        'About': 'ಬಗ್ಗೆ',
        'Contact': 'ಸಂಪರ್ಕಿಸಿ',
        'Submit': 'ಸಲ್ಲಿಸಿ',
        'Cancel': 'ರದ್ದುಮಾಡಿ',
        'Save': 'ಉಳಿಸಿ',
        'Delete': 'ಅಳಿಸಿ',
        'Edit': 'ಸಂಪಾದಿಸಿ',
        'Back': 'ಹಿಂದೆ',
        'Next': 'ಮುಂದೆ',
        'Previous': 'ಹಿಂದಿನ',
        'Loading': 'ಲೋಡ್ ಆಗುತ್ತಿದೆ',
        'Error': 'ತ್ರುಟಿ',
        'Success': 'ಯಶಸ್ವಿ',
        'Warning': 'ಎಚ್ಚರಿಕೆ',
        'View': 'ವೀಕ್ಷಿಸಿ',
        'Download': 'ಡೌನ್‌ಲೋಡ್',
        'Upload': 'ಅಪ್‌ಲೋಡ್',
        'Search': 'ಹುಡುಕಿ',
        'Filter': 'ಫಿಲ್ಟರ್',
        'Email': 'ಇ-ಮೇಲ್',
        'Password': 'ಪಾಸ್‌ವರ್ಡ್',
        'Phone': 'ಫೋನ್',
        'Name': 'ಹೆಸರು',
    },
    'ml': {  # Malayalam
        'Home': 'ഹോം',
        'Register': 'രജിസ്റ്റർ ചെയ്യുക',
        'Login': 'പ്രവേശിക്കുക',
        'Logout': 'പ്രവേശനം അവസാനിപ്പിക്കുക',
        'Dashboard': 'ഡാഷ്‌ബോധ്',
        'Profile': 'പ്രൊഫൈൽ',
        'Settings': 'ക്രമീകരണങ്ങൾ',
        'Help': 'സഹായം',
        'About': 'കുറിച്ച്',
        'Contact': 'ബന്ധപ്പെടുക',
        'Submit': 'സമർപ്പിക്കുക',
        'Cancel': 'റദ്ദാക്കുക',
        'Save': 'സംരക്ഷിക്കുക',
        'Delete': 'ഇല്ലാതാക്കുക',
        'Edit': 'തിരുത്തുക',
        'Back': 'തിരികെ',
        'Next': 'അടുത്ത',
        'Previous': 'മുമ്പത്തെ',
        'Loading': 'ലോഡ് ചെയ്യുന്നു',
        'Error': 'പിശക്',
        'Success': 'വിജയം',
        'Warning': 'മുന്നറിപ്പ്',
        'View': 'കാണുക',
        'Download': 'ഡൗൺലോഡ്',
        'Upload': 'അപ്‌ലോഡ്',
        'Search': 'തിരയുക',
        'Filter': 'ഫിൽറ്റർ',
        'Email': 'ഇമെയിൽ',
        'Password': 'പാസ്‌വേഡ്',
        'Phone': 'ഫോൺ',
        'Name': 'പേര്',
    },
    'mr': {  # Marathi
        'Home': 'मुख्यपृष्ठ',
        'Register': 'नोंदणी करा',
        'Login': 'लॉगिन करा',
        'Logout': 'लॉगआउट करा',
        'Dashboard': 'डॅशबोर्ड',
        'Profile': 'प्रोफाईल',
        'Settings': 'सेटिंग्ज',
        'Help': 'मदत',
        'About': 'बद्दल',
        'Contact': 'संपर्क करा',
        'Submit': 'सादर करा',
        'Cancel': 'रद्द करा',
        'Save': 'जतन करा',
        'Delete': 'हटवा',
        'Edit': 'संपादित करा',
        'Back': 'मागे',
        'Next': 'पुढे',
        'Previous': 'मागील',
        'Loading': 'लोड होत आहे',
        'Error': 'त्रुटी',
        'Success': 'यशस्वी',
        'Warning': 'चेतावणी',
        'View': 'पहा',
        'Download': 'डाउनलोड करा',
        'Upload': 'अपलोड करा',
        'Search': 'शोध करा',
        'Filter': 'फिल्टर करा',
        'Email': 'ईमेल',
        'Password': 'पासवर्ड',
        'Phone': 'फोन',
        'Name': 'नाव',
    },
    'bn': {  # Bengali
        'Home': 'হোম',
        'Register': 'নিবন্ধন করুন',
        'Login': 'লগইন',
        'Logout': 'লগআউট',
        'Dashboard': 'ড্যাশবোর্ড',
        'Profile': 'প্রোফাইল',
        'Settings': 'সেটিংস',
        'Help': 'সাহায্য',
        'About': 'সম্পর্কে',
        'Contact': 'যোগাযোগ করুন',
        'Submit': 'জমা দিন',
        'Cancel': 'বাতিল করুন',
        'Save': 'সংরক্ষণ করুন',
        'Delete': 'মুছুন',
        'Edit': 'সম্পাদনা করুন',
        'Back': 'ফিরে যান',
        'Next': 'পরবর্তী',
        'Previous': 'পূর্ববর্তী',
        'Loading': 'লোড হচ্ছে',
        'Error': 'ত্রুটি',
        'Success': 'সফল',
        'Warning': 'সতর্কতা',
        'View': 'দেখুন',
        'Download': 'ডাউনলোড করুন',
        'Upload': 'আপলোড করুন',
        'Search': 'অনুসন্ধান করুন',
        'Filter': 'ফিল্টার করুন',
        'Email': 'ইমেল',
        'Password': 'পাসওয়ার্ড',
        'Phone': 'ফোন',
        'Name': 'নাম',
    },
}

def update_po_with_translations(po_path, lang_code):
    """Read a .po file, add translations, and write back"""
    translations = TRANSLATIONS.get(lang_code, {})
    
    if not translations:
        print(f"✗ No translations found for {lang_code}")
        return
    
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add translations after the header
    new_content = content
    for english, translated in translations.items():
        # Check if this string is already in the file
        search_pattern = f'msgid "{english}"'
        if search_pattern in new_content:
            # Replace the empty msgstr with the translation
            old_entry = f'msgid "{english}"\nmsgstr ""'
            new_entry = f'msgid "{english}"\nmsgstr "{translated}"'
            new_content = new_content.replace(old_entry, new_entry)
    
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Added translations for {lang_code}: {len(translations)} strings")

def main():
    """Main function"""
    base_dir = Path(__file__).parent
    locale_dir = base_dir / 'locale'
    
    print("Adding sample translations to .po files...")
    print("-" * 50)
    
    for lang_code in TRANSLATIONS.keys():
        po_path = locale_dir / lang_code / 'LC_MESSAGES' / 'django.po'
        if po_path.exists():
            update_po_with_translations(po_path, lang_code)
        else:
            print(f"✗ .po file not found: {po_path}")
    
    print("-" * 50)
    print("✓ Translations added successfully!")
    print("\nNext steps:")
    print("1. Review and edit .po files as needed")
    print("2. Run: python manage.py compilemessages")
    print("3. Test language switching on the website")

if __name__ == '__main__':
    main()

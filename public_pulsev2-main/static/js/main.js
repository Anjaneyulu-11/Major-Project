"// JS loaded
document.addEventListener('DOMContentLoaded', function() {

    /* ============================================
       LANGUAGE SELECTOR
       ============================================ */

    const langToggle = document.getElementById('langToggle');
    const langDropdown = document.getElementById('langDropdown');
    const langOptions = document.querySelectorAll('.lang-option');

    // Language translations mapping
    const translations = {
        en: {
            'home': 'Home',
            'dashboard': 'Dashboard',
            'complaints': 'Complaints',
            'citizen': 'Citizen',
            'how-it-works': 'How it Works',
            'my-complaints': 'My Complaints',
            'profile': 'Profile',
            'logout': 'Logout',
            'login': 'Login',
            'register': 'Register',
            'admin-dashboard': 'Admin Dashboard',
            'get-started': 'Get Started',
            'civic-pulse': 'CIVIC PULSE',
            'civic-subtitle': 'Smart Civic Engagement Platform'
        },
        hi: {
            'home': 'होम',
            'dashboard': 'डैशबोर्ड',
            'complaints': 'शिकायतें',
            'citizen': 'नागरिक',
            'how-it-works': 'यह कैसे काम करता है',
            'my-complaints': 'मेरी शिकायतें',
            'profile': 'प्रोफाइल',
            'logout': 'लॉग आउट',
            'login': 'लॉगिन',
            'register': 'पंजीकरण',
            'admin-dashboard': 'व्यवस्थापक डैशबोर्ड',
            'get-started': 'शुरू करें',
            'civic-pulse': 'सिविक पल्स',
            'civic-subtitle': 'स्मार्ट नागरिक सगंठन प्लेटफॉर्म'
        },
        te: {
            'home': 'హోమ్',
            'dashboard': 'డ్యాష్‌బోర్డ్',
            'complaints': 'ఫిర్యాదులు',
            'citizen': 'పౌరుడు',
            'how-it-works': 'ఇది ఎలా పనిచేస్తుంది',
            'my-complaints': 'నా ఫిర్యాదులు',
            'profile': 'ప్రొఫైల్',
            'logout': 'లాగ్ అవుట్',
            'login': 'లాగిన్',
            'register': 'నమోదు చేయండి',
            'admin-dashboard': 'ఆడ్మిన్ డ్యాష్‌బోర్డ్',
            'get-started': 'ప్రారంభించండి',
            'civic-pulse': 'సివిక్ పల్స్',
            'civic-subtitle': 'స్మార్ట్ సివిక్ ఎంగేజ్‌మెంట్ ప్లాట్‌ఫార్మ్'
        },
        ta: {
            'home': 'முகப்பு',
            'dashboard': 'ড্যাশবোর්ড',
            'complaints': 'புகார்கள்',
            'citizen': 'குடிமகன்',
            'how-it-works': 'இது எப்படி வேலை செய்கிறது',
            'my-complaints': 'என் புகார்கள்',
            'profile': 'சுயவிவரம்',
            'logout': 'வெளியேறு',
            'login': 'உள்நுழைக',
            'register': 'பதிவு செய்க',
            'admin-dashboard': 'நிர்வாகி டாஷ்போர்ட்',
            'get-started': 'தொடங்கவும்',
            'civic-pulse': 'சிவிக் பாலஸ்',
            'civic-subtitle': 'Smart Civic Engagement Platform'
        },
        kn: {
            'home': 'ಮುಖ್ಯ',
            'dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
            'complaints': 'ದೃಶ್ಯಗಳು',
            'citizen': 'ನಾಗರಿಕ',
            'how-it-works': 'ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ',
            'my-complaints': 'ನನ್ನ ದೃಶ್ಯಗಳು',
            'profile': 'ಪ್ರೊಫೈಲ್',
            'logout': 'ಲಾಗ್ ಔಟ್',
            'login': 'ಲಾಗಿನ್',
            'register': 'ನೋಂದಾಯಿತ',
            'admin-dashboard': 'ನಿರ್ವಾಹಕ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
            'get-started': 'ಪ್ರಾರಂಭಿಸಿ',
            'civic-pulse': 'ಸಿವಿಕ್ ಪಲ್ಸ್',
            'civic-subtitle': 'ಸ್ಮಾರ್ಟ್ ಸಿವಿಕ್ ಎನ್‍ಗೇಜ್‍ಮೆಂಟ್ ಪ್ಲಾಟ್‍ಫಾರ್ಮ್'
        },
        ml: {
            'home': 'ഹോം',
            'dashboard': 'ഡാഷ്ബോർഡ്',
            'complaints': 'പരാതികൾ',
            'citizen': 'പൌരൻ',
            'how-it-works': 'ഇത് എങ്ങനെ പ്രവർത്തിക്കുന്നു',
            'my-complaints': 'എന്റെ പരാതികൾ',
            'profile': 'പ്രൊഫൈൽ',
            'logout': 'ലോഗ് ഔട്ട്',
            'login': 'ലോഗിൻ',
            'register': 'രജിസ്റ്റർ ചെയ്യുക',
            'admin-dashboard': 'അഡ്മിൻ ഡാഷ്ബോർഡ്',
            'get-started': 'ആരംഭിക്കുക',
            'civic-pulse': 'സിവിക് പൾസ്',
            'civic-subtitle': 'സ്മാർട്ട സിവിക് എൻഗേജ്മെന്റ് പ്ലാറ്റ്ഫോം'
        }
    };

    // Initialize language from localStorage or default to English
    function initLanguage() {
        const savedLang = localStorage.getItem('site_language') || 'en';
        setLanguage(savedLang);
        updateLanguageUI(savedLang);
    }

    // Set language in localStorage
    function setLanguage(lang) {
        localStorage.setItem('site_language', lang);
        applyLanguage(lang);
    }

    // Apply language translations to page
    function applyLanguage(lang) {
        const langData = translations[lang] || translations.en;
        
        // Update specific elements with data-lang attributes
        document.querySelectorAll('[data-lang-key]').forEach(el => {
            const key = el.getAttribute('data-lang-key');
            if (langData[key]) {
                el.textContent = langData[key];
            }
        });
    }

    // Update language dropdown UI
    function updateLanguageUI(lang) {
        langOptions.forEach(option => {
            if (option.getAttribute('data-lang') === lang) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });
    }

    // Toggle language dropdown
    if (langToggle) {
        langToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            langDropdown.style.display = langDropdown.style.display === 'none' ? 'block' : 'none';
        });
    }

    // Language option selection
    langOptions.forEach(option => {
        option.addEventListener('click', function() {
            const lang = this.getAttribute('data-lang');
            setLanguage(lang);
            updateLanguageUI(lang);
            langDropdown.style.display = 'none';
        });
    });

    // Close language dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.nav-icon-item')) {
            langDropdown.style.display = 'none';
        }
    });


    /* ============================================
       ACCESSIBILITY PANEL
       ============================================ */

    const a11yToggle = document.getElementById('a11yToggle');
    const a11yPanel = document.getElementById('a11yPanel');
    const a11yClose = document.getElementById('a11yClose');
    const a11yButtons = document.querySelectorAll('.a11y-btn');

    // Accessibility state tracking
    let a11yState = {
        'dark-contrast': false,
        'invert-colors': false,
        'saturation': false,
        'text-increase': 0,
        'text-decrease': 0
    };

    // Initialize accessibility from localStorage
    function initAccessibility() {
        const savedState = localStorage.getItem('a11y_state');
        if (savedState) {
            a11yState = JSON.parse(savedState);
            applyAccessibilitySettings();
        }
    }

    // Apply accessibility settings to body
    function applyAccessibilitySettings() {
        const body = document.body;

        // Clear all a11y classes first
        body.classList.remove('dark-contrast', 'invert-colors', 'saturation-off', 'saturation-on');

        // Apply active classes based on state
        if (a11yState['dark-contrast']) {
            body.classList.add('dark-contrast');
        }
        if (a11yState['invert-colors']) {
            body.classList.add('invert-colors');
        }
        if (a11yState['saturation']) {
            body.classList.add('saturation-on');
        } else {
            body.classList.remove('saturation-on');
        }

        // Apply text size
        body.classList.remove('text-size-1', 'text-size-2', 'text-size-3', 'text-size-4', 'text-size-5');
        const totalSizeChange = (a11yState['text-increase'] || 0) - (a11yState['text-decrease'] || 0);
        if (totalSizeChange > 0) {
            body.classList.add(`text-size-${Math.min(totalSizeChange, 5)}`);
        }

        // Update button active states
        updateA11yButtonStates();

        // Save state to localStorage
        localStorage.setItem('a11y_state', JSON.stringify(a11yState));
    }

    // Update button active states visually
    function updateA11yButtonStates() {
        const btnMap = {
            'dark-contrast': document.getElementById('darkContrastBtn'),
            'invert-colors': document.getElementById('invertColorsBtn'),
            'saturation': document.getElementById('saturationBtn'),
            'text-increase': document.getElementById('textIncreaseBtn'),
            'text-decrease': document.getElementById('textDecreaseBtn'),
            'reset': document.getElementById('resetBtn')
        };

        Object.keys(btnMap).forEach(key => {
            if (btnMap[key]) {
                if (key === 'reset') {
                    btnMap[key].classList.remove('active');
                } else if (a11yState[key]) {
                    btnMap[key].classList.add('active');
                } else {
                    btnMap[key].classList.remove('active');
                }
            }
        });
    }

    // Toggle accessibility panel
    if (a11yToggle) {
        a11yToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const isHidden = a11yPanel.style.display === 'none';
            a11yPanel.style.display = isHidden ? 'block' : 'none';
        });
    }

    // Close accessibility panel
    if (a11yClose) {
        a11yClose.addEventListener('click', function() {
            a11yPanel.style.display = 'none';
        });
    }

    // Accessibility button handlers
    a11yButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const feature = this.getAttribute('data-feature');

            switch(feature) {
                case 'dark-contrast':
                    a11yState['dark-contrast'] = !a11yState['dark-contrast'];
                    break;
                case 'invert-colors':
                    a11yState['invert-colors'] = !a11yState['invert-colors'];
                    break;
                case 'saturation':
                    a11yState['saturation'] = !a11yState['saturation'];
                    break;
                case 'text-increase':
                    a11yState['text-increase'] = (a11yState['text-increase'] || 0) + 1;
                    if (a11yState['text-increase'] > 5) {
                        a11yState['text-increase'] = 5;
                    }
                    break;
                case 'text-decrease':
                    a11yState['text-decrease'] = (a11yState['text-decrease'] || 0) + 1;
                    if (a11yState['text-decrease'] > 5) {
                        a11yState['text-decrease'] = 5;
                    }
                    break;
                case 'reset':
                    // Reset all accessibility settings
                    a11yState = {
                        'dark-contrast': false,
                        'invert-colors': false,
                        'saturation': false,
                        'text-increase': 0,
                        'text-decrease': 0
                    };
                    document.body.classList.remove(
                        'dark-contrast', 'invert-colors', 'saturation-off', 'saturation-on',
                        'text-size-1', 'text-size-2', 'text-size-3', 'text-size-4', 'text-size-5'
                    );
                    break;
            }

            applyAccessibilitySettings();
        });
    });

    // Close panel when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.a11y-panel') && !e.target.closest('#a11yToggle')) {
            a11yPanel.style.display = 'none';
        }
    });

    // Initialize on page load
    initLanguage();
    initAccessibility();

});
" 

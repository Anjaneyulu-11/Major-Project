/**
 * Government of India Style - Accessibility & Language Controls
 * Pure JavaScript - NO Frameworks
 * 
 * CRITICAL FIX: Accessibility styles DO NOT apply on page load unless
 * the user explicitly saved preferences before. No CSS class is added
 * unless the user clicks an accessibility option.
 */

document.addEventListener('DOMContentLoaded', function() {

    /* ============================================
       LANGUAGE SELECTOR - 8 LANGUAGES
       COMPLETELY ISOLATED FROM ACCESSIBILITY
       ============================================ */

    const langDropdownWrapper = document.getElementById('langDropdownWrapper');
    const langToggleBtn = document.getElementById('langToggle');
    const langDropdownMenu = document.getElementById('langDropdown');
    const langOptions = document.querySelectorAll('.lang-option');

    // 8 Languages with native names
    const supportedLanguages = {
        'en': 'English',
        'hi': 'हिन्दी',
        'te': 'తెలుగు',
        'ta': 'தமిழ్',
        'kn': 'ಕನ್ನಡ',
        'ml': 'മലയാളം',
        'mr': 'मराठी',
        'bn': 'বাংলা'
    };

    /**
     * Initialize language selector (ISOLATED)
     * Language switching must NOT affect accessibility settings
     */
    function initLanguageSelector() {
        const savedLang = localStorage.getItem('civicpulse_language') || 'en';
        
        if (langToggleBtn) {
            langToggleBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                toggleLanguageDropdown();
            });
        }

        langOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const lang = this.getAttribute('data-lang');
                selectLanguage(lang);
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (langDropdownMenu && 
                !e.target.closest('#langDropdownWrapper') && 
                !e.target.closest('#langToggle')) {
                langDropdownMenu.style.display = 'none';
            }
        });

        // Close dropdown on ESC key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && langDropdownMenu) {
                langDropdownMenu.style.display = 'none';
            }
        });

        updateLanguageUI(savedLang);
    }

    /**
     * Toggle language dropdown visibility
     */
    function toggleLanguageDropdown() {
        if (langDropdownMenu) {
            const isHidden = langDropdownMenu.style.display === 'none';
            langDropdownMenu.style.display = isHidden ? 'block' : 'none';
        }
    }

    /**
     * Select and save language
     * NOTE: Does NOT call any accessibility functions
     */
    function selectLanguage(lang) {
        if (supportedLanguages[lang]) {
            localStorage.setItem('civicpulse_language', lang);
            updateLanguageUI(lang);
            
            // Close dropdown
            if (langDropdownMenu) {
                langDropdownMenu.style.display = 'none';
            }
            
            // Reload page to apply language (if backend translation implemented)
            // window.location.reload();
            // For now, just update UI visual indicators
        }
    }

    /**
     * Update language UI to show selected language
     */
    function updateLanguageUI(lang) {
        langOptions.forEach(option => {
            if (option.getAttribute('data-lang') === lang) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });
    }


    /* ============================================
       ACCESSIBILITY PANEL - CLEAN STATE MANAGEMENT
       
       KEY PRINCIPLE:
       - NO styles applied on page load
       - Only apply if user EXPLICITLY saved settings
       - Each feature is independent
       ============================================ */

    const a11yToggle = document.getElementById('a11yToggle');
    const a11yBackdrop = document.getElementById('a11yBackdrop');
    const a11yPanel = document.getElementById('a11yPanel');
    const a11yCloseBtn = document.getElementById('a11yCloseBtn');
    const a11yButtons = document.querySelectorAll('[data-a11y-feature]');

    /**
     * CLEAN ACCESSIBILITY STATE OBJECT
     * Explicit booleans, no magic values
     * Default values represent "NOT APPLIED" state
     */
    let a11yState = {
        'dark-contrast': false,
        'invert-colors': false,
        'saturation': false,  // saturation = high saturation mode (if true, applies saturate(1.8))
        'text-increase': 0,
        'text-decrease': 0,
        'cursor-default': false
    };

    /**
     * Initialize accessibility panel
     * CRITICAL: Load preferences but DO NOT apply them on init
     */
    function initAccessibilityPanel() {
        // Load state from localStorage (if it exists)
        loadA11yPreferences();
        
        // Setup event handlers
        if (a11yToggle) {
            a11yToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                openA11yPanel();
            });
        }

        if (a11yCloseBtn) {
            a11yCloseBtn.addEventListener('click', function() {
                closeA11yPanel();
            });
        }

        if (a11yBackdrop) {
            a11yBackdrop.addEventListener('click', function() {
                closeA11yPanel();
            });
        }

        // Close panel on ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && a11yPanel && a11yPanel.style.display !== 'none') {
                closeA11yPanel();
            }
        });

        // Feature buttons
        a11yButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const feature = this.getAttribute('data-a11y-feature');
                handleA11yFeature(feature);
            });
        });
    }

    /**
     * Open accessibility panel
     */
    function openA11yPanel() {
        if (a11yBackdrop) a11yBackdrop.style.display = 'block';
        if (a11yPanel) a11yPanel.style.display = 'flex';
    }

    /**
     * Close accessibility panel
     */
    function closeA11yPanel() {
        if (a11yBackdrop) a11yBackdrop.style.display = 'none';
        if (a11yPanel) a11yPanel.style.display = 'none';
    }

    /**
     * Handle accessibility feature toggling
     * Called ONLY when user clicks a button
     */
    function handleA11yFeature(feature) {
        switch(feature) {
            case 'dark-contrast':
                a11yState['dark-contrast'] = !a11yState['dark-contrast'];
                applyDarkContrast(a11yState['dark-contrast']);
                break;
            case 'invert-colors':
                a11yState['invert-colors'] = !a11yState['invert-colors'];
                applyInvertColors(a11yState['invert-colors']);
                break;
            case 'saturation':
                a11yState['saturation'] = !a11yState['saturation'];
                applySaturation(a11yState['saturation']);
                break;
            case 'text-increase':
                a11yState['text-increase']++;
                if (a11yState['text-increase'] > 4) a11yState['text-increase'] = 4;
                a11yState['text-decrease'] = 0; // Reset decrease to avoid conflict
                applyTextSize();
                break;
            case 'text-decrease':
                a11yState['text-decrease']++;
                if (a11yState['text-decrease'] > 2) a11yState['text-decrease'] = 2;
                a11yState['text-increase'] = 0; // Reset increase to avoid conflict
                applyTextSize();
                break;
            case 'cursor-default':
                a11yState['cursor-default'] = !a11yState['cursor-default'];
                applyCursorDefault(a11yState['cursor-default']);
                break;
            case 'reset':
                resetAllA11y();
                break;
        }
        
        saveA11yPreferences();
        updateA11yButtonStates();
    }

    /**
     * Apply dark contrast
     * Only called when explicitly toggled by user
     */
    function applyDarkContrast(active) {
        const body = document.body;
        if (active) {
            body.classList.add('accessibility-dark-contrast');
        } else {
            body.classList.remove('accessibility-dark-contrast');
        }
    }

    /**
     * Apply invert colors
     * Only called when explicitly toggled by user
     */
    function applyInvertColors(active) {
        const body = document.body;
        if (active) {
            body.classList.add('accessibility-invert-colors');
        } else {
            body.classList.remove('accessibility-invert-colors');
        }
    }

    /**
     * Apply high saturation
     * FIXED: Only adds CSS class if TRUE (saturation/high-saturation enabled)
     * Does NOT add any class when false (normal saturation is default)
     */
    function applySaturation(active) {
        const body = document.body;
        // Always remove both possible states
        body.classList.remove('accessibility-saturation-off', 'accessibility-saturation-high');
        
        // ONLY add class if high-saturation is explicitly enabled
        if (active) {
            body.classList.add('accessibility-saturation-high');
        }
        // NOTE: We do NOT add 'accessibility-saturation-off' here
        // The normal appearance (no class) is saturate(100%)
    }

    /**
     * Apply text size changes
     * Only called when user explicitly changes text size
     */
    function applyTextSize() {
        const body = document.body;
        // Remove all text size classes
        body.classList.remove(
            'accessibility-text-size-increase-1',
            'accessibility-text-size-increase-2',
            'accessibility-text-size-increase-3',
            'accessibility-text-size-increase-4',
            'accessibility-text-size-decrease-1',
            'accessibility-text-size-decrease-2'
        );

        // Only add class if text-increase is active
        if (a11yState['text-increase'] > 0) {
            body.classList.add(`accessibility-text-size-increase-${a11yState['text-increase']}`);
        } 
        // Only add class if text-decrease is active
        else if (a11yState['text-decrease'] > 0) {
            body.classList.add(`accessibility-text-size-decrease-${a11yState['text-decrease']}`);
        }
        // If both are 0, no class is added (default size)
    }

    /**
     * Apply cursor default
     * Only called when explicitly toggled by user
     */
    function applyCursorDefault(active) {
        const body = document.body;
        if (active) {
            body.classList.add('accessibility-cursor-default');
        } else {
            body.classList.remove('accessibility-cursor-default');
        }
    }

    /**
     * Reset ALL accessibility features
     * - Resets state object to defaults
     * - Removes ALL CSS classes
     * - Clears localStorage
     * - Restores original design
     */
    function resetAllA11y() {
        // Reset state to defaults
        a11yState = {
            'dark-contrast': false,
            'invert-colors': false,
            'saturation': false,
            'text-increase': 0,
            'text-decrease': 0,
            'cursor-default': false
        };

        // Remove ALL accessibility CSS classes
        const body = document.body;
        body.classList.remove(
            'accessibility-dark-contrast',
            'accessibility-invert-colors',
            'accessibility-saturation-off',
            'accessibility-saturation-high',
            'accessibility-text-size-increase-1',
            'accessibility-text-size-increase-2',
            'accessibility-text-size-increase-3',
            'accessibility-text-size-increase-4',
            'accessibility-text-size-decrease-1',
            'accessibility-text-size-decrease-2',
            'accessibility-cursor-default'
        );

        // Clear localStorage
        localStorage.removeItem('civicpulse_a11y');
        
        // Update UI
        updateA11yButtonStates();
    }

    /**
     * Update button active states visually
     * Called after state changes or when restoring saved state
     */
    function updateA11yButtonStates() {
        const btnMap = {
            'dark-contrast': document.getElementById('a11yDarkContrast'),
            'invert-colors': document.getElementById('a11yInvertColors'),
            'saturation': document.getElementById('a11ySaturation'),
            'text-increase': document.getElementById('a11yTextIncrease'),
            'text-decrease': document.getElementById('a11yTextDecrease'),
            'cursor-default': document.getElementById('a11yCursorDefault')
        };

        Object.keys(btnMap).forEach(key => {
            const btn = btnMap[key];
            if (btn) {
                if (a11yState[key]) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            }
        });
    }

    /**
     * Save preferences to localStorage
     * Called ONLY after user explicitly changes a setting
     */
    function saveA11yPreferences() {
        localStorage.setItem('civicpulse_a11y', JSON.stringify(a11yState));
    }

    /**
     * Load preferences from localStorage
     * CRITICAL: Only applies styles if valid saved data exists
     * 
     * This function:
     * 1. Reads localStorage
     * 2. Validates the data
     * 3. Applies CSS classes ONLY if user previously saved settings
     * 4. Does NOT apply defaults on first page load
     */
    function loadA11yPreferences() {
        const saved = localStorage.getItem('civicpulse_a11y');
        
        // No saved preferences = do nothing
        if (!saved) {
            console.log('✓ No saved accessibility settings. Default appearance loaded.');
            return;
        }
        
        // Try to parse and validate saved preferences
        try {
            const parsed = JSON.parse(saved);
            
            // Validate structure before applying
            if (isValidA11yState(parsed)) {
                a11yState = parsed;
                
                // Now apply the SAVED preferences to the page
                applyDarkContrast(a11yState['dark-contrast']);
                applyInvertColors(a11yState['invert-colors']);
                applySaturation(a11yState['saturation']);
                applyTextSize();
                applyCursorDefault(a11yState['cursor-default']);
                
                // Update button UI to show which features are active
                updateA11yButtonStates();
                
                console.log('✓ Accessibility settings restored from localStorage');
            } else {
                console.warn('Invalid accessibility state in localStorage. Using defaults.');
            }
        } catch (e) {
            console.error('Error loading accessibility preferences:', e);
            // On error, clear the corrupted data
            localStorage.removeItem('civicpulse_a11y');
        }
    }

    /**
     * Validate accessibility state object
     * Ensures data structure is correct before applying
     */
    function isValidA11yState(state) {
        if (typeof state !== 'object' || state === null) {
            return false;
        }
        
        // Check required properties exist and have correct types
        return (
            typeof state['dark-contrast'] === 'boolean' &&
            typeof state['invert-colors'] === 'boolean' &&
            typeof state['saturation'] === 'boolean' &&
            typeof state['text-increase'] === 'number' &&
            typeof state['text-decrease'] === 'number' &&
            typeof state['cursor-default'] === 'boolean' &&
            state['text-increase'] >= 0 && state['text-increase'] <= 4 &&
            state['text-decrease'] >= 0 && state['text-decrease'] <= 2
        );
    }

    /**
     * Keyboard Navigation Support
     */
    document.addEventListener('keydown', function(e) {
        // Alt + L = Language toggle
        if (e.altKey && e.key === 'l') {
            e.preventDefault();
            if (langToggleBtn) langToggleBtn.click();
        }
        // Alt + A = Accessibility toggle
        if (e.altKey && e.key === 'a') {
            e.preventDefault();
            if (a11yToggle) a11yToggle.click();
        }
    });

    /* ============================================
       INITIALIZATION
       ============================================ */
    initLanguageSelector();
    initAccessibilityPanel();

    console.log('✓ Accessibility & Language Controls Initialized');
});

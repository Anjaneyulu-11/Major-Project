# Code Citations

## License: unknown
https://github.com/lawrimon/PDA_SWE/blob/692d0786eff244988c567cb8cb448d958ef4c716/src/client/react_js_app/src/components/SpeechFunctions.js

```
✅ Voice input successfully integrated! The microphone button with Web Speech API is now in place. Here's what was added:

### **HTML Addition (Microphone Button)**
```html
<button type="button" class="btn btn-mic" id="micButton" title="Click to start voice input" aria-label="Microphone input">
    <i class="fas fa-microphone"></i>
</button>
```
Added next to the Send button in the input-group-append.

### **CSS Styles**
```css
/* Microphone Button Styling */
.btn-mic {
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    color: #333;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 5px;
}

.btn-mic:hover {
    background-color: #e8e8e8;
    border-color: #999;
}

.btn-mic.listening {
    background-color: #ff4444;
    color: white;
    border-color: #cc0000;
    animation: pulse-glow 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
    0% {
        box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(255, 68, 68, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(255, 68, 68, 0);
    }
}
```

### **JavaScript Implementation**
```javascript
// Web Speech API for Voice Input
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

// Initialize Speech Recognition if supported
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    // Handle speech recognition start
    recognition.onstart = function() {
        isListening = true;
        micButton.classList.add('listening');
        micButton.innerHTML = '<i class="fas fa-circle"></i>';
        micButton.title = 'Listening... Click to stop';
    };
    
    // Handle speech recognition results
    recognition.onresult = function(event) {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Update input field with final or interim transcript
        if (finalTranscript) {
            messageInput.value = (messageInput.value + finalTranscript).trim();
        } else if (interimTranscript) {
            messageInput.value = (messageInput.value + interimTranscript).trim();
        }
    };
    
    // Handle errors
    recognition.onerror = function(event) {
        let errorMessage = 'Voice input error: ';
        
        switch
```


## License: unknown
https://github.com/JorgeAcostaDLP/lyricsearch/blob/50843675dd8495f6d3ced1a9ad14ba1ca3ffd128/client/components/ListenButton.js

```
✅ Voice input successfully integrated! The microphone button with Web Speech API is now in place. Here's what was added:

### **HTML Addition (Microphone Button)**
```html
<button type="button" class="btn btn-mic" id="micButton" title="Click to start voice input" aria-label="Microphone input">
    <i class="fas fa-microphone"></i>
</button>
```
Added next to the Send button in the input-group-append.

### **CSS Styles**
```css
/* Microphone Button Styling */
.btn-mic {
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    color: #333;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 5px;
}

.btn-mic:hover {
    background-color: #e8e8e8;
    border-color: #999;
}

.btn-mic.listening {
    background-color: #ff4444;
    color: white;
    border-color: #cc0000;
    animation: pulse-glow 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
    0% {
        box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(255, 68, 68, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(255, 68, 68, 0);
    }
}
```

### **JavaScript Implementation**
```javascript
// Web Speech API for Voice Input
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

// Initialize Speech Recognition if supported
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    // Handle speech recognition start
    recognition.onstart = function() {
        isListening = true;
        micButton.classList.add('listening');
        micButton.innerHTML = '<i class="fas fa-circle"></i>';
        micButton.title = 'Listening... Click to stop';
    };
    
    // Handle speech recognition results
    recognition.onresult = function(event) {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Update input field with final or interim transcript
        if (finalTranscript) {
            messageInput.value = (messageInput.value + finalTranscript).trim();
        } else if (interimTranscript) {
            messageInput.value = (messageInput.value + interimTranscript).trim();
        }
    };
    
    // Handle errors
    recognition.onerror = function(event) {
        let errorMessage = 'Voice input error: ';
        
        switch
```


## License: unknown
https://github.com/tlodge/fmtrainer/blob/e28c7f4d5ebe15593ac2f001c1f702f08857736c/src/features/train/components/Main/Main.js

```
✅ Voice input successfully integrated! The microphone button with Web Speech API is now in place. Here's what was added:

### **HTML Addition (Microphone Button)**
```html
<button type="button" class="btn btn-mic" id="micButton" title="Click to start voice input" aria-label="Microphone input">
    <i class="fas fa-microphone"></i>
</button>
```
Added next to the Send button in the input-group-append.

### **CSS Styles**
```css
/* Microphone Button Styling */
.btn-mic {
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    color: #333;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 5px;
}

.btn-mic:hover {
    background-color: #e8e8e8;
    border-color: #999;
}

.btn-mic.listening {
    background-color: #ff4444;
    color: white;
    border-color: #cc0000;
    animation: pulse-glow 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
    0% {
        box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(255, 68, 68, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(255, 68, 68, 0);
    }
}
```

### **JavaScript Implementation**
```javascript
// Web Speech API for Voice Input
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

// Initialize Speech Recognition if supported
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    // Handle speech recognition start
    recognition.onstart = function() {
        isListening = true;
        micButton.classList.add('listening');
        micButton.innerHTML = '<i class="fas fa-circle"></i>';
        micButton.title = 'Listening... Click to stop';
    };
    
    // Handle speech recognition results
    recognition.onresult = function(event) {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Update input field with final or interim transcript
        if (finalTranscript) {
            messageInput.value = (messageInput.value + finalTranscript).trim();
        } else if (interimTranscript) {
            messageInput.value = (messageInput.value + interimTranscript).trim();
        }
    };
    
    // Handle errors
    recognition.onerror = function(event) {
        let errorMessage = 'Voice input error: ';
        
        switch
```


## License: unknown
https://github.com/vigneshnagavel/communication-video/blob/41d4e88b907e85e7442def251f9334328a6da77a/src/SubtitleGenerator.js

```
✅ Voice input successfully integrated! The microphone button with Web Speech API is now in place. Here's what was added:

### **HTML Addition (Microphone Button)**
```html
<button type="button" class="btn btn-mic" id="micButton" title="Click to start voice input" aria-label="Microphone input">
    <i class="fas fa-microphone"></i>
</button>
```
Added next to the Send button in the input-group-append.

### **CSS Styles**
```css
/* Microphone Button Styling */
.btn-mic {
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    color: #333;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 5px;
}

.btn-mic:hover {
    background-color: #e8e8e8;
    border-color: #999;
}

.btn-mic.listening {
    background-color: #ff4444;
    color: white;
    border-color: #cc0000;
    animation: pulse-glow 1.5s ease-in-out infinite;
}

@keyframes pulse-glow {
    0% {
        box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(255, 68, 68, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(255, 68, 68, 0);
    }
}
```

### **JavaScript Implementation**
```javascript
// Web Speech API for Voice Input
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

// Initialize Speech Recognition if supported
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    // Handle speech recognition start
    recognition.onstart = function() {
        isListening = true;
        micButton.classList.add('listening');
        micButton.innerHTML = '<i class="fas fa-circle"></i>';
        micButton.title = 'Listening... Click to stop';
    };
    
    // Handle speech recognition results
    recognition.onresult = function(event) {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Update input field with final or interim transcript
        if (finalTranscript) {
            messageInput.value = (messageInput.value + finalTranscript).trim();
        } else if (interimTranscript) {
            messageInput.value = (messageInput.value + interimTranscript).trim();
        }
    };
    
    // Handle errors
    recognition.onerror = function(event) {
        let errorMessage = 'Voice input error: ';
        
        switch
```


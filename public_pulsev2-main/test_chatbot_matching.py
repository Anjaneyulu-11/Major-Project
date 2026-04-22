#!/usr/bin/env python
"""
Test script to verify chatbot matching logic works correctly.
Run from Django shell: python manage.py shell < test_chatbot_matching.py
"""

# Test cases
test_inputs = [
    "how can i login",
    "login",
    "how do i login",
    "sign in",
    "what does pending mean",
    "pending status",
    "track complaint",
    "how to track my complaint",
    "submit complaint",
    "lodge a complaint",
    "what is civic pulse",
    "hello",
    "hi there",
    "thank you",
    "who built this",
    "random gibberish xyz",
]

# Import FAQ_KB from chatbot.views
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')
django.setup()

from chatbot.views import FAQ_KB

print("=" * 80)
print("CHATBOT MATCHING LOGIC TEST")
print("=" * 80)
print(f"\nTotal FAQ entries: {len(FAQ_KB)}\n")

for test_input in test_inputs:
    msg_lower = test_input.lower().strip()
    response = None
    matched_keyword = None
    
    # Match against FAQ_KB
    for idx, item in enumerate(FAQ_KB):
        keywords = item.get("keywords", [])
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in msg_lower:
                response = item.get("answer")
                matched_keyword = keyword_lower
                break
        if response:
            break
    
    if not response:
        response = "Sorry, I didn't understand. You can ask about login, complaints, tracking, or system features."
        status = "FALLBACK"
    else:
        status = "✓ MATCHED"
    
    print(f"Input: '{test_input}'")
    print(f"Status: {status}")
    if matched_keyword:
        print(f"Matched keyword: '{matched_keyword}'")
    print(f"Response: {response[:70]}{'...' if len(response) > 70 else ''}")
    print("-" * 80)

print("\nTest completed!")

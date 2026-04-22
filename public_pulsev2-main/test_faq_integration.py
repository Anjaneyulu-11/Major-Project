#!/usr/bin/env python
"""
Test script to verify FAQ_KB integration in chatbot
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')
django.setup()

from chatbot.views import FAQ_KB

print(f"FAQ_KB loaded with {len(FAQ_KB)} entries")

print("\nFirst 3 entries:")
for i, item in enumerate(FAQ_KB[:3]):
    print(f"{i+1}. Keywords: {item['keywords']}")
    print(f"   Answer: {item['answer'][:50]}...")

print("\nTesting keyword matching logic:")
test_inputs = [
    "how can i login",
    "what does pending mean",
    "submit complaint",
    "hello",
    "random gibberish xyz"
]

for test_input in test_inputs:
    msg_lower = test_input.lower().strip()
    response = None

    # Test FAQ_KB matching (same logic as in chatbot function)
    for idx, item in enumerate(FAQ_KB):
        keywords = item.get("keywords", [])
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in msg_lower:
                response = item.get("answer")
                print(f"✓ '{test_input}' → Matched keyword '{keyword_lower}' at index {idx}")
                break
        if response:
            break

    if not response:
        print(f"✗ '{test_input}' → No match found (would use fallback)")

print("\nFAQ_KB integration verification: COMPLETE")
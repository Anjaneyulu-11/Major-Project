# Script to update FAQ_KB in chatbot/views.py
with open('chatbot/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the FAQ_KB section
start_marker = "# Based on Civic Pulse specifications - exact intents and answers\nFAQ_KB = ["

start_idx = content.find(start_marker)
if start_idx == -1:
    print("ERROR: Could not find FAQ_KB start marker")
    exit(1)

# Find "def chatbot" which comes after FAQ_KB
next_def = content.find("\ndef chatbot(request):", start_idx)
if next_def == -1:
    print("ERROR: Could not find def chatbot")
    exit(1)

# Find the closing ] before def chatbot
section_before_def = content[:next_def]
last_bracket_idx = section_before_def.rfind("]")

new_kb = '''# Based on Civic Pulse specifications - exact intents and answers
FAQ_KB = [
    {
        "keywords": ["submit complaint", "lodge complaint", "file complaint"],
        "answer": "To submit a complaint:\\n1. Login to Civic Pulse\\n2. Go to Dashboard\\n3. Click \\"Lodge Complaint\\"\\n4. Select category\\n5. Enter details\\n6. Upload images (optional)\\n7. Click Submit\\nYou will receive a Complaint ID."
    },
    {
        "keywords": ["track complaint", "check status"],
        "answer": "Go to \\"Track Complaint\\", enter your Complaint ID, and click Track to see the current status."
    },
    {
        "keywords": ["my complaints", "all complaints"],
        "answer": "Click \\"My Complaints\\" from the dashboard or sidebar to see all complaints submitted by you."
    },
    {
        "keywords": ["pending", "still pending"],
        "answer": "Pending means the department has received your complaint but has not yet resolved it."
    },
    {
        "keywords": ["resolved"],
        "answer": "Resolved means the department has taken action and closed your complaint."
    },
    {
        "keywords": ["in progress"],
        "answer": "In Progress means your complaint is currently being worked on by the department."
    },
    {
        "keywords": ["who handles", "assigned department"],
        "answer": "Your complaint is automatically assigned to the relevant government department based on category."
    },
    {
        "keywords": ["view complaint", "see details"],
        "answer": "Go to \\"My Complaints\\" and click the \\"View\\" button next to the complaint."
    },
    {
        "keywords": ["change password"],
        "answer": "Go to Profile, click \\"Change Password\\", enter your old password, and set a new password."
    },
    {
        "keywords": ["change username"],
        "answer": "Usernames cannot be changed once created."
    },
    {
        "keywords": ["logout", "log out"],
        "answer": "Yes. Click the \\"Logout\\" button to safely exit and protect your account."
    },
    {
        "keywords": ["count different", "total complaints"],
        "answer": "The dashboard shows total complaints. The My Complaints page may use pagination."
    },
]
'''

# Replace from start_idx to last_bracket_idx + 1
new_content = content[:start_idx] + new_kb + content[last_bracket_idx + 1:]

# Write back
with open('chatbot/views.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✓ FAQ_KB updated successfully")

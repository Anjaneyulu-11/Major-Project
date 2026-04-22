import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings') 
import django 
django.setup() 
from django.core.mail import send_mail 
 
test_emails = ['227r1a05j1@cmrtc.ac.in', 'test1@example.com', 'test2@example.com'] 
 
for email in test_emails: 
    print(f'Sending to: {email}') 
    try: 
        send_mail('Test', f'Test to {email}', 'civicpulse.govt@gmail.com', [email]) 
        print(f'  ? Sent to {email}') 
    except Exception as e: 
        print(f'  ? Failed for {email}: {e}') 

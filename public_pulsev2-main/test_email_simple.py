import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings') 
import django 
django.setup() 
from django.core.mail import send_mail 
 
print("Testing Civic Pulse Email System...") 
try: 
    send_mail( 
        'Test from Civic Pulse', 
        'This is a test email. Your complaint system should now work!', 
        ['227r1a05j1@cmrtc.ac.in'], 
        fail_silently=False 
    ) 
    print('SUCCESS: Email sent! Check the recipient email.') 
    print('If not in inbox, check spam folder.') 
except Exception as e: 
    print(f'ERROR: {e}') 

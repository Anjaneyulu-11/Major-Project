import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings') 
import django 
django.setup() 
from django.core.mail import send_mail 
from django.conf import settings 
import datetime 
 
print("="*60) 
print("FINAL EMAIL TEST") 
print("="*60) 
 
complaint_id = "CP-20251230-TEST123" 
citizen_email = "227r1a05j1@cmrtc.ac.in" 
 
try: 
    send_mail( 
        'Complaint Registered - ID: ' + complaint_id, 
        'Dear Test User,\\n\\nYour complaint has been registered.\\n\\nComplaint ID: ' + complaint_id + '\\nDate: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + '\\n\\nTrack at: http://127.0.0.1:8000/\\n\\nThank you,\\nCivic Pulse Team', 
        settings.DEFAULT_FROM_EMAIL, 
        [citizen_email], 
        fail_silently=False 
    ) 
    print('? Email sent to ' + citizen_email) 
    print('?? Check your inbox/spam folder') 
except Exception as e: 
    print('? Error: ' + str(e)) 

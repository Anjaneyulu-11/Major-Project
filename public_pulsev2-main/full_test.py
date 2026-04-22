import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings') 
import django 
django.setup() 
from complaints.models import Complaint 
from django.core.mail import send_mail 
from django.conf import settings 
import datetime 
 
print("="*60) 
"FULL COMPLAINT EMAIL TEST") 
print("="*60) 
 
# Simulate a real complaint 
complaint_id = f"CP-{datetime.datetime.now().strftime('%Y%m%d')}-ABC123" 
citizen_email = "227r1a05j1@cmrtc.ac.in"  # Change to your real email 
 
try: 
    send_mail( 
        subject=f'Complaint Registered - ID: {complaint_id}', 
        message=f'''Dear Test User, 
ECHO is on.
Your complaint has been registered. 
ECHO is on.
?? Complaint ID: {complaint_id} 
?? Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")} 
?? Category: Municipal Issues 
?? Location: Test City 
ECHO is on.
You can track your complaint using this ID at: 
http://127.0.0.1:8000/track-complaint/ 
ECHO is on.
Thank you, 
Civic Pulse Team''', 
        from_email=settings.DEFAULT_FROM_EMAIL, 
        recipient_list=[citizen_email], 
        fail_silently=False 
    ) 
    print(f'? Email sent to {citizen_email}') 
    print(f'?? Subject: Complaint Registered - ID: {complaint_id}') 
    print('?? Check your email inbox now!') 
except Exception as e: 
    print(f'? Error: {e}') 

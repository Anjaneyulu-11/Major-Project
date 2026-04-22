import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings') 
import django 
django.setup() 
from django.core.mail import send_mail 
from django.conf import settings 
import datetime 
 
print("Testing for DIFFERENT CITIZENS") 
print("="*60) 
 
# Different citizen emails (like in real system) 
citizen_emails = [ 
    '227r1a05j1@cmrtc.ac.in',      # Student 1 
    'student2@college.edu',         # Student 2 
    'resident@citymail.com',        # City resident 
    'user@gmail.com',               # Gmail user 
] 
 
for i, email in enumerate(citizen_emails): 
    complaint_id = f'CP-20251230-{chr(65+i)}123'  # Different IDs 
    print(f'Citizen {i+1}: {email}') 
    print(f'  Complaint ID: {complaint_id}') 
 
    try: 
        send_mail( 
            f'Complaint Registered - ID: {complaint_id}', 
            f'Your complaint ID is {complaint_id}. Track at: http://127.0.0.1:8000/', 
            settings.DEFAULT_FROM_EMAIL, 
            [email],  #  Each citizen gets their own email 
            fail_silently=False 
        ) 
        print(f'  ? Email sent to this citizen') 
    except Exception as e: 
        print(f'  ? Failed: {e}') 
    print() 

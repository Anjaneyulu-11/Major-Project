# force_debug.py 
import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings') 
 
import django 
django.setup() 
 
print("="*80) 
print("?? FORCE DEBUG - TESTING COMPLAINT SUBMISSION") 
print("="*80) 
 
from complaints.models import Complaint 
count = Complaint.objects.count() 
print(f"1?? Complaints in DB: {count}") 
 
try: 
    complaint = Complaint.objects.create( 
        name='Force Test', 
        email='force@test.com', 
        category='Test', 
        details='Force test complaint', 
        city='Test City', 
        status='Submitted' 
    ) 
    print(f"2?? Complaint created: {complaint.complaint_id}") 
except Exception as e: 
    print(f"2?? Error creating complaint: {e}") 
 
from django.core.mail import send_mail 
from django.conf import settings 
 
print(f"3?? Email Backend: {settings.EMAIL_BACKEND}") 
 
try: 
    send_mail( 
        subject='FORCE TEST EMAIL', 
        message='This should appear in terminal!', 
        from_email=settings.DEFAULT_FROM_EMAIL, 
        recipient_list=['test@example.com'], 
        fail_silently=False, 
    ) 
    print("? Email sent! Check BELOW for email content ") 
except Exception as e: 
    print(f"? Email error: {e}") 
 
print("="*80) 
print("? Force debug complete") 

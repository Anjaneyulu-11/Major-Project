import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings') 
import django 
django.setup() 
from django.core.mail import send_mail 
from django.conf import settings 
print("="*70) 
print("?? EMAIL CONFIGURATION TEST") 
print("="*70) 
print(f"Email Backend: {settings.EMAIL_BACKEND}") 
print(f"From Email: {settings.DEFAULT_FROM_EMAIL}") 
try: 
    send_mail( 
        subject='Public Pulse - Test Email', 
        message='If you see this in terminal, email system works!', 
        from_email=settings.DEFAULT_FROM_EMAIL, 
        recipient_list=['test@example.com'], 
        fail_silently=False, 
    ) 
    print("\n? SUCCESS: Email sent!") 
    print("?? Since you're using console backend, email appears below ") 
except Exception as e: 
    print(f"\n? ERROR: {e}") 

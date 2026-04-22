# test_email.py
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 50)
print("Testing Email Configuration")
print("=" * 50)
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print("=" * 50)

try:
    # Test with a real email or use a test one
    recipient_email = "your-email@gmail.com"  # ← CHANGE THIS TO YOUR EMAIL
    
    print(f"Sending test email to: {recipient_email}")
    
    send_mail(
        subject='✅ Test Email from Public Pulse',
        message='This is a test email to verify email configuration.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )
    print("\n" + "=" * 50)
    print("✅ Test email sent successfully!")
    print("📧 Check your console/terminal for email output")
    print("=" * 50)
except Exception as e:
    print("\n" + "=" * 50)
    print(f"❌ Error sending test email:")
    print(f"Error: {str(e)}")
    print("=" * 50)
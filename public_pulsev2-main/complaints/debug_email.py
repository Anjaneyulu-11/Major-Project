# debug_email.py
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from complaints.models import Complaint
from complaints.forms import ComplaintForm

print("=" * 70)
print("🔍 PUBLIC PULSE - EMAIL DEBUG TOOL")
print("=" * 70)

# 1. Check settings
print("\n1️⃣ SETTINGS CHECK:")
print("-" * 40)
print(f"EMAIL_BACKEND:     {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST:        {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
print(f"EMAIL_PORT:        {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
print(f"EMAIL_USE_TLS:     {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
print(f"EMAIL_HOST_USER:   {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"DEBUG:             {settings.DEBUG}")
print("-" * 40)

# 2. Test simple email
print("\n2️⃣ SIMPLE EMAIL TEST:")
print("-" * 40)
try:
    send_mail(
        subject='Test Email - Public Pulse',
        message='This is a simple test email.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['test@example.com'],  # Change this
        fail_silently=False,
    )
    print("✅ Simple email sent successfully!")
    print("📝 If using console backend, check terminal for email output.")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
    print(f"   Error type: {type(e).__name__}")

# 3. Check if console backend is working
if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
    print("\n3️⃣ CONSOLE BACKEND DETECTED:")
    print("-" * 40)
    print("ℹ️  Emails will be printed to terminal, not actually sent.")
    print("   To send real emails, change to SMTP backend in settings.py")
else:
    print("\n3️⃣ SMTP BACKEND DETECTED")
    print("-" * 40)

# 4. Test complaint form submission simulation
print("\n4️⃣ TEST COMPLAINT FORM SIMULATION:")
print("-" * 40)
try:
    # Create a test complaint
    test_data = {
        'name': 'Test User',
        'email': 'test@example.com',  # Change to your email
        'phone': '1234567890',
        'category': 'Municipal Issues',
        'sub_category': 'Road Repair',
        'details': 'There is a big pothole on Main Street',
        'city': 'Test City',
    }
    
    form = ComplaintForm(data=test_data)
    if form.is_valid():
        print("✅ Form validation passed")
        complaint = form.save(commit=False)
        complaint.status = 'Submitted'
        complaint.save()
        print(f"✅ Test complaint created: ID={complaint.complaint_id}")
        print(f"   Email: {complaint.email}")
    else:
        print("❌ Form validation failed")
        print(f"   Errors: {form.errors}")
except Exception as e:
    print(f"❌ Error: {e}")

# 5. Direct email test with real complaint
print("\n5️⃣ DIRECT COMPLAINT EMAIL TEST:")
print("-" * 40)
from complaints.views import send_confirmation_email
try:
    # Get latest complaint or create one
    latest_complaint = Complaint.objects.last()
    if latest_complaint:
        print(f"Testing with complaint: {latest_complaint.complaint_id}")
        print(f"Email: {latest_complaint.email}")
        
        success = send_confirmation_email(latest_complaint)
        if success:
            print("✅ Complaint email function worked!")
        else:
            print("❌ Complaint email function failed")
    else:
        print("ℹ️ No complaints in database to test with")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("🛠️  TROUBLESHOOTING GUIDE")
print("=" * 70)

if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
    print("\n📝 For Console Backend:")
    print("   1. Submit a complaint through your form")
    print("   2. Check the terminal/CMD where Django is running")
    print("   3. You should see email content printed there")
    print("   4. This proves email logic is working")
else:
    print("\n📝 For SMTP Backend (Gmail/Outlook):")
    print("   1. Make sure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct")
    print("   2. For Gmail: Use App Password, not regular password")
    print("   3. Enable 2-Step Verification first")
    print("   4. Check spam folder")

print("\n" + "=" * 70)
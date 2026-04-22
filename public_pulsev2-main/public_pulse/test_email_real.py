# test_email_real.py
import os
import django
import sys
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public_pulse.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 70)
print("PUBLIC PULSE - EMAIL CONFIGURATION TEST")
print("=" * 70)

# Display current email configuration
print("\n📧 CURRENT EMAIL SETTINGS:")
print("-" * 40)
print(f"EMAIL_BACKEND:    {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST:       {getattr(settings, 'EMAIL_HOST', 'Not set')}")
print(f"EMAIL_PORT:       {getattr(settings, 'EMAIL_PORT', 'Not set')}")
print(f"EMAIL_USE_TLS:    {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
print(f"EMAIL_HOST_USER:  {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
print(f"DEFAULT_FROM:     {settings.DEFAULT_FROM_EMAIL}")
print(f"DEBUG:            {settings.DEBUG}")
print("-" * 40)

# Get current datetime for email
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Get recipient email
print("\n👤 Enter recipient email address:")
print("(Use your own email to test)")
recipient_email = input("Email: ").strip()

if not recipient_email:
    print("❌ No email provided. Exiting.")
    sys.exit(1)

print("\n" + "=" * 70)
print("🚀 SENDING TEST EMAIL...")
print("=" * 70)

try:
    # Send test email
    send_mail(
        subject='✅ Public Pulse - Test Email Configuration',
        message=f'''Hello,

This is a test email from the Public Pulse Complaint System.

If you receive this email, it means your email configuration is working correctly!

Technical Details:
- Backend: {settings.EMAIL_BACKEND}
- Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}:{getattr(settings, 'EMAIL_PORT', 'Not set')}
- From: {settings.DEFAULT_FROM_EMAIL}
- To: {recipient_email}
- Date: {current_datetime}

You can now submit complaints and receive Complaint IDs via email.

Best regards,
Public Pulse Team
''',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        html_message=f'''<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .success {{ color: #28a745; font-weight: bold; }}
        .details {{ background: white; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #007bff; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Public Pulse Test Email</h1>
            <p>Email Configuration Test</p>
        </div>
        <div class="content">
            <h2>Congratulations! 🎉</h2>
            <p>Your email configuration is working correctly!</p>
            
            <div class="details">
                <h3>📋 Technical Details:</h3>
                <p><strong>Email Backend:</strong> {settings.EMAIL_BACKEND}</p>
                <p><strong>SMTP Host:</strong> {getattr(settings, 'EMAIL_HOST', 'Not set')}:{getattr(settings, 'EMAIL_PORT', 'Not set')}</p>
                <p><strong>From Address:</strong> {settings.DEFAULT_FROM_EMAIL}</p>
                <p><strong>To Address:</strong> {recipient_email}</p>
                <p><strong>TLS Enabled:</strong> {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}</p>
                <p><strong>Debug Mode:</strong> {settings.DEBUG}</p>
            </div>
            
            <p>You can now:</p>
            <ul>
                <li>Submit complaints through the Public Pulse system</li>
                <li>Receive Complaint IDs via email</li>
                <li>Track complaint status</li>
                <li>Get updates on your complaints</li>
            </ul>
            
            <p><strong>Next Steps:</strong> Submit a test complaint to verify the complete flow.</p>
            
            <div class="footer">
                This is an automated test email from Public Pulse Complaint System.<br>
                Date: {current_datetime}<br>
                Server: Public Pulse - Complaint Management System
            </div>
        </div>
    </div>
</body>
</html>''',
        fail_silently=False,
    )
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS: Test email sent!")
    print("=" * 70)
    print("\n📬 What to check:")
    print("   1. Your email inbox")
    print("   2. Spam/Junk folder")
    print("   3. Promotions tab (Gmail)")
    print("\n⏰ It may take 1-2 minutes to arrive.")
    
    # If using console backend, provide special instructions
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("\n" + "=" * 70)
        print("ℹ️  CONSOLE EMAIL MODE DETECTED")
        print("=" * 70)
        print("\nEmails are being printed to terminal (not actually sent).")
        print("Check the terminal output above to see the email content.")
        print("\nTo send real emails, change EMAIL_BACKEND in settings.py:")
        print("1. Comment out the console backend")
        print("2. Uncomment Gmail/Outlook backend")
        print("3. Configure your email credentials")
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print("\n" + "=" * 70)
    print("❌ ERROR: Failed to send email")
    print("=" * 70)
    print(f"\nError Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    
    # Provide helpful troubleshooting
    error_msg = str(e).lower()
    
    if "authentication" in error_msg:
        print("\n🔐 AUTHENTICATION PROBLEM:")
        print("   For Gmail users:")
        print("   1. Enable 2-Step Verification")
        print("   2. Generate an 'App Password' (16 characters)")
        print("   3. Use App Password in settings.py, NOT your regular password")
        print("   Tutorial: https://support.google.com/accounts/answer/185833")
        
    elif "connection" in error_msg or "refused" in error_msg:
        print("\n🔌 CONNECTION PROBLEM:")
        print("   1. Check internet connection")
        print("   2. Verify EMAIL_HOST and EMAIL_PORT in settings.py")
        print("   3. Try port 465 instead of 587 (with SSL instead of TLS)")
        print("   4. Check firewall/antivirus blocking SMTP")
        
    elif "timeout" in error_msg:
        print("\n⏰ TIMEOUT PROBLEM:")
        print("   1. Slow internet connection")
        print("   2. SMTP server busy")
        print("   3. Try again in a few minutes")
        
    elif "smtp" in error_msg:
        print("\n📧 SMTP CONFIGURATION PROBLEM:")
        print("   1. Make sure EMAIL_BACKEND is correctly set")
        print("   2. Verify EMAIL_HOST_USER is valid")
        print("   3. Check EMAIL_HOST_PASSWORD is correct")
        print("   4. Try using console backend first: EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'")
        
    else:
        print("\n🔧 GENERAL TROUBLESHOOTING:")
        print("   1. Verify all settings in settings.py")
        print("   2. Check if email provider allows SMTP")
        print("   3. Try different email provider (Gmail recommended)")
        print("   4. Test with console backend first")
    
    print("\n📝 Current settings check:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    
    print("\n" + "=" * 70)

# Additional utility: Test email configuration
print("\n" + "=" * 70)
print("🔧 QUICK CONFIGURATION TEST")
print("=" * 70)

# Check if email settings are properly configured
try:
    # Test email connection (simplified)
    if hasattr(settings, 'EMAIL_BACKEND'):
        print(f"✓ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            print("✓ Console backend - emails will show in terminal")
        elif settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
            print("✓ SMTP backend configured")
            if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST:
                print(f"✓ SMTP Host: {settings.EMAIL_HOST}")
            else:
                print("✗ EMAIL_HOST not set")
    else:
        print("✗ EMAIL_BACKEND not configured")
        
except Exception as e:
    print(f"✗ Configuration test failed: {e}")

print("=" * 70)
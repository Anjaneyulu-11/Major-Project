# complaints/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .forms import ComplaintForm
from .models import Complaint, Notification
import uuid
import logging
import sys
import random
import string
import datetime

# Create a logger for this module
logger = logging.getLogger(__name__)

def lodge_complaint(request):
    """
    View to handle complaint submission
    """
    # ========== DEBUG SECTION ==========
    print("\n" + "="*80, file=sys.stderr)
    print("🚨 LODGE_COMPLAINT FUNCTION CALLED", file=sys.stderr)
    print(f"📱 Method: {request.method}", file=sys.stderr)
    print(f"📍 Path: {request.path}", file=sys.stderr)
    print("="*80, file=sys.stderr)
    
    if request.method == 'POST':
        print("📋 POST DATA RECEIVED:", file=sys.stderr)
        print(f"   Keys: {list(request.POST.keys())}", file=sys.stderr)
        
        # Print all form data for debugging
        for field in ['name', 'email', 'phone', 'category', 'details', 'city']:
            value = request.POST.get(field, 'NOT FOUND')
            print(f"   {field}: '{value}'", file=sys.stderr)
    
    # ========== MAIN FUNCTION LOGIC ==========
    if request.method == 'POST':
        # Create form instance with POST data and FILES
        form = ComplaintForm(request.POST, request.FILES)
        
        print(f"\n🔍 FORM CREATED", file=sys.stderr)
        
        # Validate form
        is_valid = form.is_valid()
        print(f"✅ FORM VALIDATION RESULT: {is_valid}", file=sys.stderr)
        
        if not is_valid:
            print("❌ FORM ERRORS:", file=sys.stderr)
            for field, errors in form.errors.items():
                print(f"   {field}: {errors}", file=sys.stderr)
            
            # Return form with errors
            return render(request, 'complaints/lodge_complaint.html', {'form': form})
        
        print("✅✅✅ FORM IS VALID - PROCESSING...", file=sys.stderr)
        
        try:
            # Get cleaned data
            complaint_data = form.cleaned_data
            print(f"📝 Cleaned data keys: {list(complaint_data.keys())}", file=sys.stderr)
            
            # Print cleaned data for debugging
            for key, value in complaint_data.items():
                if key != 'attachments':  # Don't print file objects
                    print(f"   {key}: {value}", file=sys.stderr)
            
            # Perform AI analysis
            ai_analysis = perform_ai_analysis(complaint_data['details'])
            print(f"🤖 AI Analysis:", file=sys.stderr)
            print(f"   Category: {ai_analysis['category']}", file=sys.stderr)
            
            # Create complaint instance but don't save yet
            complaint = form.save(commit=False)
            
            # Add AI analysis fields
            complaint.ai_category = ai_analysis['category']
            complaint.ai_priority = ai_analysis['priority']
            complaint.ai_sentiment = ai_analysis['sentiment']
            complaint.ai_confidence = ai_analysis['confidence']
            
            # Set default status
            complaint.status = 'Submitted'
            
            # If user is logged in, associate with user
            if request.user.is_authenticated:
                complaint.user = request.user
            
            # 🚨 DEBUG BEFORE SAVE
            print(f"\n💾 ABOUT TO SAVE COMPLAINT:", file=sys.stderr)
            print(f"   Name: {complaint.name}", file=sys.stderr)
            print(f"   Email: {complaint.email}", file=sys.stderr)
            
            # ========== CRITICAL FIX: SAVE AND SEND EMAIL ==========
            # Save the complaint to database
            complaint.save()
            
            # ✅ Save many-to-many relationships if any
            form.save_m2m()
            
            # ✅ VERIFY SAVE
            print(f"\n✅ COMPLAINT SAVED SUCCESSFULLY!", file=sys.stderr)
            print(f"   Database ID: {complaint.id}", file=sys.stderr)
            print(f"   Readable ID: {complaint.readable_id}", file=sys.stderr)
            print(f"   Complaint ID: {complaint.complaint_id}", file=sys.stderr)
            print(f"   Email to send to: {complaint.email}", file=sys.stderr)
            
            # ========== CRITICAL: SEND EMAIL ==========
            print(f"\n📧 CALLING send_confirmation_email...", file=sys.stderr)
            email_sent = send_confirmation_email(complaint)
            print(f"   Email sent result: {email_sent}", file=sys.stderr)
            
            # Store in session for success page
            request.session['last_complaint_id'] = str(complaint.readable_id)
            request.session['last_complaint_email'] = complaint.email
            request.session['email_sent'] = email_sent
            
            # Add success message
            messages.success(
                request, 
                f"✅ Complaint submitted successfully! Check your email at {complaint.email}"
            )
            
            print(f"\n🎯 REDIRECTING to success page with ID: {complaint.readable_id}", file=sys.stderr)
            
            # ✅✅✅ FIXED: Redirect to success page with readable_id
            return redirect('complaint_success', complaint_id=complaint.readable_id)
            
        except Exception as e:
            print(f"\n❌ EXCEPTION DURING COMPLAINT SAVE:", file=sys.stderr)
            print(f"   Error: {e}", file=sys.stderr)
            
            # Print full traceback
            import traceback
            traceback.print_exc(file=sys.stderr)
            
            # Add error message
            messages.error(
                request, 
                f"An error occurred while saving your complaint. Please try again."
            )
            
            # Return form with error
            return render(request, 'complaints/lodge_complaint.html', {'form': form})
    
    else:
        # GET request - show empty form
        form = ComplaintForm()
        print("📄 GET request - showing empty form", file=sys.stderr)
    
    return render(request, 'complaints/lodge_complaint.html', {'form': form})

def perform_ai_analysis(text):
    """
    Perform basic AI analysis on complaint text
    """
    lower_text = text.lower()
    
    analysis = {
        'category': 'General',
        'priority': 'Medium',
        'sentiment': 'Neutral',
        'confidence': '85%'
    }
    
    # Category detection
    categories = {
        'Municipal Issues': ['road', 'pothole', 'garbage', 'drain', 'street', 'sanitation', 'clean'],
        'Electricity': ['power', 'electricity', 'current', 'blackout', 'voltage', 'transformer', 'wire'],
        'Water Supply': ['water', 'supply', 'pipeline', 'leak', 'drainage', 'tap', 'shortage'],
        'Healthcare': ['hospital', 'doctor', 'health', 'medical', 'treatment', 'medicine', 'ambulance'],
        'Corruption': ['bribe', 'corruption', 'fraud', 'illegal', 'scam', 'money', 'bribery'],
        'Public Safety': ['police', 'safety', 'crime', 'theft', 'accident', 'dangerous', 'unsafe'],
        'Transport': ['bus', 'train', 'traffic', 'road', 'vehicle', 'transport', 'metro'],
        'Education': ['school', 'college', 'teacher', 'education', 'exam', 'admission', 'fee'],
    }
    
    for category, keywords in categories.items():
        if any(keyword in lower_text for keyword in keywords):
            analysis['category'] = category
            break
    
    # Priority detection
    if any(word in lower_text for word in ['emergency', 'urgent', 'immediate', 'critical', 'dangerous', 'serious']):
        analysis['priority'] = 'High'
    elif any(word in lower_text for word in ['minor', 'small', 'suggestion', 'whenever']):
        analysis['priority'] = 'Low'
    
    # Sentiment analysis
    if any(word in lower_text for word in ['angry', 'frustrated', 'disappointed', 'helpless', 'terrible', 'worst']):
        analysis['sentiment'] = 'Very Negative'
    elif any(word in lower_text for word in ['sad', 'worried', 'concerned', 'anxious', 'problem', 'issue']):
        analysis['sentiment'] = 'Negative'
    elif any(word in lower_text for word in ['happy', 'satisfied', 'thank', 'appreciate', 'good', 'excellent']):
        analysis['sentiment'] = 'Positive'
    elif any(word in lower_text for word in ['love', 'best', 'amazing', 'wonderful', 'perfect', 'great']):
        analysis['sentiment'] = 'Very Positive'
    
    # Confidence based on text length
    if len(text) > 200:
        analysis['confidence'] = '95%'
    elif len(text) > 100:
        analysis['confidence'] = '90%'
    elif len(text) > 50:
        analysis['confidence'] = '85%'
    else:
        analysis['confidence'] = '75%'
    
    return analysis

def send_confirmation_email(complaint):
    """
    Send email confirmation to the user with Complaint ID - FIXED VERSION
    """
    print("\n" + "="*60, file=sys.stderr)
    print("📧 ATTEMPTING TO SEND EMAIL", file=sys.stderr)
    print(f"To: {complaint.email}", file=sys.stderr)
    
    try:
        # ✅ FIXED: Use readable_id for emails (email-friendly format)
        # The complaint model now has both complaint_id and readable_id
        email_id = complaint.readable_id or complaint.complaint_id
        
        print(f"📝 Available IDs:", file=sys.stderr)
        print(f"   complaint_id: {complaint.complaint_id}", file=sys.stderr)
        print(f"   readable_id: {complaint.readable_id}", file=sys.stderr)
        print(f"   Using for email: {email_id}", file=sys.stderr)
        
        subject = f'Complaint Registered - ID: {email_id}'
        
        message = f"""Dear {complaint.name},

Your complaint has been registered!

COMPLAINT ID: {email_id}

Track your complaint at: http://127.0.0.1:8000/complaints/track/

You can use either:
- Your Complaint ID: {email_id}
- Or your email: {complaint.email}

Thank you,
Public Pulse Team"""
        
        print(f"Subject: {subject}", file=sys.stderr)
        print(f"Message: {message[:100]}...", file=sys.stderr)
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[complaint.email],
            fail_silently=False,
        )
        
        print("✅ EMAIL SENT SUCCESSFULLY (to console)", file=sys.stderr)
        print("="*60, file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"❌ EMAIL ERROR: {e}", file=sys.stderr)
        print("="*60, file=sys.stderr)
        return False

def complaint_success(request, complaint_id):
    """
    Success page after complaint submission
    """
    try:
        print(f"\n🎉 SUCCESS PAGE CALLED:", file=sys.stderr)
        print(f"   Complaint ID from URL: {complaint_id}", file=sys.stderr)
        
        # Try to find complaint by readable_id first
        complaint = Complaint.objects.filter(readable_id=complaint_id).first()
        
        # If not found by readable_id, try complaint_id
        if not complaint:
            complaint = Complaint.objects.filter(complaint_id=complaint_id).first()
        
        # If still not found, try partial match
        if not complaint:
            complaint = Complaint.objects.filter(
                complaint_id__icontains=complaint_id
            ).first()
        
        if not complaint:
            print(f"❌ Complaint not found in database", file=sys.stderr)
            raise Complaint.DoesNotExist
        
        print(f"✅ Complaint found:", file=sys.stderr)
        print(f"   Name: {complaint.name}", file=sys.stderr)
        print(f"   Email: {complaint.email}", file=sys.stderr)
        print(f"   Readable ID: {complaint.readable_id}", file=sys.stderr)
        print(f"   Complaint ID: {complaint.complaint_id}", file=sys.stderr)
        
        # Get email status from session
        email_sent = request.session.get('email_sent', False)
        
        # ✅ FIXED: Use readable_id for display
        context = {
            'complaint': complaint,
            'email_sent': email_sent,
            'readable_id': complaint.readable_id or complaint.complaint_id
        }
        
        return render(request, 'complaints/complaint_success.html', context)
        
    except Complaint.DoesNotExist:
        print(f"❌ COMPLAINT NOT FOUND", file=sys.stderr)
        messages.error(request, "Complaint not found! Please check your Complaint ID.")
        return redirect('lodge_complaint')
    except Exception as e:
        print(f"❌ ERROR IN SUCCESS PAGE:", file=sys.stderr)
        print(f"   Error: {e}", file=sys.stderr)
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('lodge_complaint')

def track_complaint(request):
    """
    Track complaint status - FIXED VERSION
    """
    print(f"\n🔍 TRACK COMPLAINT CALLED:", file=sys.stderr)
    print(f"   Method: {request.method}", file=sys.stderr)
    
    if request.method == 'POST':
        search_query = request.POST.get('complaint_id', '').strip()
        print(f"   Search query: '{search_query}'", file=sys.stderr)
        
        if not search_query:
            messages.error(request, "Please enter a Complaint ID, name, or email.")
            return render(request, 'complaints/track_complaint.html')
        
        try:
            # Try multiple search methods
            complaint = None
            
            # Method 1: Search by readable_id (CP-XXXXXXX format)
            complaint = Complaint.objects.filter(
                readable_id__iexact=search_query
            ).first()
            if complaint:
                print(f"✅ Found by readable_id: {complaint.readable_id}", file=sys.stderr)
            
            # Method 2: Search by complaint_id (CP-YYYYMMDD-XXXXXX format)
            if not complaint:
                complaint = Complaint.objects.filter(
                    complaint_id__iexact=search_query
                ).first()
                if complaint:
                    print(f"✅ Found by complaint_id: {complaint.complaint_id}", file=sys.stderr)
            
            # Method 3: Search by partial match (without CP- prefix)
            if not complaint and search_query.startswith('CP-'):
                search_part = search_query.replace('CP-', '').strip()
                # Try readable_id first
                complaint = Complaint.objects.filter(
                    readable_id__icontains=search_part
                ).first()
                # Then try complaint_id
                if not complaint:
                    complaint = Complaint.objects.filter(
                        complaint_id__icontains=search_part
                    ).first()
                if complaint:
                    print(f"✅ Found by partial match", file=sys.stderr)
            
            # Method 4: Search by email
            if not complaint and '@' in search_query:
                complaint = Complaint.objects.filter(
                    email__iexact=search_query
                ).order_by('-created_at').first()
                if complaint:
                    print(f"✅ Found by email", file=sys.stderr)
            
            # Method 5: Search by name
            if not complaint:
                complaint = Complaint.objects.filter(
                    name__icontains=search_query
                ).order_by('-created_at').first()
                if complaint:
                    print(f"✅ Found by name", file=sys.stderr)
            
            # Method 6: Search by UUID
            if not complaint and len(search_query) > 20:
                try:
                    uuid_obj = uuid.UUID(search_query)
                    complaint = Complaint.objects.filter(
                        uuid_id=uuid_obj
                    ).first()
                    if complaint:
                        print(f"✅ Found by UUID", file=sys.stderr)
                except ValueError:
                    pass  # Not a valid UUID
            
            if not complaint:
                print(f"❌ No complaint found for: '{search_query}'", file=sys.stderr)
                messages.error(request, f"No complaint found for '{search_query}'. Please check and try again.")
                return render(request, 'complaints/track_complaint.html', {
                    'error': True,
                    'search_query': search_query
                })
            else:
                print(f"✅ Complaint found:", file=sys.stderr)
                print(f"   Name: {complaint.name}", file=sys.stderr)
                print(f"   Email: {complaint.email}", file=sys.stderr)
                print(f"   Readable ID: {complaint.readable_id}", file=sys.stderr)
                print(f"   Complaint ID: {complaint.complaint_id}", file=sys.stderr)
                print(f"   Status: {complaint.status}", file=sys.stderr)
                
                # ✅ FIXED: Show results on a separate page
                return render(request, 'complaints/track_result.html', {
                    'complaint': complaint,
                    'search_query': search_query,
                    'success': True
                })
                
        except Exception as e:
            print(f"❌ Error tracking complaint:", file=sys.stderr)
            print(f"   Error: {e}", file=sys.stderr)
            messages.error(request, "Error processing your request. Please try again.")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return render(request, 'complaints/track_complaint.html', {
                'error': True,
                'search_query': search_query
            })
    
    # GET request - show tracking form
    return render(request, 'complaints/track_complaint.html')

# ========== KEEP YOUR EXISTING TEST FUNCTIONS (unchanged) ==========

def quick_email_test(request):
    """Quick email test"""
    from django.http import HttpResponse
    
    html = """
    <h1>Email Test</h1>
    <p>Testing email configuration...</p>
    """
    
    print("\n" + "="*60, file=sys.stderr)
    print("🧪 QUICK EMAIL TEST STARTED", file=sys.stderr)
    
    try:
        # Test 1: Check settings
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}", file=sys.stderr)
        print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}", file=sys.stderr)
        
        # Test 2: Send a test email
        print("\n📤 Sending test email...", file=sys.stderr)
        
        send_mail(
            subject='QUICK TEST - Public Pulse',
            message='This is a quick test email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        
        print("✅ EMAIL SENT TO CONSOLE!", file=sys.stderr)
        html += "<p style='color: green;'>✅ Email sent! Check terminal.</p>"
        
    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        html += f"<p style='color: red;'>❌ Error: {e}</p>"
    
    print("="*60, file=sys.stderr)
    
    return HttpResponse(html)

def test_email_view(request):
    """Simple view to test email functionality"""
    print(f"\n📧 TEST EMAIL VIEW CALLED", file=sys.stderr)
    
    try:
        send_mail(
            subject='Test Email from Public Pulse',
            message='This is a test email from the complaints system.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        print(f"✅ Test email sent", file=sys.stderr)
        html = "<h1>Test Email</h1><p>✅ Test email sent! Check terminal.</p>"
    except Exception as e:
        print(f"❌ Test email failed:", file=sys.stderr)
        print(f"   Error: {e}", file=sys.stderr)
        html = f"<h1>Test Email</h1><p>❌ Failed: {e}</p>"
    
    from django.http import HttpResponse
    return HttpResponse(html)

def direct_email_test(request):
    """Direct test endpoint for email"""
    print(f"\n📧 DIRECT EMAIL TEST CALLED", file=sys.stderr)
    
    if request.method == 'GET':
        try:
            send_mail(
                subject='DIRECT TEST - Public Pulse Email System',
                message='If you receive this, your email system is working!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['test@example.com'],
                fail_silently=False,
            )
            print(f"✅ Direct test email sent", file=sys.stderr)
            html = "<h1>Direct Email Test</h1><p>✅ Email sent! Check terminal.</p>"
        except Exception as e:
            print(f"❌ Direct test email failed:", file=sys.stderr)
            print(f"   Error: {e}", file=sys.stderr)
            html = f"<h1>Direct Email Test</h1><p>❌ Failed: {e}</p>"
    
    from django.http import HttpResponse
    return HttpResponse(html)

def emergency_debug(request):
    """Emergency debugging endpoint"""
    print("\n" + "="*80, file=sys.stderr)
    print("🚨 EMERGENCY DEBUG FUNCTION CALLED", file=sys.stderr)
    print("="*80, file=sys.stderr)
    
    # Test 1: Check database
    from .models import Complaint
    count = Complaint.objects.count()
    print(f"📊 Complaints in database: {count}", file=sys.stderr)
    
    # List recent complaints
    recent = Complaint.objects.order_by('-created_at')[:5]
    print(f"📋 Recent complaints:", file=sys.stderr)
    for comp in recent:
        print(f"   • ID: {comp.id}", file=sys.stderr)
        print(f"     Readable ID: {comp.readable_id}", file=sys.stderr)
        print(f"     Complaint ID: {comp.complaint_id}", file=sys.stderr)
        print(f"     UUID ID: {comp.uuid_id}", file=sys.stderr)
        print(f"     Name: {comp.name} - Email: {comp.email}", file=sys.stderr)
        print(f"     Status: {comp.status}", file=sys.stderr)
        print(f"     ---", file=sys.stderr)
    
    # Create a simple response
    html_content = f"""
    <h1>Emergency Debug</h1>
    <p>Check terminal for debug output.</p>
    <p>Complaints in database: {count}</p>
    <h3>Recent complaints:</h3>
    <ul>
    {"".join([f'<li>ID: {comp.id}<br>Readable: {comp.readable_id}<br>Complaint: {comp.complaint_id}<br>UUID: {comp.uuid_id}<br>Name: {comp.name}<br>Email: {comp.email}<br>Status: {comp.status}</li><hr>' for comp in recent])}
    </ul>
    """
    
    from django.http import HttpResponse
    return HttpResponse(html_content)

def direct_test_complaint(request):
    """Direct test complaint submission"""
    print(f"\n🧪 DIRECT TEST COMPLAINT CALLED", file=sys.stderr)
    
    if request.method == 'POST':
        from .forms import ComplaintForm
        
        test_data = {
            'name': 'Direct Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'category': 'Municipal Issues',
            'details': 'Direct test complaint submission for debugging',
            'city': 'Test City',
        }
        
        print(f"🧪 Test data:", file=sys.stderr)
        for key, value in test_data.items():
            print(f"   {key}: {value}", file=sys.stderr)
        
        form = ComplaintForm(data=test_data)
        
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.status = 'Submitted'
            complaint.save()
            
            print(f"✅ Test complaint saved:", file=sys.stderr)
            print(f"   ID: {complaint.id}", file=sys.stderr)
            print(f"   Readable ID: {complaint.readable_id}", file=sys.stderr)
            print(f"   Complaint ID: {complaint.complaint_id}", file=sys.stderr)
            print(f"   UUID ID: {complaint.uuid_id}", file=sys.stderr)
            
            # Send email
            email_sent = send_confirmation_email(complaint)
            
            html = f"""
            <h1>Direct Test Result</h1>
            <p>✅ Test complaint saved!</p>
            <p>Database ID: {complaint.id}</p>
            <p>Readable ID: {complaint.readable_id}</p>
            <p>Complaint ID: {complaint.complaint_id}</p>
            <p>UUID: {complaint.uuid_id}</p>
            <p>Email sent: {'✅ Yes' if email_sent else '❌ No'}</p>
            """
        else:
            print(f"❌ Test form invalid:", file=sys.stderr)
            errors = "<br>".join([f"{field}: {error}" for field, error in form.errors.items()])
            html = f"""
            <h1>Direct Test Result</h1>
            <p>❌ Form invalid!</p>
            <p>Errors: {errors}</p>
            """
    
    else:
        html = """
        <h1>Direct Test Complaint</h1>
        <form method="post">
            <button type="submit">Run Direct Test</button>
        </form>
        """
    
    from django.http import HttpResponse
    return HttpResponse(html)

def test_email_configuration(request):
    """Test email configuration"""
    from django.http import HttpResponse
    
    print("\n" + "="*60, file=sys.stderr)
    print("🧪 TEST EMAIL CONFIGURATION", file=sys.stderr)
    print("="*60, file=sys.stderr)
    
    try:
        send_mail(
            subject='Test Email Configuration',
            message='This is a test email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],
            fail_silently=False,
        )
        
        html = "<h1>Email Test</h1><p>✅ Email sent to console!</p>"
    except Exception as e:
        html = f"<h1>Email Test</h1><p>❌ Error: {e}</p>"
    
    return HttpResponse(html)

def test_send_to_user(request):
    """Test sending to a specific user email"""
    from django.http import HttpResponse
    
    # Test sending to YOUR email
    test_email = 'mulkalanjaneyulu@gmail.com'
    
    print("\n" + "="*60, file=sys.stderr)
    print("🧪 TEST SEND TO USER EMAIL", file=sys.stderr)
    print(f"   Sending to: {test_email}", file=sys.stderr)
    print("="*60, file=sys.stderr)
    
    try:
        result = send_mail(
            subject='TEST - Public Pulse System',
            message='This is a test email from Public Pulse.\n\nIf you receive this, email system is working correctly!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        print(f"✅ Email sent! Result: {result}", file=sys.stderr)
        print("="*60, file=sys.stderr)
        
        html = f"""
        <h1>✅ Test Email Sent!</h1>
        <p><strong>Sent to:</strong> {test_email}</p>
        <p><strong>From:</strong> {settings.DEFAULT_FROM_EMAIL}</p>
        <p><strong>Check:</strong> Your inbox AND spam folder!</p>
        <p><strong>Result:</strong> {result} email(s) sent</p>
        <hr>
        <p><a href="/complaints/lodge/">Go to Complaint Form</a></p>
        """
        
    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        print("="*60, file=sys.stderr)
        
        html = f"""
        <h1>❌ Email Test Failed</h1>
        <p><strong>Error:</strong> {e}</p>
        <p><strong>Check:</strong> Your email settings in settings.py</p>
        <p><strong>Make sure:</strong> You're using App Password for Gmail</p>
        <hr>
        <p><a href="/complaints/lodge/">Go to Complaint Form</a></p>
        """
    
    return HttpResponse(html)


# ==========================================
# NOTIFICATION VIEWS
# ==========================================

def notifications_list(request):
    """View to display all notifications for logged-in user"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    from django.core.paginator import Paginator
    from .models import Notification
    
    # Get all notifications for this user, ordered by newest first
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unread count
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'notifications': page_obj,
        'unread_count': unread_count,
    }
    
    return render(request, 'complaints/notifications_list.html', context)


def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    from .models import Notification
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    if request.method == 'POST':
        notification.is_read = True
        notification.save()
        
        # Redirect to referrer or notifications page
        return redirect(request.POST.get('next', 'complaints:notifications_list'))
    
    return redirect('complaints:notifications_list')


def get_unread_count(request):
    """AJAX endpoint to get unread notification count"""
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0})
    
    from .models import Notification
    from django.http import JsonResponse
    
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


def mark_all_notifications_read(request):
    """Mark all notifications as read for the logged-in user"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    from .models import Notification
    
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('complaints:notifications_list')
    
    return redirect('complaints:notifications_list')

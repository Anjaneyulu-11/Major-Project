# landing_page/views.py - MODIFIED VERSION WITH 3-WAY LOGIN
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
import json
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
import uuid
import random
from django.core.mail import send_mail
from django.apps import apps  # ADDED for safe model access
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

# Import models
from complaints.models import Complaint

# Import public_admin models
from public_admin.models import DepartmentUser, Department

# ========== HELPER FUNCTIONS ==========

def get_complaint_model():
    """Safely get the Complaint model to avoid circular imports"""
    try:
        return apps.get_model('landing_page', 'Complaint')
    except:
        # Fallback to simple model for testing
        class SimpleComplaint:
            """Simple Complaint model for testing"""
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
                if not hasattr(self, 'id'):
                    self.id = random.randint(1000, 9999)
                if not hasattr(self, 'complaint_id'):
                    self.complaint_id = f"COMP-{random.randint(1000, 9999)}"
                if not hasattr(self, 'created_at'):
                    self.created_at = timezone.now()
                if not hasattr(self, 'status'):
                    self.status = 'Pending'
                if not hasattr(self, 'priority'):
                    self.priority = 'Medium'

            def save(self):
                pass

        # Simple manager
        class ComplaintManager:
            _instances = []

            def create(self, **kwargs):
                obj = SimpleComplaint(**kwargs)
                self._instances.append(obj)
                return obj

            def filter(self, **kwargs):
                filtered = []
                for obj in self._instances:
                    match = True
                    for key, value in kwargs.items():
                        if key == 'user':
                            continue
                        if getattr(obj, key, None) != value:
                            match = False
                            break
                    if match:
                        filtered.append(obj)
                return filtered

            def all(self):
                return self._instances

            def count(self):
                return len(self._instances)

            def get(self, **kwargs):
                for obj in self._instances:
                    match = True
                    for key, value in kwargs.items():
                        if getattr(obj, key, None) != value:
                            match = False
                            break
                    if match:
                        return obj
                raise Exception("Complaint not found")

        Complaint = type('Complaint', (), {'objects': ComplaintManager()})()

        for i in range(1, 6):
            Complaint.objects.create(
                id=i,
                complaint_id=f"COMP-TEST{str(i).zfill(3)}",
                title=f"Test Complaint {i}",
                description=f"This is test complaint number {i}",
                category=['Municipal Issues', 'Electricity', 'Water Supply'][i % 3],
                status=['Pending', 'In Progress', 'Resolved'][i % 3],
                priority=['Low', 'Medium', 'High'][i % 3],
                created_at=timezone.now() - timedelta(days=i)
            )

        return Complaint

def perform_ai_analysis(complaint):
    """Perform AI analysis on complaint"""
    try:
        details = getattr(complaint, 'description', '') or getattr(complaint, 'details', '')
        details_lower = details.lower() if details else ""

        positive_words = ['good', 'thanks', 'helpful', 'appreciate', 'excellent']
        negative_words = ['bad', 'poor', 'terrible', 'angry', 'frustrated']

        positive_count = sum(1 for word in positive_words if word in details_lower)
        negative_count = sum(1 for word in negative_words if word in details_lower)

        if positive_count > negative_count:
            sentiment = 'Positive'
        elif negative_count > positive_count:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        urgent_keywords = ['urgent', 'emergency', 'immediate', 'critical']
        priority_keywords = ['high', 'important', 'serious']

        is_urgent = any(keyword in details_lower for keyword in urgent_keywords)
        has_priority = any(keyword in details_lower for keyword in priority_keywords)

        if is_urgent:
            priority = 'High'
        elif has_priority:
            priority = 'Medium'
        else:
            priority = 'Low'

        complaint.priority = priority
        complaint.sentiment = sentiment
        complaint.ai_confidence = 85.5

        return {
            'priority': priority,
            'sentiment': sentiment,
            'confidence': 85.5
        }

    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {
            'priority': 'Medium',
            'sentiment': 'Neutral',
            'confidence': 0.0
        }

# ========== AUTHENTICATION VIEWS ==========

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()

        errors = []
        if not username or not email or not password:
            errors.append('All required fields must be filled!')
        if password != confirm_password:
            errors.append('Passwords do not match!')
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists!')
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered!')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters!')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'landing_page/register.html', {'form_data': request.POST})

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            login(request, user)
            messages.success(request, f'🎉 Registration successful! Welcome to Public Pulse.')
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'landing_page/register.html', {'form_data': request.POST})

    return render(request, 'landing_page/register.html')

def user_login(request):
    """User login with 3-way system (Citizen, Admin, Department)"""
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')
        else:
            return redirect('citizen_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user_type = request.POST.get('user_type', 'citizen')

        if not username or not password:
            messages.error(request, 'Please enter both username and password')
            return render(request, 'landing_page/login.html')

        if user_type == 'department':
            if username == 'department123' and password == 'department123':
                request.session['department_auth'] = True
                messages.success(request, 'Welcome Department Admin')
                return redirect('department_portal')
            else:
                messages.error(request, 'Invalid department credentials')
                return render(request, 'landing_page/login.html', {'user_type': 'department'})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user_type == 'admin':
                if user.is_staff or user.is_superuser:
                    login(request, user)
                    messages.success(request, f'Welcome Admin {user.username}!')
                    return redirect('/pulse_admin/')
                else:
                    messages.error(request, 'You do not have admin privileges')
                    return render(request, 'landing_page/login.html', {'username': username, 'user_type': user_type})
            else:
                if user.is_staff or user.is_superuser:
                    messages.warning(request, 'Admin users should use the Admin login option')
                    return render(request, 'landing_page/login.html', {'username': username, 'user_type': 'admin'})
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', '/')
                if next_url == '/':
                    return redirect('citizen_dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'landing_page/login.html')

def user_logout(request):
    """User logout"""
    logout(request)
    request.session.pop('department_auth', None)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

def department_portal(request):
    """Department portal - show all departments as cards"""
    if not request.session.get('department_auth'):
        messages.error(request, 'Please login as Department first')
        return redirect('login')
    
    try:
        departments = Department.objects.exclude(slug__isnull=True).exclude(slug="").filter(is_active=True).order_by('name')
    except:
        departments = []
    
    return render(request, 'landing_page/department_portal.html', {'departments': departments})

def department_login(request, dept_slug):
    """Department-specific login with captcha"""
    if request.session.get(f'dept_{dept_slug}_auth'):
        return redirect('department_dashboard', dept_slug=dept_slug)
    
    try:
        department = Department.objects.get(slug=dept_slug, is_active=True)
    except Department.DoesNotExist:
        messages.error(request, 'Department not found')
        return redirect('department_portal')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        captcha_value = request.POST.get('captcha', '').strip()
        
        if not username or not password or not captcha_value:
            messages.error(request, 'Please fill all fields')
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            request.session[f'captcha_a_{dept_slug}'] = a
            request.session[f'captcha_b_{dept_slug}'] = b
            return render(request, 'landing_page/department_login.html', {
                'department': department,
                'captcha_a': a,
                'captcha_b': b,
            })
        
        try:
            a = int(request.session.get(f'captcha_a_{dept_slug}', 0))
            b = int(request.session.get(f'captcha_b_{dept_slug}', 0))
        except:
            a = b = 0
        
        if not captcha_value.isdigit() or int(captcha_value) != (a + b):
            messages.error(request, 'Invalid captcha answer')
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            request.session[f'captcha_a_{dept_slug}'] = a
            request.session[f'captcha_b_{dept_slug}'] = b
            return render(request, 'landing_page/department_login.html', {
                'department': department,
                'captcha_a': a,
                'captcha_b': b,
            })
        
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            if username == 'department123' and password == 'department123':
                request.session[f'dept_{dept_slug}_auth'] = True
                request.session['current_department'] = dept_slug
                messages.success(request, f'Welcome to {department.name}')
                return redirect('department_dashboard', dept_slug=dept_slug)
            else:
                messages.error(request, 'Invalid credentials')
                a = random.randint(2, 9)
                b = random.randint(2, 9)
                request.session[f'captcha_a_{dept_slug}'] = a
                request.session[f'captcha_b_{dept_slug}'] = b
                return render(request, 'landing_page/department_login.html', {
                    'department': department,
                    'captcha_a': a,
                    'captcha_b': b,
                })
        
        try:
            dept_user = DepartmentUser.objects.get(user=user, department=department, is_active=True)
            login(request, user)
            request.session[f'dept_{dept_slug}_auth'] = True
            request.session['current_department'] = dept_slug
            messages.success(request, f'Welcome {user.username}')
            return redirect('department_dashboard', dept_slug=dept_slug)
        except:
            messages.error(request, 'Unauthorized for this department')
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            request.session[f'captcha_a_{dept_slug}'] = a
            request.session[f'captcha_b_{dept_slug}'] = b
            return render(request, 'landing_page/department_login.html', {
                'department': department,
                'captcha_a': a,
                'captcha_b': b,
            })
    
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    request.session[f'captcha_a_{dept_slug}'] = a
    request.session[f'captcha_b_{dept_slug}'] = b
    
    return render(request, 'landing_page/department_login.html', {
        'department': department,
        'captcha_a': a,
        'captcha_b': b,
    })

def department_dashboard(request, dept_slug):
    """Department dashboard - show complaints for logged-in department"""
    if not request.session.get(f'dept_{dept_slug}_auth'):
        messages.error(request, 'Please login to access this dashboard')
        return redirect('department_login', dept_slug=dept_slug)
    
    try:
        department = Department.objects.get(slug=dept_slug, is_active=True)
    except Department.DoesNotExist:
        messages.error(request, 'Department not found')
        return redirect('department_portal')
    
    try:
        complaints = Complaint.objects.filter(department=department).order_by('-created_at')
        total_complaints = complaints.count()
        pending_complaints = complaints.filter(status='Submitted').count()
        in_progress = complaints.filter(status='In Progress').count()
        resolved = complaints.filter(status='Resolved').count()
    except Exception as e:
        complaints = []
        total_complaints = pending_complaints = in_progress = resolved = 0
    
    if request.method == 'POST':
        action = request.POST.get('action')
        complaint_id = request.POST.get('complaint_id')
        
        if action == 'update_status' and complaint_id:
            try:
                new_status = request.POST.get('status')
                complaint = Complaint.objects.get(id=complaint_id, department=department)
                complaint.status = new_status
                complaint.save()
                messages.success(request, f'Complaint #{complaint_id} updated')
            except:
                messages.error(request, 'Error updating complaint')
            
            return redirect('department_dashboard', dept_slug=dept_slug)
    
    return render(request, 'landing_page/department_dashboard.html', {
        'department': department,
        'complaints': complaints,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'in_progress': in_progress,
        'resolved': resolved,
    })

def department_complaint_detail(request, complaint_id):
    """View complaint details - department version"""
    try:
        complaint = Complaint.objects.get(id=complaint_id)
        department = complaint.department
    except Complaint.DoesNotExist:
        messages.error(request, 'Complaint not found')
        return redirect('department_portal')
    
    if not request.session.get(f'dept_{department.slug}_auth'):
        messages.error(request, 'Unauthorized access')
        return redirect('department_login', dept_slug=department.slug)
    
    return render(request, 'landing_page/department_complaint_detail.html', {
        'complaint': complaint,
        'department': department,
    })

def index(request):
    """Home/Landing Page"""
    try:
        Complaint = get_complaint_model()
        total_complaints = Complaint.objects.count()
        resolved_complaints = len([c for c in Complaint.objects.all() if getattr(c, 'status', '').lower() == 'resolved'])
    except:
        total_complaints = 1500
        resolved_complaints = 1200

    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'user': request.user,
    }
    return render(request, 'landing_page/index.html', context)

def how_it_works(request):
    """How It Works page"""
    steps = [
        {'number': 1, 'title': 'Register', 'desc': 'Create your account with username and email'},
        {'number': 2, 'title': 'Login', 'desc': 'Sign in with your credentials'},
        {'number': 3, 'title': 'Lodge Complaint', 'desc': 'Fill complaint form with details'},
        {'number': 4, 'title': 'Get Complaint ID', 'desc': 'Receive unique ID for tracking'},
        {'number': 5, 'title': 'Track Complaint', 'desc': 'Enter Complaint ID to check status'},
    ]
    return render(request, 'landing_page/how_it_works.html', {'steps': steps})

def about(request):
    """About page"""
    return render(request, 'landing_page/about.html')

def contact(request):
    """Contact page"""
    return render(request, 'landing_page/contact.html')

def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'landing_page/privacy_policy.html')

def terms_conditions(request):
    """Terms & Conditions page"""
    return render(request, 'landing_page/terms_conditions.html')

def faq(request):
    """FAQ page"""
    faqs = [
        {'question': 'How do I lodge a complaint?', 'answer': 'Register first, then login and go to Lodge Complaint page.'},
        {'question': 'How do I track my complaint?', 'answer': 'Use Track Complaint page and enter your Complaint ID (format: COMP-XXXXXXX).'},
        {'question': 'What is a Complaint ID?', 'answer': 'Unique ID sent after complaint submission. Format: COMP-XXXXXXX'},
    ]
    return render(request, 'landing_page/faq.html', {'faqs': faqs})

# ========== DASHBOARD VIEWS ==========

@login_required
def dashboard(request):
    """Main Dashboard - Redirects to role-specific dashboard"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    elif hasattr(request.user, 'department_profile'):
        return redirect('/department/')
    else:
        return redirect('citizen_dashboard')

@login_required
def citizen_dashboard(request):
    """Citizen Dashboard - FIXED VERSION"""
    total_complaints = 0
    resolved_complaints = 0
    pending_complaints = 0
    in_progress_complaints = 0
    recent_complaints = []

    try:
        from complaints.models import Complaint
        user = request.user

        user_complaints_by_user = Complaint.objects.filter(user=user)
        user_complaints_by_email = Complaint.objects.none()
        if user.email:
            user_complaints_by_email = Complaint.objects.filter(email__iexact=user.email)

        user_complaints = user_complaints_by_user | user_complaints_by_email
        user_complaints = user_complaints.distinct()

        total_complaints = user_complaints.count()
        resolved_complaints = user_complaints.filter(status='Resolved').count()
        pending_complaints = user_complaints.filter(status='Submitted').count()
        in_progress_complaints = user_complaints.filter(status='In Progress').count()
        recent_complaints = user_complaints.order_by('-created_at')[:5]

        print(f"User: {user.username}, Email: {user.email}")
        print(f"Total complaints found: {total_complaints}")

    except ImportError:
        print("Could not import complaints.models.Complaint")
    except Exception as e:
        print(f"Dashboard error: {e}")

    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'recent_complaints': recent_complaints,
    }

    return render(request, 'landing_page/user/dashboard.html', context)

@login_required
def official_dashboard(request):
    """Department Official Dashboard"""
    try:
        Complaint = get_complaint_model()
        assigned_complaints = Complaint.objects.filter(assigned_to=request.user)

        context = {
            'user': request.user,
            'assigned_complaints': list(assigned_complaints)[:10],
            'total_assigned': assigned_complaints.count(),
            'role': 'official',
        }
    except:
        context = {
            'user': request.user,
            'assigned_complaints': [],
            'total_assigned': 0,
            'role': 'official',
        }

    return render(request, 'landing_page/dashboard/official_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_dashboard(request):
    """Admin Dashboard - Redirects to pulse_admin"""
    return redirect('/pulse_admin/')

@login_required
def my_complaints(request):
    if not request.user.is_authenticated:
        return redirect('login')

    from complaints.models import Complaint
    from django.core.paginator import Paginator

    user = request.user

    user_email = user.email if user.email else f"{user.username}@example.com"

    user_complaints_by_user = Complaint.objects.filter(user=user)
    user_complaints_by_email = Complaint.objects.none()
    if user.email:
        user_complaints_by_email = Complaint.objects.filter(email__iexact=user.email)

    user_complaints = (user_complaints_by_user | user_complaints_by_email).distinct()

    if not user_complaints.exists():
        email_variations = [
            user_email.lower(),
            user_email.replace('@example.com', '@gmail.com'),
            f"{user.username}@gmail.com",
        ]
        for email in email_variations:
            complaints = Complaint.objects.filter(email__iexact=email)
            if complaints.exists():
                user_complaints = complaints
                break

    user_complaints = user_complaints.order_by('-created_at')
    page_obj = user_complaints

    return render(request, 'landing_page/my_complaints.html', {
        'page_obj': page_obj,
        'total': user_complaints.count(),
    })

# ========== COMPLAINT WORKFLOW ==========

@login_required
def lodge_complaint(request):
    """Lodge Complaint"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'General')

        if not title or not description:
            messages.error(request, 'Title and description are required!')
            return redirect('lodge_complaint')

        try:
            Complaint = get_complaint_model()

            import uuid
            complaint_id = f"CGR{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"

            complaint = Complaint.objects.create(
                user=request.user,
                title=title,
                details=description,
                category=category,
                complaint_id=complaint_id,
                status='Pending',
                priority='Medium',
                created_at=timezone.now()
            )

            try:
                send_mail(
                    subject=f'Your Complaint Registered - ID: {complaint_id}',
                    message=f"""Dear {request.user.get_full_name() or request.user.username},

Your complaint has been successfully registered with Public Pulse!

📋 **Complaint Details:**
- Complaint ID: {complaint_id}
- Title: {title}
- Category: {category}
- Status: Pending
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🔍 **Track Your Complaint:**
You can track your complaint status at:
http://127.0.0.1:8000/track-complaint/

Use your Complaint ID: {complaint_id}

Thank you for using Public Pulse to make your voice heard!

Best regards,
Public Pulse Team
support@publicpulse.com""",
                    from_email='noreply@publicpulse.com',
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email error: {e}")

            messages.success(request,
                f'✅ Complaint submitted successfully!<br>'
                f'📋 Your Complaint ID: <strong>{complaint_id}</strong><br>'
                f'💾 Save this ID to track your complaint status.'
            )

            return redirect('citizen_dashboard')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('lodge_complaint')

    categories = [
        ('Municipal Issues', 'Municipal Issues'),
        ('Electricity', 'Electricity'),
        ('Water Supply', 'Water Supply'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Transport', 'Transport'),
        ('Waste Management', 'Waste Management'),
        ('Road Infrastructure', 'Road Infrastructure'),
        ('Public Safety', 'Public Safety'),
        ('General', 'General'),
    ]

    return render(request, 'complaints/lodge_complaint.html', {
        'categories': categories,
        'user': request.user,
    })

def track_complaint(request):
    """Track Complaint"""
    complaint = None
    complaint_id = request.POST.get('complaint_id') or request.GET.get('id', '')

    if complaint_id:
        try:
            Complaint = get_complaint_model()
            complaint = Complaint.objects.get(complaint_id=complaint_id)
        except:
            messages.error(request, 'Complaint ID not found!')

    return render(request, 'complaints/track_complaint.html', {
        'complaint': complaint,
        'complaint_id': complaint_id,
    })

@login_required
def complaint_detail(request, complaint_id):
    """Complaint Details: fetch by complaint_id or readable_id and enforce ownership."""
    from django.core.exceptions import PermissionDenied
    from django.http import Http404
    try:
        from complaints.models import Complaint

        complaint = Complaint.objects.filter(
            Q(complaint_id=complaint_id) | Q(readable_id=complaint_id)
        ).first()

        if not complaint:
            raise Http404("Complaint not found")

        if request.user.is_staff:
            pass
        else:
            owner_ok = False
            if getattr(complaint, 'user', None):
                if complaint.user == request.user:
                    owner_ok = True
            else:
                comp_email = (getattr(complaint, 'email', None) or '').lower()
                user_email = (getattr(request.user, 'email', '') or '').lower()
                if comp_email and user_email and comp_email == user_email:
                    owner_ok = True

            if not owner_ok:
                raise PermissionDenied("You do not have permission to view this complaint")

    except Http404:
        raise
    except PermissionDenied:
        raise
    except Exception:
        raise Http404("Complaint not found")

    return render(request, 'landing_page/complaint_detail.html', {'complaint': complaint})

# ========== USER PROFILE ==========

@login_required
def profile(request):
    """User Profile - FIXED VERSION"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        errors = []

        if not first_name:
            errors.append('First name is required')
        if not last_name:
            errors.append('Last name is required')
        if not email:
            errors.append('Email is required')
        elif email and User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
            errors.append('This email is already in use. Please use a different email.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('profile')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        try:
            UserProfile = apps.get_model('chatbot', 'UserProfile')
            profile = UserProfile.objects.filter(user=user).first()
            if profile:
                profile.first_name = user.first_name
                profile.last_name = user.last_name
                profile.email = user.email
                profile.full_name = f"{user.first_name} {user.last_name}"
                profile.save()
        except:
            pass

        messages.success(request, '✅ Your profile has been updated successfully!')
        return redirect('profile')

    try:
        from complaints.models import Complaint
        user_complaints = Complaint.objects.filter(email__iexact=request.user.email).order_by('-created_at')[:5]
        total_complaints = user_complaints.count()
        resolved_count = user_complaints.filter(status='Resolved').count()
    except:
        user_complaints = []
        total_complaints = 0
        resolved_count = 0

    return render(request, 'landing_page/user/profile.html', {
        'user_complaints': user_complaints,
        'total_complaints': total_complaints,
        'resolved_count': resolved_count,
    })

@login_required
def change_password(request):
    """Change Password - FIXED VERSION"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '✅ Your password has been changed successfully!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'landing_page/user/change_password.html', {'form': form})

# ========== AI ASSISTANT - FIXED CHATBOT ==========

def normalize_message(text):
    import re
    clean_text = (text or '').strip().lower()
    clean_text = re.sub(r'[^a-z0-9\s]', ' ', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text)
    return clean_text.strip()


def get_chatbot_response(user_input):
    """Direct response mapping for all user questions - NO MORE 'STILL LEARNING'"""
    msg = user_input.lower().strip()
    
    # LOGIN QUESTIONS
    if "how do i login" in msg or "how to login" in msg or "login help" in msg or "sign in" in msg:
        return """🔑 **Login Instructions**

1️⃣ Go to Homepage
2️⃣ Click 'Login' button (top right)
3️⃣ Enter Username OR Email
4️⃣ Enter Password
5️⃣ Click 'Sign In'

**Having trouble?**
• Use 'Forgot Password' if you can't remember
• Check Caps Lock is OFF
• Passwords are case-sensitive

After login, you'll see your Dashboard where you can lodge complaints!"""

    # DEPARTMENTS QUESTION
    elif "what departments" in msg or "departments available" in msg or "list of departments" in msg or "available departments" in msg:
        return """🏛️ **Departments Available in Civic Pulse**

1. **Education Department** 🏫 - Schools, colleges, teachers, fees
2. **Healthcare Department** 🏥 - Hospitals, doctors, medical services
3. **Transport Department** 🚌 - Roads, potholes, buses, traffic
4. **Water Supply Department** 💧 - Water shortage, leaks, quality
5. **Electricity Department** ⚡ - Power outages, bills, transformers
6. **Municipal Corporation** 🗑️ - Garbage, drainage, street lights
7. **Police Department** 🚔 - Safety, crime, law enforcement
8. **Anti-Corruption Bureau** 💰 - Bribery, misconduct
9. **General Administration** 📝 - Other government services

Select the department that matches your issue for faster resolution!"""

    # WATER COMPLAINT
    elif "water" in msg and ("problem" in msg or "complaint" in msg or "how to complain" in msg or "i have water" in msg):
        return """💧 **How to File a Water Supply Complaint**

**Step-by-Step Process:**

1️⃣ **Login** to your Civic Pulse account
2️⃣ Go to **'Lodge a Complaint'**
3️⃣ Select Category: **'Water Supply'**
4️⃣ In description, include:
   • Exact location (area, street, house number)
   • Duration of problem (how many days/weeks)
   • Type of issue (no water/low pressure/leakage/dirty water)
   • Number of families affected
5️⃣ Upload photos of the issue (recommended)
6️⃣ Click **Submit**

**Priority Level:**
🔴 High Priority - No water for 3+ days (2-5 days resolution)
🟡 Medium Priority - Low pressure, irregular supply (5-10 days)
🟢 Low Priority - Minor leakages (10-15 days)

**💡 Tip:** Include photos for faster resolution!"""

    # TRACK COMPLAINT
    elif "track" in msg and ("complaint" in msg or "status" in msg):
        return """🔍 **How to Track Your Complaint**

**Three Easy Ways:**

**Method 1:** Go to 'Track Complaint' page → Enter Complaint ID → View status

**Method 2:** Login → 'My Complaints' → See all your complaints

**Method 3:** Ask me directly with your Complaint ID (e.g., "Check CP-UNC60906")

**Status Meanings:**
• 📝 **Submitted** - Received, in queue
• 🔄 **In Progress** - Being worked on
• ✅ **Resolved** - Issue addressed
• 📁 **Closed** - Completed

You'll get email updates for every status change!"""

    # LODGE COMPLAINT
    elif "lodge" in msg or "how to submit" in msg or "submit complaint" in msg or "how to file" in msg:
        return """📋 **How to Lodge a Complaint**

**Step-by-Step Process:**

1️⃣ **Login** to your account
2️⃣ Go to **Dashboard**
3️⃣ Click **'Lodge a Complaint'** button
4️⃣ **Fill the form:**
   • Select Category (Education, Healthcare, Water, etc.)
   • Write detailed description (location, issue, impact)
   • Add city/location
   • Upload photos (optional)
5️⃣ Click **'Submit'**
6️⃣ Receive unique **Complaint ID** via email instantly

**Total time:** Less than 3 minutes!"""

    # DETAILS REQUIRED
    elif "details" in msg and ("required" in msg or "what" in msg or "need" in msg):
        return """📝 **Required Details for Complaint**

**Mandatory Fields:**
✅ Category - Select from 9 departments
✅ Description - Explain your issue clearly
✅ City/District - Where problem is located

**Optional but Recommended:**
📸 Images - Upload photos (JPG, PNG, GIF, max 5MB)
📍 Full address - Street, landmark, PIN code
📞 Phone number - For urgent contact

**What to include in description:**
• Exact location with landmarks
• When problem started
• How severe it is
• How many people affected
• Any previous attempts to resolve"""

    # IMAGE UPLOAD
    elif "image" in msg or "upload" in msg or "photo" in msg:
        return """📸 **Yes, you can upload images!**

**Supported formats:** JPG, JPEG, PNG, GIF
**Max size:** 5MB per image

**Tips:**
• Take clear, well-lit photos
• Show problem from multiple angles
• Include landmarks for location

Photos help authorities understand the issue better and lead to faster resolution!"""

    # REGISTRATION
    elif "register" in msg or "sign up" in msg or "create account" in msg:
        return """📝 **How to Register**

1️⃣ Click 'Register' on homepage
2️⃣ Enter Username (unique name)
3️⃣ Enter Email (for notifications)
4️⃣ Create Password (min 8 characters)
5️⃣ Confirm Password
6️⃣ Click 'Register'

✅ Free and takes less than 2 minutes!
✅ After registration, you're automatically logged in
✅ Start lodging complaints immediately"""

    # FORGOT PASSWORD
    elif "forgot" in msg or "reset password" in msg:
        return """🔐 **Forgot Password**

1️⃣ Go to Login Page
2️⃣ Click 'Forgot Password?'
3️⃣ Enter your registered email
4️⃣ Click 'Send Reset Link'
5️⃣ Check email (including spam)
6️⃣ Click reset link (valid 15 minutes)
7️⃣ Enter new password (min 8 characters)
8️⃣ Confirm new password
9️⃣ Login with new password

**Password Tips:**
• Use mix of letters, numbers, symbols
• Minimum 8 characters
• Don't use personal information"""

    # PENDING STATUS
    elif "pending" in msg and "mean" in msg:
        return """📊 **What Does 'Pending' Mean?**

"Pending" means your complaint is waiting for department action.

**Status possibilities:**
• **Submitted** - Received, in queue for review (1-2 days)
• **In Progress** - Department is working on it (5-15 days)

**Resolution time:**
• 🔴 High Priority: 2-5 days
• 🟡 Medium Priority: 5-15 days
• 🟢 Low Priority: 15-30 days

You'll receive email updates when status changes!"""

    # HOW IT WORKS
    elif "how it works" in msg or "how does civic pulse work" in msg:
        return """⚙️ **How Civic Pulse Works**

**6 Simple Steps:**

1. **Register/Login** - Create free account
2. **Submit Complaint** - Fill details with location
3. **AI Processing** - Auto-categorizes and sets priority
4. **Get Complaint ID** - Unique ID sent via email
5. **Department Action** - Routed to relevant department
6. **Track & Feedback** - Track anytime with ID

**Total time:** Less than 5 minutes!"""

    # DATA SECURITY
    elif "secure" in msg or "privacy" in msg or "data safe" in msg:
        return """🔒 **Your data is completely secure!**

**Security measures:**
• Passwords are hashed (never stored in plain text)
• HTTPS encryption for all communications
• Role-based access control
• No data sold to third parties

**Your Privacy Rights:**
✅ You can view all your data
✅ Request data deletion
✅ Update profile information

Your information is safe with Civic Pulse!"""

    # WHAT IS CIVIC PULSE
    elif "what is civic pulse" in msg or "about civic pulse" in msg:
        return """🌟 **Civic Pulse - Smart Civic Engagement Platform**

Civic Pulse is an AI-powered digital platform that revolutionizes how citizens interact with government departments for grievance redressal.

**Core Features:**
🤖 AI-powered complaint categorization
😊 Real-time sentiment analysis
🔍 Unique complaint tracking ID
📧 Instant email notifications
👥 Three-tier system (Citizen, Admin, Department)
💬 24/7 AI chatbot assistant

**Mission:** Bridge the gap between citizens and government through transparent, efficient, and technology-driven complaint resolution."""

    # GREETINGS
    elif msg in ["hi", "hello", "hey", "greetings"] or msg.startswith("hi ") or msg.startswith("hello "):
        return """👋 **Hello! Welcome to Civic Pulse!**

I'm your AI Assistant. Here's what you can ask me:

**📝 Account & Login**
• "How do I login?"
• "How to register?"
• "Forgot password"

**📋 Complaints**
• "How to lodge a complaint?"
• "What details are required?"
• "Can I upload images?"
• "Water problem how to complain?"

**🔍 Tracking**
• "How to track my complaint?"
• "What does pending mean?"

**🏛️ Information**
• "What departments are available?"
• "How does Civic Pulse work?"
• "Is my data secure?"

How can I help you today? 🌟"""

    # THANK YOU
    elif "thank" in msg:
        return """😊 **You're very welcome!**

Glad I could help! Feel free to ask if you need anything else.

**Remember:**
• Keep your Complaint ID safe
• Track status anytime
• Provide feedback after resolution

Have a great day! 🌟"""

    # GOODBYE
    elif "bye" in msg or "goodbye" in msg:
        return """👋 **Goodbye! Thanks for visiting Civic Pulse!**

**Before you go:**
✅ Remember your Complaint ID for tracking
✅ Check email for updates
✅ Come back anytime to track progress

Have a great day! 🌟"""

    # DEFAULT FALLBACK - NO MORE "STILL LEARNING"
    else:
        return """🤔 I can help with these topics:

**📝 Account & Login**
• "How do I login?"
• "How to register?"
• "Forgot password"

**📋 Complaints**
• "How to lodge a complaint?"
• "What details are required?"
• "Can I upload images?"
• "Water problem how to complain?"

**🔍 Tracking**
• "How to track my complaint?"
• "What does pending mean?"

**🏛️ Information**
• "What departments are available?"
• "How does Civic Pulse work?"
• "Is my data secure?"

Just type your question naturally and I'll help you! 💬"""


def chatbot_assistant(request):
    """AI Assistant Chatbot"""
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to use the AI Assistant')
        return redirect('login')

    if request.method == 'POST':
        raw_message = request.POST.get('message', '') or ''
        response = get_chatbot_response(raw_message)

        return JsonResponse({
            'response': response,
            'timestamp': timezone.now().isoformat(),
            'user_message': raw_message
        })

    # GET request
    return render(request, 'landing_page/chatbot.html', {
        'title': 'AI Assistant',
        'user': request.user,
    })

# ========== ADMIN MANAGEMENT ==========

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def manage_complaints(request):
    """Manage Complaints (Admin)"""
    try:
        Complaint = get_complaint_model()
        complaints = Complaint.objects.all()

        paginator = Paginator(list(complaints), 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    except:
        page_obj = []

    return render(request, 'landing_page/manage_complaints.html', {'page_obj': page_obj})

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_complaint_detail(request, complaint_id):
    """Admin Complaint Detail"""
    try:
        Complaint = get_complaint_model()
        complaint = Complaint.objects.get(complaint_id=complaint_id)
    except:
        messages.error(request, 'Complaint not found!')
        return redirect('manage_complaints')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '').strip()

        if new_status:
            complaint.status = new_status
            if new_status == 'Resolved' and not hasattr(complaint, 'resolved_at'):
                complaint.resolved_at = timezone.now()

            messages.success(request, f'Status updated to {new_status}')

        return redirect('admin_complaint_detail', complaint_id=complaint_id)

    return render(request, 'landing_page/admin_complaint_detail.html', {'complaint': complaint})

# ========== ERROR HANDLERS ==========

def handler404(request, exception):
    return render(request, 'landing_page/errors/404.html', status=404)

def handler500(request):
    return render(request, 'landing_page/errors/500.html', status=500)

def handler403(request, exception):
    return render(request, 'landing_page/errors/403.html', status=403)

def handler400(request, exception):
    return render(request, 'landing_page/errors/400.html', status=400)

# ========== ADDITIONAL VIEWS FOR YOUR TEMPLATES ==========

def home(request):
    """Alias for index"""
    return index(request)

@login_required
def update_profile(request):
    """Update Profile - alternative to profile"""
    return profile(request)

@login_required
def settings(request):
    """User Settings"""
    return render(request, 'landing_page/settings.html', {'user': request.user})

# ========== PUBLIC HOMEPAGE CHATBOT API (NO LOGIN REQUIRED) ==========

def public_homepage_chatbot(request):
    """Public chatbot API for homepage - NO LOGIN REQUIRED"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            # Get response from the function below
            response = get_public_chatbot_response(message)
            
            return JsonResponse({
                'response': response,
                'status': 'success'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ========== PUBLIC CHATBOT API FOR HOMEPAGE ==========

def public_chatbot_api(request):
    """Public chatbot API - NO LOGIN REQUIRED - Same responses as dashboard chatbot"""
    import json
    from django.http import JsonResponse
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Get response using the same logic as dashboard chatbot
            response = get_public_chatbot_response(user_message)
            
            return JsonResponse({
                'response': response,
                'status': 'success'
            })
        except Exception as e:
            return JsonResponse({'error': str(e), 'status': 'error'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_public_chatbot_response(user_message):
    """Same response logic as dashboard chatbot - NO LOGIN REQUIRED"""
    msg = user_message.lower().strip()
    
    # ========== GREETINGS ==========
    if any(word in msg for word in ['hi', 'hello', 'hey', 'greetings']):
        return """👋 **Hello! Welcome to Civic Pulse!**

I'm your AI Assistant. Here's what you can ask me:

**📝 Account & Login**
• "How do I login?"
• "How to register?"
• "Forgot password"

**📋 Complaints**
• "How to lodge a complaint?"
• "What details are required?"
• "Can I upload images?"
• "Water problem how to complain?"

**🔍 Tracking**
• "How to track my complaint?"
• "What does pending mean?"

**🏛️ Information**
• "What departments are available?"
• "How does Civic Pulse work?"
• "Is my data secure?"

How can I help you today? 🌟"""
    
    # ========== LOGIN QUESTIONS ==========
    elif any(word in msg for word in ['how do i login', 'how to login', 'login help', 'sign in']):
        return """🔑 **Login Instructions**

1️⃣ Go to Homepage
2️⃣ Click 'Login' button (top right)
3️⃣ Enter Username OR Email
4️⃣ Enter Password
5️⃣ Click 'Sign In'

**Having trouble?**
• Use 'Forgot Password' if you can't remember
• Check Caps Lock is OFF
• Passwords are case-sensitive

After login, you'll see your Dashboard where you can lodge complaints!"""
    
    # ========== REGISTRATION ==========
    elif any(word in msg for word in ['how to register', 'sign up', 'create account', 'register']):
        return """📝 **How to Register**

1️⃣ Click 'Register' on homepage
2️⃣ Enter Username (unique name)
3️⃣ Enter Email (for notifications)
4️⃣ Create Password (min 8 characters)
5️⃣ Confirm Password
6️⃣ Click 'Register'

✅ After registration, you're automatically logged in
✅ Check email for confirmation
✅ Start lodging complaints immediately

**Time:** Less than 2 minutes!
**Cost:** Completely FREE!"""
    
    # ========== WHAT IS CIVIC PULSE ==========
    elif any(word in msg for word in ['what is civic pulse', 'about civic pulse']):
        return """🌟 **Civic Pulse - Smart Civic Engagement Platform**

Civic Pulse is an AI-powered digital platform that helps citizens submit complaints and feedback to government departments.

**Core Features:**
🤖 AI-powered complaint categorization
😊 Real-time sentiment analysis
🔍 Unique complaint tracking ID
📧 Instant email notifications
👥 Three-tier system (Citizen, Admin, Department)
💬 24/7 AI chatbot assistant

**Mission:** Bridge the gap between citizens and government through transparent, efficient, and technology-driven complaint resolution.

**It's completely FREE for all citizens!**"""
    
    # ========== HOW IT WORKS ==========
    elif any(word in msg for word in ['how it works', 'how does civic pulse work', 'how does it work']):
        return """⚙️ **How Civic Pulse Works - 6 Simple Steps**

**Step 1: Register/Login** 📝
Create your free account with email and password

**Step 2: Submit Complaint** 📋
• Select category (Education, Healthcare, etc.)
• Describe your issue with location
• Upload supporting images (optional)
• AI analyzes in real-time

**Step 3: AI Processing** 🤖
• Auto-categorizes complaint
• Detects sentiment (positive/negative/neutral)
• Assigns priority (High/Medium/Low)

**Step 4: Get Complaint ID** 🆔
• Unique ID sent to your email instantly
• Format: CP-XXXYYYYYY (e.g., CP-UNC60906)

**Step 5: Department Action** 🏛️
• Complaint routed to relevant department
• Status updates: Submitted → In Progress → Resolved

**Step 6: Track & Feedback** 📊
• Track anytime using Complaint ID
• Provide feedback after resolution

**Total time:** Registration <2 min | Complaint submission <3 min | Tracking instant!"""
    
    # ========== LODGE COMPLAINT ==========
    elif any(word in msg for word in ['how to submit complaint', 'lodge complaint', 'how to lodge', 'submit complaint', 'file complaint']):
        return """📋 **How to Lodge a Complaint**

**Step-by-Step Process:**

1️⃣ **Login** to your account
2️⃣ Go to **Dashboard**
3️⃣ Click **'Lodge a Complaint'** button
4️⃣ **Fill the form:**
   • Select Category (Education, Healthcare, Water, etc.)
   • Write detailed description (location, issue, impact)
   • Add city/location
   • Upload photos (optional but recommended)
5️⃣ Click **'Submit'**
6️⃣ Receive unique **Complaint ID** via email instantly

**Tips for Better Resolution:**
• Be specific about location with landmarks
• Add photos as evidence
• Describe the impact clearly
• Keep your Complaint ID safe

**Total time:** Less than 3 minutes!"""
    
    # ========== WHAT CAN I COMPLAIN ABOUT / CATEGORIES ==========
    elif any(word in msg for word in ['what can i complain about', 'categories', 'what categories', 'types of complaints']):
        return """📂 **What You Can Complain About - 9 Categories**

**1. Education** 🏫 - Schools, colleges, teachers, fees
**2. Healthcare** 🏥 - Hospitals, doctors, medical services
**3. Transport** 🚌 - Roads, potholes, buses, traffic
**4. Water Supply** 💧 - Water shortage, leaks, quality
**5. Electricity** ⚡ - Power outages, bills, transformers
**6. Municipal** 🗑️ - Garbage, drainage, street lights
**7. Police** 🚔 - Safety, crime, law enforcement
**8. Anti-Corruption** 💰 - Bribery, misconduct
**9. General** 📝 - Other government services

Your complaint will be automatically routed to the right department!"""
    
    # ========== WATER COMPLAINT ==========
    elif 'water' in msg and ('problem' in msg or 'complaint' in msg):
        return """💧 **How to File a Water Supply Complaint**

**Step-by-Step Process:**

1️⃣ **Login** to your Civic Pulse account
2️⃣ Go to **'Lodge a Complaint'**
3️⃣ Select Category: **'Water Supply'**
4️⃣ In description, include:
   • Exact location (area, street, house number)
   • Duration of problem (how many days/weeks)
   • Type of issue (no water/low pressure/leakage/dirty water)
   • Number of families affected
5️⃣ Upload photos of the issue (recommended)
6️⃣ Click **Submit**

**Priority Level:**
🔴 **High Priority** - No water for 3+ days (2-5 days)
🟡 **Medium Priority** - Low pressure, irregular supply (5-10 days)
🟢 **Low Priority** - Minor leakages (10-15 days)

**💡 Tip:** Include photos for faster resolution!"""
    
    # ========== TRACK COMPLAINT ==========
    elif any(word in msg for word in ['track complaint', 'how to track', 'check status', 'track my complaint']):
        return """🔍 **How to Track Your Complaint**

**Three Easy Ways:**

**Method 1:** Go to 'Track Complaint' page → Enter Complaint ID → View status

**Method 2:** Login → 'My Complaints' → See all your complaints

**Method 3:** Ask me directly with your Complaint ID (e.g., "Check CP-UNC60906")

**What You'll See:**
📝 **Current Status** - Submitted/In Progress/Resolved/Closed
📅 **Submission Date** - When complaint was filed
📍 **Location** - Where issue was reported
🏛️ **Department** - Who is handling it

**Status Meanings:**
• **Submitted** - Received, in queue (1-2 days)
• **In Progress** - Being worked on (5-15 days)
• **Resolved** - Issue addressed
• **Closed** - Completed

You'll get email updates for every status change!"""
    
    # ========== WHAT DOES PENDING MEAN ==========
    elif 'pending' in msg and 'mean' in msg:
        return """📊 **What Does 'Pending' Mean?**

"Pending" means your complaint is waiting for department action.

**Status possibilities:**
• **Submitted** - Received, in queue for review (1-2 days)
• **In Progress** - Department is working on it (5-15 days)

**Resolution timeframes:**
• 🔴 High Priority: 2-5 days
• 🟡 Medium Priority: 5-15 days
• 🟢 Low Priority: 15-30 days

You'll receive email updates when status changes! No action needed from you - just wait for updates or track using your Complaint ID."""
    
    # ========== DEPARTMENTS AVAILABLE ==========
    elif any(word in msg for word in ['what departments', 'departments available', 'list of departments', 'available departments']):
        return """🏛️ **Departments Available in Civic Pulse**

1. **Education Department** 🏫 - Schools, colleges, teachers, fees
2. **Healthcare Department** 🏥 - Hospitals, doctors, medical services
3. **Transport Department** 🚌 - Roads, potholes, buses, traffic
4. **Water Supply Department** 💧 - Water shortage, leaks, quality
5. **Electricity Department** ⚡ - Power outages, bills, transformers
6. **Municipal Corporation** 🗑️ - Garbage, drainage, street lights
7. **Police Department** 🚔 - Safety, crime, law enforcement
8. **Anti-Corruption Bureau** 💰 - Bribery, misconduct
9. **General Administration** 📝 - Other government services

Select the department that matches your issue for faster resolution!"""
    
    # ========== CAN I UPLOAD IMAGES ==========
    elif any(word in msg for word in ['upload images', 'can i upload images', 'upload photo']):
        return """📸 **Yes, you can upload images with your complaint!**

**How to Upload:**
1️⃣ In the complaint form, click **'Choose File'** button
2️⃣ Select image from your device
3️⃣ Submit your complaint

**Supported formats:** JPG, JPEG, PNG, GIF
**Max size:** 5MB per image

**Tips for Good Photos:**
• Take clear, well-lit photos
• Capture problem from multiple angles
• Include landmarks for location reference

**💡 Tip:** Photos help authorities understand the issue better and lead to faster resolution!"""
    
    # ========== WHAT DETAILS ARE REQUIRED ==========
    elif any(word in msg for word in ['what details are required', 'required details', 'details needed']):
        return """📝 **Required Details for Complaint**

**Mandatory Fields (Must Fill):**
✅ **Category** - Select from 9 departments
✅ **Description** - Detailed explanation of your issue
✅ **City/District** - Where the problem is located

**Optional but Recommended:**
📸 **Images** - Upload photos as evidence (JPG, PNG, GIF, max 5MB)
📍 **Full Address** - Street name, landmark, PIN code
📞 **Phone Number** - For urgent contact if needed

**What to Include in Description:**
• Exact location with landmarks
• When the problem started
• How severe the issue is
• How many people are affected
• Any previous attempts to resolve
• What resolution you expect

**💡 Tip:** The more details you provide, the faster your complaint gets resolved!"""
    
    # ========== FORGOT PASSWORD ==========
    elif any(word in msg for word in ['forgot password', 'reset password']):
        return """🔐 **Forgot Password - Reset Process**

1️⃣ Go to Login Page
2️⃣ Click 'Forgot Password?' link
3️⃣ Enter your registered email address
4️⃣ Click 'Send Reset Link'
5️⃣ Check your email (including spam folder)
6️⃣ Click the reset link (valid for 15 minutes)
7️⃣ Enter new password (min 8 characters)
8️⃣ Confirm new password
9️⃣ Click 'Reset Password'
🔟 Login with new password

**Password Tips:**
• Use mix of letters, numbers, symbols
• Minimum 8 characters
• Don't use personal information
• Don't reuse old passwords"""
    
    # ========== IS MY DATA SECURE ==========
    elif any(word in msg for word in ['is my data secure', 'data secure', 'privacy', 'data safe']):
        return """🔒 **Yes, your data is completely secure!**

**Security Measures:**

**Password Security** 🔐
• Passwords are hashed and never stored in plain text
• 100,000 iterations of SHA-256 encryption

**Data Encryption** 🔒
• HTTPS for all communications
• SSL/TLS encryption
• Secure data transmission

**Access Control** 👥
• Citizens see only their complaints
• Departments see only assigned complaints
• Admins have monitored access

**What We DON'T Do:**
❌ Sell your data to third parties
❌ Share information without consent
❌ Use data for marketing

**Your Privacy Rights:**
✅ You can view all your data
✅ Request data deletion
✅ Update profile information

**💡 Remember:** Your data is safe with Civic Pulse!"""
    
    # ========== IS IT FREE ==========
    elif any(word in msg for word in ['is it free', 'free', 'cost', 'pay']):
        return """💰 **Completely FREE!**

**Yes, Civic Pulse is 100% FREE for all citizens!**

**No Hidden Costs:**
✅ Free registration
✅ Free complaint submission
✅ Free tracking
✅ Free email notifications
✅ Free chatbot assistance
✅ Free dashboard access

**No Subscription Fees:**
• No monthly charges
• No annual fees
• No premium tiers
• No payment required

**Forever Free:** Civic Pulse is committed to keeping services free for all citizens.

**Start using Civic Pulse today - no credit card, no payment, no catch!** 🌟"""
    
    # ========== CONTACT SUPPORT ==========
    elif any(word in msg for word in ['contact support', 'contact', 'support']):
        return """📞 **Contact Support**

**Email Support:** civicpulse.govt@gmail.com
**Response Time:** 24-48 hours

**Chat Support:** Use this chatbot! (Instant response)

**Emergency Numbers:**
• Police: 100
• Fire: 101
• Ambulance: 102
• Women Helpline: 1091
• Child Helpline: 1098

**Support Hours:**
• Chat: 24/7 (AI assistant always available)
• Email: Mon-Fri, 9 AM - 6 PM

For complaint-related queries, include your Complaint ID for faster assistance!"""
    
    # ========== THANK YOU ==========
    elif 'thank' in msg:
        return """😊 **You're very welcome!**

Glad I could help! Feel free to ask if you need anything else.

**Remember:**
• Keep your Complaint ID safe
• Track status anytime
• Provide feedback after resolution

Have a great day! 🌟"""
    
    # ========== GOODBYE ==========
    elif any(word in msg for word in ['bye', 'goodbye']):
        return """👋 **Goodbye! Thanks for visiting Civic Pulse!**

**Before you go:**
✅ Remember your Complaint ID for tracking
✅ Check email for updates
✅ Come back anytime to track progress

Have a great day! 🌟"""
    
    # ========== DEFAULT FALLBACK - NO "STILL LEARNING" ==========
    else:
        return """🤔 **I can help with these topics:**

**📝 Account & Login**
• "How do I login?"
• "How to register?"
• "Forgot password"

**📋 Complaints**
• "How to lodge a complaint?"
• "What details are required?"
• "Can I upload images?"
• "Water problem how to complain?"

**🔍 Tracking**
• "How to track my complaint?"
• "What does pending mean?"

**🏛️ Information**
• "What departments are available?"
• "How does Civic Pulse work?"
• "Is my data secure?"
• "Is it free?"

Just type your question naturally and I'll help you! 💬"""
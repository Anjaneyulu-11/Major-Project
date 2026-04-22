from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import models
import json
from datetime import datetime, timedelta

from .models import Feedback, UserProfile, Department, Category, FeedbackResponse
from .forms import (
    CustomUserCreationForm, UserProfileForm, FeedbackForm,
    FeedbackResponseForm, FeedbackFilterForm
)

# Utility functions for user type checking
def is_citizen(user):
    return hasattr(user, 'profile') and user.profile.user_type == 'citizen'

def is_official(user):
    return hasattr(user, 'profile') and user.profile.user_type == 'official'

def is_admin_user(user):
    return hasattr(user, 'profile') and user.profile.user_type == 'admin'

# ---------------------------------------------------------------------
# AUTHENTICATION VIEWS
# ---------------------------------------------------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            # Create user profile
            profile = profile_form.save(commit=False)
            profile.user = user
            
            # Handle user type selection
            user_type = request.POST.get('user_type', 'citizen')
            profile.user_type = user_type
            
            # If official, set department
            if user_type == 'official' and 'department' in request.POST:
                try:
                    department_id = request.POST.get('department')
                    if department_id:
                        profile.department = Department.objects.get(id=department_id)
                except (ValueError, Department.DoesNotExist):
                    pass
            
            profile.save()
            
            # Auto login after registration
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Public Pulse.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = CustomUserCreationForm()
        profile_form = UserProfileForm()
    
    # Get departments for officials dropdown
    departments = Department.objects.all()
    
    return render(request, 'auth/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'departments': departments,
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

# ---------------------------------------------------------------------
# DASHBOARD VIEWS
# ---------------------------------------------------------------------
@login_required
def dashboard(request):
    # Create profile if it doesn't exist
    if not hasattr(request.user, 'profile'):
        UserProfile.objects.create(user=request.user, user_type='citizen')
    
    user_profile = request.user.profile
    
    if user_profile.user_type == 'citizen':
        return citizen_dashboard(request)
    elif user_profile.user_type == 'official':
        return official_dashboard(request)
    elif user_profile.user_type == 'admin':
        return admin_dashboard(request)
    else:
        # Default to citizen if no user type
        user_profile.user_type = 'citizen'
        user_profile.save()
        return citizen_dashboard(request)

@login_required
def citizen_dashboard(request):
    user_feedbacks = Feedback.objects.filter(user=request.user)
    
    # Statistics
    total_feedbacks = user_feedbacks.count()
    resolved_feedbacks = user_feedbacks.filter(status='resolved').count()
    pending_feedbacks = user_feedbacks.filter(status='pending').count()
    rejected_feedbacks = user_feedbacks.filter(status='rejected').count()
    
    recent_feedbacks = user_feedbacks.order_by('-created_at')[:5]
    
    context = {
        'total_feedbacks': total_feedbacks,
        'resolved_feedbacks': resolved_feedbacks,
        'pending_feedbacks': pending_feedbacks,
        'rejected_feedbacks': rejected_feedbacks,
        'recent_feedbacks': recent_feedbacks,
    }
    
    return render(request, 'dashboard/citizen_dashboard.html', context)

@login_required
def official_dashboard(request):
    department = request.user.profile.department
    if not department:
        messages.error(request, 'No department assigned to your account.')
        return redirect('dashboard')
    
    department_feedbacks = Feedback.objects.filter(department=department)
    
    # Statistics
    total_feedbacks = department_feedbacks.count()
    unresolved_feedbacks = department_feedbacks.exclude(status='resolved').count()
    high_priority = department_feedbacks.filter(priority='high').count()
    resolved_feedbacks = department_feedbacks.filter(status='resolved').count()
    
    # Recent feedbacks
    recent_feedbacks = department_feedbacks.order_by('-created_at')[:10]
    
    context = {
        'department': department,
        'total_feedbacks': total_feedbacks,
        'unresolved_feedbacks': unresolved_feedbacks,
        'high_priority': high_priority,
        'resolved_feedbacks': resolved_feedbacks,
        'recent_feedbacks': recent_feedbacks,
    }
    
    return render(request, 'dashboard/official_dashboard.html', context)

@login_required
def admin_dashboard(request):
    # Overall statistics
    total_users = User.objects.count()
    total_feedbacks = Feedback.objects.count()
    total_departments = Department.objects.count()
    total_citizens = UserProfile.objects.filter(user_type='citizen').count()
    
    # Recent activities
    recent_feedbacks = Feedback.objects.select_related('user', 'department').order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_feedbacks': total_feedbacks,
        'total_departments': total_departments,
        'total_citizens': total_citizens,
        'recent_feedbacks': recent_feedbacks,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

# ---------------------------------------------------------------------
# FEEDBACK VIEWS
# ---------------------------------------------------------------------
@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.status = 'pending'
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('feedback_list')
    else:
        form = FeedbackForm()
    
    return render(request, 'feedback/submit_feedback.html', {'form': form})

@login_required
def feedback_list(request):
    user_profile = request.user.profile
    feedbacks = Feedback.objects.all()
    
    if user_profile.user_type == 'citizen':
        feedbacks = feedbacks.filter(user=request.user)
    elif user_profile.user_type == 'official':
        if user_profile.department:
            feedbacks = feedbacks.filter(department=user_profile.department)
    
    # Filtering
    filter_form = FeedbackFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data['department']:
            feedbacks = feedbacks.filter(department=filter_form.cleaned_data['department'])
        if filter_form.cleaned_data['category']:
            feedbacks = feedbacks.filter(category=filter_form.cleaned_data['category'])
        if filter_form.cleaned_data['status']:
            feedbacks = feedbacks.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data['priority']:
            feedbacks = feedbacks.filter(priority=filter_form.cleaned_data['priority'])
        if filter_form.cleaned_data['start_date']:
            feedbacks = feedbacks.filter(created_at__date__gte=filter_form.cleaned_data['start_date'])
        if filter_form.cleaned_data['end_date']:
            feedbacks = feedbacks.filter(created_at__date__lte=filter_form.cleaned_data['end_date'])
    
    # Pagination
    paginator = Paginator(feedbacks.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'feedback/feedback_list.html', {
        'page_obj': page_obj,
        'filter_form': filter_form,
    })

@login_required
def feedback_detail(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    # Check permissions
    user_profile = request.user.profile
    if user_profile.user_type == 'citizen' and feedback.user != request.user:
        messages.error(request, 'You are not authorized to view this feedback.')
        return redirect('feedback_list')
    elif user_profile.user_type == 'official' and feedback.department != user_profile.department:
        messages.error(request, 'This feedback is not from your department.')
        return redirect('feedback_list')
    
    response_form = None
    if user_profile.user_type in ['official', 'admin']:
        response_form = FeedbackResponseForm()
    
    return render(request, 'feedback/feedback_detail.html', {
        'feedback': feedback,
        'response_form': response_form,
    })

@login_required
def respond_to_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    if request.method == 'POST':
        form = FeedbackResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.feedback = feedback
            response.official = request.user
            response.save()
            
            # Update feedback status
            feedback.status = 'resolved'
            feedback.save()
            
            messages.success(request, 'Response submitted successfully!')
            return redirect('feedback_detail', feedback_id=feedback.id)
    
    return redirect('feedback_detail', feedback_id=feedback.id)

# ---------------------------------------------------------------------
# ANALYTICS VIEWS
# ---------------------------------------------------------------------
@login_required
def analytics_view(request):
    department = request.user.profile.department if request.user.profile.user_type == 'official' else None
    
    # Date range for analytics (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    if department:
        feedbacks = Feedback.objects.filter(department=department, created_at__range=[start_date, end_date])
    else:
        feedbacks = Feedback.objects.filter(created_at__range=[start_date, end_date])
    
    # Status distribution
    status_counts = feedbacks.values('status').annotate(count=Count('id'))
    
    # Priority distribution
    priority_counts = feedbacks.values('priority').annotate(count=Count('id'))
    
    # Daily submissions
    daily_submissions = {}
    for i in range(30):
        date = (end_date - timedelta(days=i)).date()
        count = feedbacks.filter(created_at__date=date).count()
        daily_submissions[str(date)] = count
    
    # Category distribution
    if department:
        category_counts = Category.objects.filter(department=department).annotate(
            count=Count('feedback')
        ).values('name', 'count')
    else:
        category_counts = Category.objects.annotate(
            count=Count('feedback')
        ).values('name', 'count')
    
    context = {
        'status_counts': json.dumps(list(status_counts)),
        'priority_counts': json.dumps(list(priority_counts)),
        'daily_submissions': json.dumps(daily_submissions),
        'category_counts': json.dumps(list(category_counts)),
        'department': department,
    }
    
    return render(request, 'analytics/analytics.html', context)

# ---------------------------------------------------------------------
# API VIEWS
# ---------------------------------------------------------------------
@login_required
def get_categories(request):
    department_id = request.GET.get('department_id')
    if department_id:
        categories = Category.objects.filter(department_id=department_id).values('id', 'name')
    else:
        categories = []
    return JsonResponse(list(categories), safe=False)

# ---------------------------------------------------------------------
# HOME VIEW
# ---------------------------------------------------------------------
def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')
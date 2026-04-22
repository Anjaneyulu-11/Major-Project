# pulse_admin/views.py - FINAL FIXED VERSION
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse

# ✅ Import the CORRECT Complaint model where data actually exists
from complaints.models import Complaint as CitizenComplaint

# Import your admin models (remove ComplaintUpdate as it doesn't exist)
from .models import (
    Category, AdminLog, AdminNotification, DashboardMetric,
    Department, DepartmentUser, QuickAction, SystemSetting,  # ADDED DepartmentUser here
    log_admin_action, create_admin_notification, get_dashboard_metrics
)

@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with real-time stats - USING CORRECT MODEL"""
    
    # ✅ Use CitizenComplaint (from complaints app) where real data exists
    today = timezone.now().date()
    
    # Calculate real statistics
    total_complaints = CitizenComplaint.objects.count()
    
    # Pending = Submitted + In Progress
    pending_complaints = CitizenComplaint.objects.filter(
        status__in=['Submitted', 'In Progress']
    ).count()
    
    # Resolved today
    resolved_today = CitizenComplaint.objects.filter(
        status='Resolved',
        updated_at__date=today
    ).count()
    
    # User satisfaction (placeholder - can integrate with feedback if exists)
    user_satisfaction = 4.2  # Default or calculate from feedback
    
    # Get complaints by status for chart
    status_data = {
        'Submitted': CitizenComplaint.objects.filter(status='Submitted').count(),
        'In Progress': CitizenComplaint.objects.filter(status='In Progress').count(),
        'Resolved': CitizenComplaint.objects.filter(status='Resolved').count(),
        'Closed': CitizenComplaint.objects.filter(status='Closed').count(),
    }
    
    # Get complaints by category (top 5)
    category_stats = list(CitizenComplaint.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:5])
    
    # Get high priority complaints
    high_priority_complaints = CitizenComplaint.objects.filter(
        ai_priority__in=['High'],
        status__in=['Submitted', 'In Progress']
    ).order_by('-created_at')[:10]
    
    # Get recent complaints
    recent_complaints = CitizenComplaint.objects.all().order_by('-created_at')[:10]
    
    # Get quick actions (if admin model exists)
    try:
        quick_actions = QuickAction.objects.filter(is_active=True).order_by('order')
    except:
        quick_actions = []
    
    # Get unread notifications
    try:
        unread_notifications = AdminNotification.objects.filter(is_read=False).order_by('-created_at')[:10]
    except:
        unread_notifications = []
    
    context = {
        # Real statistics
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_today': resolved_today,
        'user_satisfaction': user_satisfaction,
        
        # Charts data
        'status_data': json.dumps(status_data),
        'category_stats': category_stats,  # ✅ FIXED: Use category_stats directly
        
        # Lists
        'critical_complaints': high_priority_complaints,
        'recent_complaints': recent_complaints,
        'quick_actions': quick_actions,
        'unread_notifications': unread_notifications,
        
        # Date
        'today': today,
    }
    
    return render(request, 'pulse_admin/dashboard.html', context)

@staff_member_required
def manage_complaints(request):
    """Manage all complaints with filtering and pagination - USING CORRECT MODEL"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    priority_filter = request.GET.get('priority', '')
    assigned_filter = request.GET.get('assigned', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')
    
    # ✅ Use CitizenComplaint where data exists
    complaints = CitizenComplaint.objects.all().order_by('-created_at')
    
    # Apply filters
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    
    if priority_filter:
        complaints = complaints.filter(ai_priority=priority_filter)
    
    if assigned_filter:
        if assigned_filter == 'unassigned':
            complaints = complaints.filter(assigned_to__isnull=True)
        else:
            complaints = complaints.filter(assigned_to__icontains=assigned_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            complaints = complaints.filter(created_at__date__gte=date_from_obj)
        except:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            complaints = complaints.filter(created_at__date__lte=date_to_obj)
        except:
            pass
    
    # Apply search
    if search:
        complaints = complaints.filter(
            Q(complaint_id__icontains=search) |
            Q(readable_id__icontains=search) |
            Q(category__icontains=search) |
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(details__icontains=search) |
            Q(city__icontains=search)
        )
    
    # Get unique categories for filter dropdown
    categories = CitizenComplaint.objects.values_list('category', flat=True).distinct().order_by('category')
    
    # Get staff users for assignment (from User model)
    staff_users = User.objects.filter(is_staff=True, is_active=True)
    
    # Get stats for display
    total_complaints = complaints.count()
    pending_count = complaints.filter(status__in=['Submitted', 'In Progress']).count()
    in_progress_count = complaints.filter(status='In Progress').count()
    resolved_count = complaints.filter(status='Resolved').count()
    high_priority_count = complaints.filter(ai_priority__in=['High']).count()
    
    # Today's stats
    today = timezone.now().date()
    complaints_today = CitizenComplaint.objects.filter(created_at__date=today).count()
    resolved_today = CitizenComplaint.objects.filter(status='Resolved', updated_at__date=today).count()
    
    # Calculate resolution rate
    resolution_rate = (resolved_count / total_complaints * 100) if total_complaints > 0 else 0
    
    # Pagination
    paginator = Paginator(complaints, 20)  # 20 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Status choices - use CitizenComplaint's STATUS_CHOICES
    status_choices = [
        ('', 'All Status'),
        ('Submitted', 'Submitted'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]
    
    # Priority choices - use CitizenComplaint's PRIORITY_CHOICES
    priority_choices = [
        ('', 'All Priorities'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    context = {
        'complaints': page_obj,
        'page_obj': page_obj,
        'total_complaints': total_complaints,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'high_priority_count': high_priority_count,
        'complaints_today': complaints_today,
        'resolved_today': resolved_today,
        'resolution_rate': round(resolution_rate, 1),
        'categories': categories,
        'staff_users': staff_users,
        'status_choices': status_choices,
        'priority_choices': priority_choices,
        'current_status': status_filter,
        'current_category': category_filter,
        'current_priority': priority_filter,
        'current_assigned': assigned_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
    }
    
    return render(request, 'pulse_admin/manage_complaints.html', context)

@staff_member_required
def complaint_detail(request, complaint_id):
    """View and update complaint details - USING CORRECT MODEL"""
    
    # ✅ Use CitizenComplaint where data exists
    complaint = get_object_or_404(CitizenComplaint, complaint_id=complaint_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            resolution_details = request.POST.get('resolution_details', '')
            assigned_to = request.POST.get('assigned_to', '')
            
            if new_status and new_status != complaint.status:
                complaint.status = new_status
                if resolution_details:
                    complaint.resolution_details = resolution_details
                if assigned_to:
                    complaint.assigned_to = assigned_to
                complaint.updated_at = timezone.now()
                complaint.save()
                
                # Log the action
                log_admin_action(
                    admin=request.user,
                    action='update',
                    model_name='Complaint',
                    object_id=complaint.id,
                    description=f"Status changed from {complaint.status} to {new_status}"
                )
                
                messages.success(request, f'Complaint status updated to {new_status}')
                return redirect('pulse_admin:complaint_detail', complaint_id=complaint_id)
        
        elif action == 'update_priority':
            new_priority = request.POST.get('priority')
            if new_priority:
                complaint.ai_priority = new_priority
                complaint.save()
                messages.success(request, f'Priority updated to {new_priority}')
                return redirect('pulse_admin:complaint_detail', complaint_id=complaint_id)
    
    # Get similar complaints
    similar_complaints = CitizenComplaint.objects.filter(
        category=complaint.category
    ).exclude(id=complaint.id).order_by('-created_at')[:5]
    
    # Get status choices
    status_choices = [
        ('Submitted', 'Submitted'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]
    
    # Get priority choices
    priority_choices = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    context = {
        'complaint': complaint,
        'similar_complaints': similar_complaints,
        'status_choices': status_choices,
        'priority_choices': priority_choices,
    }
    
    return render(request, 'pulse_admin/complaint_detail.html', context)

@require_POST
@staff_member_required
def update_complaint_status_ajax(request):
    """AJAX endpoint for quick status updates - USING CORRECT MODEL"""
    try:
        complaint_id = request.POST.get('complaint_id')
        status = request.POST.get('status')
        
        if not complaint_id or not status:
            return JsonResponse({'success': False, 'error': 'Missing parameters'})
        
        # ✅ Use CitizenComplaint
        complaint = CitizenComplaint.objects.get(complaint_id=complaint_id)
        complaint.status = status
        complaint.updated_at = timezone.now()
        complaint.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Status updated to {status}',
            'new_status': status,
            'complaint_id': complaint_id,
        })
    except CitizenComplaint.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Complaint not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
@staff_member_required
def bulk_update_complaints(request):
    """Bulk update complaints - USING CORRECT MODEL"""
    try:
        action = request.POST.get('action')
        complaint_ids = request.POST.get('complaint_ids', '')
        
        if not complaint_ids:
            messages.error(request, 'No complaints selected')
            return redirect('pulse_admin:manage_complaints')
        
        complaint_ids = [cid.strip() for cid in complaint_ids.split(',') if cid.strip()]
        
        # ✅ Use CitizenComplaint
        complaints = CitizenComplaint.objects.filter(complaint_id__in=complaint_ids)
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            
            if not new_status:
                messages.error(request, 'Please select a status')
                return redirect('pulse_admin:manage_complaints')
            
            updated_count = complaints.update(status=new_status, updated_at=timezone.now())
            messages.success(request, f'Successfully updated {updated_count} complaint(s) to {new_status}')
        
        elif action == 'assign':
            assigned_to = request.POST.get('assigned_to', '')
            
            if not assigned_to:
                messages.error(request, 'Please enter department/person name')
                return redirect('pulse_admin:manage_complaints')
            
            updated_count = complaints.update(assigned_to=assigned_to, updated_at=timezone.now())
            messages.success(request, f'Successfully assigned {updated_count} complaint(s) to {assigned_to}')
        
        elif action == 'delete':
            if not request.user.is_superuser:
                messages.error(request, 'Only superusers can delete complaints')
                return redirect('pulse_admin:manage_complaints')
            
            deleted_count = complaints.count()
            
            # Log before deletion
            for complaint in complaints:
                log_admin_action(
                    admin=request.user,
                    action='delete',
                    model_name='Complaint',
                    object_id=complaint.id,
                    description=f"Deleted complaint: {complaint.name} - {complaint.category}"
                )
            
            complaints.delete()
            messages.success(request, f'Successfully deleted {deleted_count} complaint(s)')
        
        else:
            messages.error(request, 'Invalid action')
    
    except Exception as e:
        messages.error(request, f'Error processing request: {str(e)}')
    
    return redirect('pulse_admin:manage_complaints')

@staff_member_required
def get_dashboard_stats(request):
    """API endpoint for dashboard charts and stats - USING CORRECT MODEL"""
    
    # Get complaints by status
    status_stats = list(CitizenComplaint.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status'))
    
    # Get complaints by category
    category_stats = list(CitizenComplaint.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:10])
    
    # Get last 7 days data
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)
    
    daily_stats = []
    current_date = start_date
    while current_date <= end_date:
        count = CitizenComplaint.objects.filter(created_at__date=current_date).count()
        daily_stats.append({
            'date': current_date.strftime('%b %d'),
            'count': count
        })
        current_date += timedelta(days=1)
    
    return JsonResponse({
        'status_stats': status_stats,
        'category_stats': category_stats,
        'daily_stats': daily_stats,
    })

@staff_member_required
def get_complaint_stats(request):
    """Get real-time complaint statistics for dashboard widgets"""
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Today's stats
    today_complaints = CitizenComplaint.objects.filter(created_at__date=today).count()
    today_resolved = CitizenComplaint.objects.filter(status='Resolved', updated_at__date=today).count()
    
    # Yesterday's stats
    yesterday_complaints = CitizenComplaint.objects.filter(created_at__date=yesterday).count()
    yesterday_resolved = CitizenComplaint.objects.filter(status='Resolved', updated_at__date=yesterday).count()
    
    # Calculate trends
    complaint_trend = ((today_complaints - yesterday_complaints) / yesterday_complaints * 100) if yesterday_complaints > 0 else 0
    resolution_trend = ((today_resolved - yesterday_resolved) / yesterday_resolved * 100) if yesterday_resolved > 0 else 0
    
    # Get pending high priority complaints
    pending_high = CitizenComplaint.objects.filter(
        status__in=['Submitted', 'In Progress'], 
        ai_priority__in=['High']
    ).count()
    
    # Get total pending
    total_pending = CitizenComplaint.objects.filter(status__in=['Submitted', 'In Progress']).count()
    
    # Get total resolved
    total_resolved = CitizenComplaint.objects.filter(status='Resolved').count()
    
    return JsonResponse({
        'today_complaints': today_complaints,
        'today_resolved': today_resolved,
        'complaint_trend': round(complaint_trend, 1),
        'resolution_trend': round(resolution_trend, 1),
        'pending_high': pending_high,
        'total_pending': total_pending,
        'total_resolved': total_resolved,
        'total_complaints': CitizenComplaint.objects.count(),
    })

# Other functions that might reference ComplaintUpdate need to be simplified
# Since ComplaintUpdate model doesn't exist, we'll create simpler versions

@staff_member_required
def user_management(request):
    """View and manage users (citizens)"""
    
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Start with all users
    users = User.objects.filter(is_staff=False, is_active=True).order_by('-date_joined')
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Get user stats
    user_stats = []
    for user in users:
        total_complaints = CitizenComplaint.objects.filter(user=user).count()
        resolved_complaints = CitizenComplaint.objects.filter(user=user, status='Resolved').count()
        pending_complaints = CitizenComplaint.objects.filter(
            user=user,
            status__in=['Submitted', 'In Progress']
        ).count()
        
        user_stats.append({
            'user': user,
            'total_complaints': total_complaints,
            'resolved_complaints': resolved_complaints,
            'pending_complaints': pending_complaints,
            'resolution_rate': (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
        })
    
    # Pagination
    paginator = Paginator(user_stats, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate average resolution rate
    avg_resolution_rate = 0
    if user_stats:
        total_rate = sum(stat['resolution_rate'] for stat in user_stats)
        avg_resolution_rate = total_rate / len(user_stats)
    
    context = {
        'user_stats': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'total_users': users.count(),
        'avg_resolution_rate': avg_resolution_rate,
    }
    
    return render(request, 'pulse_admin/user_management.html', context)

@staff_member_required
def user_detail(request, user_id):
    """View user details and their complaints"""
    
    user = get_object_or_404(User, id=user_id)
    
    # Get user's complaints
    complaints = CitizenComplaint.objects.filter(user=user).order_by('-created_at')
    
    # Get statistics
    total_complaints = complaints.count()
    resolved_complaints = complaints.filter(status='Resolved').count()
    pending_complaints = complaints.filter(status__in=['Submitted', 'In Progress']).count()
    
    context = {
        'user': user,
        'complaints': complaints,
        'stats': {
            'total': total_complaints,
            'resolved': resolved_complaints,
            'pending': pending_complaints,
            'resolution_rate': (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
        }
    }
    
    return render(request, 'pulse_admin/user_detail.html', context)

# Simplified analytics dashboard (removed references to ComplaintUpdate)
@staff_member_required
def analytics_dashboard(request):
    """Advanced analytics dashboard"""
    
    # Time period filter
    period = request.GET.get('period', '7d')  # 7d, 30d, 90d, 1y
    
    if period == '7d':
        days = 7
    elif period == '30d':
        days = 30
    elif period == '90d':
        days = 90
    else:  # 1y
        days = 365
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Time series data
    time_series = []
    current_date = start_date
    while current_date <= end_date:
        # Complaints submitted
        submitted_count = CitizenComplaint.objects.filter(
            created_at__date=current_date
        ).count()
        
        # Complaints resolved
        resolved_count = CitizenComplaint.objects.filter(
            status='Resolved',
            updated_at__date=current_date
        ).count()
        
        time_series.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'submitted': submitted_count,
            'resolved': resolved_count
        })
        
        current_date += timedelta(days=1)
    
    # Category performance
    category_performance = []
    unique_categories = CitizenComplaint.objects.values_list('category', flat=True).distinct()
    for category in unique_categories[:10]:  # Limit to top 10
        category_complaints = CitizenComplaint.objects.filter(category=category)
        total = category_complaints.count()
        resolved = category_complaints.filter(status='Resolved').count()
        
        if total > 0:
            category_performance.append({
                'category': category,
                'total': total,
                'resolved': resolved,
                'resolution_rate': round(resolved / total * 100, 1),
                'pending': total - resolved
            })
    
    # Priority analysis
    priority_stats = []
    priority_choices = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    
    for priority_value in priority_choices:
        priority_complaints = CitizenComplaint.objects.filter(ai_priority=priority_value[0])
        total = priority_complaints.count()
        resolved = priority_complaints.filter(status='Resolved').count()
        
        priority_stats.append({
            'priority': priority_value[0],
            'total': total,
            'resolved': resolved,
            'pending': total - resolved,
            'resolution_rate': round(resolved / total * 100, 1) if total > 0 else 0
        })
    
    # Staff performance
    staff_performance = []
    for staff in User.objects.filter(is_staff=True, is_active=True):
        assigned_complaints = CitizenComplaint.objects.filter(assigned_to__icontains=staff.username)
        total = assigned_complaints.count()
        resolved = assigned_complaints.filter(status='Resolved').count()
        
        if total > 0:
            staff_performance.append({
                'staff': staff.get_full_name() or staff.username,
                'total': total,
                'resolved': resolved,
                'resolution_rate': round(resolved / total * 100, 1),
                'pending': total - resolved
            })
    
    context = {
        'time_series': json.dumps(time_series),
        'category_performance': category_performance,
        'priority_stats': priority_stats,
        'staff_performance': staff_performance,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'pulse_admin/analytics.html', context)

@require_POST
@staff_member_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = AdminNotification.objects.get(id=notification_id)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return JsonResponse({'success': True})
    except AdminNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@require_POST
@staff_member_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    AdminNotification.objects.filter(is_read=False).update(
        is_read=True, 
        read_at=timezone.now()
    )
    return JsonResponse({'success': True})

@staff_member_required
def export_complaints(request):
    """Export complaints to CSV"""
    import csv
    
    # Get all filter parameters from request
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    priority_filter = request.GET.get('priority', '')
    assigned_filter = request.GET.get('assigned', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')
    
    # Filter complaints
    complaints = CitizenComplaint.objects.all()
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    if priority_filter:
        complaints = complaints.filter(ai_priority=priority_filter)
    if assigned_filter:
        if assigned_filter == 'unassigned':
            complaints = complaints.filter(assigned_to__isnull=True)
        else:
            complaints = complaints.filter(assigned_to__icontains=assigned_filter)
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            complaints = complaints.filter(created_at__date__gte=date_from_obj)
        except:
            pass
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            complaints = complaints.filter(created_at__date__lte=date_to_obj)
        except:
            pass
    if search:
        complaints = complaints.filter(
            Q(complaint_id__icontains=search) |
            Q(category__icontains=search) |
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(details__icontains=search)
        )
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="complaints_export_{}.csv"'.format(
        datetime.now().strftime('%Y%m%d_%H%M%S')
    )
    
    writer = csv.writer(response)
    writer.writerow([
        'Complaint ID', 'Name', 'Email', 'Phone', 'Category', 'Sub Category',
        'Details', 'City', 'Pincode', 'Status', 'Priority', 'Assigned To',
        'Submitted Date', 'Updated Date', 'Resolution Details'
    ])
    
    for complaint in complaints:
        writer.writerow([
            complaint.display_id,
            complaint.name,
            complaint.email,
            complaint.phone or '',
            complaint.category,
            complaint.sub_category or '',
            complaint.details[:200] if complaint.details else '',
            complaint.city,
            complaint.pincode or '',
            complaint.status,
            complaint.ai_priority or '',
            complaint.assigned_to or '',
            complaint.created_at.strftime('%Y-%m-%d %H:%M') if complaint.created_at else '',
            complaint.updated_at.strftime('%Y-%m-%d %H:%M') if complaint.updated_at else '',
            complaint.resolution_details[:200] if complaint.resolution_details else '',
        ])
    
    return response

@staff_member_required
def category_management(request):
    """Manage complaint categories"""
    
    # Get existing categories from complaints
    existing_categories = list(CitizenComplaint.objects.values_list('category', flat=True).distinct().order_by('category'))
    
    # Get or create Category model instances
    categories = []
    for cat_name in existing_categories:
        category, created = Category.objects.get_or_create(
            name=cat_name,
            defaults={'is_active': True}
        )
        categories.append(category)
    
    # Also get any predefined categories
    categories.extend(Category.objects.exclude(name__in=existing_categories).order_by('name'))
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_category':
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            
            if name:
                Category.objects.create(
                    name=name,
                    description=description,
                    is_active=True
                )
                messages.success(request, f'Category "{name}" added successfully')
                return redirect('pulse_admin:category_management')
        
        elif action == 'edit_category':
            category_id = request.POST.get('category_id')
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            
            try:
                category = Category.objects.get(id=category_id)
                category.name = name
                category.description = description
                category.save()
                messages.success(request, f'Category updated successfully')
                return redirect('pulse_admin:category_management')
            except Category.DoesNotExist:
                messages.error(request, 'Category not found')
        
        elif action == 'toggle_category':
            category_id = request.POST.get('category_id')
            try:
                category = Category.objects.get(id=category_id)
                category.is_active = not category.is_active
                category.save()
                status = "activated" if category.is_active else "deactivated"
                messages.success(request, f'Category "{category.name}" {status}')
                return redirect('pulse_admin:category_management')
            except Category.DoesNotExist:
                messages.error(request, 'Category not found')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'pulse_admin/category_management.html', context)

# Additional view for complaints dashboard
@staff_member_required
def complaints_dashboard(request):
    """Alternative view for complaints with enhanced dashboard"""
    return manage_complaints(request)  # Reuse the same function

# ========== DEPARTMENT VIEWS ==========

@login_required
def department_dashboard(request):
    """Department User Dashboard"""
    # Check if user is a department user
    try:
        dept_user = DepartmentUser.objects.get(user=request.user)
        if not dept_user.is_active:
            messages.error(request, 'Your department account is inactive')
            return redirect('logout')
        
        # Get department complaints
        department_complaints = CitizenComplaint.objects.filter(
            category=dept_user.department.name  # Use category field to match department
        ).order_by('-created_at')
        
        # Get statistics
        total = department_complaints.count()
        pending = department_complaints.filter(status='Submitted').count()
        in_progress = department_complaints.filter(status='In Progress').count()
        resolved = department_complaints.filter(status='Resolved').count()
        
        # Get high priority complaints
        high_priority = department_complaints.filter(
            ai_priority='High',
            status__in=['Submitted', 'In Progress']
        ).order_by('-created_at')[:10]
        
        # Get recent complaints
        recent_complaints = department_complaints[:10]
        
        return render(request, 'pulse_admin/department_dashboard.html', {
            'user': request.user,
            'dept_user': dept_user,
            'department': dept_user.department,
            'total_complaints': total,
            'pending_complaints': pending,
            'in_progress_complaints': in_progress,
            'resolved_complaints': resolved,
            'high_priority_complaints': high_priority,
            'recent_complaints': recent_complaints,
        })
        
    except DepartmentUser.DoesNotExist:
        messages.error(request, 'You are not authorized to access department dashboard')
        return redirect('citizen_dashboard')

@login_required
def department_complaints(request):
    """View complaints for department"""
    try:
        dept_user = DepartmentUser.objects.get(user=request.user)
        
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        search = request.GET.get('search', '')
        
        # Get department complaints
        complaints = CitizenComplaint.objects.filter(
            category=dept_user.department.name
        ).order_by('-created_at')
        
        # Apply filters
        if status_filter:
            complaints = complaints.filter(status=status_filter)
        if priority_filter:
            complaints = complaints.filter(ai_priority=priority_filter)
        if search:
            complaints = complaints.filter(
                Q(complaint_id__icontains=search) |
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(details__icontains=search)
            )
        
        # Pagination
        paginator = Paginator(complaints, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'pulse_admin/department_complaints.html', {
            'dept_user': dept_user,
            'department': dept_user.department,
            'complaints': page_obj,
            'page_obj': page_obj,
            'status_filter': status_filter,
            'priority_filter': priority_filter,
            'search': search,
        })
        
    except DepartmentUser.DoesNotExist:
        messages.error(request, 'You are not authorized')
        return redirect('citizen_dashboard')

@login_required
def department_complaint_detail(request, complaint_id):
    """View and update department complaint"""
    try:
        dept_user = DepartmentUser.objects.get(user=request.user)
        complaint = get_object_or_404(CitizenComplaint, complaint_id=complaint_id)
        
        # Check if complaint belongs to this department
        if complaint.category != dept_user.department.name:
            messages.error(request, 'This complaint does not belong to your department')
            return redirect('department_dashboard')
        
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'update_status':
                new_status = request.POST.get('status')
                resolution_details = request.POST.get('resolution_details', '')
                
                if new_status and new_status != complaint.status:
                    complaint.status = new_status
                    if resolution_details:
                        complaint.resolution_details = resolution_details
                    complaint.updated_at = timezone.now()
                    complaint.save()
                    
                    messages.success(request, f'Complaint status updated to {new_status}')
                    return redirect('department_complaint_detail', complaint_id=complaint_id)
            
            elif action == 'add_comment':
                comment = request.POST.get('comment', '').strip()
                if comment:
                    # Create a simple comment (you might want to create a Comment model)
                    complaint.resolution_details = f"{complaint.resolution_details or ''}\n\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {request.user.username}: {comment}"
                    complaint.save()
                    messages.success(request, 'Comment added successfully')
                    return redirect('department_complaint_detail', complaint_id=complaint_id)
        
        return render(request, 'pulse_admin/department_complaint_detail.html', {
            'dept_user': dept_user,
            'complaint': complaint,
            'status_choices': [
                ('Submitted', 'Submitted'),
                ('In Progress', 'In Progress'),
                ('Resolved', 'Resolved'),
                ('Closed', 'Closed'),
            ],
        })
        
    except DepartmentUser.DoesNotExist:
        messages.error(request, 'You are not authorized')
        return redirect('citizen_dashboard')

@login_required
def department_profile(request):
    """Department user profile"""
    try:
        dept_user = DepartmentUser.objects.get(user=request.user)
        
        if request.method == 'POST':
            # Update basic info
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            
            messages.success(request, 'Profile updated successfully')
            return redirect('department_profile')
        
        return render(request, 'pulse_admin/department_profile.html', {
            'dept_user': dept_user,
            'department': dept_user.department,
        })
        
    except DepartmentUser.DoesNotExist:
        messages.error(request, 'You are not authorized')
        return redirect('citizen_dashboard')
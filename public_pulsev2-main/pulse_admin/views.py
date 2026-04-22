from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import json
import csv
from complaints.models import Complaint

@staff_member_required
def admin_dashboard(request):
    today = timezone.now().date()
    
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status__in=['Submitted', 'In Progress']).count()
    resolved_today = Complaint.objects.filter(status='Resolved', updated_at__date=today).count()
    
    status_data = {
        'Submitted': Complaint.objects.filter(status='Submitted').count(),
        'In Progress': Complaint.objects.filter(status='In Progress').count(),
        'Resolved': Complaint.objects.filter(status='Resolved').count(),
        'Closed': Complaint.objects.filter(status='Closed').count(),
    }
    
    category_stats = list(Complaint.objects.values('category').annotate(count=Count('id')).order_by('-count')[:5])
    high_priority_complaints = Complaint.objects.filter(ai_priority='High', status__in=['Submitted', 'In Progress']).order_by('-created_at')[:10]
    recent_complaints = Complaint.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_today': resolved_today,
        'user_satisfaction': 4.2,
        'status_data': json.dumps(status_data),
        'category_stats': category_stats,
        'critical_complaints': high_priority_complaints,
        'recent_complaints': recent_complaints,
        'today': today,
    }
    return render(request, 'pulse_admin/dashboard.html', context)

@staff_member_required
def manage_complaints(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    priority_filter = request.GET.get('priority', '')
    search = request.GET.get('search', '')
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    if priority_filter:
        complaints = complaints.filter(ai_priority=priority_filter)
    if search:
        complaints = complaints.filter(Q(complaint_id__icontains=search) | Q(name__icontains=search) | Q(email__icontains=search))
    
    categories = Complaint.objects.values_list('category', flat=True).distinct()
    
    context = {
        'complaints': complaints,
        'total_complaints': complaints.count(),
        'pending_count': complaints.filter(status__in=['Submitted', 'In Progress']).count(),
        'resolved_count': complaints.filter(status='Resolved').count(),
        'high_priority_count': complaints.filter(ai_priority='High').count(),
        'categories': categories,
    }
    return render(request, 'pulse_admin/manage_complaints.html', context)

@staff_member_required
def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            complaint.status = new_status
            complaint.updated_at = timezone.now()
            complaint.save()
            messages.success(request, f'Complaint status updated to {new_status}')
            return redirect('pulse_admin:complaint_detail', complaint_id=complaint_id)
    return render(request, 'pulse_admin/complaint_detail.html', {'complaint': complaint})

@staff_member_required
def export_complaints(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="complaints_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Complaint ID', 'Name', 'Email', 'Phone', 'Category', 'Details', 'City', 'Status', 'Priority', 'Submitted Date'])
    for complaint in complaints:
        writer.writerow([
            complaint.complaint_id, complaint.name, complaint.email, complaint.phone or '',
            complaint.category, complaint.details[:200] if complaint.details else '',
            complaint.city or '', complaint.status, complaint.ai_priority or 'Medium',
            complaint.created_at.strftime('%Y-%m-%d %H:%M') if complaint.created_at else '',
        ])
    return response

@staff_member_required
def bulk_update_complaints(request):
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        assigned_to = request.POST.get('assigned_to', '')
        if complaint_id and assigned_to:
            try:
                complaint = Complaint.objects.get(complaint_id=complaint_id)
                complaint.assigned_to = assigned_to
                complaint.save()
                return JsonResponse({'success': True})
            except Complaint.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Complaint not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@staff_member_required
def update_complaint_status_ajax(request):
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        status = request.POST.get('status')
        try:
            complaint = Complaint.objects.get(complaint_id=complaint_id)
            complaint.status = status
            complaint.updated_at = timezone.now()
            complaint.save()
            return JsonResponse({'success': True, 'message': f'Status updated to {status}'})
        except Complaint.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Complaint not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

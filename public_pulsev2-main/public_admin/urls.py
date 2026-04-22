from django.urls import path
from . import views

app_name = 'pulse_admin'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Complaint Management
    path('complaints/', views.manage_complaints, name='manage_complaints'),
    path('complaints/dashboard/', views.complaints_dashboard, name='complaints_dashboard'),
    path('complaints/bulk-update/', views.bulk_update_complaints, name='bulk_update_complaints'),
    path('complaints/update-status/', views.update_complaint_status_ajax, name='update_complaint_status_ajax'),
    path('complaints/<str:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/export/', views.export_complaints, name='export_complaints'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('stats/dashboard/', views.get_dashboard_stats, name='dashboard_stats'),
    path('stats/complaints/', views.get_complaint_stats, name='complaint_stats'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    
    # Category Management
    path('categories/', views.category_management, name='category_management'),
    
    # Notifications
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
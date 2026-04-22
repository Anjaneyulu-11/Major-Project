from django.urls import path
from . import views

app_name = 'department'

urlpatterns = [
    # Department Dashboard
    path('', views.department_dashboard, name='dashboard'),
    path('dashboard/', views.department_dashboard, name='department_dashboard'),
    
    # Complaint Management (Department specific)
    path('complaints/', views.department_complaints, name='complaints'),
    path('complaints/pending/', views.department_pending_complaints, name='pending_complaints'),
    path('complaints/in-progress/', views.department_inprogress_complaints, name='inprogress_complaints'),
    path('complaints/resolved/', views.department_resolved_complaints, name='resolved_complaints'),
    path('complaints/<str:complaint_id>/', views.department_complaint_detail, name='complaint_detail'),
    path('complaints/<str:complaint_id>/resolve/', views.resolve_complaint, name='resolve_complaint'),
    path('complaints/<str:complaint_id>/assign/', views.assign_complaint, name='assign_complaint'),
    path('complaints/<str:complaint_id>/comment/', views.add_comment, name='add_comment'),
    
    # Analytics
    path('analytics/', views.department_analytics, name='analytics'),
    path('stats/', views.department_stats, name='stats'),
    
    # User Management (Department staff)
    path('staff/', views.department_staff, name='staff'),
    path('profile/', views.department_profile, name='profile'),
    
    # Reports
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/download/', views.download_report, name='download_report'),
]
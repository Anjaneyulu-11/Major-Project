from django.urls import path
from . import views

app_name = 'pulse_admin'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('complaints/', views.manage_complaints, name='manage_complaints'),
    path('complaint/<str:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('export/', views.export_complaints, name='export_complaints'),
    path('bulk-update/', views.bulk_update_complaints, name='bulk_update_complaints'),
    path('update-status/', views.update_complaint_status_ajax, name='update_complaint_status_ajax'),
]

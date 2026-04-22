# complaints/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main complaint handling
    path('lodge/', views.lodge_complaint, name='lodge_complaint'),
    path('success/<str:complaint_id>/', views.complaint_success, name='complaint_success'),
    path('track/', views.track_complaint, name='track_complaint'),
    # REMOVE THIS LINE: path('track/results/', views.track_results, name='track_results'),
    
    # Notification endpoints
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/unread-count/', views.get_unread_count, name='get_unread_count'),
    
    # Testing and debugging endpoints
    path('test-email/', views.test_email_view, name='test_email'),
    path('direct-email/', views.direct_email_test, name='direct_email'),
    path('debug/', views.emergency_debug, name='emergency_debug'),
    path('direct-test/', views.direct_test_complaint, name='direct_test_complaint'),
    path('test-email-config/', views.test_email_configuration, name='test_email_configuration'),
    path('quick-email-test/', views.quick_email_test, name='quick_email_test'),
    path('test-send/', views.test_send_to_user, name='test_send'),
]

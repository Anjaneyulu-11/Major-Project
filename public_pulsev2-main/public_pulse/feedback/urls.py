from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Feedback Management
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/<int:feedback_id>/', views.feedback_detail, name='feedback_detail'),
    path('feedback/<int:feedback_id>/respond/', views.respond_to_feedback, name='respond_to_feedback'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    
    # API Endpoints
    path('api/categories/', views.get_categories, name='get_categories'),
    
    # Home
    path('', views.home_view, name='home'),
]
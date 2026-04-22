# public_pulse/landing_page/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ========== PUBLIC PAGES ==========
    path('', views.index, name='home'),  # Home page
    path('index/', views.index, name='index'),  # Alternative home URL
    path('register/', views.register, name='register'),  # Registration
    path('login/', views.user_login, name='login'),  # Login
    path('logout/', views.user_logout, name='logout'),  # Logout
    
    # ========== DASHBOARD PAGES ==========
    path('dashboard/', views.dashboard, name='dashboard'),  # Main dashboard (redirects based on role)
    path('citizen-dashboard/', views.citizen_dashboard, name='citizen_dashboard'),  # Citizen dashboard
    path('official-dashboard/', views.official_dashboard, name='official_dashboard'),  # Official dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Admin dashboard
    
    # ========== USER PROFILE ==========
    path('profile/', views.profile, name='profile'),  # Profile page
    path('settings/', views.profile, name='settings'),  # ADD THIS LINE: Settings page (alias for profile)
    path('change-password/', views.change_password, name='change_password'),  # Change password
    
    # ========== COMPLAINT WORKFLOW ==========
    path('lodge-complaint/', views.lodge_complaint, name='lodge_complaint'),
    path('new-complaint/', views.lodge_complaint, name='new_complaint'),  # Alternative URL
    path('track-complaint/', views.track_complaint, name='track_complaint'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('complaints/', views.my_complaints, name='complaints'),  # Alternative URL
    path('complaint/<str:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    
    # ========== STATIC PAGES ==========
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    
    # ========== ADMIN PAGES ==========
    path('admin/complaints/', views.manage_complaints, name='manage_complaints'),
    path('admin/complaint/<str:complaint_id>/', views.admin_complaint_detail, name='admin_complaint_detail'),
    path('admin/manage-complaints/', views.manage_complaints, name='admin_manage_complaints'),  # Alternative URL
    
    # ========== AI ASSISTANT ==========
    path('ai-chat/', views.chatbot_assistant, name='ai_chat'),
    path('chatbot/', views.chatbot_assistant, name='chatbot'),
    path('ai-assistant/', views.chatbot_assistant, name='ai_assistant'),  # Alternative URL
    
    # ========== DEPARTMENT ROUTES ==========
    path('department/', views.department_portal, name='department_portal'),
    path('department/<slug:dept_slug>/login/', views.department_login, name='department_login'),
    path('department/<slug:dept_slug>/dashboard/', views.department_dashboard, name='department_dashboard'),
    path('department/complaint/<int:complaint_id>/', views.department_complaint_detail, name='department_complaint_detail'),
    
    # ========== ADDITIONAL ROUTES FOR TEMPLATES ==========
    path('history/', views.my_complaints, name='history'),
]
from django.urls import path 
from . import views 
from .ai_views import ai_chat_api 
 
urlpatterns = [ 
    path('', views.chatbot, name='chatbot'), 
    path('ai-chat/', ai_chat_api, name='ai_chat_api'), 
    path('user_profile', views.user_profile, name='user_profile'), 
    path('chat_history', views.chat_history, name='chat_history'), 
    path('status_tracking', views.status_tracking, name='status_tracking'), 
    path('change-password', views.change_password, name='change_password') 
] 

from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    # Public department information
    path('', views.departments_list, name='list'),
    path('<str:category>/', views.department_info, name='info'),
    path('<str:category>/complaints/', views.department_public_complaints, name='complaints'),
    path('<str:category>/performance/', views.department_performance, name='performance'),
    path('<str:category>/contact/', views.department_contact, name='contact'),
]
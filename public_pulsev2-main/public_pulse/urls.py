from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.i18n import set_language

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('pulse_admin/', include('pulse_admin.urls')),
    
    # i18n - Use Django's built-in set_language
    path('i18n/', include('django.conf.urls.i18n')),
    
    # Landing page
    path('', include('landing_page.urls')),
    
    # Complaints
    path('complaints/', include('complaints.urls')),
    
    # Redirects
    path('lodge-complaint/', RedirectView.as_view(url='/complaints/lodge/', permanent=True)),
    path('track-complaint/', RedirectView.as_view(url='/complaints/track/', permanent=True)),
    path('home/', RedirectView.as_view(url='/', permanent=True)),
    path('index/', RedirectView.as_view(url='/', permanent=True)),
    path('login/', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('register/', RedirectView.as_view(pattern_name='register', permanent=False)),
]

# Static and media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = 'landing_page.views.handler404'
handler500 = 'landing_page.views.handler500'
handler403 = 'landing_page.views.handler403'
handler400 = 'landing_page.views.handler400'
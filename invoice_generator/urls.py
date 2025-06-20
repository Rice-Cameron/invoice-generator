"""
URL configuration for invoice_generator project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from core import views as core_views

# Customize the admin site
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'Invoice Generator Administration')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'Invoice Generator Admin')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Welcome to Invoice Generator Administration')

def root_view(request):
    """Root view that shows homepage or API info based on Accept header."""
    if request.headers.get('Accept') == 'application/json':
        # Return JSON for API clients
        return JsonResponse({
            'message': 'Time-Tracked Invoice Generator API',
            'version': '1.0.0',
            'endpoints': {
                'admin': '/admin/',
                'api': '/api/',
                'authentication': '/api/token/',
                'clients': '/api/clients/',
                'projects': '/api/projects/',
                'time_entries': '/api/time-entries/',
                'invoices': '/api/invoices/',
                'stripe': '/api/stripe/',
            },
            'documentation': 'See README.md for API documentation'
        })
    else:
        # Show HTML homepage for web browsers
        return render(request, 'home.html')

def api_docs_view(request):
    """API documentation view."""
    return render(request, 'api_docs.html')

urlpatterns = [
    path('', root_view, name='home'),
    path('dashboard/', core_views.dashboard_view, name='dashboard'),
    path('login/', core_views.login_view, name='login'),
    path('logout/', core_views.logout_view, name='logout'),
    path('register/', core_views.register_view, name='register'),
    path('api-docs/', api_docs_view, name='api-docs'),
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('api/', include('core.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/time-entries/', include('time_entries.urls')),
    path('api/invoices/', include('invoices.urls')),
    path('api/stripe/', include('stripe_integration.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
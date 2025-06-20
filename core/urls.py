from django.urls import path
from django.http import JsonResponse
from .views import (
    UserRegistrationView,
    UserProfileView,
    ChangePasswordView,
    user_dashboard
)

def api_root(request):
    """Root API view that provides endpoint information."""
    return JsonResponse({
        'message': 'Time-Tracked Invoice Generator API',
        'version': '1.0.0',
        'endpoints': {
            'authentication': {
                'login': '/api/token/',
                'refresh': '/api/token/refresh/',
            },
            'users': {
                'register': '/api/register/',
                'profile': '/api/profile/',
                'change_password': '/api/change-password/',
                'dashboard': '/api/dashboard/',
            },
            'clients': '/api/clients/',
            'projects': '/api/projects/',
            'time_entries': '/api/time-entries/',
            'invoices': '/api/invoices/',
            'stripe': '/api/stripe/',
        },
        'documentation': '/api-docs/'
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('dashboard/', user_dashboard, name='user-dashboard'),
] 
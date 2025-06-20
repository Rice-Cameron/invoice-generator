from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)
from .forms import CustomUserCreationForm

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for user profile management.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    View for changing user password.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    """
    View for user dashboard with summary statistics.
    """
    user = request.user
    
    # Get summary statistics
    from clients.models import Client
    from projects.models import Project
    from time_entries.models import TimeEntry
    from invoices.models import Invoice
    
    total_clients = Client.objects.filter(user=user).count()
    total_projects = Project.objects.filter(user=user).count()
    total_time_entries = TimeEntry.objects.filter(user=user).count()
    total_invoices = Invoice.objects.filter(user=user).count()
    
    # Get recent activity
    recent_time_entries = TimeEntry.objects.filter(user=user).order_by('-date')[:5]
    recent_invoices = Invoice.objects.filter(user=user).order_by('-created_at')[:5]
    
    dashboard_data = {
        'summary': {
            'total_clients': total_clients,
            'total_projects': total_projects,
            'total_time_entries': total_time_entries,
            'total_invoices': total_invoices,
        },
        'recent_time_entries': [
            {
                'id': entry.id,
                'project': entry.project.name,
                'date': entry.date,
                'hours': float(entry.hours),
                'description': entry.description
            } for entry in recent_time_entries
        ],
        'recent_invoices': [
            {
                'id': invoice.id,
                'client': invoice.client.name,
                'amount': float(invoice.total_amount),
                'status': invoice.status,
                'created_at': invoice.created_at
            } for invoice in recent_invoices
        ]
    }
    
    return Response(dashboard_data)


# Template-based views

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect('dashboard')
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home') 
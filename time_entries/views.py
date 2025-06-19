from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from .models import TimeEntry
from .serializers import (
    TimeEntrySerializer, 
    TimeEntryListSerializer, 
    TimeEntryDetailSerializer,
    TimeEntryBulkCreateSerializer
)


class TimeEntryListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating time entries.
    """
    serializer_class = TimeEntrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'date', 'is_billable', 'project__client']
    search_fields = ['description', 'project__name', 'tags']
    ordering_fields = ['date', 'hours', 'hourly_rate', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        return TimeEntry.objects.filter(user=self.request.user).select_related('project', 'project__client')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TimeEntryListSerializer
        return TimeEntrySerializer


class TimeEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a specific time entry.
    """
    serializer_class = TimeEntryDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TimeEntry.objects.filter(user=self.request.user).select_related('project', 'project__client')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TimeEntrySerializer
        return TimeEntryDetailSerializer


class TimeEntryBulkCreateView(generics.CreateAPIView):
    """
    View for bulk creating time entries.
    """
    serializer_class = TimeEntryBulkCreateSerializer
    permission_classes = [IsAuthenticated]


class TimeEntryByProjectView(generics.ListAPIView):
    """
    View for listing time entries by project.
    """
    serializer_class = TimeEntryListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return TimeEntry.objects.filter(
            user=self.request.user,
            project_id=project_id
        ).select_related('project', 'project__client')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def time_entry_summary(request):
    """
    View for getting time entry summary statistics.
    """
    user = request.user
    period = request.GET.get('period', 'month')  # week, month, year
    
    # Calculate date range
    today = datetime.now().date()
    if period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=30)
    
    # Get time entries for the period
    time_entries = TimeEntry.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=today
    )
    
    # Calculate summary
    total_hours = time_entries.aggregate(total=Sum('hours'))['total'] or 0
    total_billable_hours = time_entries.filter(is_billable=True).aggregate(total=Sum('hours'))['total'] or 0
    total_amount = time_entries.filter(is_billable=True).aggregate(
        total=Sum('hours' * 'hourly_rate')
    )['total'] or 0
    
    # Get top projects
    top_projects = time_entries.values('project__name').annotate(
        hours=Sum('hours')
    ).order_by('-hours')[:5]
    
    summary_data = {
        'period': period,
        'start_date': start_date,
        'end_date': today,
        'total_hours': float(total_hours),
        'total_billable_hours': float(total_billable_hours),
        'total_amount': float(total_amount),
        'top_projects': list(top_projects)
    }
    
    return Response(summary_data) 
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Project
from .serializers import ProjectSerializer, ProjectListSerializer, ProjectDetailSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'auto_invoice', 'invoice_frequency', 'client']
    search_fields = ['name', 'description', 'client__name']
    ordering_fields = ['name', 'status', 'created_at', 'start_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).select_related('client')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectSerializer


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a specific project.
    """
    serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).select_related('client')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectSerializer
        return ProjectDetailSerializer
    
    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        
        # Check if project has associated time entries
        if project.time_entries.exists():
            return Response(
                {'error': 'Cannot delete project with associated time entries. Please delete time entries first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)


class ProjectByClientView(generics.ListAPIView):
    """
    View for listing projects by client.
    """
    serializer_class = ProjectListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        return Project.objects.filter(
            user=self.request.user,
            client_id=client_id
        ).select_related('client') 
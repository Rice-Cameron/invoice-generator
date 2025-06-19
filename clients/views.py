from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Client
from .serializers import ClientSerializer, ClientListSerializer


class ClientListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating clients.
    """
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'recurring_invoice', 'recurring_frequency']
    search_fields = ['name', 'company_name', 'email']
    ordering_fields = ['name', 'company_name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClientListSerializer
        return ClientSerializer


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a specific client.
    """
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        client = self.get_object()
        
        # Check if client has associated projects or invoices
        if client.projects.exists():
            return Response(
                {'error': 'Cannot delete client with associated projects. Please delete projects first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if client.invoices.exists():
            return Response(
                {'error': 'Cannot delete client with associated invoices. Please delete invoices first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs) 
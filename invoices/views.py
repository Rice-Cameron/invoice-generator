from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Invoice
from .serializers import (
    InvoiceSerializer, 
    InvoiceListSerializer, 
    InvoiceDetailSerializer,
    InvoiceCreateFromTimeEntriesSerializer,
    InvoiceSendSerializer
)
from .services.invoice_service import InvoiceService


class InvoiceListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating invoices.
    """
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'client', 'project', 'issue_date']
    search_fields = ['invoice_number', 'client__name', 'project__name']
    ordering_fields = ['invoice_number', 'issue_date', 'due_date', 'total_amount', 'created_at']
    ordering = ['-issue_date', '-created_at']
    
    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user).select_related('client', 'project')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return InvoiceListSerializer
        return InvoiceSerializer


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting a specific invoice.
    """
    serializer_class = InvoiceDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user).select_related('client', 'project')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InvoiceSerializer
        return InvoiceDetailSerializer


class InvoiceCreateFromTimeEntriesView(generics.CreateAPIView):
    """
    View for creating invoices from time entries.
    """
    serializer_class = InvoiceCreateFromTimeEntriesSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            invoice = InvoiceService.create_invoice_from_time_entries(
                user=request.user,
                data=serializer.validated_data
            )
            
            # Generate PDF
            InvoiceService.generate_pdf(invoice)
            
            return Response({
                'message': 'Invoice created successfully',
                'invoice': InvoiceDetailSerializer(invoice, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InvoiceSendView(generics.GenericAPIView):
    """
    View for sending invoices via email.
    """
    serializer_class = InvoiceSendSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            InvoiceService.send_invoice_email(invoice, serializer.validated_data)
            return Response({'message': 'Invoice sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_pdf_download(request, pk):
    """
    View for downloading invoice PDF.
    """
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    # Generate PDF if not exists
    if not invoice.pdf_file:
        InvoiceService.generate_pdf(invoice)
    
    # Return PDF file
    response = HttpResponse(invoice.pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invoice_mark_paid(request, pk):
    """
    View for marking invoice as paid.
    """
    invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
    
    payment_method = request.data.get('payment_method', '')
    stripe_payment_intent_id = request.data.get('stripe_payment_intent_id', '')
    
    InvoiceService.mark_as_paid(invoice, payment_method, stripe_payment_intent_id)
    
    return Response({'message': 'Invoice marked as paid'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_summary(request):
    """
    View for getting invoice summary statistics.
    """
    period = request.GET.get('period', 'month')
    summary = InvoiceService.get_invoice_summary(request.user, period)
    return Response(summary)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def overdue_invoices(request):
    """
    View for getting overdue invoices.
    """
    overdue = InvoiceService.get_overdue_invoices(request.user)
    serializer = InvoiceListSerializer(overdue, many=True, context={'request': request})
    return Response(serializer.data) 
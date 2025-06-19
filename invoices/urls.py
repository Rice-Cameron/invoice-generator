from django.urls import path
from .views import (
    InvoiceListCreateView,
    InvoiceDetailView,
    InvoiceCreateFromTimeEntriesView,
    InvoiceSendView,
    invoice_pdf_download,
    invoice_mark_paid,
    invoice_summary,
    overdue_invoices
)

urlpatterns = [
    path('', InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('create-from-time-entries/', InvoiceCreateFromTimeEntriesView.as_view(), name='invoice-create-from-time-entries'),
    path('<int:pk>/send/', InvoiceSendView.as_view(), name='invoice-send'),
    path('<int:pk>/pdf/', invoice_pdf_download, name='invoice-pdf-download'),
    path('<int:pk>/mark-paid/', invoice_mark_paid, name='invoice-mark-paid'),
    path('summary/', invoice_summary, name='invoice-summary'),
    path('overdue/', overdue_invoices, name='overdue-invoices'),
] 
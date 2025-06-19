from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .pdf_generator import InvoicePDFGenerator
from ..models import Invoice, InvoiceItem
from time_entries.models import TimeEntry
from django.db import models


class InvoiceService:
    """
    Service for invoice-related business logic.
    """
    
    @staticmethod
    def create_invoice_from_time_entries(user, data):
        """
        Create an invoice from time entries within a date range.
        """
        with transaction.atomic():
            # Get time entries for the specified date range and client
            time_entries = TimeEntry.objects.filter(
                user=user,
                client=data['client'],
                date__gte=data['start_date'],
                date__lte=data['end_date'],
                is_billable=True
            ).select_related('project')
            
            if not time_entries.exists():
                raise ValueError("No billable time entries found for the specified date range.")
            
            # Create invoice
            invoice_data = {
                'user': user,
                'client': data['client'],
                'project': data.get('project'),
                'issue_date': data.get('issue_date', timezone.now().date()),
                'due_date': data.get('due_date', timezone.now().date() + timedelta(days=30)),
                'tax_rate': data.get('tax_rate', 0.00),
                'discount_rate': data.get('discount_rate', 0.00),
                'notes': data.get('notes', ''),
                'terms_conditions': data.get('terms_conditions', ''),
            }
            
            invoice = Invoice.objects.create(**invoice_data)
            
            # Group time entries by project and create invoice items
            project_entries = {}
            for entry in time_entries:
                project_key = entry.project.id if entry.project else 'no_project'
                if project_key not in project_entries:
                    project_entries[project_key] = {
                        'project': entry.project,
                        'entries': [],
                        'total_hours': 0,
                        'total_amount': 0
                    }
                
                project_entries[project_key]['entries'].append(entry)
                project_entries[project_key]['total_hours'] += entry.hours
                project_entries[project_key]['total_amount'] += entry.total_amount
            
            # Create invoice items
            subtotal = 0
            for project_data in project_entries.values():
                project = project_data['project']
                total_hours = project_data['total_hours']
                total_amount = project_data['total_amount']
                
                # Create description from time entries
                descriptions = []
                for entry in project_data['entries']:
                    descriptions.append(f"{entry.date}: {entry.description}")
                
                description = f"Time tracking for {project.name if project else 'General Work'}\n" + "\n".join(descriptions)
                
                # Create invoice item
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=description,
                    quantity=total_hours,
                    unit_price=total_amount / total_hours if total_hours > 0 else 0,
                    total=total_amount
                )
                
                subtotal += total_amount
            
            # Update invoice subtotal
            invoice.subtotal = subtotal
            invoice.save()
            
            return invoice
    
    @staticmethod
    def generate_pdf(invoice):
        """
        Generate PDF for an invoice.
        """
        generator = InvoicePDFGenerator(invoice)
        return generator.generate_pdf()
    
    @staticmethod
    def send_invoice_email(invoice, data):
        """
        Send invoice via email.
        """
        from django.core.mail import EmailMessage
        from django.template.loader import render_to_string
        
        # Generate PDF if not exists
        if not invoice.pdf_file:
            InvoiceService.generate_pdf(invoice)
        
        # Prepare email
        subject = data.get('email_subject', f'Invoice {invoice.invoice_number} from {invoice.user.get_full_name()}')
        message = data.get('email_message', '')
        
        # Create email content
        email_context = {
            'invoice': invoice,
            'user': invoice.user,
            'client': invoice.client,
            'message': message
        }
        
        email_content = render_to_string('invoices/email_template.html', email_context)
        
        # Send email to client
        if data.get('send_to_client', True):
            email = EmailMessage(
                subject=subject,
                body=email_content,
                from_email=invoice.user.email,
                to=[invoice.client.email],
                reply_to=[invoice.user.email]
            )
            email.attach_file(invoice.pdf_file.path)
            email.send()
        
        # Send copy to user
        if data.get('send_copy_to_user', False):
            email = EmailMessage(
                subject=f"Copy: {subject}",
                body=email_content,
                from_email=invoice.user.email,
                to=[invoice.user.email]
            )
            email.attach_file(invoice.pdf_file.path)
            email.send()
        
        # Update invoice status
        invoice.status = 'sent'
        invoice.save()
        
        return True
    
    @staticmethod
    def mark_as_paid(invoice, payment_method='', stripe_payment_intent_id=''):
        """
        Mark invoice as paid.
        """
        invoice.status = 'paid'
        invoice.paid_date = timezone.now().date()
        invoice.payment_method = payment_method
        invoice.stripe_payment_intent_id = stripe_payment_intent_id
        invoice.save()
        
        return invoice
    
    @staticmethod
    def get_overdue_invoices(user):
        """
        Get all overdue invoices for a user.
        """
        return Invoice.objects.filter(
            user=user,
            status='sent',
            due_date__lt=timezone.now().date()
        ).select_related('client', 'project')
    
    @staticmethod
    def get_invoice_summary(user, period='month'):
        """
        Get invoice summary statistics for a user.
        """
        today = timezone.now().date()
        
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)
        
        invoices = Invoice.objects.filter(
            user=user,
            issue_date__gte=start_date,
            issue_date__lte=today
        )
        
        total_invoices = invoices.count()
        total_amount = invoices.aggregate(total=models.Sum('total_amount'))['total'] or 0
        paid_amount = invoices.filter(status='paid').aggregate(total=models.Sum('total_amount'))['total'] or 0
        overdue_amount = InvoiceService.get_overdue_invoices(user).aggregate(total=models.Sum('total_amount'))['total'] or 0
        
        return {
            'period': period,
            'total_invoices': total_invoices,
            'total_amount': float(total_amount),
            'paid_amount': float(paid_amount),
            'overdue_amount': float(overdue_amount),
            'outstanding_amount': float(total_amount - paid_amount)
        } 
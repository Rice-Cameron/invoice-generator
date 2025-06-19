from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Invoice
from .services.invoice_service import InvoiceService
from clients.models import Client
from projects.models import Project


@shared_task
def generate_recurring_invoices():
    """
    Task to generate recurring invoices for clients and projects.
    """
    today = timezone.now().date()
    
    # Process client recurring invoices
    clients_with_recurring = Client.objects.filter(
        recurring_invoice=True,
        next_invoice_date__lte=today,
        is_active=True
    )
    
    for client in clients_with_recurring:
        try:
            # Get time entries for the period
            if client.recurring_frequency == 'weekly':
                start_date = today - timedelta(days=7)
            elif client.recurring_frequency == 'monthly':
                start_date = today - timedelta(days=30)
            elif client.recurring_frequency == 'quarterly':
                start_date = today - timedelta(days=90)
            else:
                continue
            
            # Create invoice from time entries
            invoice_data = {
                'client': client,
                'start_date': start_date,
                'end_date': today,
                'issue_date': today,
                'due_date': today + timedelta(days=30),
                'notes': f'Recurring invoice for {client.recurring_frequency} period ending {today}',
            }
            
            invoice = InvoiceService.create_invoice_from_time_entries(client.user, invoice_data)
            
            # Generate PDF
            InvoiceService.generate_pdf(invoice)
            
            # Update next invoice date
            if client.recurring_frequency == 'weekly':
                client.next_invoice_date = today + timedelta(days=7)
            elif client.recurring_frequency == 'monthly':
                client.next_invoice_date = today + timedelta(days=30)
            elif client.recurring_frequency == 'quarterly':
                client.next_invoice_date = today + timedelta(days=90)
            
            client.save()
            
            print(f"Generated recurring invoice {invoice.invoice_number} for client {client.name}")
            
        except Exception as e:
            print(f"Error generating recurring invoice for client {client.name}: {str(e)}")
    
    # Process project recurring invoices
    projects_with_recurring = Project.objects.filter(
        auto_invoice=True,
        next_invoice_date__lte=today,
        status='active'
    )
    
    for project in projects_with_recurring:
        try:
            # Get time entries for the period
            if project.invoice_frequency == 'weekly':
                start_date = today - timedelta(days=7)
            elif project.invoice_frequency == 'monthly':
                start_date = today - timedelta(days=30)
            elif project.invoice_frequency == 'quarterly':
                start_date = today - timedelta(days=90)
            else:
                continue
            
            # Create invoice from time entries
            invoice_data = {
                'client': project.client,
                'project': project,
                'start_date': start_date,
                'end_date': today,
                'issue_date': today,
                'due_date': today + timedelta(days=30),
                'notes': f'Recurring invoice for project {project.name} - {project.invoice_frequency} period ending {today}',
            }
            
            invoice = InvoiceService.create_invoice_from_time_entries(project.user, invoice_data)
            
            # Generate PDF
            InvoiceService.generate_pdf(invoice)
            
            # Update next invoice date
            if project.invoice_frequency == 'weekly':
                project.next_invoice_date = today + timedelta(days=7)
            elif project.invoice_frequency == 'monthly':
                project.next_invoice_date = today + timedelta(days=30)
            elif project.invoice_frequency == 'quarterly':
                project.next_invoice_date = today + timedelta(days=90)
            
            project.save()
            
            print(f"Generated recurring invoice {invoice.invoice_number} for project {project.name}")
            
        except Exception as e:
            print(f"Error generating recurring invoice for project {project.name}: {str(e)}")


@shared_task
def send_overdue_invoice_reminders():
    """
    Task to send reminders for overdue invoices.
    """
    overdue_invoices = Invoice.objects.filter(
        status='sent',
        due_date__lt=timezone.now().date()
    ).select_related('user', 'client')
    
    for invoice in overdue_invoices:
        try:
            # Send reminder email
            email_data = {
                'email_subject': f'Reminder: Invoice {invoice.invoice_number} is overdue',
                'email_message': f'This is a reminder that invoice {invoice.invoice_number} for {invoice.total_amount} was due on {invoice.due_date}. Please process this payment as soon as possible.',
                'send_to_client': True,
                'send_copy_to_user': True
            }
            
            InvoiceService.send_invoice_email(invoice, email_data)
            
            print(f"Sent overdue reminder for invoice {invoice.invoice_number}")
            
        except Exception as e:
            print(f"Error sending overdue reminder for invoice {invoice.invoice_number}: {str(e)}")


@shared_task
def generate_invoice_pdf(invoice_id):
    """
    Task to generate PDF for a specific invoice.
    """
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        InvoiceService.generate_pdf(invoice)
        print(f"Generated PDF for invoice {invoice.invoice_number}")
    except Invoice.DoesNotExist:
        print(f"Invoice with id {invoice_id} not found")
    except Exception as e:
        print(f"Error generating PDF for invoice {invoice_id}: {str(e)}")


@shared_task
def send_invoice_email_task(invoice_id, email_data):
    """
    Task to send invoice email.
    """
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        InvoiceService.send_invoice_email(invoice, email_data)
        print(f"Sent email for invoice {invoice.invoice_number}")
    except Invoice.DoesNotExist:
        print(f"Invoice with id {invoice_id} not found")
    except Exception as e:
        print(f"Error sending email for invoice {invoice_id}: {str(e)}") 
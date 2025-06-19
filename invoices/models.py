from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import BaseModel, User
from clients.models import Client
from projects.models import Project


class Invoice(BaseModel):
    """
    Model for storing invoice information.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invoices', null=True, blank=True)
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Financial details
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Additional information
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    
    # File storage
    pdf_file = models.FileField(upload_to='invoices/pdfs/', null=True, blank=True)
    
    # Payment tracking
    paid_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-issue_date', '-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.client.name}"
    
    def save(self, *args, **kwargs):
        # Generate invoice number if not provided
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Calculate financial amounts
        self.calculate_amounts()
        
        # Set due date if not provided
        if not self.due_date:
            self.due_date = self.issue_date + timezone.timedelta(days=30)
        
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate a unique invoice number."""
        year = timezone.now().year
        last_invoice = Invoice.objects.filter(
            user=self.user,
            invoice_number__startswith=f"INV-{year}-"
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            try:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"INV-{year}-{new_number:04d}"
    
    def calculate_amounts(self):
        """Calculate invoice amounts."""
        # Calculate tax amount
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        
        # Calculate discount amount
        self.discount_amount = self.subtotal * (self.discount_rate / 100)
        
        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue."""
        return self.status == 'sent' and self.due_date < timezone.now().date()
    
    @property
    def days_overdue(self):
        """Calculate days overdue."""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0


class InvoiceItem(BaseModel):
    """
    Model for storing invoice line items.
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    time_entry = models.ForeignKey('time_entries.TimeEntry', on_delete=models.SET_NULL, null=True, blank=True)
    
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"
    
    def save(self, *args, **kwargs):
        # Calculate total if not provided
        if not self.total:
            self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs) 
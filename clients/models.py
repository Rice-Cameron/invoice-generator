from django.db import models
from django.core.validators import RegexValidator
from core.models import BaseModel, User


class Client(BaseModel):
    """
    Model for storing client information.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Invoice settings
    default_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_terms = models.CharField(max_length=100, default='Net 30')
    currency = models.CharField(max_length=3, default='USD')
    
    # Recurring invoice settings
    recurring_invoice = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ],
        default='monthly'
    )
    next_invoice_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['user', 'email']
    
    def __str__(self):
        return f"{self.name} ({self.company_name})" if self.company_name else self.name
    
    def save(self, *args, **kwargs):
        # If no default hourly rate is set, use user's default
        if not self.default_hourly_rate:
            self.default_hourly_rate = self.user.default_hourly_rate
        super().save(*args, **kwargs) 
from django.db import models
from core.models import BaseModel, User
from invoices.models import Invoice


class StripePaymentIntent(BaseModel):
    """
    Model for storing Stripe payment intent information.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stripe_payment_intents')
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='stripe_payment_intents')
    
    # Stripe fields
    payment_intent_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=255)
    
    # Additional fields
    payment_method_types = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment Intent {self.payment_intent_id} - {self.invoice.invoice_number}"


class StripeWebhookEvent(BaseModel):
    """
    Model for storing Stripe webhook events.
    """
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Webhook Event {self.event_id} - {self.event_type}" 
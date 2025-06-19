from rest_framework import serializers
from .models import StripePaymentIntent, StripeWebhookEvent


class StripePaymentIntentSerializer(serializers.ModelSerializer):
    """
    Serializer for StripePaymentIntent model.
    """
    invoice_number = serializers.ReadOnlyField(source='invoice.invoice_number')
    client_name = serializers.ReadOnlyField(source='invoice.client.name')
    
    class Meta:
        model = StripePaymentIntent
        fields = '__all__'
        read_only_fields = ('user', 'invoice', 'created_at', 'updated_at')


class StripeWebhookEventSerializer(serializers.ModelSerializer):
    """
    Serializer for StripeWebhookEvent model.
    """
    class Meta:
        model = StripeWebhookEvent
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class CreatePaymentIntentSerializer(serializers.Serializer):
    """
    Serializer for creating payment intents.
    """
    invoice_id = serializers.IntegerField()
    
    def validate_invoice_id(self, value):
        from invoices.models import Invoice
        user = self.context['request'].user
        
        try:
            invoice = Invoice.objects.get(id=value, user=user)
            if invoice.status == 'paid':
                raise serializers.ValidationError("Invoice is already paid.")
            return invoice
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("Invoice not found.")


class CreateCheckoutSessionSerializer(serializers.Serializer):
    """
    Serializer for creating checkout sessions.
    """
    invoice_id = serializers.IntegerField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()
    
    def validate_invoice_id(self, value):
        from invoices.models import Invoice
        user = self.context['request'].user
        
        try:
            invoice = Invoice.objects.get(id=value, user=user)
            if invoice.status == 'paid':
                raise serializers.ValidationError("Invoice is already paid.")
            return invoice
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("Invoice not found.") 
from django.contrib import admin
from .models import StripePaymentIntent, StripeWebhookEvent


@admin.register(StripePaymentIntent)
class StripePaymentIntentAdmin(admin.ModelAdmin):
    list_display = ('payment_intent_id', 'invoice', 'user', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('payment_intent_id', 'invoice__invoice_number', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'invoice', 'payment_intent_id', 'status')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'client_secret', 'payment_method_types')
        }),
        ('Additional Data', {
            'fields': ('metadata',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'invoice')


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'event_type', 'processed', 'created_at')
    list_filter = ('event_type', 'processed', 'created_at')
    search_fields = ('event_id', 'event_type')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_id', 'event_type', 'processed')
        }),
        ('Event Data', {
            'fields': ('event_data', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 
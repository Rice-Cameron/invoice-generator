from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'email', 'user', 'is_active', 'recurring_invoice')
    list_filter = ('is_active', 'recurring_invoice', 'recurring_frequency', 'created_at')
    search_fields = ('name', 'company_name', 'email', 'user__email')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'email', 'phone_number', 'company_name')
        }),
        ('Address & Tax', {
            'fields': ('address', 'tax_id', 'notes')
        }),
        ('Invoice Settings', {
            'fields': ('default_hourly_rate', 'payment_terms', 'currency')
        }),
        ('Recurring Invoice', {
            'fields': ('recurring_invoice', 'recurring_frequency', 'next_invoice_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 
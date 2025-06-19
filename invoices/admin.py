from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('description', 'quantity', 'unit_price', 'total')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client', 'user', 'issue_date', 'due_date', 'total_amount', 'status', 'is_overdue')
    list_filter = ('status', 'issue_date', 'due_date', 'client', 'user', 'created_at')
    search_fields = ('invoice_number', 'client__name', 'user__email', 'notes')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'is_overdue', 'days_overdue')
    date_hierarchy = 'issue_date'
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'client', 'project', 'invoice_number', 'status')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'paid_date')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_rate', 'discount_amount', 'total_amount')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'stripe_payment_intent_id')
        }),
        ('Content', {
            'fields': ('notes', 'terms_conditions')
        }),
        ('File', {
            'fields': ('pdf_file',)
        }),
        ('Calculated Fields', {
            'fields': ('is_overdue', 'days_overdue'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'user', 'project')


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'total')
    list_filter = ('invoice__status', 'created_at')
    search_fields = ('description', 'invoice__invoice_number')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('invoice', 'time_entry') 
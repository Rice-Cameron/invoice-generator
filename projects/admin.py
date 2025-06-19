from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'user', 'status', 'hourly_rate', 'total_hours', 'total_billed', 'is_over_budget')
    list_filter = ('status', 'auto_invoice', 'invoice_frequency', 'created_at', 'client')
    search_fields = ('name', 'description', 'client__name', 'user__email')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'total_hours', 'total_billed', 'is_over_budget')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'client', 'name', 'description', 'status')
        }),
        ('Project Settings', {
            'fields': ('start_date', 'end_date', 'hourly_rate', 'budget')
        }),
        ('Invoice Settings', {
            'fields': ('auto_invoice', 'invoice_frequency', 'next_invoice_date')
        }),
        ('Calculated Fields', {
            'fields': ('total_hours', 'total_billed', 'is_over_budget'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'user') 
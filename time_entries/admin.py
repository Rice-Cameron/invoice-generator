from django.contrib import admin
from .models import TimeEntry


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'date', 'hours', 'hourly_rate', 'total_amount', 'is_billable')
    list_filter = ('date', 'is_billable', 'project__client', 'user', 'created_at')
    search_fields = ('description', 'project__name', 'user__email', 'tags')
    list_editable = ('is_billable',)
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'project', 'date', 'hours', 'description')
        }),
        ('Time Details', {
            'fields': ('start_time', 'end_time', 'hourly_rate', 'is_billable')
        }),
        ('Additional Info', {
            'fields': ('tags',)
        }),
        ('Calculated Fields', {
            'fields': ('total_amount',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'user', 'project__client') 
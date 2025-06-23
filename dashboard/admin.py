from django.contrib import admin
from .models import Activity, UserPreference

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'timestamp', 'related_object_type')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'description')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'timezone', 'default_hourly_rate', 'auto_generate_invoices')
    list_filter = ('theme', 'auto_generate_invoices')
    search_fields = ('user__username', 'invoice_template')
    fieldsets = (
        ('User Settings', {
            'fields': ('user',)
        }),
        ('Appearance', {
            'fields': ('theme', 'timezone')
        }),
        ('Invoice Settings', {
            'fields': ('default_hourly_rate', 'invoice_template', 'auto_generate_invoices', 'invoice_frequency')
        }),
        ('Advanced', {
            'fields': ('last_invoice_number',)
        })
    )

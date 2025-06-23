from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Activity(models.Model):
    """
    Model to track user activities in the dashboard.
    """
    ACTIVITY_TYPES = (
        ('client', 'Client Management'),
        ('project', 'Project Management'),
        ('time_entry', 'Time Entry'),
        ('invoice', 'Invoice Generation'),
        ('system', 'System Event'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f"{self.activity_type} - {self.description[:50]}"

class UserPreference(models.Model):
    """
    Model to store user preferences for the dashboard.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=20, default='light', choices=[('light', 'Light'), ('dark', 'Dark')])
    timezone = models.CharField(max_length=50, default='UTC')
    default_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    invoice_template = models.CharField(max_length=50, default='default')
    auto_generate_invoices = models.BooleanField(default=False)
    invoice_frequency = models.CharField(max_length=20, null=True, blank=True)
    last_invoice_number = models.CharField(max_length=20, default='INV-0001')

    def __str__(self):
        return f"Preferences for {self.user.username}"

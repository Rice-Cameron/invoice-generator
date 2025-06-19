from django.db import models
from core.models import BaseModel, User
from clients.models import Client


class Project(BaseModel):
    """
    Model for storing project information.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Project settings
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Invoice settings
    auto_invoice = models.BooleanField(default=False)
    invoice_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('on_completion', 'On Completion'),
        ],
        default='monthly'
    )
    next_invoice_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'client', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"
    
    def save(self, *args, **kwargs):
        # If no hourly rate is set, use client's default or user's default
        if not self.hourly_rate:
            if self.client.default_hourly_rate:
                self.hourly_rate = self.client.default_hourly_rate
            else:
                self.hourly_rate = self.user.default_hourly_rate
        super().save(*args, **kwargs)
    
    @property
    def total_hours(self):
        """Calculate total hours logged for this project."""
        return self.time_entries.aggregate(
            total=models.Sum('hours')
        )['total'] or 0
    
    @property
    def total_billed(self):
        """Calculate total amount billed for this project."""
        return self.time_entries.aggregate(
            total=models.Sum(models.F('hours') * models.F('hourly_rate'))
        )['total'] or 0
    
    @property
    def is_over_budget(self):
        """Check if project is over budget."""
        if self.budget:
            return self.total_billed > self.budget
        return False 
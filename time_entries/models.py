from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import BaseModel, User
from projects.models import Project


class TimeEntry(BaseModel):
    """
    Model for storing time entries.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='time_entries')
    date = models.DateField()
    hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    description = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Optional fields
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_billable = models.BooleanField(default=True)
    tags = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'project', 'date', 'description']
    
    def __str__(self):
        return f"{self.project.name} - {self.date} - {self.hours}h"
    
    def save(self, *args, **kwargs):
        # If no hourly rate is set, use project's hourly rate
        if not self.hourly_rate:
            self.hourly_rate = self.project.hourly_rate
        super().save(*args, **kwargs)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate that date is not in the future
        if self.date and self.date > timezone.now().date():
            raise ValidationError("Time entries cannot be logged for future dates.")
        
        # Validate that project belongs to the user
        if self.project and self.project.user != self.user:
            raise ValidationError("You can only log time for your own projects.")
    
    @property
    def total_amount(self):
        """Calculate total amount for this time entry."""
        return self.hours * self.hourly_rate
    
    @property
    def duration_minutes(self):
        """Calculate duration in minutes if start and end times are provided."""
        if self.start_time and self.end_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            return end_minutes - start_minutes
        return None 
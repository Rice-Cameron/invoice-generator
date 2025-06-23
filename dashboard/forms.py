from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import UserPreference

User = get_user_model()

class UserPreferenceForm(forms.ModelForm):
    """
    Form for managing user preferences.
    """
    class Meta:
        model = UserPreference
        fields = [
            'theme',
            'timezone',
            'default_hourly_rate',
            'invoice_template',
            'auto_generate_invoices',
            'invoice_frequency'
        ]
        widgets = {
            'theme': forms.RadioSelect(choices=[
                ('light', _('Light Theme')),
                ('dark', _('Dark Theme'))
            ]),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'default_hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'invoice_template': forms.Select(attrs={'class': 'form-control'}),
            'auto_generate_invoices': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'invoice_frequency': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('weekly', _('Weekly')),
                ('monthly', _('Monthly')),
                ('quarterly', _('Quarterly'))
            ])
        }
        labels = {
            'theme': _('Theme'),
            'timezone': _('Timezone'),
            'default_hourly_rate': _('Default Hourly Rate'),
            'invoice_template': _('Invoice Template'),
            'auto_generate_invoices': _('Auto Generate Invoices'),
            'invoice_frequency': _('Invoice Frequency')
        }

class ActivityFilterForm(forms.Form):
    """
    Form for filtering activities in the dashboard.
    """
    ACTIVITY_TYPES = [
        ('', _('All Activities')),
        ('client', _('Client Management')),
        ('project', _('Project Management')),
        ('time_entry', _('Time Entry')),
        ('invoice', _('Invoice Generation')),
        ('system', _('System Event')),
    ]

    activity_type = forms.ChoiceField(
        choices=ACTIVITY_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

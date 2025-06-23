from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('clients/', views.clients_view, name='clients'),
    path('projects/', views.projects_view, name='projects'),
    path('time-entries/', views.time_entries_view, name='time_entries'),
    path('invoices/', views.invoices_view, name='invoices'),
    
    # AJAX endpoints
    path('delete/client/<int:client_id>/', views.delete_client, name='delete_client'),
    path('delete/project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('delete/time-entry/<int:entry_id>/', views.delete_time_entry, name='delete_time_entry'),
    path('delete/invoice/<int:invoice_id>/', views.delete_invoice, name='delete_invoice'),
]

from django.urls import path
from .views import (
    TimeEntryListCreateView, 
    TimeEntryDetailView, 
    TimeEntryBulkCreateView,
    TimeEntryByProjectView,
    time_entry_summary
)

urlpatterns = [
    path('', TimeEntryListCreateView.as_view(), name='time-entry-list-create'),
    path('<int:pk>/', TimeEntryDetailView.as_view(), name='time-entry-detail'),
    path('bulk-create/', TimeEntryBulkCreateView.as_view(), name='time-entry-bulk-create'),
    path('by-project/<int:project_id>/', TimeEntryByProjectView.as_view(), name='time-entry-by-project'),
    path('summary/', time_entry_summary, name='time-entry-summary'),
] 
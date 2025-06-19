from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView, ProjectByClientView

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('by-client/<int:client_id>/', ProjectByClientView.as_view(), name='project-by-client'),
] 
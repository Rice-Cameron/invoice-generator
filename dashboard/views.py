from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from clients.models import Client
from projects.models import Project
from time_entries.models import TimeEntry
from invoices.models import Invoice

@login_required
def dashboard_view(request):
    """
    Main dashboard view showing overview statistics and recent activities.
    """
    # Get user's data
    user = request.user
    
    # Get statistics
    total_clients = Client.objects.filter(user=user).count()
    total_projects = Project.objects.filter(user=user).count()
    total_time_entries = TimeEntry.objects.filter(user=user).count()
    total_invoices = Invoice.objects.filter(user=user).count()
    
    # Get recent activities
    recent_time_entries = TimeEntry.objects.filter(user=user).order_by('-start_time')[:5]
    recent_invoices = Invoice.objects.filter(user=user).order_by('-created_at')[:5]
    
    context = {
        'total_clients': total_clients,
        'total_projects': total_projects,
        'total_time_entries': total_time_entries,
        'total_invoices': total_invoices,
        'recent_time_entries': recent_time_entries,
        'recent_invoices': recent_invoices
    }
    
    return render(request, 'dashboard.html', context)
    
    # Get statistics
    total_clients = Client.objects.filter(user=user).count()
    active_projects = Project.objects.filter(user=user, is_active=True).count()
    
    # Calculate total hours
    time_entries = TimeEntry.objects.filter(user=user)
    total_hours = time_entries.aggregate(Sum('hours'))['hours__sum'] or 0
    
    # Get recent invoices
    recent_invoices = Invoice.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Get recent activities
    recent_activities = []
    for invoice in recent_invoices:
        recent_activities.append({
            'type': 'invoice',
            'text': f'Created invoice #{invoice.number}',
            'time': invoice.created_at.strftime('%b %d, %Y')
        })
    
    context = {
        'total_clients': total_clients,
        'active_projects': active_projects,
        'total_hours': round(total_hours, 2),
        'recent_invoices': len(recent_invoices),
        'recent_activities': recent_activities,
        'user': user
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
def clients_view(request):
    """
    View for managing clients.
    """
    user = request.user
    clients = Client.objects.filter(user=user)
    
    if request.method == 'POST':
        # Handle client creation
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        Client.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        
        messages.success(request, 'Client added successfully')
        return redirect('dashboard:clients')
    
    context = {
        'clients': clients,
        'user': user
    }
    return render(request, 'dashboard/clients.html', context)

@login_required
def projects_view(request):
    """
    View for managing projects.
    """
    user = request.user
    projects = Project.objects.filter(user=user)
    clients = Client.objects.filter(user=user)
    
    if request.method == 'POST':
        # Handle project creation
        name = request.POST.get('name')
        client_id = request.POST.get('client')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')
        
        client = get_object_or_404(Client, id=client_id, user=user)
        
        Project.objects.create(
            user=user,
            client=client,
            name=name,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
        
        messages.success(request, 'Project added successfully')
        return redirect('dashboard:projects')
    
    context = {
        'projects': projects,
        'clients': clients,
        'user': user
    }
    return render(request, 'dashboard/projects.html', context)

@login_required
def time_entries_view(request):
    """
    View for managing time entries.
    """
    user = request.user
    time_entries = TimeEntry.objects.filter(user=user)
    projects = Project.objects.filter(user=user)
    
    if request.method == 'POST':
        # Handle time entry creation
        date = request.POST.get('date')
        project_id = request.POST.get('project')
        hours = request.POST.get('hours')
        description = request.POST.get('description')
        hourly_rate = request.POST.get('hourly_rate')
        
        project = get_object_or_404(Project, id=project_id, user=user)
        
        TimeEntry.objects.create(
            user=user,
            project=project,
            date=date,
            hours=float(hours),
            description=description,
            hourly_rate=float(hourly_rate)
        )
        
        messages.success(request, 'Time entry added successfully')
        return redirect('dashboard:time_entries')
    
    context = {
        'time_entries': time_entries,
        'projects': projects,
        'user': user
    }
    return render(request, 'dashboard/time_entries.html', context)

@login_required
def invoices_view(request):
    """
    View for managing invoices.
    """
    user = request.user
    invoices = Invoice.objects.filter(user=user)
    clients = Client.objects.filter(user=user)
    projects = Project.objects.filter(user=user)
    
    if request.method == 'POST':
        # Handle invoice creation
        client_id = request.POST.get('client')
        project_id = request.POST.get('project')
        date = request.POST.get('date')
        due_date = request.POST.get('due_date')
        notes = request.POST.get('notes')
        
        client = get_object_or_404(Client, id=client_id, user=user)
        project = get_object_or_404(Project, id=project_id, user=user)
        
        Invoice.objects.create(
            user=user,
            client=client,
            project=project,
            date=date,
            due_date=due_date,
            notes=notes
        )
        
        messages.success(request, 'Invoice generated successfully')
        return redirect('dashboard:invoices')
    
    context = {
        'invoices': invoices,
        'clients': clients,
        'projects': projects,
        'user': user
    }
    return render(request, 'dashboard/invoices.html', context)

# AJAX endpoints
@login_required
def delete_client(request, client_id):
    """
    AJAX endpoint to delete a client.
    """
    if request.method == 'POST':
        client = get_object_or_404(Client, id=client_id, user=request.user)
        client.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_project(request, project_id):
    """
    AJAX endpoint to delete a project.
    """
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id, user=request.user)
        project.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_time_entry(request, entry_id):
    """
    AJAX endpoint to delete a time entry.
    """
    if request.method == 'POST':
        entry = get_object_or_404(TimeEntry, id=entry_id, user=request.user)
        entry.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_invoice(request, invoice_id):
    """
    AJAX endpoint to delete an invoice.
    """
    if request.method == 'POST':
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
        invoice.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Site, DailyLog, MaterialEntry, UserProfile, Attendance
from .forms import SiteForm, LogForm, MaterialForm, SignUpForm, AssignSiteForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden

# Create your views here.
def manager_required(user):
    return (user.is_authenticated and hasattr(user,"userprofile") and user.userprofile.role== "manager")

def worker_required(user):
    return (user.is_authenticated and hasattr(user,"userprofile") and user.userprofile.role== "worker")

@login_required
def dashboard(request):
    if not manager_required(request.user):
        return HttpResponseForbidden("You are not allowed to view this page.")
    profile=UserProfile.objects.get(user=request.user)
    if profile.role =='worker':
        return redirect('worker_dashboard')
    sites=Site.objects.all()
    total_sites=Site.objects.count()
    total_logs=DailyLog.objects.count()
    total_active_sites=Site.objects.filter(status='active').count()
    total_onhold_sites=Site.objects.filter(status='on hold').count()
    total_completed_sites=Site.objects.filter(status='completed').count()
    return render(request, "dashboard.html", {'sites': sites, 'total_sites':total_sites, 'total_logs':total_logs,
                                              'total_active_sites':total_active_sites, 'total_onhold_sites':total_onhold_sites, 
                                              'total_completed_sites':total_completed_sites})

@login_required
def worker_dashboard(request):
    if not worker_required(request.user):
        return redirect('dashboard')
    profile=UserProfile.objects.get(user=request.user)
    assigned_sites=request.user.assigned_sites.all()
    today=timezone.now().date()
    marked_sites=Attendance.objects.filter(
        worker=request.user,
        attendance_date=today
        ).values_list('worksite_id', flat=True)
    return render(request, 'worker_dashboard.html', {'profile': profile, 'assigned_sites':assigned_sites,
                                                    'marked_sites':marked_sites})


@login_required
def add_site(request):
    if not manager_required(request.user):
        return HttpResponseForbidden("You are not allowed to view this page.")
    if request.method == 'POST':
        form=SiteForm(request.POST)
        if form.is_valid():
            site=form.save(commit=False)
            site.created_by=request.user
            site.save()
            return redirect('dashboard')
    else:
        form=SiteForm()

    return render(request, "add_site.html", {'form': form})

@login_required
def site_detail(request, pk):
    if not manager_required(request.user):
        return HttpResponseForbidden("You are not allowed to view this page.")
    site=Site.objects.get(pk=pk)
    logdetail=DailyLog.objects.filter(site_worked_on=site)
    return render(request, "site_detail.html", {'site': site, 'logdetail': logdetail})

@login_required
def worker_site_detail(request,pk):
    if not worker_required(request.user):
        return redirect('dashboard')
    site=Site.objects.get(pk=pk)
    attendance_log=Attendance.objects.filter(worksite=site, worker=request.user)
    return render(request, 'worker_site_detail.html', {'site':site, 'attendance_log':attendance_log})

@login_required
def add_log(request,pk):
    if not manager_required(request.user):
        return HttpResponseForbidden("You are not allowed to view this page.")
    site=Site.objects.get(pk=pk)
    if request.method == 'POST':
        form=LogForm(request.POST)
        if form.is_valid():
            log=form.save(commit=False)
            log.created_by=request.user
            log.site_worked_on=site
            log.save()
            return redirect('site_detail', pk=pk)
    else:
        form=LogForm()
    return render(request, "add_log.html", {'form':form, 'site':site})

@login_required
def materials_log(request, pk):
    if not manager_required(request.user):
        return HttpResponseForbidden("You are not allowed to view this page.")
    log=DailyLog.objects.get(pk=pk)
    material_list= MaterialEntry.objects.filter(daily_log=log)
    return render(request,  "materials_log.html", {'material_list':material_list, 'log':log})

@login_required
def add_mat_log(request,pk):
    if not manager_required(request.user):
        return HttpResponseForbidden("You are not allowed to view this page.")
    log=DailyLog.objects.get(pk=pk)
    if request.method == 'POST':
        form=MaterialForm(request.POST)
        if form.is_valid():
            mat_log=form.save(commit=False)
            mat_log.daily_log=log
            mat_log.save()
            return redirect('materials_log', pk=pk)
    else:
        form=MaterialForm()
    return render(request, "add_mat_log.html", {'form':form, 'log':log})

def signup(request):
    if request.method == 'POST':
        form=SignUpForm(request.POST)
        if form.is_valid():
            user=form.save()
            role=form.cleaned_data.get('role')
            UserProfile.objects.create(user=user,role=role)
            return redirect('login')
    else:
        form=SignUpForm()
    return render(request, 'signup.html', {'form':form})

@login_required
def mark_attendance(request,pk):
    site=Site.objects.get(pk=pk)
    today=timezone.now().date()
    already_marked=Attendance.objects.filter(worker=request.user, worksite=site, attendance_date=today).exists()
    if not already_marked:
        Attendance.objects.create(
            worker=request.user,
            worksite=site,
            attendance_date=today,
            present_or_absent=True
        )
    return redirect('worker_dashboard')

@login_required
def worker_list(request):
    if not manager_required(request.user):
        return HttpResponseForbidden("You are not allowed to view this page.")
    workerlist=UserProfile.objects.filter(role='worker')
    return render(request, 'worker_list.html', {'workerlist': workerlist})

@login_required
def worker_profile(request, pk):
    if not manager_required(request.user):
        return HttpResponseForbidden("You are not allowed to view this page.")
    worker=get_object_or_404(User, pk=pk,userprofile__role='worker')
    assigned_sites=worker.assigned_sites.all()
    attendance_records=Attendance.objects.filter(worker=worker).select_related('worksite').order_by('-attendance_date')
    total_present=attendance_records.filter(present_or_absent=True).count()
    total_absent=attendance_records.filter(present_or_absent=False).count()
    context = {
        "worker": worker,
        "assigned_sites": assigned_sites,
        "attendance_records": attendance_records,
        "total_present": total_present,
        "total_absent": total_absent,
    }

    return render(request, "worker_profile.html", context)

@login_required
def assign_sites(request,pk):
    if not manager_required(request.user):
        return HttpResponseForbidden("You are not allowed to view this page.")
    worker=get_object_or_404(User, pk=pk, userprofile__role='worker')
    if request.method=='POST':
        form=AssignSiteForm(request.POST)
        if form.is_valid():
            site=form.cleaned_data['sites']
            site.workers.add(worker)
            return redirect('worker_profile', pk=pk)
    else:
        form=AssignSiteForm()
    return render(request, 'assign_sites.html', {'worker':worker,'form':form})

@login_required
def update_email(request,pk):
    if not manager_required(request.user):
        return HttpResponseForbidden("You are not allowed to view this page.")
    worker=get_object_or_404(User, pk=pk, userprofile__role='worker')
    if request.method == 'POST':
        email=request.POST.get('email')
        worker.email=email
        worker.save()
        return redirect('worker_profile', pk=pk)
    return render(request, 'worker_profile.html', {'worker': worker})
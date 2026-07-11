from django.shortcuts import render, redirect, get_object_or_404
from .models import Site, DailyLog, MaterialEntry, UserProfile, Attendance, AttendanceQRCode
from .forms import SiteForm, LogForm, MaterialForm, SignUpForm, AssignSiteForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST #edit
from django.urls import reverse
from datetime import timedelta
from io import BytesIO
import base64
import qrcode

#updated
from django.core.exceptions import PermissionDenied
from functools import wraps

def manager_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        profile = UserProfile.objects.filter(user=request.user).first()

        if profile is None or profile.role != "manager":
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapped
# Create your views here.

#edit
def worker_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(request, *args, **kwargs):
        profile = UserProfile.objects.filter(user=request.user).first()

        if profile is None or profile.role != "worker":
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapped


@login_required
def dashboard(request):
    if not request.user.is_superuser:
        profile = UserProfile.objects.filter(user=request.user).first()

        if profile is None:
            raise PermissionDenied

        if profile.role == "worker":
            return redirect("worker_dashboard")
        
    if request.user.is_superuser:
        sites = Site.objects.all()
    else:
        sites = Site.objects.filter(created_by=request.user)

    sites = Site.objects.filter(created_by=request.user)

    total_sites = sites.count()
    total_logs = DailyLog.objects.filter(site_worked_on__in=sites).count()
    total_workers = UserProfile.objects.filter(role="worker").count()

    total_active_sites = sites.filter(status="active").count()
    total_onhold_sites = sites.filter(status="on hold").count()
    total_completed_sites = sites.filter(status="completed").count()
    daily_logs = (
        DailyLog.objects
        .filter(site_worked_on__created_by=request.user)
        .values('date_today')
        .annotate(total=Count('id'))
        .order_by('date_today')
    )
    return render(
        request,
        "dashboard.html",
        {
            "sites": sites,
            "total_sites": total_sites,
            "total_logs": total_logs,
            "total_workers": total_workers,
            "total_active_sites": total_active_sites,
            "total_onhold_sites": total_onhold_sites,
            "total_completed_sites": total_completed_sites,

            "daily_logs": daily_logs,
        },
    )


@worker_required
def worker_dashboard(request):
    
    profile=UserProfile.objects.get(user=request.user)
    assigned_sites = request.user.assigned_sites.all()
    today = timezone.now().date()

    active_qr_codes = {
        qr.site_id: qr
        for qr in AttendanceQRCode.objects.filter(
            site__in=assigned_sites,
            is_active=True,
            expires_at__gt=timezone.now(),
        )
    }

    for site in assigned_sites:
        site.active_qr_code = active_qr_codes.get(site.pk)
    marked_sites=Attendance.objects.filter(
        worker=request.user,
        attendance_date=today
        ).values_list('worksite_id', flat=True)
    return render(request, 'worker_dashboard.html', {'profile': profile, 'assigned_sites':assigned_sites,'marked_sites':marked_sites})


@manager_required
def add_site(request):
    
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

@manager_required
def sites(request):
    if request.user.is_superuser:
        sites = Site.objects.all()
    else:
        sites = Site.objects.filter(created_by=request.user)

    return render(request, "sites.html", {
        "sites": sites,
    })

@manager_required
def site_detail(request, pk):
    
    if request.user.is_superuser:
        site = get_object_or_404(Site, pk=pk)

    else:
        site = get_object_or_404(
            Site,
            pk=pk,
            created_by=request.user
        )
    if request.method == "POST":
        status = request.POST.get("status")
        if status in ["active", "on hold", "completed"]:
            site.status = status
            site.save()
        return redirect("site_detail", pk=pk)
    logdetail = DailyLog.objects.filter(site_worked_on=site)
    return render(request, "site_detail.html", {
        "site": site,
        "logdetail": logdetail,
    })


@manager_required
@require_POST
def generate_attendance_qr(request, pk):

    if request.user.is_superuser:
        site = get_object_or_404(Site, pk=pk)
    else:
        site = get_object_or_404(
            Site,
            pk=pk,
            created_by=request.user
        )

    AttendanceQRCode.objects.filter(
        site=site,
        is_active=True
    ).update(is_active=False)

    attendance_qr = AttendanceQRCode.objects.create(
        site=site,
        created_by=request.user,
        expires_at=timezone.now() + timedelta(minutes=10),
    )

    return redirect(
        "attendance_qr",
        token=attendance_qr.token
    )


@manager_required
def attendance_qr(request, token):
    if request.user.is_superuser:
        attendance_qr = get_object_or_404(
            AttendanceQRCode,
            token=token
        )
    else:
        attendance_qr = get_object_or_404(
            AttendanceQRCode,
            token=token,
            site__created_by=request.user
        )
    check_in_url = request.build_absolute_uri(
        reverse("qr_check_in", kwargs={"token": attendance_qr.token})
    )
    image = qrcode.make(check_in_url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    qr_image = base64.b64encode(buffer.getvalue()).decode("ascii")
    return render(request, "attendance_qr.html", {
        "attendance_qr": attendance_qr,
        "qr_image": qr_image,
        "check_in_url": check_in_url,
    })


@worker_required
def qr_check_in(request, token):
    attendance_qr = get_object_or_404(AttendanceQRCode, token=token)
    is_assigned = request.user.assigned_sites.filter(pk=attendance_qr.site_id).exists()
    if not is_assigned:
        raise PermissionDenied

    if not attendance_qr.is_valid:
        return render(request, "qr_check_in.html", {
            "attendance_qr": attendance_qr,
            "expired": True,
        }, status=410)

    already_marked = Attendance.objects.filter(
        worker=request.user,
        worksite=attendance_qr.site,
        attendance_date=timezone.localdate(),
    ).exists()

    if request.method == "POST" and not already_marked:
        Attendance.objects.get_or_create(
            worker=request.user,
            worksite=attendance_qr.site,
            attendance_date=timezone.localdate(),
            defaults={"present_or_absent": True},
        )
        return render(request, "qr_check_in.html", {
            "attendance_qr": attendance_qr,
            "success": True,
        })

    return render(request, "qr_check_in.html", {
        "attendance_qr": attendance_qr,
        "already_marked": already_marked,
    })

##EDIT 2
@worker_required
def worker_site_detail(request, pk):
    site = get_object_or_404(Site, pk=pk)

    if not request.user.assigned_sites.filter(pk=site.pk).exists():
        raise PermissionDenied

    attendance_log = Attendance.objects.filter(
        worksite=site,
        worker=request.user,
    )

    return render(
        request,
        "worker_site_detail.html",
        {
            "site": site,
            "attendance_log": attendance_log,
        },
    )
@worker_required
def qr_attendance(request):
    assigned_sites = request.user.assigned_sites.all()

    active_qr_codes = {
        qr.site_id: qr
        for qr in AttendanceQRCode.objects.filter(
            site__in=assigned_sites,
            is_active=True,
            expires_at__gt=timezone.now(),
        )
    }

    for site in assigned_sites:
        site.active_qr_code = active_qr_codes.get(site.pk)

    return render(request, "qr_attendance.html", {
        "assigned_sites": assigned_sites,
    })

@manager_required
def add_log(request,pk):
    
    if request.user.is_superuser:
        site = get_object_or_404(Site, pk=pk)
    else:
        site = get_object_or_404(
            Site,
            pk=pk,
            created_by=request.user
        )
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


@manager_required
def materials_log(request, pk):
    
    log = get_object_or_404(DailyLog, pk=pk,site_worked_on__created_by=request.user)
    material_list= MaterialEntry.objects.filter(daily_log=log)
    return render(request,  "materials_log.html", {'material_list':material_list, 'log':log})

@manager_required
def add_mat_log(request,pk):
    
    log = get_object_or_404(DailyLog, pk=pk,site_worked_on__created_by=request.user)
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
            UserProfile.objects.create(user=user, role="worker") #edited
            # role=form.cleaned_data.get('role')
            # UserProfile.objects.create(user=user,role=role)
            return redirect('login')
    else:
        form=SignUpForm()
    return render(request, 'signup.html', {'form':form})

@worker_required
@require_POST
def mark_attendance(request, pk):
    site = get_object_or_404(Site, pk=pk)
    if not request.user.assigned_sites.filter(pk=site.pk).exists():
        return redirect('worker_dashboard')
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

@manager_required
def worker_list(request):
    
    workerlist=UserProfile.objects.filter(role='worker')
    return render(request, 'worker_list.html', {'workerlist': workerlist})

@login_required
@manager_required
def worker_profile(request, pk):
    
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
@manager_required
def assign_sites(request,pk):
    
    worker=get_object_or_404(User, pk=pk, userprofile__role='worker')
    if request.method=='POST':
        form=AssignSiteForm(request.POST)
        if form.is_valid():
            site=form.cleaned_data['sites']
            if site.created_by != request.user:
                raise PermissionDenied

            site.workers.add(worker)
            return redirect('worker_profile', pk=pk)
    else:
        form=AssignSiteForm()
    return render(request, 'assign_sites.html', {'worker':worker,'form':form})

@login_required
@manager_required
def update_email(request,pk):
    worker=get_object_or_404(User, pk=pk, userprofile__role='worker')
    if request.method == 'POST':
        email=request.POST.get('email')
        worker.email=email
        worker.save()
    return redirect('worker_profile', pk=pk)


@login_required
@manager_required
def delete_site(request, pk):
    site = get_object_or_404(Site, pk=pk,created_by=request.user)
    if request.method == "POST":
        site.delete()
        return redirect("dashboard")
    return redirect("site_detail", pk=pk)


@login_required
@manager_required
def delete_log(request, pk):
    log = get_object_or_404(DailyLog, pk=pk,
    site_worked_on__created_by=request.user)
    site_pk = log.site_worked_on.pk
    if request.method == "POST":
        log.delete()
    return redirect("site_detail", pk=site_pk)


@login_required
@manager_required
def delete_material(request, pk):
    material = get_object_or_404(MaterialEntry, pk=pk,daily_log__site_worked_on__created_by=request.user)
    log_pk = material.daily_log.pk
    if request.method == "POST":
        material.delete()
    return redirect("materials_log", pk=log_pk)


@login_required
@manager_required
def remove_assigned_site(request, worker_pk, site_pk):
    worker = get_object_or_404(User, pk=worker_pk, userprofile__role="worker")
    site = get_object_or_404(Site, pk=site_pk)
    if request.method == "POST":
        site.workers.remove(worker)
    return redirect("worker_profile", pk=worker_pk)

#edit
def custom_403(request, exception=None):
    return render(request, "403.html", status=403)

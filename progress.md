# Construction Daily Site Log + Material Consumption Tracker
## Project Progress Log

---

## Project Overview
A full-stack web app built with Python Django for tracking construction site daily logs and material consumption. Built as a college internship project by a 4th year BTech CSE student.

---

## Tech Stack
- **Backend:** Python 3.14.3, Django 6.0.5
- **Database:** SQLite (Django default)
- **Frontend:** HTML, Django Templates, Bootstrap (planned)
- **Auth:** Django built-in authentication

---

## Project Structure
```
construction_tracker/
    manage.py
    construction_tracker/
        settings.py
        urls.py
        wsgi.py
    logs/
        models.py
        views.py
        forms.py
        admin.py
        urls.py
        templates/
            base.html
            dashboard.html
            add_site.html
            site_detail.html
            add_log.html
            materials_log.html
            add_mat_log.html
            registration/
                login.html
```

---

## Database Models (logs/models.py)

### Site
- `name` — CharField
- `location` — CharField
- `start_date` — DateField
- `company_name` — CharField
- `created_by` — ForeignKey(User)
- `created_at` — DateTimeField(auto_now_add=True)
- `STATUS_CHOICES` — active, on hold, completed
- `status` — CharField with STATUS_CHOICES, default='active'

### DailyLog
- `site_worked_on` — ForeignKey(Site)
- `date_today` — DateField
- `worker_count` — IntegerField
- `site_manager` — CharField
- `work_overview` — TextField
- `created_by` — ForeignKey(User)
- Meta: verbose_name_plural = "Daily Log"

### MaterialEntry
- `daily_log` — ForeignKey(DailyLog)
- `material_name` — CharField
- `quantity` — DecimalField(max_digits=10, decimal_places=2)
- `UNIT_CHOICES` — bags, kg, lt, unit
- `unit` — CharField with UNIT_CHOICES
- Meta: verbose_name_plural = "Material Entries"


### UserProfile
- `user` - OneToOneField(to User)
- `ROLE_CHOICES` - manager, worker
- `role` - CharField with ROLE_CHOICES

### Attendance
- `worker`- ForeignKey(User)
- `worksite` - ForeignKey(Site)
- `attendance_date` - DateField
- `present_or_absent` - BooleanField

---

## Forms (logs/forms.py)

### SiteForm
- Model: Site
- Fields: name, location, start_date, company_name
- (created_by and created_at are set automatically)

### LogForm
- Model: DailyLog
- Fields: date_today, worker_count, site_manager, work_overview
- (site_worked_on and created_by set automatically)

### MaterialForm
- Model: MaterialEntry
- Fields: material_name, quantity, unit
- (daily_log set automatically)

### SignUpForm
- Model: User
- Fields: username, password1, password2, role
- (extends UserCreationForm, adds role fields)

### AssignSiteForm 
- plain Form (not ModelForm) 
- single sites field using ModelChoiceField(queryset=Site.objects.all())

---

## URLs

### Main urls.py (construction_tracker/urls.py)
- `admin/` → Django admin
- `login/` → auth_views.LoginView
- `logout/` → auth_views.LogoutView
- `''` → includes logs.urls

### logs/urls.py
- `dashboard/` → views.dashboard (name='dashboard')
- `add_site/` → views.add_site (name='add_site')
- `sites/<int:pk>/` → views.site_detail (name='site_detail')
- `sites/<int:pk>/add_log/` → views.add_log (name='add_log')
- `logs/<int:pk>/materials_log` → views.materials_log (name='materials_log')
- `logs/<int:pk>/materials_log/add_mat_log/` → views.add_mat_log (name='add_mat_log')
- `signup/` → views.signup (name='signup')
- `worker_dashboard/` → views.worker_dashboard (name='worker_dashboard')
- `worker/site/<int:pk>/` → views.worker_site_detail (name='worker_site_detail')
- `worker/site/<int:pk>/mark_attendance/` → views.mark_attendance (name='mark_attendance')
- `dashboard/worker_list/` → views.worker_list (name='worker_list')
- `dashboard/worker_list/<int:pk>/` → views.worker_profile (name='worker_profile')
- `worker/<int:pk>/assign_sites/` → views.assign_sites (name='assign_sites')
- `worker_list/<int:pk>/update_email/` → views.update_email (name='update_email')
- 

---

## Views (logs/views.py)
All views are protected with `@login_required`.

### dashboard
- Fetches all sites
- Counts: total_sites, total_logs, total_active_sites, total_onhold_sites, total_completed_sites
- Renders: dashboard.html

### add_site
- GET: shows empty SiteForm
- POST: saves new Site, sets created_by=request.user
- Redirects to: dashboard

### site_detail(pk)
- Fetches Site by pk
- Fetches all DailyLogs for that site
- Renders: site_detail.html

### add_log(pk)
- pk = site pk
- GET: shows empty LogForm
- POST: saves new DailyLog, sets site_worked_on=site, created_by=request.user
- Redirects to: site_detail

### materials_log(pk)
- pk = DailyLog pk
- Fetches all MaterialEntries for that log
- Renders: materials_log.html

### add_mat_log(pk)
- pk = DailyLog pk
- GET: shows empty MaterialForm
- POST: saves new MaterialEntry, sets daily_log=log
- Redirects to: materials_log

### signup
- GET: shows empty SignUpForm
- POST: saves new User, creates UserProfile with selected role
- Redirects to: login

### worker_dashboard
- Fetches assigned sites for current worker (request.user.assigned_sites.all())
- Fetches today's marked site IDs (marked_sites)
- Renders: worker_dashboard.html

### worker_site_detail(pk)
- pk = site pk
- Fetches Site by pk
- Fetches Attendance records for current worker on that site
- Renders: worker_site_detail.html

### mark_attendance(pk)
- pk = site pk
- Checks if attendance already marked today for this worker on this site
- If not marked → creates Attendance record (present=True, today's date)
- Redirects to: worker_dashboard

### worker_list
- Fetches all UserProfiles where role='worker'
- Renders: worker_list.html


### worker_profile(pk)
- pk = User pk
- Fetches User by pk (only if role='worker')
- Fetches all attendance records for that worker
- Counts total_present and total_absent
- Renders: worker_profile.html

### assign_sites(pk)
- pk = worker (User) pk
- GET: shows AssignSiteForm with site dropdown
- POST: assigns selected site to worker using site.workers.add(worker)
- Redirects to: worker_profile

### update_email(pk)
- pk = worker (User) pk
- POST only: gets email from request.POST, saves to worker.email
- Redirects to: worker_profile

---

## Settings (settings.py additions)
```python
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
```

---

## What's Working
- Login/logout with Django built-in auth
- All pages protected with @login_required
- Dashboard page (in progress) — shows all sites + stats
- Add site form — creates new Site in DB
- Site detail page — shows site info + all daily logs for that site
- Add log form — creates new DailyLog linked to a site
- Materials log page — shows all materials for a specific daily log
- Add material form — creates new MaterialEntry linked to a daily log
- Base template with navbar on every page
- Django admin panel with all 3 models registered
- Dashboard page working — shows all sites with status, created by, created at
- Dashboard stats — total sites, active, on hold, completed, total logs
- UserProfile model with role field (manager/worker)
- Signup page with role selection
- Role-based redirect after login — managers go to full dashboard, workers go to worker dashboard
- Navbar shows login/signup when logged out, logout when logged in
- Worker dashboard (basic, ready for attendance and queries)
- Worker dashboard showing assigned sites
- Mark Attendance button — marks present for today, disabled after marking
- Attendance log page per site showing date and present/absent
- Auto-disabled button if already marked today using marked_sites check
- Workers assigned to sites by manager via admin panel
- ManyToManyField linking workers to sites
- Worker list page — managers can see all workers
- Worker profile page — shows assigned sites, attendance summary, full attendance history
- Assign worker to site feature — manager can assign sites to workers from worker profile page
- Worker list link on manager dashboard
-  Inline email editing on worker profile — click Edit, enter email, saves and reloads



---

## Current State
Just finished building the dashboard view with stats. Now building dashboard.html template which should show:
- Welcome message with logged in username ({{ request.user.username }})
- Stats: total sites, active sites, on hold sites, completed sites, total logs
- All sites displayed as cards/blocks with name, location, status
- Each site card links to /sites/<pk>/
- Dashboard complete. Deciding on next feature to build.
- Role system complete. Starting Attendance model for workers.
- Attendance system complete. Deciding next feature.
- Worker profile system complete. Building assign worker to site feature next.
- Assign worker feature complete. Moving to Query system next, then Bootstrap styling.

---

## Next Steps (planned)
1. Finish dashboard.html template
2. Add Bootstrap styling across all pages
3. Build material inventory/stock management feature
4. Add worker vs manager roles
5. Query/notification system for workers to raise issues
6. Dashboard sidebar with quick stats
7. Attendance model and marking system for workers
8. Query/notification system
9. Manager view of worker profiles and attendance
10. Material inventory/stock management
11. Bootstrap styling across all pages

---

## Key Django Concepts Learned
- Models, migrations, Django ORM
- ForeignKey relationships
- Views (function-based), GET vs POST
- Django forms and ModelForms
- URL routing, include(), dynamic URLs with <int:pk>
- Django templates, template tags ({% %} and {{ }})
- Base templates and {% block content %}
- @login_required decorator
- Django admin registration
- Built-in auth system (LoginView, LogoutView)
- Settings: LOGIN_URL, LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL

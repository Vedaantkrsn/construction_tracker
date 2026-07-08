from  django.urls import path
from . import views


urlpatterns= [
    path("dashboard/", views.dashboard, name='dashboard'),
    path("add_site/", views.add_site, name='add_site'),
    path("sites/<int:pk>/", views.site_detail, name='site_detail'),
    path("sites/<int:pk>/add_log/", views.add_log, name='add_log'),
    path("logs/<int:pk>/materials_log", views.materials_log, name='materials_log'),
    path("logs/<int:pk>/materials_log/add_mat_log/", views.add_mat_log, name='add_mat_log'),
    path("signup/", views.signup, name='signup'),
    path("worker_dashboard/", views.worker_dashboard, name='worker_dashboard'),
    path("worker/site/<int:pk>/", views.worker_site_detail, name='worker_site_detail'),
    path("worker/site/<int:pk>/mark_attendance/", views.mark_attendance, name='mark_attendance'),
    path("dashboard/worker_list/", views.worker_list, name='worker_list'),
    path("dashboard/worker_list/<int:pk>/", views.worker_profile, name='worker_profile'),
    path("worker/<int:pk>/assign_sites/", views.assign_sites, name='assign_sites'),
    path("worker_list/<int:pk>/update_email/", views.update_email, name='update_email'),
]
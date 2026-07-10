from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Site(models.Model):
    STATUS_CHOICES=[
        ('active','Active'),
        ('on hold', 'On Hold'),
        ('completed', 'Completed'),
    ]
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    name=models.CharField(max_length=200)
    location=models.CharField(max_length=200)
    start_date=models.DateField()
    company_name=models.CharField(max_length=200)
    created_by=models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    workers=models.ManyToManyField(User, related_name='assigned_sites', blank=True)
    
    def __str__(self):
        return self.name
    
class DailyLog(models.Model):
    site_worked_on=models.ForeignKey(Site, on_delete=models.CASCADE)
    date_today=models.DateField()
    worker_count=models.IntegerField()
    site_manager=models.CharField(max_length=200)
    work_overview=models.TextField()
    created_by=models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural="Daily Log"

    def __str__(self):
        return f"{self.site_worked_on.name} - {self.date_today}"
    
class MaterialEntry(models.Model):
    daily_log=models.ForeignKey(DailyLog, on_delete=models.CASCADE)
    material_name=models.CharField(max_length=200)
    quantity=models.DecimalField(max_digits=10, decimal_places=2)
    UNIT_CHOICES=[
        ('bags','Bags'),
        ('kg', 'Kilogram'),
        ('lt', 'Litres'),
        ('unit', 'Units'),
    ]
    unit=models.CharField(max_length=20, choices=UNIT_CHOICES)

    class Meta:
        verbose_name_plural="Material Entries"

    def __str__(self):
        return f"{self.material_name} - {self.quantity} {self.unit}"

class UserProfile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES=[
        ('manager', 'Manager'),
        ('worker', 'Worker'),
    ]
    role=models.CharField(max_length=20, choices=ROLE_CHOICES)
    def __str__(self):
        return self.role
    
class Attendance(models.Model):
    worker=models.ForeignKey(User, on_delete=models.CASCADE)
    worksite=models.ForeignKey(Site, on_delete=models.CASCADE)
    attendance_date=models.DateField()
    present_or_absent=models.BooleanField()
    def __str__(self):
        return f"{self.worker.username} - {self.attendance_date}"
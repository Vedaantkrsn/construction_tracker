from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

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
    worker_count=models.PositiveIntegerField()
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
    quantity=models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(0)])
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
    
# class Attendance(models.Model):
#     worker=models.ForeignKey(User, on_delete=models.CASCADE)
#     worksite=models.ForeignKey(Site, on_delete=models.CASCADE)
#     attendance_date=models.DateField()
#     present_or_absent=models.BooleanField()
#     def __str__(self):
#         return f"{self.worker.username} - {self.attendance_date}"

class Attendance(models.Model):
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    worksite = models.ForeignKey(Site, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    present_or_absent = models.BooleanField()
    marked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["worker", "worksite", "attendance_date"],
                name="one_attendance_per_worker_site_day",
            )
        ]

    def __str__(self):
        return f"{self.worker.username} - {self.attendance_date}"


class AttendanceQRCode(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="attendance_qr_codes")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_valid(self):
        return self.is_active and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.site.name} QR - expires {self.expires_at:%d %b %Y %H:%M}"

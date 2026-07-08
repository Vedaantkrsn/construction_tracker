from django.contrib import admin
from .models import Site,DailyLog,MaterialEntry,UserProfile,Attendance
# Register your models here.

admin.site.register(Site)
admin.site.register(DailyLog)
admin.site.register(MaterialEntry)
admin.site.register(UserProfile)
admin.site.register(Attendance)

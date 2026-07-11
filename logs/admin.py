from django.contrib import admin
from .models import Site,DailyLog,MaterialEntry,UserProfile,Attendance,AttendanceQRCode
# Register your models here.

#editfrom django.contrib import admin

admin.site.site_header = "Construction Tracker Admin"
admin.site.site_title = "Construction Tracker"
admin.site.index_title = "Administration"

admin.site.register(Site)
admin.site.register(DailyLog)
admin.site.register(MaterialEntry)
# admin.site.register(UserProfile)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username",)
    ordering = ("user__username",)
admin.site.register(Attendance)
admin.site.register(AttendanceQRCode)

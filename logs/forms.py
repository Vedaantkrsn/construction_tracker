from django import forms
from .models import Site, DailyLog, MaterialEntry, UserProfile, User
from django.contrib.auth.forms import UserCreationForm

class SiteForm(forms.ModelForm):
    class Meta:
        model= Site
        fields= ['name', 'location', 'start_date', 'company_name']

class LogForm(forms.ModelForm):
    class Meta:
        model= DailyLog
        fields= ['date_today','worker_count','site_manager','work_overview']

class MaterialForm(forms.ModelForm):
    class Meta:
        model=MaterialEntry
        fields= ['material_name','quantity','unit']

class SignUpForm(UserCreationForm):
    role=forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    class Meta:
        model=User
        fields=['username', 'password1', 'password2','role']

class AssignSiteForm(forms.Form):
    sites=forms.ModelChoiceField(queryset=Site.objects.all())
    
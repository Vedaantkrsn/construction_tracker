from django import forms
from .models import Site, DailyLog, MaterialEntry, UserProfile, User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class SiteForm(forms.ModelForm):
    class Meta:
        model= Site
        fields= ['name', 'location', 'start_date', 'company_name','status']

class LogForm(forms.ModelForm):

    class Meta:
        model = DailyLog
        fields = "__all__"

    def clean_worker_count(self):
        count = self.cleaned_data["worker_count"]

        if count < 0:
            raise forms.ValidationError(
                "Worker count cannot be negative"
            )

        return count

class MaterialForm(forms.ModelForm):

    class Meta:
        model = MaterialEntry
        fields = "__all__"

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if quantity < 0:
            raise forms.ValidationError(
                "Quantity cannot be negative"
            )

        return quantity

class SignUpForm(UserCreationForm): #edited
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

class AssignSiteForm(forms.Form):
    sites=forms.ModelChoiceField(queryset=Site.objects.all())

class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Choose a username",
        })

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Create a password",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm password",
        })
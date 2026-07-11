from .models import UserProfile


def user_role(request):
    role = None

    if request.user.is_authenticated and not request.user.is_superuser:
        profile = UserProfile.objects.filter(user=request.user).first()

        if profile:
            role = profile.role

    return {
        "user_role": role
    }
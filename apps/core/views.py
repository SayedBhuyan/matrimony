from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from apps.profiles.services import calculate_profile_completion


def landing_page(request):
    """Public landing page for the matrimony platform."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/landing.html')


@login_required
def dashboard(request):
    """Authenticated user dashboard with profile health overview."""
    profile = getattr(request.user, 'profile', None)
    completion = calculate_profile_completion(profile) if profile else None

    context = {
        'profile': profile,
        'completion': completion,
    }
    return render(request, 'core/dashboard.html', context)

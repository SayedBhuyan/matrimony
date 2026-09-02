from django.shortcuts import render


def landing_page(request):
    """Public landing page for the matrimony platform."""
    if request.user.is_authenticated:
        return render(request, 'core/dashboard.html')
    return render(request, 'core/landing.html')


def dashboard(request):
    """Authenticated user dashboard."""
    return render(request, 'core/dashboard.html')

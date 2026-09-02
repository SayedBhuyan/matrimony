from django.contrib import messages
from django.contrib.auth import login, views as auth_views
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import (
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    LoginForm,
    RegistrationForm,
)


def register(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'Welcome! Your account has been created successfully.'
            )
            return redirect('core:dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(auth_views.LoginView):
    """Custom login view using our styled form."""
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class CustomLogoutView(auth_views.LogoutView):
    """Logout and redirect to landing page."""
    next_page = reverse_lazy('core:landing')


class CustomPasswordResetView(auth_views.PasswordResetView):
    """Custom password reset view."""
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    form_class = CustomPasswordResetForm


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    """Password reset email sent confirmation."""
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """Set new password after clicking reset link."""
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    form_class = CustomSetPasswordForm


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    """Password reset complete confirmation."""
    template_name = 'accounts/password_reset_complete.html'

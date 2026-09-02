from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from apps.connections.models import Interest, Favorite
from apps.messaging.models import Message
from apps.messaging.models import Notification
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
    unread_messages = Message.objects.filter(
        Q(conversation__interest__receiver=request.user) | Q(conversation__interest__sender=request.user),
        read_at__isnull=True,
    ).exclude(sender=request.user).count()

    context = {
        'profile': profile,
        'completion': completion,
        'profile_views_count': profile.views.count() if profile else 0,
        'interests_received_count': Interest.objects.filter(receiver=request.user, status='pending').count(),
        'interests_sent_pending_count': Interest.objects.filter(sender=request.user, status='pending').count(),
        'accepted_connections_count': Interest.objects.filter(
            status='accepted',
        ).filter(sender=request.user) | Interest.objects.filter(
            status='accepted', receiver=request.user,
        ),
        'unread_messages_count': unread_messages,
        'unread_notifications_count': Notification.objects.filter(recipient=request.user, is_read=False).count(),
        'favorites_count': Favorite.objects.filter(user=request.user).count(),
    }
    return render(request, 'core/dashboard.html', context)

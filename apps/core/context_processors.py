from apps.messaging.models import Notification


def activity_counts(request):
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}
    return {
        'unread_notifications_count': Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).count(),
    }

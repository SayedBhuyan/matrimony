from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.connections.models import Interest
from .models import Conversation, Message, Notification


@login_required
def conversations(request):
    conversations = Conversation.objects.filter(
        Q(interest__sender=request.user) | Q(interest__receiver=request.user)
    ).annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__read_at__isnull=True) & ~Q(messages__sender=request.user),
        )
    ).select_related('interest__sender__profile', 'interest__receiver__profile')
    return render(request, 'messaging/conversations.html', {'conversations': conversations.distinct()})


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in [conversation.interest.sender, conversation.interest.receiver]:
        return JsonResponse({'error': 'Not allowed'}, status=403)

    messages = conversation.messages.select_related('sender__profile').all()
    conversation.messages.filter(read_at__isnull=True).exclude(sender=request.user).update(read_at=timezone.now())
    return render(request, 'messaging/conversation_detail.html', {
        'conversation': conversation,
        'conversation_messages': messages,
    })


@login_required
@require_http_methods(['POST'])
def send_message(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user not in [conversation.interest.sender, conversation.interest.receiver]:
        return JsonResponse({'error': 'Not allowed'}, status=403)

    body = request.POST.get('body', '').strip()
    if not body:
        return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        body=body,
    )

    recipient = conversation.interest.receiver if request.user == conversation.interest.sender else conversation.interest.sender
    Notification.objects.create(
        recipient=recipient,
        notification_type='new_message',
        title='New message',
        message=f'{request.user.email} sent you a message.',
        action_url=f'/messages/conversation/{conversation.id}/',
    )

    return JsonResponse({'status': 'success', 'message': 'Message sent.', 'message_id': str(message.id), 'body': message.body})


@login_required
def notifications(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).update(is_read=True)
    items = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'messaging/notifications.html', {'notifications': items})


@login_required
@require_http_methods(['POST'])
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return JsonResponse({'status': 'success', 'message': 'Notification marked as read.'})

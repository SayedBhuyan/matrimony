from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Case, IntegerField, Value, When
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from apps.messaging.models import Conversation, Notification
from apps.profiles.models import Profile
from .models import Interest, Favorite, Block, Report


@login_required
@require_http_methods(["POST"])
def send_interest(request, profile_id):
    """Send an interest to a profile."""
    profile = get_object_or_404(Profile, id=profile_id)

    if profile.user == request.user:
        return JsonResponse({'error': 'You cannot send interest to yourself.'}, status=400)

    message = request.POST.get('message', '')
    
    # Check if user has already sent a pending interest
    existing = Interest.objects.filter(
        sender=request.user,
        receiver=profile.user,
        status='pending'
    ).exists()
    
    if existing:
        return JsonResponse({'error': 'You already sent an interest to this profile.'}, status=400)
    
    # Check if users have blocked each other
    if Block.objects.filter(
        user=request.user,
        blocked_user=profile.user
    ).exists():
        return JsonResponse({'error': 'You have blocked this user.'}, status=400)
    
    if Block.objects.filter(
        user=profile.user,
        blocked_user=request.user
    ).exists():
        return JsonResponse({'error': 'This user has blocked you.'}, status=400)
    
    # Create interest
    interest = Interest.objects.create(
        sender=request.user,
        receiver=profile.user,
        message=message,
    )
    sender_profile = getattr(request.user, 'profile', None)
    Notification.objects.create(
        recipient=profile.user,
        notification_type='interest_received',
        title='New interest received',
        message=f'{getattr(getattr(request.user, "profile", None), "display_name", request.user.email)} sent you an interest.',
        action_url=f'/profiles/{sender_profile.id}/' if sender_profile else '',
    )
    
    return JsonResponse({
        'status': 'success',
        'message': 'Interest sent successfully!'
    })


@login_required
@require_http_methods(["POST"])
def accept_interest(request, interest_id):
    """Accept an interest."""
    interest = get_object_or_404(Interest, id=interest_id)
    
    if interest.receiver != request.user:
        return HttpResponseForbidden('You are not authorized to accept this interest.')
    
    if interest.status != 'pending':
        return JsonResponse({'error': 'This interest is no longer pending.'}, status=400)
    
    interest.status = 'accepted'
    interest.responded_at = timezone.now()
    interest.save()

    conversation, _ = Conversation.objects.get_or_create(interest=interest)
    Notification.objects.create(
        recipient=interest.sender,
        notification_type='interest_accepted',
        title='Interest accepted',
        message=f'{interest.receiver.profile.display_name if hasattr(interest.receiver, "profile") and interest.receiver.profile else "A member"} accepted your interest.',
        action_url=f'/messages/conversation/{conversation.id}/',
    )

    return JsonResponse({'status': 'success', 'message': 'Interest accepted!', 'status_label': interest.get_status_display()})


@login_required
@require_http_methods(["POST"])
def reject_interest(request, interest_id):
    """Reject an interest."""
    interest = get_object_or_404(Interest, id=interest_id)
    
    if interest.receiver != request.user:
        return HttpResponseForbidden('You are not authorized to reject this interest.')
    
    if interest.status != 'pending':
        return JsonResponse({'error': 'This interest is no longer pending.'}, status=400)
    
    interest.status = 'rejected'
    interest.responded_at = timezone.now()
    interest.save()
    
    return JsonResponse({'status': 'success', 'message': 'Interest rejected.', 'status_label': interest.get_status_display()})


@login_required
@require_http_methods(["POST"])
def cancel_interest(request, interest_id):
    """Cancel an interest sent by the user."""
    interest = get_object_or_404(Interest, id=interest_id)
    
    if interest.sender != request.user:
        return HttpResponseForbidden('You are not authorized to cancel this interest.')
    
    if interest.status != 'pending':
        return JsonResponse({'error': 'This interest is no longer pending.'}, status=400)
    
    interest.status = 'cancelled'
    interest.responded_at = timezone.now()
    interest.save()
    
    return JsonResponse({'status': 'success', 'message': 'Interest cancelled.', 'status_label': interest.get_status_display()})


@login_required
def received_interests(request):
    """View received interests."""
    interests = Interest.objects.filter(
        receiver=request.user
    ).select_related(
        'sender__profile'
    ).annotate(
        pending_first=Case(
            When(status='pending', then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by('pending_first', '-sent_at')
    
    context = {
        'interests': interests,
    }
    return render(request, 'connections/received_interests.html', context)


@login_required
def sent_interests(request):
    """View sent interests."""
    interests = Interest.objects.filter(
        sender=request.user
    ).select_related(
        'receiver__profile'
    ).annotate(
        pending_first=Case(
            When(status='pending', then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by('pending_first', '-sent_at')
    
    context = {
        'interests': interests,
    }
    return render(request, 'connections/sent_interests.html', context)


@login_required
@require_http_methods(["POST"])
def add_favorite(request, profile_id):
    """Add a profile to favorites."""
    profile = get_object_or_404(Profile, id=profile_id)
    
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        profile=profile
    )
    
    if created:
        return JsonResponse({'status': 'success', 'message': 'Added to favorites!'})
    else:
        return JsonResponse({'status': 'info', 'message': 'Already in favorites.'})


@login_required
@require_http_methods(["POST"])
def remove_favorite(request, profile_id):
    """Remove a profile from favorites."""
    profile = get_object_or_404(Profile, id=profile_id)
    
    Favorite.objects.filter(
        user=request.user,
        profile=profile
    ).delete()
    
    return JsonResponse({'status': 'success', 'message': 'Removed from favorites.'})


@login_required
def favorites_list(request):
    """View favorite profiles."""
    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related(
        'profile__user'
    ).order_by('-created_at')
    
    context = {
        'favorites': favorites,
    }
    return render(request, 'connections/favorites_list.html', context)


@login_required
@require_http_methods(["POST"])
def block_user(request, user_id):
    """Block another user from future contact or visibility."""
    target_user = get_object_or_404(get_user_model(), id=user_id)

    if target_user == request.user:
        return JsonResponse({'error': 'You cannot block yourself.'}, status=400)

    block, created = Block.objects.get_or_create(
        user=request.user,
        blocked_user=target_user,
        defaults={'reason': request.POST.get('reason', '').strip()},
    )

    if created:
        return JsonResponse({'status': 'success', 'message': 'User blocked successfully.'})
    return JsonResponse({'status': 'info', 'message': 'This user is already blocked.'})


@login_required
@require_http_methods(["POST"])
def unblock_user(request, user_id):
    """Remove a block placed by the current user."""
    target_user = get_object_or_404(get_user_model(), id=user_id)
    deleted, _ = Block.objects.filter(user=request.user, blocked_user=target_user).delete()
    if not deleted:
        return JsonResponse({'error': 'This user is not currently blocked.'}, status=400)
    return JsonResponse({'status': 'success', 'message': 'User unblocked successfully.'})


@login_required
def blocked_users(request):
    """List profiles blocked by the current user."""
    blocks = Block.objects.filter(user=request.user).select_related('blocked_user__profile')
    return render(request, 'connections/blocked_users.html', {'blocks': blocks})


@login_required
@require_http_methods(["POST"])
def report_user(request, user_id):
    """Submit a trust & safety report for another user."""
    target_user = get_object_or_404(get_user_model(), id=user_id)

    if target_user == request.user:
        return JsonResponse({'error': 'You cannot report yourself.'}, status=400)

    report_type = request.POST.get('report_type', '').strip()
    description = request.POST.get('description', '').strip()

    if not report_type or not description:
        return JsonResponse({'error': 'Please provide both a report type and a description.'}, status=400)

    report = Report.objects.create(
        reporter=request.user,
        reported_user=target_user,
        report_type=report_type,
        description=description,
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Your report has been submitted successfully.',
        'report_id': str(report.id),
    })

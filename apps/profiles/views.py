from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    EducationForm,
    FamilyForm,
    LifestyleForm,
    PartnerPreferenceForm,
    ProfessionForm,
    ProfileBasicForm,
    ProfilePhotoUploadForm,
)
from .models import (
    EducationDetail,
    FamilyDetail,
    LifestyleDetail,
    PartnerPreference,
    ProfessionDetail,
    Profile,
    ProfilePhoto,
    ProfileView,
)
from .services import calculate_profile_completion
from apps.connections.models import Block, Interest


@login_required
def my_profile(request):
    """View user's own profile with completion analytics and edit options."""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return redirect('profiles:profile_setup')

    completion = calculate_profile_completion(profile)
    photos = profile.photos.all()

    context = {
        'profile': profile,
        'completion': completion,
        'photos': photos,
        'is_owner': True,
    }
    return render(request, 'profiles/my_profile.html', context)


@login_required
def profile_setup(request):
    """Initial profile setup for users who just registered."""
    profile = getattr(request.user, 'profile', None)
    if profile:
        return redirect('profiles:profile_edit', section='basic')

    if request.method == 'POST':
        form = ProfileBasicForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Basic profile created! Now add your education and profession details.')
            return redirect('profiles:profile_edit', section='education')
    else:
        initial_name = request.user.get_short_name().capitalize()
        form = ProfileBasicForm(initial={'display_name': initial_name})

    return render(request, 'profiles/setup.html', {'form': form})


@login_required
def profile_edit(request, section='basic'):
    """
    Unified multi-tab profile editor:
    Sections: basic, education, profession, family, lifestyle, preferences, photos.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return redirect('profiles:profile_setup')

    valid_sections = ['basic', 'education', 'profession', 'family', 'lifestyle', 'preferences', 'photos']
    if section not in valid_sections:
        section = 'basic'

    form = None
    photo_form = None

    if section == 'basic':
        if request.method == 'POST':
            form = ProfileBasicForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Basic profile updated successfully.')
                return redirect('profiles:profile_edit', section='education')
        else:
            form = ProfileBasicForm(instance=profile)

    elif section == 'education':
        edu_instance, _ = EducationDetail.objects.get_or_create(profile=profile)
        if request.method == 'POST':
            form = EducationForm(request.POST, instance=edu_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Education details saved.')
                return redirect('profiles:profile_edit', section='profession')
        else:
            form = EducationForm(instance=edu_instance)

    elif section == 'profession':
        prof_instance, _ = ProfessionDetail.objects.get_or_create(profile=profile)
        if request.method == 'POST':
            form = ProfessionForm(request.POST, instance=prof_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Career and profession details saved.')
                return redirect('profiles:profile_edit', section='family')
        else:
            form = ProfessionForm(instance=prof_instance)

    elif section == 'family':
        family_instance, _ = FamilyDetail.objects.get_or_create(profile=profile)
        if request.method == 'POST':
            form = FamilyForm(request.POST, instance=family_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Family background details saved.')
                return redirect('profiles:profile_edit', section='lifestyle')
        else:
            form = FamilyForm(instance=family_instance)

    elif section == 'lifestyle':
        lifestyle_instance, _ = LifestyleDetail.objects.get_or_create(profile=profile)
        if request.method == 'POST':
            form = LifestyleForm(request.POST, instance=lifestyle_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Lifestyle habits & diet saved.')
                return redirect('profiles:profile_edit', section='preferences')
        else:
            form = LifestyleForm(instance=lifestyle_instance)

    elif section == 'preferences':
        pref_instance, _ = PartnerPreference.objects.get_or_create(profile=profile)
        if request.method == 'POST':
            form = PartnerPreferenceForm(request.POST, instance=pref_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Partner preferences updated.')
                return redirect('profiles:my_profile')
        else:
            form = PartnerPreferenceForm(instance=pref_instance)

    elif section == 'photos':
        photo_form = ProfilePhotoUploadForm()

    completion = calculate_profile_completion(profile)
    photos = profile.photos.all()

    context = {
        'profile': profile,
        'active_section': section,
        'form': form,
        'photo_form': photo_form,
        'photos': photos,
        'completion': completion,
    }
    return render(request, 'profiles/edit.html', context)


@login_required
@require_POST
def photo_upload(request):
    """Handle asynchronous or standard profile photo upload."""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return redirect('profiles:profile_setup')

    form = ProfilePhotoUploadForm(request.POST, request.FILES)
    if form.is_valid():
        photo = form.save(commit=False)
        photo.profile = profile
        # If this is user's first photo, make it primary automatically
        if not profile.photos.exists():
            photo.is_primary = True
        photo.save()
        messages.success(request, 'Profile photo uploaded successfully.')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Photo upload error: {error}")

    return redirect('profiles:profile_edit', section='photos')


@login_required
@require_POST
def photo_delete(request, photo_id):
    """Securely delete a photo owned by the logged-in user."""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        raise PermissionDenied

    photo = get_object_or_404(ProfilePhoto, id=photo_id, profile=profile)
    is_was_primary = photo.is_primary
    photo.image.delete(save=False)
    photo.delete()

    # If deleted photo was primary, assign primary to the next photo if any exists
    if is_was_primary:
        next_photo = profile.photos.first()
        if next_photo:
            next_photo.is_primary = True
            next_photo.save()

    messages.success(request, 'Photo removed successfully.')
    return redirect('profiles:profile_edit', section='photos')


@login_required
@require_POST
def photo_set_primary(request, photo_id):
    """Set a specific photo as primary for the profile."""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        raise PermissionDenied

    photo = get_object_or_404(ProfilePhoto, id=photo_id, profile=profile)
    photo.is_primary = True
    photo.save()

    messages.success(request, 'Primary profile photo updated.')
    return redirect('profiles:profile_edit', section='photos')


def profile_detail(request, profile_id):
    """
    Public or member detail view for a specific matrimonial profile.
    Enforces privacy settings, visibility rules, and IDOR protection.
    """
    profile = get_object_or_404(
        Profile.objects.select_related(
            'user', 'education', 'profession', 'family', 'lifestyle', 'partner_preference'
        ).prefetch_related('photos'),
        id=profile_id,
    )

    is_owner = request.user.is_authenticated and request.user == profile.user

    if request.user.is_authenticated and not is_owner and Block.objects.filter(
        Q(user=request.user, blocked_user=profile.user) |
        Q(user=profile.user, blocked_user=request.user)
    ).exists():
        raise Http404

    if request.user.is_authenticated and not is_owner:
        ProfileView.objects.get_or_create(
            profile=profile,
            viewer=request.user,
            viewed_date=timezone.localdate(),
        )

    # Visibility Enforcement:
    # 1. Registered only
    if profile.visibility == 'registered_only' and not request.user.is_authenticated:
        messages.info(request, 'Please log in to view full member profiles.')
        return redirect(f"{reverse('accounts:login')}?next={request.path}")

    # 2. Connections only (unless owner)
    if profile.visibility == 'connections_only' and not is_owner:
        if not request.user.is_authenticated:
            messages.info(request, 'Please log in to view this profile.')
            return redirect('accounts:login')
        has_connection = Interest.objects.filter(
            Q(sender=request.user, receiver=profile.user) |
            Q(sender=profile.user, receiver=request.user),
            status='accepted',
        ).exists()
        if not has_connection:
            raise Http404

    current_interest = None
    if request.user.is_authenticated and not is_owner:
        current_interest = Interest.objects.filter(
            Q(sender=request.user, receiver=profile.user) |
            Q(sender=profile.user, receiver=request.user),
        ).select_related('conversation').order_by('-sent_at').first()

    # Visible photos based on privacy
    if is_owner:
        photos = profile.photos.all()
    elif request.user.is_authenticated:
        photos = profile.photos.filter(is_approved=True)
    else:
        photos = profile.photos.filter(is_approved=True, visibility='public')

    context = {
        'profile': profile,
        'photos': photos,
        'is_owner': is_owner,
        'current_interest': current_interest,
    }
    return render(request, 'profiles/detail.html', context)

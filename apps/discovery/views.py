from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from apps.profiles.models import Profile
from .filters import ProfileFilter
from .matching import SimplePreferenceScorer, score_profile_candidates


def get_base_discovery_queryset(request):
    """
    Base queryset for discovery enforcing:
    - User is active and not deactivated
    - Excludes requester's own profile
    - Optimizes queries with select_related & prefetch_related
    """
    qs = Profile.objects.filter(
        user__is_active=True,
        user__deactivated_at__isnull=True,
    ).select_related(
        'user',
        'education',
        'profession',
        'family',
        'lifestyle',
        'partner_preference',
    ).prefetch_related('photos')

    # Exclude own profile if logged in
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        qs = qs.exclude(user=request.user)

    # If unauthenticated, only show public visibility profiles
    if not request.user.is_authenticated:
        qs = qs.filter(visibility='public')

    return qs


def matches_view(request):
    """
    Personalized Match Recommendations page.
    Automatically filters by opposite gender and scores candidates against
    the user's PartnerPreferences.
    """
    searcher_profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None

    queryset = get_base_discovery_queryset(request)

    # Filter by opposite gender by default if searcher's gender is known
    target_gender = None
    if searcher_profile and searcher_profile.gender:
        if searcher_profile.gender == 'male':
            target_gender = 'female'
        elif searcher_profile.gender == 'female':
            target_gender = 'male'

    if target_gender:
        queryset = queryset.filter(gender=target_gender)

    # Score all candidates
    scorer = SimplePreferenceScorer()
    scored_candidates = score_profile_candidates(searcher_profile, list(queryset), scorer)

    # Pagination
    paginator = Paginator(scored_candidates, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'searcher_profile': searcher_profile,
        'total_matches_count': len(scored_candidates),
    }
    return render(request, 'discovery/matches.html', context)


def search_view(request):
    """
    Full Search & Filter catalog.
    Enables multi-facet search across religion, age, location, profession, etc.
    """
    searcher_profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None
    queryset = get_base_discovery_queryset(request)

    # Default to opposite gender if query parameters are completely empty and searcher has a gender
    if not request.GET and searcher_profile and searcher_profile.gender:
        opposite = 'female' if searcher_profile.gender == 'male' else 'male'
        profile_filter = ProfileFilter({'gender': opposite}, queryset=queryset)
    else:
        profile_filter = ProfileFilter(request.GET or None, queryset=queryset)

    filtered_qs = profile_filter.qs

    sort_param = request.GET.get('sort', 'match')
    scorer = SimplePreferenceScorer()

    if sort_param == 'match':
        candidates = score_profile_candidates(searcher_profile, list(filtered_qs), scorer)
    else:
        # Pre-sorted by Django ORM in filter_sort
        candidates = []
        for cand in filtered_qs:
            cand.match_breakdown = scorer.calculate_compatibility(searcher_profile, cand)
            candidates.append(cand)

    # Pagination
    paginator = Paginator(candidates, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'filter': profile_filter,
        'page_obj': page_obj,
        'searcher_profile': searcher_profile,
        'total_results_count': len(candidates),
    }
    return render(request, 'discovery/search.html', context)

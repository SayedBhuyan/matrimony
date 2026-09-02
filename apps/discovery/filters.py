from datetime import date, timedelta
import django_filters
from django import forms
from django.db.models import Q
from apps.profiles.models import Profile, EducationDetail, LifestyleDetail


class ProfileFilter(django_filters.FilterSet):
    """
    Comprehensive, declarative search filter for Matrimonial Profiles.
    """

    q = django_filters.CharFilter(
        method='filter_keyword_search',
        label='Keyword Search',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Search by name, profession, city, or bio...',
        }),
    )

    gender = django_filters.ChoiceFilter(
        choices=Profile.GENDER_CHOICES,
        label='Looking For (Gender)',
        widget=forms.Select(attrs={'class': 'form-input form-select'}),
    )

    min_age = django_filters.NumberFilter(
        method='filter_min_age',
        label='Min Age',
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Min (18)'}),
    )

    max_age = django_filters.NumberFilter(
        method='filter_max_age',
        label='Max Age',
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Max (70)'}),
    )

    marital_status = django_filters.ChoiceFilter(
        choices=Profile.MARITAL_STATUS_CHOICES,
        label='Marital Status',
        widget=forms.Select(attrs={'class': 'form-input form-select'}),
        empty_label='Any Marital Status',
    )

    religion = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Religion',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Hindu, Muslim, Christian'}),
    )

    mother_tongue = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Mother Tongue',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. English, Hindi, Bengali'}),
    )

    country = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Country',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. India, USA, Canada'}),
    )

    city = django_filters.CharFilter(
        lookup_expr='icontains',
        label='City',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Mumbai, New York'}),
    )

    highest_education = django_filters.ChoiceFilter(
        field_name='education__highest_education',
        choices=EducationDetail.EDUCATION_LEVEL_CHOICES,
        label='Education Level',
        widget=forms.Select(attrs={'class': 'form-input form-select'}),
        empty_label='Any Education Level',
    )

    diet = django_filters.ChoiceFilter(
        field_name='lifestyle__diet',
        choices=LifestyleDetail.DIET_CHOICES,
        label='Dietary Preference',
        widget=forms.Select(attrs={'class': 'form-input form-select'}),
        empty_label='Any Diet',
    )

    has_photo = django_filters.BooleanFilter(
        method='filter_has_photo',
        label='Only Profiles with Photo',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
    )

    is_verified = django_filters.BooleanFilter(
        field_name='is_verified',
        label='Only Verified Profiles',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
    )

    sort = django_filters.ChoiceFilter(
        method='filter_sort',
        label='Sort By',
        choices=(
            ('match', 'Best Compatibility'),
            ('newest', 'Recently Joined'),
            ('age_asc', 'Age: Youngest First'),
            ('age_desc', 'Age: Eldest First'),
        ),
        widget=forms.Select(attrs={'class': 'form-input form-select'}),
    )

    class Meta:
        model = Profile
        fields = [
            'q',
            'gender',
            'min_age',
            'max_age',
            'marital_status',
            'religion',
            'mother_tongue',
            'country',
            'city',
            'highest_education',
            'diet',
            'has_photo',
            'is_verified',
            'sort',
        ]

    def filter_keyword_search(self, queryset, name, value):
        if not value:
            return queryset
        val = value.strip()
        return queryset.filter(
            Q(display_name__icontains=val)
            | Q(about_me__icontains=val)
            | Q(city__icontains=val)
            | Q(state__icontains=val)
            | Q(country__icontains=val)
            | Q(profession__occupation__icontains=val)
            | Q(education__institution__icontains=val)
            | Q(education__field_of_study__icontains=val)
        )

    def filter_min_age(self, queryset, name, value):
        if not value:
            return queryset
        # Date of birth <= today - min_age years
        today = date.today()
        latest_dob = date(today.year - int(value), today.month, today.day)
        return queryset.filter(date_of_birth__lte=latest_dob)

    def filter_max_age(self, queryset, name, value):
        if not value:
            return queryset
        # Date of birth >= today - (max_age + 1) years + 1 day
        today = date.today()
        earliest_dob = date(today.year - int(value) - 1, today.month, today.day) + timedelta(days=1)
        return queryset.filter(date_of_birth__gte=earliest_dob)

    def filter_has_photo(self, queryset, name, value):
        if value:
            return queryset.filter(photos__is_approved=True).distinct()
        return queryset

    def filter_sort(self, queryset, name, value):
        if value == 'newest':
            return queryset.order_by('-created_at')
        if value == 'age_asc':
            return queryset.order_by('-date_of_birth')  # Youngest has later birthdate
        if value == 'age_desc':
            return queryset.order_by('date_of_birth')   # Eldest has earlier birthdate
        return queryset  # 'match' sorting will be handled by scoring engine

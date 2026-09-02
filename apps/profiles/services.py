"""
Profile Completion & Business Logic Service.
Provides declarative calculation of profile readiness, completion percentage,
and recommended missing fields.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class SectionReport:
    name: str
    key: str
    weight: int
    score: int
    completed: bool
    missing_fields: List[str] = field(default_factory=list)


def calculate_profile_completion(profile) -> Dict[str, Any]:
    """
    Calculate the profile completion percentage and generate an actionable report.
    Total weight equals 100 points:
    - Basic Information: 25 points
    - Profile Photo: 20 points
    - Education: 15 points
    - Profession: 15 points
    - Family Details: 10 points
    - Lifestyle & Habits: 5 points
    - Partner Preferences: 10 points
    """
    if not profile:
        return {
            'percentage': 0,
            'is_ready_for_discovery': False,
            'sections': [],
            'missing_recommended': ['Basic Profile', 'Photo', 'Education', 'Profession'],
        }

    sections = []
    total_score = 0

    # 1. Basic Information (Weight: 25)
    basic_missing = []
    if not profile.display_name:
        basic_missing.append('Display Name')
    if not profile.date_of_birth:
        basic_missing.append('Date of Birth')
    if not profile.gender:
        basic_missing.append('Gender')
    if not profile.city:
        basic_missing.append('City')
    if not profile.about_me or len(profile.about_me.strip()) < 20:
        basic_missing.append('About Me (min 20 chars)')

    basic_weight = 25
    basic_score = int(basic_weight * (1 - (len(basic_missing) / 5)))
    total_score += basic_score
    sections.append(SectionReport(
        name='Basic Profile',
        key='basic',
        weight=basic_weight,
        score=basic_score,
        completed=len(basic_missing) == 0,
        missing_fields=basic_missing,
    ))

    # 2. Photos (Weight: 20)
    photo_missing = []
    has_primary_photo = profile.photos.filter(is_primary=True, is_approved=True).exists()
    total_photos_count = profile.photos.filter(is_approved=True).count()
    if not has_primary_photo and total_photos_count == 0:
        photo_missing.append('Primary Profile Photo')
    elif total_photos_count < 2:
        photo_missing.append('Additional Photos (min 2 recommended)')

    photo_weight = 20
    if has_primary_photo or total_photos_count > 0:
        photo_score = 20 if total_photos_count >= 2 else 15
    else:
        photo_score = 0
    total_score += photo_score
    sections.append(SectionReport(
        name='Profile Photos',
        key='photos',
        weight=photo_weight,
        score=photo_score,
        completed=len(photo_missing) == 0,
        missing_fields=photo_missing,
    ))

    # 3. Education (Weight: 15)
    edu_missing = []
    if hasattr(profile, 'education') and profile.education:
        if not profile.education.highest_education:
            edu_missing.append('Highest Education')
        if not profile.education.institution:
            edu_missing.append('College / University')
        edu_score = 15 if len(edu_missing) == 0 else (8 if profile.education.highest_education else 0)
    else:
        edu_missing = ['Highest Education', 'College / University']
        edu_score = 0
    total_score += edu_score
    sections.append(SectionReport(
        name='Education',
        key='education',
        weight=15,
        score=edu_score,
        completed=len(edu_missing) == 0,
        missing_fields=edu_missing,
    ))

    # 4. Profession (Weight: 15)
    prof_missing = []
    if hasattr(profile, 'profession') and profile.profession:
        if not profile.profession.occupation:
            prof_missing.append('Occupation / Job Title')
        if not profile.profession.annual_income:
            prof_missing.append('Income Range')
        prof_score = 15 if len(prof_missing) == 0 else (10 if profile.profession.occupation else 0)
    else:
        prof_missing = ['Occupation / Job Title', 'Income Range']
        prof_score = 0
    total_score += prof_score
    sections.append(SectionReport(
        name='Profession & Career',
        key='profession',
        weight=15,
        score=prof_score,
        completed=len(prof_missing) == 0,
        missing_fields=prof_missing,
    ))

    # 5. Family (Weight: 10)
    fam_missing = []
    if hasattr(profile, 'family') and profile.family:
        if not profile.family.family_location:
            fam_missing.append('Family Location')
        fam_score = 10 if len(fam_missing) == 0 else 5
    else:
        fam_missing = ['Family Structure & Location']
        fam_score = 0
    total_score += fam_score
    sections.append(SectionReport(
        name='Family Details',
        key='family',
        weight=10,
        score=fam_score,
        completed=len(fam_missing) == 0,
        missing_fields=fam_missing,
    ))

    # 6. Lifestyle (Weight: 5)
    life_missing = []
    if hasattr(profile, 'lifestyle') and profile.lifestyle:
        if not profile.lifestyle.diet:
            life_missing.append('Dietary Preferences')
        life_score = 5
    else:
        life_missing = ['Diet & Habits']
        life_score = 0
    total_score += life_score
    sections.append(SectionReport(
        name='Lifestyle & Habits',
        key='lifestyle',
        weight=5,
        score=life_score,
        completed=len(life_missing) == 0,
        missing_fields=life_missing,
    ))

    # 7. Partner Preferences (Weight: 10)
    pref_missing = []
    if hasattr(profile, 'partner_preference') and profile.partner_preference:
        pref_score = 10
    else:
        pref_missing = ['Partner Preferences']
        pref_score = 0
    total_score += pref_score
    sections.append(SectionReport(
        name='Partner Preferences',
        key='partner_preference',
        weight=10,
        score=pref_score,
        completed=len(pref_missing) == 0,
        missing_fields=pref_missing,
    ))

    # Compile missing recommended checklist
    missing_recommended = []
    for s in sections:
        if not s.completed:
            missing_recommended.extend(s.missing_fields)

    percentage = max(0, min(100, total_score))
    # Ready for discovery if basic info + at least education/profession is present
    is_ready = percentage >= 40 and bool(profile.display_name and profile.gender and profile.date_of_birth)

    return {
        'percentage': percentage,
        'is_ready_for_discovery': is_ready,
        'sections': sections,
        'missing_recommended': missing_recommended,
    }

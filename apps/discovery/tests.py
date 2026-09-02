import io
from datetime import date
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from apps.profiles.models import (
    EducationDetail,
    LifestyleDetail,
    PartnerPreference,
    ProfessionDetail,
    Profile,
    ProfilePhoto,
)
from .matching import SimplePreferenceScorer, score_profile_candidates

User = get_user_model()


def make_test_photo(profile, is_primary=True):
    file_obj = io.BytesIO()
    img = Image.new('RGB', (300, 300), (200, 100, 50))
    img.save(file_obj, 'JPEG')
    file_obj.seek(0)
    uploaded = SimpleUploadedFile("photo.jpg", file_obj.read(), content_type="image/jpeg")
    return ProfilePhoto.objects.create(
        profile=profile,
        image=uploaded,
        is_primary=is_primary,
        is_approved=True,
    )


class MatchingEngineTests(TestCase):
    """Tests for the pluggable matrimonial compatibility scoring algorithm."""

    def setUp(self):
        self.user_seeker = User.objects.create_user(email='seeker@example.com', password='password123')
        self.seeker_profile = Profile.objects.create(
            user=self.user_seeker,
            display_name='Amitabh Roy',
            gender='male',
            date_of_birth=date(1994, 1, 1),
            religion='Hindu',
            mother_tongue='Bengali',
            country='India',
            city='Kolkata',
        )

        # Partner Preferences for seeker:
        # Age: 25 to 30 (birth between 1996 and 2001)
        # Height: 155 to 175 cm
        # Religion: Hindu
        # Mother tongue: Bengali
        # Education: Masters
        # Country: India
        # Diet: Vegetarian
        self.preferences = PartnerPreference.objects.create(
            profile=self.seeker_profile,
            min_age=25,
            max_age=30,
            min_height_cm=155,
            max_height_cm=175,
            preferred_religion='Hindu',
            preferred_mother_tongue='Bengali',
            preferred_education='masters',
            preferred_country='India',
            preferred_diet='vegetarian',
        )

        # Candidate 1: Perfect match (100%)
        self.user_cand1 = User.objects.create_user(email='cand1@example.com', password='password123')
        self.cand1 = Profile.objects.create(
            user=self.user_cand1,
            display_name='Tanushree Das',
            gender='female',
            date_of_birth=date(1998, 6, 15),  # 28 yrs (in range)
            height_cm=165,                    # in range
            religion='Hindu',                 # match
            mother_tongue='Bengali',          # match
            country='India',                  # match
            city='Kolkata',
        )
        EducationDetail.objects.create(profile=self.cand1, highest_education='masters')
        LifestyleDetail.objects.create(profile=self.cand1, diet='vegetarian')

        # Candidate 2: Partial match
        self.user_cand2 = User.objects.create_user(email='cand2@example.com', password='password123')
        self.cand2 = Profile.objects.create(
            user=self.user_cand2,
            display_name='Sarah Jenkins',
            gender='female',
            date_of_birth=date(1985, 3, 10),  # 41 yrs (out of range)
            height_cm=180,                    # out of range
            religion='Christian',             # mismatch
            mother_tongue='English',          # mismatch
            country='USA',                    # mismatch
            city='Boston',
        )
        EducationDetail.objects.create(profile=self.cand2, highest_education='bachelors')
        LifestyleDetail.objects.create(profile=self.cand2, diet='non_vegetarian')

    def test_full_compatibility_score(self):
        scorer = SimplePreferenceScorer()
        breakdown = scorer.calculate_compatibility(self.seeker_profile, self.cand1)
        self.assertEqual(breakdown.score, 100)
        self.assertGreaterEqual(len(breakdown.matched_traits), 5)
        self.assertEqual(breakdown.badge_color, 'gold')

    def test_partial_compatibility_score(self):
        scorer = SimplePreferenceScorer()
        breakdown = scorer.calculate_compatibility(self.seeker_profile, self.cand2)
        self.assertLess(breakdown.score, 50)
        self.assertGreater(len(breakdown.unmatched_traits), 3)

    def test_score_profile_candidates_sorts_descending(self):
        candidates = [self.cand2, self.cand1]
        sorted_candidates = score_profile_candidates(self.seeker_profile, candidates)
        self.assertEqual(sorted_candidates[0].id, self.cand1.id)
        self.assertEqual(sorted_candidates[1].id, self.cand2.id)
        self.assertGreater(sorted_candidates[0].match_breakdown.score, sorted_candidates[1].match_breakdown.score)


class DiscoveryFilterAndViewsTests(TestCase):
    """Tests for search filters and discovery views."""

    def setUp(self):
        self.client = Client()

        # Searcher user
        self.user_male = User.objects.create_user(email='male@example.com', password='password123')
        self.male_profile = Profile.objects.create(
            user=self.user_male,
            display_name='Rohan Mehra',
            gender='male',
            date_of_birth=date(1995, 4, 12),
            religion='Hindu',
            country='India',
            city='Delhi',
            visibility='registered_only',
        )

        # Candidate Female 1 (Delhi, Doctor, Photo)
        self.u1 = User.objects.create_user(email='f1@example.com', password='password123')
        self.p1 = Profile.objects.create(
            user=self.u1,
            display_name='Dr. Neha Kapoor',
            gender='female',
            date_of_birth=date(1996, 7, 20),
            religion='Hindu',
            country='India',
            city='Delhi',
            is_verified=True,
            visibility='registered_only',
            about_me='Cardiologist who enjoys yoga and classical music.',
        )
        ProfessionDetail.objects.create(profile=self.p1, occupation='Cardiologist')
        make_test_photo(self.p1)

        # Candidate Female 2 (Mumbai, Engineer, No Photo)
        self.u2 = User.objects.create_user(email='f2@example.com', password='password123')
        self.p2 = Profile.objects.create(
            user=self.u2,
            display_name='Pooja Singhania',
            gender='female',
            date_of_birth=date(1998, 10, 5),
            religion='Jain',
            country='India',
            city='Mumbai',
            is_verified=False,
            visibility='registered_only',
            about_me='Software engineer building mobile apps.',
        )
        ProfessionDetail.objects.create(profile=self.p2, occupation='Software Engineer')

        # Deactivated User Profile (should never appear)
        self.u_deact = User.objects.create_user(email='deact@example.com', password='password123', is_active=False)
        self.p_deact = Profile.objects.create(
            user=self.u_deact,
            display_name='Inactive User',
            gender='female',
            date_of_birth=date(1997, 1, 1),
            city='Delhi',
        )

    def test_matches_view_shows_opposite_gender_and_excludes_self(self):
        self.client.login(username='male@example.com', password='password123')
        response = self.client.get(reverse('discovery:matches'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discovery/matches.html')

        profiles_in_page = response.context['page_obj'].object_list
        profile_ids = [p.id for p in profiles_in_page]

        # Should contain female candidates
        self.assertIn(self.p1.id, profile_ids)
        self.assertIn(self.p2.id, profile_ids)
        # Should exclude searcher's own profile
        self.assertNotIn(self.male_profile.id, profile_ids)
        # Should exclude inactive users
        self.assertNotIn(self.p_deact.id, profile_ids)

    def test_search_view_keyword_filter(self):
        self.client.login(username='male@example.com', password='password123')
        # Search by occupation 'Cardiologist'
        response = self.client.get(reverse('discovery:search'), {'q': 'Cardiologist'})
        self.assertEqual(response.status_code, 200)
        profile_ids = [p.id for p in response.context['page_obj'].object_list]
        self.assertIn(self.p1.id, profile_ids)
        self.assertNotIn(self.p2.id, profile_ids)

    def test_search_view_location_and_photo_filter(self):
        self.client.login(username='male@example.com', password='password123')
        # Filter by city 'Mumbai'
        response = self.client.get(reverse('discovery:search'), {'city': 'Mumbai'})
        profile_ids = [p.id for p in response.context['page_obj'].object_list]
        self.assertIn(self.p2.id, profile_ids)
        self.assertNotIn(self.p1.id, profile_ids)

        # Filter by photo only
        response_photo = self.client.get(reverse('discovery:search'), {'has_photo': 'true'})
        photo_profile_ids = [p.id for p in response_photo.context['page_obj'].object_list]
        self.assertIn(self.p1.id, photo_profile_ids)
        self.assertNotIn(self.p2.id, photo_profile_ids)

    def test_search_view_verified_only_filter(self):
        self.client.login(username='male@example.com', password='password123')
        response = self.client.get(reverse('discovery:search'), {'is_verified': 'true'})
        verified_ids = [p.id for p in response.context['page_obj'].object_list]
        self.assertIn(self.p1.id, verified_ids)
        self.assertNotIn(self.p2.id, verified_ids)

import io
from datetime import date
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from .models import (
    EducationDetail,
    FamilyDetail,
    LifestyleDetail,
    PartnerPreference,
    ProfessionDetail,
    Profile,
    ProfilePhoto,
)
from .services import calculate_profile_completion
from .validators import validate_profile_photo

User = get_user_model()


def generate_test_image(format='JPEG', size=(300, 300), color=(200, 50, 100)):
    """Helper to generate a valid PIL image file in memory."""
    file_obj = io.BytesIO()
    image = Image.new('RGB', size=size, color=color)
    image.save(file_obj, format=format)
    file_obj.seek(0)
    ext = 'jpg' if format == 'JPEG' else format.lower()
    return SimpleUploadedFile(f"test_image.{ext}", file_obj.read(), content_type=f"image/{ext}")


class ProfileModelTests(TestCase):
    """Tests for Profile and detail models."""

    def setUp(self):
        self.user = User.objects.create_user(email='profileuser@example.com', password='password123')
        self.profile = Profile.objects.create(
            user=self.user,
            display_name='Priya Sharma',
            gender='female',
            date_of_birth=date(1996, 5, 15),
            height_cm=165,
            marital_status='never_married',
            religion='Hindu',
            mother_tongue='Hindi',
            country='India',
            city='Mumbai',
            about_me='Software engineer passionate about literature and music.',
        )

    def test_profile_age_calculation(self):
        expected_age = date.today().year - 1996 - (
            (date.today().month, date.today().day) < (5, 15)
        )
        self.assertEqual(self.profile.age, expected_age)

    def test_height_formatted(self):
        # 165 cm -> 5'5" (165 cm)
        self.assertEqual(self.profile.height_formatted, '5\'5" (165 cm)')

    def test_detail_models_creation(self):
        edu = EducationDetail.objects.create(
            profile=self.profile,
            highest_education='masters',
            institution='IIT Bombay',
            field_of_study='Computer Science',
        )
        prof = ProfessionDetail.objects.create(
            profile=self.profile,
            occupation='Lead Architect',
            employer='Tech Corp',
            annual_income='$120,000',
        )
        family = FamilyDetail.objects.create(
            profile=self.profile,
            family_type='nuclear',
            family_values='moderate',
            family_location='Mumbai',
        )
        lifestyle = LifestyleDetail.objects.create(
            profile=self.profile,
            diet='vegetarian',
            smoking='never',
            drinking='never',
        )
        pref = PartnerPreference.objects.create(
            profile=self.profile,
            min_age=27,
            max_age=34,
            preferred_religion='Hindu',
        )

        self.assertEqual(self.profile.education, edu)
        self.assertEqual(self.profile.profession, prof)
        self.assertEqual(self.profile.family, family)
        self.assertEqual(self.profile.lifestyle, lifestyle)
        self.assertEqual(self.profile.partner_preference, pref)


class ProfilePhotoTests(TestCase):
    """Tests for Profile Photo uploading, validation, and primary photo management."""

    def setUp(self):
        self.user = User.objects.create_user(email='photouser@example.com', password='password123')
        self.profile = Profile.objects.create(
            user=self.user,
            display_name='Rahul Kumar',
            gender='male',
            date_of_birth=date(1994, 8, 20),
            city='Delhi',
        )

    def test_validate_valid_photo(self):
        img = generate_test_image('JPEG')
        # Should not raise exception
        validate_profile_photo(img)

    def test_validate_invalid_extension(self):
        bad_file = SimpleUploadedFile("script.exe", b"malicious content", content_type="application/octet-stream")
        with self.assertRaises(ValidationError):
            validate_profile_photo(bad_file)

    def test_validate_too_small_resolution(self):
        tiny_img = generate_test_image('JPEG', size=(50, 50))
        with self.assertRaises(ValidationError):
            validate_profile_photo(tiny_img)

    def test_photo_primary_switch(self):
        img1 = generate_test_image('JPEG')
        img2 = generate_test_image('PNG')

        photo1 = ProfilePhoto.objects.create(profile=self.profile, image=img1, is_primary=True)
        self.assertTrue(photo1.is_primary)
        self.assertEqual(self.profile.primary_photo, photo1)

        # Creating or updating photo2 to primary should automatically unset photo1
        photo2 = ProfilePhoto.objects.create(profile=self.profile, image=img2, is_primary=True)
        photo1.refresh_from_db()
        self.assertFalse(photo1.is_primary)
        self.assertTrue(photo2.is_primary)
        self.assertEqual(self.profile.primary_photo, photo2)


class ProfileCompletionServiceTests(TestCase):
    """Tests for profile completion percentage calculation."""

    def setUp(self):
        self.user = User.objects.create_user(email='completion@example.com', password='password123')
        self.profile = Profile.objects.create(
            user=self.user,
            display_name='Ananya Sen',
            gender='female',
            date_of_birth=date(1997, 2, 10),
            city='Kolkata',
            about_me='A creative professional who loves art, travel, and spending time with family.',
        )

    def test_partial_profile_completion(self):
        EducationDetail.objects.create(
            profile=self.profile,
            highest_education='bachelors',
            institution='Calcutta University',
        )
        report = calculate_profile_completion(self.profile)
        self.assertEqual(report['percentage'], 40)
        self.assertTrue(report['is_ready_for_discovery'])

    def test_full_profile_completion(self):
        img1 = generate_test_image('JPEG')
        img2 = generate_test_image('PNG')
        ProfilePhoto.objects.create(profile=self.profile, image=img1, is_primary=True)
        ProfilePhoto.objects.create(profile=self.profile, image=img2)

        EducationDetail.objects.create(
            profile=self.profile,
            highest_education='masters',
            institution='Jadavpur University',
        )
        ProfessionDetail.objects.create(
            profile=self.profile,
            occupation='UX Designer',
            annual_income='$90,000',
        )
        FamilyDetail.objects.create(
            profile=self.profile,
            family_type='nuclear',
            family_location='Kolkata',
        )
        LifestyleDetail.objects.create(
            profile=self.profile,
            diet='non_vegetarian',
        )
        PartnerPreference.objects.create(
            profile=self.profile,
            min_age=26,
            max_age=32,
        )

        report = calculate_profile_completion(self.profile)
        self.assertEqual(report['percentage'], 100)
        self.assertEqual(len(report['missing_recommended']), 0)


class ProfileViewsTests(TestCase):
    """Tests for profile views, multi-tab editing, IDOR and privacy checks."""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(email='user2@example.com', password='password123')

        self.profile1 = Profile.objects.create(
            user=self.user1,
            display_name='Arjun Verma',
            gender='male',
            date_of_birth=date(1993, 11, 4),
            city='Bangalore',
            visibility='registered_only',
        )

    def test_profile_setup_redirect_if_exists(self):
        self.client.login(username='user1@example.com', password='password123')
        response = self.client.get(reverse('profiles:profile_setup'))
        self.assertRedirects(response, reverse('profiles:profile_edit', kwargs={'section': 'basic'}))

    def test_profile_setup_for_new_user(self):
        self.client.login(username='user2@example.com', password='password123')
        response = self.client.get(reverse('profiles:profile_setup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/setup.html')

        post_data = {
            'display_name': 'Meera Patel',
            'gender': 'female',
            'date_of_birth': '1995-06-20',
            'height_cm': 162,
            'marital_status': 'never_married',
            'profile_created_for': 'self',
            'religion': 'Hindu',
            'mother_tongue': 'Gujarati',
            'country': 'India',
            'city': 'Ahmedabad',
            'visibility': 'registered_only',
        }
        response = self.client.post(reverse('profiles:profile_setup'), post_data, follow=True)
        self.assertRedirects(response, reverse('profiles:profile_edit', kwargs={'section': 'education'}))
        self.assertTrue(Profile.objects.filter(user=self.user2).exists())

    def test_profile_edit_tabs(self):
        self.client.login(username='user1@example.com', password='password123')
        sections = ['basic', 'photos', 'education', 'profession', 'family', 'lifestyle', 'preferences']
        for sec in sections:
            response = self.client.get(reverse('profiles:profile_edit', kwargs={'section': sec}))
            self.assertEqual(response.status_code, 200)

    def test_photo_upload_and_delete(self):
        self.client.login(username='user1@example.com', password='password123')
        img = generate_test_image('JPEG')
        response = self.client.post(reverse('profiles:photo_upload'), {
            'image': img,
            'caption': 'My portrait',
            'visibility': 'public',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        photo = self.profile1.photos.first()
        self.assertIsNotNone(photo)
        self.assertTrue(photo.is_primary)

        # Delete photo
        delete_url = reverse('profiles:photo_delete', kwargs={'photo_id': photo.id})
        del_response = self.client.post(delete_url, follow=True)
        self.assertEqual(del_response.status_code, 200)
        self.assertEqual(self.profile1.photos.count(), 0)

    def test_cannot_delete_other_user_photo(self):
        # User 1 has a photo
        img = generate_test_image('JPEG')
        photo = ProfilePhoto.objects.create(profile=self.profile1, image=img, is_primary=True)

        # User 2 logs in and tries to delete User 1's photo
        self.client.login(username='user2@example.com', password='password123')
        delete_url = reverse('profiles:photo_delete', kwargs={'photo_id': photo.id})
        response = self.client.post(delete_url)
        # Should be forbidden or 404
        self.assertIn(response.status_code, [403, 404])
        self.assertTrue(ProfilePhoto.objects.filter(id=photo.id).exists())

    def test_profile_detail_registered_only_anonymous_redirects(self):
        detail_url = reverse('profiles:profile_detail', kwargs={'profile_id': self.profile1.id})
        response = self.client.get(detail_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={detail_url}")

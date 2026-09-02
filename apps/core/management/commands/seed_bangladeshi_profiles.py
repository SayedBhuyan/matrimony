from datetime import date
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw

from apps.connections.models import Block, Favorite, Interest, Report
from apps.messaging.models import Conversation, Message, Notification
from apps.profiles.models import (
    EducationDetail,
    FamilyDetail,
    LifestyleDetail,
    PartnerPreference,
    ProfessionDetail,
    Profile,
    ProfilePhoto,
)


class Command(BaseCommand):
    help = 'Reset demo data and create 25 complete Bangladeshi profiles.'

    names = [
        'Arafat Rahman', 'Nusrat Jahan', 'Tanvir Hasan', 'Maliha Chowdhury',
        'Sajid Ahmed', 'Fariha Islam', 'Mahin Kabir', 'Sumaiya Akter',
        'Rafiul Karim', 'Tasmia Haque', 'Adnan Hossain', 'Jannatul Ferdous',
        'Shakil Mahmud', 'Mim Sultana', 'Faisal Khan', 'Sadia Rahman',
        'Imran Chowdhury', 'Rumana Yasmin', 'Nayeem Islam', 'Ishrat Jahan',
        'Siam Ahmed', 'Nabila Sultana', 'Shuvo Das', 'Priya Saha', 'Arif Uddin',
    ]
    cities = ['Dhaka', 'Chattogram', 'Sylhet', 'Rajshahi', 'Khulna', 'Rangpur', 'Mymensingh']
    occupations = ['Software Engineer', 'Doctor', 'Architect', 'Lecturer', 'Banker', 'Entrepreneur', 'Civil Engineer']
    religions = ['Islam', 'Islam', 'Islam', 'Islam', 'Hinduism']

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing non-admin platform data first.')
        parser.add_argument('--password', default='Bangladesh123!', help='Password assigned to seeded accounts.')

    def handle(self, *args, **options):
        if not options['reset']:
            self.stdout.write(self.style.WARNING('Nothing changed. Re-run with --reset to replace demo data.'))
            return

        User = get_user_model()
        with transaction.atomic():
            User.objects.filter(is_superuser=False).delete()
            for index, name in enumerate(self.names, start=1):
                self.create_profile(User, index, name, options['password'])

        self.stdout.write(self.style.SUCCESS('Created 25 complete Bangladeshi demo profiles.'))
        self.stdout.write(f'Demo password: {options["password"]}')

    def create_profile(self, User, index, name, password):
        email_name = name.lower().replace(' ', '.')
        user = User.objects.create_user(email=f'{email_name}{index}@example.com', password=password)
        profile = Profile.objects.create(
            user=user,
            display_name=name,
            gender='male' if index % 2 else 'female',
            date_of_birth=date(1988 + index % 10, (index % 12) + 1, (index % 26) + 1),
            height_cm=157 + (index * 3 % 28),
            marital_status='never_married',
            profile_created_for='self',
            religion=self.religions[index % len(self.religions)],
            caste='Not specified',
            sub_caste='Not specified',
            mother_tongue='Bangla',
            country='Bangladesh',
            state='Dhaka Division',
            city=self.cities[index % len(self.cities)],
            citizenship='Bangladeshi',
            about_me=f'I am {name}, a thoughtful and family-oriented Bangladeshi professional. I value honesty, kindness, personal growth, and building a warm partnership grounded in mutual respect.',
            visibility='public',
            is_verified=True,
        )
        EducationDetail.objects.create(profile=profile, highest_education='bachelors', ug_degree='Bachelor of Science', institution='University of Dhaka', field_of_study='Computer Science and Engineering')
        ProfessionDetail.objects.create(profile=profile, occupation=self.occupations[index % len(self.occupations)], industry='Professional Services', employer='A respected Bangladesh-based organization', annual_income='BDT 10-20 Lakhs', working_city=profile.city, working_country='Bangladesh', income_visible=True)
        FamilyDetail.objects.create(profile=profile, family_type='nuclear', family_values='moderate', family_status='upper_middle_class', father_occupation='Retired government service', mother_occupation='Homemaker', brothers_count=1, sisters_count=1, living_with_parents=False, family_location=profile.city, about_family='A close, educated, and supportive family that values tradition, learning, and kindness.')
        LifestyleDetail.objects.create(profile=profile, diet='halal' if profile.religion == 'Islam' else 'vegetarian', smoking='never', drinking='never', hobbies='Reading, travel, photography, cooking', spoken_languages='Bangla, English')
        PartnerPreference.objects.create(profile=profile, min_age=23, max_age=38, min_height_cm=150, max_height_cm=190, preferred_marital_status='Never Married', preferred_religion='', preferred_mother_tongue='Bangla', preferred_education='Bachelor degree or above', preferred_occupation='', preferred_country='Bangladesh', preferred_diet='', notes='Looking for a kind, emotionally mature, family-oriented partner who values communication and mutual support.')
        self.create_avatar(profile, index)

    def create_avatar(self, profile, index):
        image = Image.new('RGB', (800, 800), ((220 + index * 3) % 255, (230 + index * 5) % 255, (240 + index * 7) % 255))
        draw = ImageDraw.Draw(image)
        draw.ellipse((250, 150, 550, 450), fill=(80, 110, 150))
        draw.ellipse((150, 380, 650, 760), fill=(60, 85, 130))
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=88)
        profile_photo = ProfilePhoto(profile=profile, is_primary=True, is_approved=True, caption=f'{profile.display_name} profile photo')
        profile_photo.image.save(f'{profile.user_id}.jpg', ContentFile(buffer.getvalue()), save=True)

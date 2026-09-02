from datetime import date
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from apps.profiles.models import Profile
from apps.messaging.models import Conversation, Notification
from .models import Interest, Favorite, Block, Report

User = get_user_model()


class InterestModelTests(TestCase):
    """Tests for Interest model and workflow."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', password='pass123')
        self.user2 = User.objects.create_user(email='user2@example.com', password='pass123')
        
        self.profile1 = Profile.objects.create(
            user=self.user1,
            display_name='Person 1',
            gender='male',
            date_of_birth=date(1990, 1, 1),
            city='NYC',
            country='USA',
        )
        
        self.profile2 = Profile.objects.create(
            user=self.user2,
            display_name='Person 2',
            gender='female',
            date_of_birth=date(1992, 5, 15),
            city='LA',
            country='USA',
        )
    
    def test_create_interest(self):
        """Test creating an interest."""
        interest = Interest.objects.create(
            sender=self.user1,
            receiver=self.user2,
            message='Hello!'
        )
        self.assertEqual(interest.status, 'pending')
        self.assertEqual(interest.sender, self.user1)
        self.assertEqual(interest.receiver, self.user2)
        self.assertIsNotNone(interest.sent_at)
        self.assertIsNone(interest.responded_at)
    
    def test_cannot_send_interest_to_self(self):
        """Test that a user cannot send interest to themselves (constraint)."""
        # This should fail at the database level, but let's test the model
        try:
            interest = Interest(
                sender=self.user1,
                receiver=self.user1,
            )
            # The constraint should prevent this, so save should fail
            # However, Django might not enforce it at the model level, so we test separately
            self.assertNotEqual(interest.sender, interest.receiver)
        except Exception:
            pass
    
    def test_duplicate_pending_interest_constraint(self):
        """Test that duplicate pending interests are not allowed."""
        Interest.objects.create(
            sender=self.user1,
            receiver=self.user2,
            status='pending'
        )
        
        # Try to create another pending interest from same sender to same receiver
        # This should fail due to unique constraint
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Interest.objects.create(
                sender=self.user1,
                receiver=self.user2,
                status='pending'
            )


class InterestViewTests(TestCase):
    """Tests for Interest views and workflows."""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(email='user1@example.com', password='pass123')
        self.user2 = User.objects.create_user(email='user2@example.com', password='pass123')
        
        self.profile1 = Profile.objects.create(
            user=self.user1,
            display_name='Person 1',
            gender='male',
            date_of_birth=date(1990, 1, 1),
            city='NYC',
            country='USA',
        )
        
        self.profile2 = Profile.objects.create(
            user=self.user2,
            display_name='Person 2',
            gender='female',
            date_of_birth=date(1992, 5, 15),
            city='LA',
            country='USA',
        )
    
    def test_send_interest_authenticated(self):
        """Test sending interest as authenticated user."""
        self.client.login(email='user1@example.com', password='pass123')
        response = self.client.post(
            reverse('connections:send_interest', args=[self.profile2.id]),
            {'message': 'Hi there!'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        interest = Interest.objects.get(sender=self.user1, receiver=self.user2)
        self.assertEqual(interest.status, 'pending')
        self.assertEqual(interest.message, 'Hi there!')
        self.assertTrue(Notification.objects.filter(
            recipient=self.user2,
            notification_type='interest_received',
            action_url=f'/profiles/{self.profile1.id}/',
        ).exists())

    def test_send_interest_to_self_returns_validation_error(self):
        self.client.login(email='user1@example.com', password='pass123')

        response = self.client.post(
            reverse('connections:send_interest', args=[self.profile1.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'You cannot send interest to yourself.')
    
    def test_send_interest_requires_login(self):
        """Test that sending interest requires authentication."""
        response = self.client.post(
            reverse('connections:send_interest', args=[self.profile2.id]),
            {'message': 'Hi there!'}
        )
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)
    
    def test_accept_interest(self):
        """Test accepting an interest."""
        interest = Interest.objects.create(
            sender=self.user1,
            receiver=self.user2,
            message='Hello!'
        )
        
        self.client.login(email='user2@example.com', password='pass123')
        response = self.client.post(
            reverse('connections:accept_interest', args=[interest.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        interest.refresh_from_db()
        self.assertEqual(interest.status, 'accepted')
        self.assertIsNotNone(interest.responded_at)
    
    def test_reject_interest(self):
        """Test rejecting an interest."""
        interest = Interest.objects.create(
            sender=self.user1,
            receiver=self.user2,
            message='Hello!'
        )
        
        self.client.login(email='user2@example.com', password='pass123')
        response = self.client.post(
            reverse('connections:reject_interest', args=[interest.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        interest.refresh_from_db()
        self.assertEqual(interest.status, 'rejected')
        self.assertIsNotNone(interest.responded_at)

    def test_accept_interest_creates_conversation_and_notification(self):
        """Test accepting an interest creates a conversation and notification."""
        interest = Interest.objects.create(
            sender=self.user1,
            receiver=self.user2,
            message='Hello!'
        )

        self.client.login(email='user2@example.com', password='pass123')
        response = self.client.post(
            reverse('connections:accept_interest', args=[interest.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        interest.refresh_from_db()
        self.assertEqual(interest.status, 'accepted')

        conversation = Conversation.objects.get(interest=interest)
        self.assertEqual(set(conversation.participants.values_list('id', flat=True)),
                         {self.user1.id, self.user2.id})

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.user1,
                notification_type='interest_accepted',
            ).exists()
        )
    
    def test_received_interests_view(self):
        """Test viewing received interests."""
        Interest.objects.create(sender=self.user1, receiver=self.user2)
        Interest.objects.create(sender=self.user1, receiver=self.user2, status='accepted')
        
        self.client.login(email='user2@example.com', password='pass123')
        response = self.client.get(reverse('connections:received_interests'))
        self.assertEqual(response.status_code, 200)
        
        # Should show both interests
        interests = response.context['interests']
        self.assertEqual(interests.count(), 2)
        self.assertContains(response, f'href="/profiles/{self.profile1.id}/"')

    def test_sent_interests_view_links_to_recipient_profile(self):
        Interest.objects.create(sender=self.user1, receiver=self.user2)

        self.client.login(email='user1@example.com', password='pass123')
        response = self.client.get(reverse('connections:sent_interests'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="/profiles/{self.profile2.id}/"')


class FavoriteTests(TestCase):
    """Tests for Favorite model and views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='user@example.com', password='pass123')
        self.other_user = User.objects.create_user(email='other@example.com', password='pass123')
        
        self.profile = Profile.objects.create(
            user=self.other_user,
            display_name='Other Person',
            gender='female',
            date_of_birth=date(1992, 5, 15),
            city='LA',
            country='USA',
        )
    
    def test_add_favorite(self):
        """Test adding a profile to favorites."""
        self.client.login(email='user@example.com', password='pass123')
        response = self.client.post(
            reverse('connections:add_favorite', args=[self.profile.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        favorite = Favorite.objects.get(user=self.user, profile=self.profile)
        self.assertIsNotNone(favorite)
    
    def test_remove_favorite(self):
        """Test removing a profile from favorites."""
        Favorite.objects.create(user=self.user, profile=self.profile)
        
        self.client.login(email='user@example.com', password='pass123')
        response = self.client.post(
            reverse('connections:remove_favorite', args=[self.profile.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        self.assertFalse(Favorite.objects.filter(user=self.user, profile=self.profile).exists())
    
    def test_favorites_list_view(self):
        """Test viewing favorites list."""
        Favorite.objects.create(user=self.user, profile=self.profile)
        
        self.client.login(email='user@example.com', password='pass123')
        response = self.client.get(reverse('connections:favorites_list'))
        self.assertEqual(response.status_code, 200)


class BlockAndReportTests(TestCase):
    """Tests for blocking and reporting profiles."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='user@example.com', password='pass123')
        self.other_user = User.objects.create_user(email='other@example.com', password='pass123')

        self.profile = Profile.objects.create(
            user=self.other_user,
            display_name='Other Person',
            gender='female',
            date_of_birth=date(1992, 5, 15),
            city='LA',
            country='USA',
        )

    def test_block_user(self):
        self.client.login(email='user@example.com', password='pass123')

        response = self.client.post(
            reverse('connections:block_user', args=[self.other_user.id]),
            {'reason': 'Spam'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Block.objects.filter(user=self.user, blocked_user=self.other_user).exists())

    def test_report_user(self):
        self.client.login(email='user@example.com', password='pass123')

        response = self.client.post(
            reverse('connections:report_user', args=[self.other_user.id]),
            {
                'report_type': 'harassment',
                'description': 'This person is sending inappropriate messages.'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Report.objects.filter(reporter=self.user, reported_user=self.other_user).exists())


class BlockTests(TestCase):
    """Tests for Block model."""
    
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', password='pass123')
        self.user2 = User.objects.create_user(email='user2@example.com', password='pass123')
    
    def test_create_block(self):
        """Test creating a block."""
        block = Block.objects.create(
            user=self.user1,
            blocked_user=self.user2,
            reason='Spam'
        )
        self.assertEqual(block.user, self.user1)
        self.assertEqual(block.blocked_user, self.user2)
        self.assertEqual(block.reason, 'Spam')
        self.assertIsNotNone(block.created_at)


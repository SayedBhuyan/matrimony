from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UserModelTests(TestCase):
    """Tests for Custom User model and UserManager."""

    def test_create_user_successful(self):
        email = 'test@example.com'
        password = 'password123'
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_email_verified)
        self.assertIsNotNone(user.id)

    def test_create_user_email_normalized(self):
        email = 'test@EXAMPLE.COM'
        user = User.objects.create_user(email=email, password='password123')
        self.assertEqual(user.email, 'test@example.com')

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='password123')

    def test_create_superuser_successful(self):
        email = 'admin@example.com'
        password = 'adminpassword123'
        superuser = User.objects.create_superuser(email=email, password=password)

        self.assertEqual(superuser.email, email)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_create_superuser_invalid_staff_flag(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin2@example.com',
                password='password123',
                is_staff=False
            )

    def test_create_superuser_invalid_superuser_flag(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin3@example.com',
                password='password123',
                is_superuser=False
            )

    def test_get_short_name(self):
        user = User.objects.create_user(email='john.doe@example.com', password='password123')
        self.assertEqual(user.get_short_name(), 'john.doe')


class AuthViewsTests(TestCase):
    """Tests for authentication views (register, login, logout, password reset)."""

    def setUp(self):
        self.client = Client()
        self.email = 'member@example.com'
        self.password = 'StrongP@ssw0rd!'
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_register_page_loads(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_user_successful(self):
        new_email = 'newuser@example.com'
        response = self.client.post(reverse('accounts:register'), {
            'email': new_email,
            'password1': 'NewStrongP@ss123',
            'password2': 'NewStrongP@ss123',
        }, follow=True)

        self.assertRedirects(response, reverse('core:dashboard'))
        self.assertTrue(User.objects.filter(email=new_email).exists())
        # Check user is logged in
        self.assertTrue(response.context['user'].is_authenticated)

    def test_register_duplicate_email_fails(self):
        response = self.client.post(reverse('accounts:register'), {
            'email': self.email,
            'password1': 'NewStrongP@ss123',
            'password2': 'NewStrongP@ss123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'An account with this email address already exists.')

    def test_register_password_mismatch_fails(self):
        response = self.client.post(reverse('accounts:register'), {
            'email': 'mismatch@example.com',
            'password1': 'Password123',
            'password2': 'Password456',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'password2', 'Passwords do not match.')

    def test_login_successful(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': self.email,
            'password': self.password,
        }, follow=True)
        self.assertRedirects(response, reverse('core:dashboard'))
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': self.email,
            'password': 'WrongPassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct email address and password.')

    def test_logout(self):
        self.client.login(username=self.email, password=self.password)
        response = self.client.post(reverse('accounts:logout'), follow=True)
        self.assertRedirects(response, reverse('core:landing'))
        self.assertFalse(response.context['user'].is_authenticated)

    def test_password_reset_flow(self):
        # 1. Request reset
        response = self.client.post(reverse('accounts:password_reset'), {
            'email': self.email,
        }, follow=True)
        self.assertRedirects(response, reverse('accounts:password_reset_done'))
        self.assertContains(response, 'Check Your Email')


class CoreViewsTests(TestCase):
    """Tests for Core landing and dashboard views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='user@example.com', password='password123')

    def test_landing_page_unauthenticated(self):
        response = self.client.get(reverse('core:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/landing.html')
        self.assertContains(response, 'Find Your')

    def test_landing_page_authenticated_redirects_or_shows_dashboard(self):
        self.client.login(username='user@example.com', password='password123')
        response = self.client.get(reverse('core:landing'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

    def test_dashboard_page(self):
        self.client.login(username='user@example.com', password='password123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

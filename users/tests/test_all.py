from django.test import TestCase, Client
from users.forms import UserRegisterForm
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core import mail
from django.middleware.csrf import CsrfViewMiddleware
from django.test.client import RequestFactory
from sds_app.models import RequestConfig
from sds_app.forms import RequestConfigForm
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta

class UserRegisterFormTest(TestCase):
    @patch('captcha.fields.ReCaptchaField.clean')
    def test_valid_form(self, mock_clean):
        mock_clean.return_value = None
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
            'school_acronym': 'ICEF',          # ADDED
            'captcha': 'PASSED'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    @patch('captcha.fields.ReCaptchaField.clean')
    def test_invalid_form(self, mock_clean):
        mock_clean.return_value = None
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Differentpassword123',
            'school_acronym': 'ICEF',          # ADDED (still invalid because passwords differ)
            'captcha': 'PASSED'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    @patch('captcha.fields.ReCaptchaField.clean')
    def test_register_form_missing_fields(self, mock_clean):
        mock_clean.return_value = None
        form_data = {
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
            'school_acronym': '',              # ADDED
            'captcha': 'PASSED'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)

    @patch('captcha.fields.ReCaptchaField.clean')
    def test_valid_form_with_captcha(self, mock_clean):
        mock_clean.return_value = None
        form_data = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
            'school_acronym': 'ICEF',          # ADDED
            'captcha': 'PASSED',               # Ensure we post the actual field name
            'g-recaptcha-response': 'PASSED'   # (harmless extra; mocked anyway)
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    @patch('captcha.fields.ReCaptchaField.clean')
    def test_invalid_form_missing_captcha(self, mock_clean):
        from django.core.exceptions import ValidationError
        mock_clean.side_effect = ValidationError('Please complete the CAPTCHA to register.')
        form_data = {
            'username': 'testuser3',
            'email': 'testuser3@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
            'school_acronym': 'ICEF'           # ADDED
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('captcha', form.errors)
        self.assertIn('Please complete the CAPTCHA to register.', form.errors['captcha'])


class UserRegisterViewTest(TestCase):
    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    @patch('captcha.fields.ReCaptchaField.clean')
    def test_register_view_post(self, mock_clean):
        mock_clean.return_value = None
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
            'school_acronym': 'ICEF',          # ADDED
            'captcha': 'PASSED'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_view_duplicate_username(self):
        User.objects.create_user(username='testuser', email='testuser@example.com', password='Testpassword123')
        form_data = {
            'username': 'testuser',
            'email': 'newuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
            'school_acronym': 'ICEF',          # ADDED
            'captcha': 'PASSED'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'Username already exists. Please choose a different username.')

    def test_register_view_csrf_protection(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123',
            'school_acronym': 'ICEF',          # ADDED
            'captcha': 'PASSED'
        }
        factory = RequestFactory()
        request = factory.post(reverse('register'), data=form_data)
        middleware = CsrfViewMiddleware(lambda req: None)
        response = middleware.process_view(request, None, None, None)
        self.assertEqual(response.status_code, 403)


class UserLoginViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='Testpassword123')

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_view_post(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'Testpassword123'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_inactive_user_login(self):
        user = get_user_model().objects.create_user(username='inactiveuser', password='Testpassword123', is_active=False)
        response = self.client.post(reverse('login'), {'username': 'inactiveuser', 'password': 'Testpassword123'})
        self.assertEqual(response.status_code, 200)  # Login page should reload
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class UserProfileUpdateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='Testpassword123')
        self.client.login(username='testuser', password='Testpassword123')

    def test_profile_view_get(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_view_post(self):
        form_data = {
            'username': 'updateduser',
            'email': 'updateduser@example.com'
        }
        response = self.client.post(reverse('profile'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful profile update
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updateduser@example.com')


class UserPasswordResetViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='Testpassword123')

    def test_password_reset_view_get(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')

    def test_password_reset_view_post(self):
        response = self.client.post(reverse('password_reset'), {'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful password reset request
        self.assertEqual(len(mail.outbox), 1)  # Ensure an email was sent
        self.assertIn('testuser@example.com', mail.outbox[0].to)

    def test_password_reset_view_invalid_email(self):
        response = self.client.post(reverse('password_reset'), {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 302)  # Redirect after form submission
        self.assertEqual(len(mail.outbox), 0)  # No email should be sent

    def test_password_reset_email_content(self):
        response = self.client.post(reverse('password_reset'), {'email': 'testuser@example.com'})
        self.assertEqual(len(mail.outbox), 1)  # Ensure an email was sent
        email = mail.outbox[0]
        self.assertIn('Password reset', email.subject)
        self.assertIn('testuser@example.com', email.to)
        self.assertIn('http://', email.body)  # Ensure the email contains a reset link


class UserLogoutViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='Testpassword123')
        self.client.login(username='testuser', password='Testpassword123')

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class AccessControlTest(TestCase):
    def test_profile_view_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn(reverse('login'), response.url)



class CreateRequestConfigTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.user.is_active = True
        self.user.save()
        self.superuser = User.objects.create_superuser(username='admin', password='admin123')
        self.superuser.is_active = True
        self.superuser.save()
        self.client = Client()
        self.url = reverse('submit-requests')

    def test_create_request_as_authenticated_user(self):
        self.client.login(username='testuser', password='password123')
        future = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        post_data = {
            'request_title': 'Test Request',
            'priority_status': 'low',          # lowercase key
            'schedule_time': future,
            'email_content': 'Test email content',
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(RequestConfig.objects.count(), 1)
        rc = RequestConfig.objects.first()
        self.assertEqual(rc.priority_status, 'low')

    def test_create_request_as_superuser(self):
        self.client.login(username='admin', password='admin123')
        future = (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
        post_data = {
            'request_title': 'Admin Request',
            'priority_status': 'urgent',       # lowercase key
            'schedule_time': future,
            'email_content': 'Superuser email content',
            'user_id': self.user.id,
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(RequestConfig.objects.count(), 1)
        rc = RequestConfig.objects.first()
        self.assertEqual(rc.priority_status, 'urgent')

    def test_create_request_as_unauthenticated_user(self):
        post_data = {
            'request_title': 'Should Fail',
            'priority_status': 'low',          # lowercase key
            'schedule_time': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'email_content': 'Unauthenticated user email content',
        }
        response = self.client.post(self.url, post_data)
        self.assertEqual(RequestConfig.objects.count(), 0)


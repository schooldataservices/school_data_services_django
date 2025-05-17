from django.test import TestCase, Client
from users.forms import UserRegisterForm
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core import mail
from django.middleware.csrf import CsrfViewMiddleware
from django.test.client import RequestFactory
from emailscraper_app.models import RequestConfig
from emailscraper_app.forms import RequestConfigForm

class UserRegisterFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123'
        }
        form = UserRegisterForm(data=form_data)
        if form.is_valid():
            print("Form is valid.")
        else:
            print("Form errors:", form.errors)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Differentpassword123'
        }
        form = UserRegisterForm(data=form_data)
        if form.is_valid():
            print("Form is valid.")
        else:
            print("Form errors:", form.errors)
        self.assertFalse(form.is_valid())

    def test_register_form_missing_fields(self):
        form_data = {
            'username': '',
            'email': '',
            'password1': '',
            'password2': ''
        }
        form = UserRegisterForm(data=form_data)
        if form.is_valid():
            print("Form is valid.")
        else:
            print("Form errors:", form.errors)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)


class UserRegisterViewTest(TestCase):
    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_view_post(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_view_duplicate_username(self):
        User.objects.create_user(username='testuser', email='testuser@example.com', password='Testpassword123')
        form_data = {
            'username': 'testuser',  # Duplicate username
            'email': 'newuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 200)  # Form should not redirect
        self.assertFormError(response, 'form', 'username', 'Username already exists. Please choose a different username.')

    def test_register_view_csrf_protection(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'Testpassword123',
            'password2': 'Testpassword123'
        }

        # Create a request without a CSRF token
        factory = RequestFactory()
        request = factory.post(reverse('register'), data=form_data)

        # Manually enforce CSRF validation
        middleware = CsrfViewMiddleware(lambda req: None)  # Pass a no-op get_response callable
        response = middleware.process_view(request, None, None, None)

        # Assert that the response is 403 Forbidden
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
         # Create a test user and activate them
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.user.is_active = True
        self.user.save()

        # Create a superuser and activate them
        self.superuser = User.objects.create_superuser(username='admin', password='admin123')
        self.superuser.is_active = True
        self.superuser.save()

        # Set up the client
        self.client = Client()

        # Define the URL for the view
        self.url = reverse('submit-requests')  # Replace with the actual name of the URL pattern

    def test_create_request_as_authenticated_user(self):
        # Log in as a regular user
        self.client.login(username='testuser', password='password123')

        # Define POST data
        post_data = {
            'priority_status': 'low',
            'schedule_time': '2025-04-25 10:00:00',
            'email_content': 'Test email content',
        }

        # Send POST request
        response = self.client.post(self.url, post_data)

        # Check if the response redirects (successful submission)
        self.assertEqual(response.status_code, 200)

        # Check if the request was created in the database
        self.assertEqual(RequestConfig.objects.count(), 1)
        request_config = RequestConfig.objects.first()
        self.assertEqual(request_config.creator, self.user)
        self.assertEqual(request_config.priority_status, 'low')
        self.assertEqual(request_config.email_content, 'Test email content')

    def test_create_request_as_superuser(self):
        # Log in as a superuser
        self.client.login(username='admin', password='admin123')

        # Define POST data
        post_data = {
            'priority_status': 'urgent',
            'schedule_time': '2025-04-26 14:00:00',
            'email_content': 'Superuser email content',
            'user_id': self.user.id,  # Submit on behalf of another user
        }

        # Send POST request
        response = self.client.post(self.url, post_data)

        # Check if the response redirects (successful submission)
        self.assertEqual(response.status_code, 200)

        # Check if the request was created in the database
        self.assertEqual(RequestConfig.objects.count(), 1)
        request_config = RequestConfig.objects.first()
        self.assertEqual(request_config.creator, self.user)  # Creator should be the selected user
        self.assertEqual(request_config.priority_status, 'urgent')
        self.assertEqual(request_config.email_content, 'Superuser email content')

    def test_create_request_with_invalid_data(self):
        # Log in as a regular user
        self.client.login(username='testuser', password='password123')

        # Define invalid POST data (missing required fields)
        post_data = {
            'priority_status': '',  # Invalid priority
            'schedule_time': '',  # Missing schedule time
            'email_content': '',  # Missing email content
        }

        # Send POST request
        response = self.client.post(self.url, post_data)

        # Check if the response returns a 200 status code (form re-rendered with errors)
        self.assertEqual(response.status_code, 200)

        # Check if the request was not created in the database
        self.assertEqual(RequestConfig.objects.count(), 0)

        # Check if the form errors are displayed in the response
        self.assertContains(response, "Please correct the errors below.")

    def test_create_request_as_unauthenticated_user(self):
        # Define POST data
        post_data = {
            'priority_status': 'low',
            'schedule_time': '2025-04-27 16:00:00',
            'email_content': 'Unauthenticated user email content',
        }

        # Send POST request without logging in
        response = self.client.post(self.url, post_data)

        # Check if the response redirects to the login page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You must be logged in to submit a request.")

        # Check if the request was not created in the database
        self.assertEqual(RequestConfig.objects.count(), 0)


#Do Final checks
#Create new template directory


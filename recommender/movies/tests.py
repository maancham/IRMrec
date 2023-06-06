from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .views import home, login_view


# Create your tests here.
# class HomeTest(TestCase):
#     """
#     TODO:
#     Must include the link to google form
#     Must include the link to the first unrated movie
#     No unlogged dudes should be able to view it.
#     """
#     def setUp(self):
#         User.objects.create_user(username="akbar", password="random_pass")
#         self.client.login(username="akbar", password="random_pass")
#         self.response = self.client.get(reverse('home'))

#     def test_home_view_status_code(self):
#         self.assertEquals(self.response.status_code, 200)

#     def test_home_url_resolves_home_view(self):
#         view = resolve('/home/')
#         self.assertEquals(view.func, home)

#     def test_home_template_contains_title(self):
#         self.assertContains(self.response, 'IRMrec')


# class LoginTest(TestCase):

#     def setUp(self):
#         url = reverse('login')
#         self.response = self.client.get(url)

#     def test_login_view_status_code(self):
#         self.assertEquals(self.response.status_code, 200)

#     def test_csrf(self):
#         self.assertContains(self.response, 'csrfmiddlewaretoken')

#     def test_login_url_resolves_login_view(self):
#         view = resolve('/')
#         self.assertEquals(view.func, login_view)


# class SuccessfulLoginTests(TestCase):
#     def setUp(self):
#         User.objects.create_user(username="akbar", password="random_pass")
#         url = reverse('login')
#         self.home_url = reverse('home')
#         self.get_response = self.client.get(url)
#         data = {
#             'username': 'akbar',
#             'password': 'random_pass'
#         }
#         self.response = self.client.post(url, data)

#     def test_redirection(self):
#         '''
#         A valid submission should redirect the user to the home page
#         '''
#         self.assertRedirects(self.response, self.home_url)

#     def test_user_authentication(self):
#         response = self.client.get(self.home_url)
#         user = response.context.get('user')
#         self.assertTrue(user.is_authenticated)

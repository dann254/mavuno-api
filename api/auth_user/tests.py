import json
from django.urls import include, path, reverse
from rest_framework import status, routers
from rest_framework.test import APITestCase, APIClient, URLPatternsTestCase
from .views import AddUserView, LoginView, UserListView

from .models import User


class UserTest(APITestCase, URLPatternsTestCase):
    """ Test module for User """

    router = routers.DefaultRouter()

    router.register(r'api/auth/create', AddUserView, basename='create')
    router.register(r'api/auth/login', LoginView, basename='login')
    router.register(r'api/auth/users', UserListView, basename='users')

    urlpatterns = [
        path('', include(router.urls)),
    ]

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='test1@example.com',
            password='password1',
        )

        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin1',
        )

    def test_login(self):
        """ Test if a user can login and get a JWT response token """
        url = reverse('login-list')
        data = {
            'email': 'admin@example.com',
            'password': 'admin1'
        }
        response = self.client.post(url, data)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['success'], True)
        self.assertTrue('access' in response_data)

    def test_user_registration(self):
        """ Test if a supervisor can create new user """

        url = reverse('login-list')
        data = {'email': 'admin@example.com', 'password': 'admin1'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('create-list')
        data = {
            'email': 'test2@example.com',
            'password': 'password2',
        }
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_all_users_as_admin(self):
        """ Test fetching all users as supervisor """
        # Setup the token
        url = reverse('login-list')
        data = {'email': 'admin@example.com', 'password': 'admin1'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        # Test the endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.get(reverse('users-list'))
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), len(response_data['users']))

    def test_only_admins_can_view_users(self):
        """ Test fetching all users fails as non supervisor """
        # Setup the token
        url = reverse('login-list')
        data = {'email': 'test1@example.com', 'password': 'password1'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        # Test the endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.get(reverse('users-list'))
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_view_single_user_as_admin(self):
        """ Test fetching one user As supervisor """
        # Setup the token
        url = reverse('login-list')
        data = {'email': 'admin@example.com', 'password': 'admin1'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        # get user id
        user_id = User.objects.all().first().uid

        # test endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.get(reverse('users-detail', kwargs={'uid': user_id}))
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('test1@example.com',  response_data['email'])

    def test_view_single_user_denied(self):
        """ Test fetching one users fails as non supervisor """
        # Setup the token
        url = reverse('login-list')
        data = {'email': 'test1@example.com', 'password': 'password1'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        # get user id
        user_id = User.objects.all().first().uid

        # test endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.get(reverse('users-detail', kwargs={'uid': user_id}))
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_update_single_users_role_as_admin(self):
        """ Test update one user's role As supervisor """
        # Setup the token
        url = reverse('login-list')
        data = {'email': 'admin@example.com', 'password': 'admin1'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        # get user id
        user_id = User.objects.all().first().uid

        data = {
            'role': 2
        }

        # test endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.put(reverse('users-detail', kwargs={'uid': user_id}), data)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2,  response_data['updatedUser']['role'])

    def test_update_single_users_role_denied(self):
        """ Test updating one user's role fails as non supervisor """
        # Setup the token
        url = reverse('login-list')
        data = {'email': 'test1@example.com', 'password': 'password1'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        # get user id
        user_id = User.objects.all().first().uid

        data = {
            'role': 2
        }

        # test endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.put(reverse('users-detail', kwargs={'uid': user_id}), data)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_admin_role_denied(self):
        """ Test updating supervisors role fails """
        # Setup the token
        url = reverse('login-list')
        data = {'email': 'test1@example.com', 'password': 'password1'}
        response = self.client.post(url, data)
        login_response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in login_response_data)
        token = login_response_data['access']

        # get user id
        user_id = User.objects.all()[1].uid

        data = {
            'role': 2
        }

        # test endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = client.put(reverse('users-detail', kwargs={'uid': user_id}), data)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

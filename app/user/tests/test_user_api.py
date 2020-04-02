from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):  # ** params is a dynamic  list of arguments
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):  # separee private and public
    """ Test the usesr API (pulic) """

    def setUp(self):
        self.Client = APIClient()

    def test_create_valid_user_succes(self):
        """ Test createing user with valid palyload is successful"""
        payload = {
            'email': 'Hash@mnp.ca',
            'password': 'testpass',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exsts(self):
        """ Test creation of a user that already exists fails"""

        payload = {
            'email': 'Hash@mnp.ca',
            'password': 'testpass',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Check password is more than 5 charaters"""

        payload = {
            'email': 'Hash@mnp.ca',
            'password': 'pw',
        }
        # create_user (**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test that the token is created for the user """

        payload = {
            'email': 'test@mnp.ca',
            'password': 'password123'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """ Test that a token is not created if credentials are not valide  """
        create_user(email='Test@Email.ca', password='testpass')
        payload = {'email': 'Test@Email.ca', 'password': 'NOTtestpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """ Test that a token is not create if the user does not exist """
        payload = {'email': 'Test@Email.ca', 'password': 'NOTtestpass'}

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """ Test that email and password are required for a token """
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """ Test that users are authenticated """
        res = self.client.post(ME_URL)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_not_allowed(self):
        """ Test post is not allowed """
        res = self.client.post(ME_URL)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    class PrivateUserAPITEst(TestCase):
        """ Test API requests that require authentication """

        def setUp(self):
            self.user = create_user(
                email='HashTest@mnp.ca',
                passsword='test1234',
                name='Hash Test User'
            )
            self.Client = APIClient()
            self.client.forced_authetiucate(user=self.user)

        def test_retrieveing_information_for_autheticated_user(self):
            """ Test retrieveing information for autheticated user """
            res = self.client.get(ME_URL)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res.data, {
                'name': self.user.name,
                'email': self.user.email
            })

        def test_post_me_not_allowed(self):
            """ Test that post is not allowe me is not allwoed """
            res = self.client.post(ME_URL, {})
            self.assertEqual(res.status_code,
                             status.HTTP_405_METHOD_NOT_ALLOWED)

        def test_update_user_profile(self):
            """ Test that the user can update their information """
            payload = {
                        'email': 'test@mnp.ca',
                        'password': 'password123456',
                        'name': 'Test User'
                    }

            res = self.client.patch(ME_URL, payload)
            self.user.refresh_fro_mdb()
            self.assertEqual(self.user.email, payload['email'])
            self.assertEqual(self.user.name, payload['name'])
            self.assertTrue(self.user.check_password(payload['password']))
            self.assertEqual(res.status_code, status.HTTP_200_OK)

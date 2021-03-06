from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@mnp.ca', password='testadmin123'):
    """ Create a sample user """
    return get_user_model().objects.create_user(email, password)


class ModelTests (TestCase):
    def test_create_user_with_email_successful(self):
        """ A test to make sure a new user was created successfully """
        email = 'test@mnp.ca'
        password = '6TuttiFruity9'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ This test checks to see if domain name is normalzied """
        email = "test@MNP.COM"
        user = get_user_model().objects.create_user(email, 'test123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ This test confirms that the email is valid"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_superuser(self):
        """Test confirms newsuper user has is_superuser & is_staff set"""
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test123')

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_model_as_string(self):
        """ Test the tag string representation """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

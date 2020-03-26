from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests (TestCase):
	def test_create_user_with_email_successful (self):
		""" A test to make sure a new user was created successfully with an email"""
		email = 'test@mnp.ca'
		password = '6TuttiFruity9'
		user = get_user_model().objects.create_user(
			email=email,
			password = password
		)

		self.assertEqual(user.email, email)
		self.assertTrue(user.check_password(password))

	def test_new_user_email_normalized (self):
		""" This test checks to see if domain name is normalzied """
		email = "test@MNP.COM"
		user = get_user_model().objects.create_user(email, 'test123');
		self.assertEqual(user.email, email.lower())

	def test_new_user_invalid_email(self):
		""" This test confirms that the email is valid"""
		with self.assertRaises(ValueError):
			get_user_model().objects.create_user(None, 'test123')


	def test_create_superuser(self):
		""" This test confirms that a new super user has is_superuser and is_staff set"""
		user = get_user_model().objects.create_superuser('test@test.com', 'test123')

		self.assertTrue(user.is_staff)
		self.assertTrue(user.is_superuser)





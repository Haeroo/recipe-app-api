from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITests(TestCase):
    """ Test the publical available tags API """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that checks that a login is required for Recipe tag API """

        self.user = get_user_model().objects.create_user(
            'Hash.Qureshi@mnp.ca',
            'password123'
        )

        self.client.force_authenticate(self.user)
        self.client = APIClient()
        res = self.client.get(TAGS_URL)
        # unclear why this works
        self.assertEqual(res.status_code,
                         status.HTTP_403_FORBIDDEN)


class PrivateTagsAPITests(TestCase):
    """ Tests for authenticated user Test API """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'User@test.ca',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Tet getting tags for an authenticated user"""
        # Create tags
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Desert')
        # retriev tags
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test that th tags returned are for the authenticated user """
        user2 = get_user_model().objects.create_user(
            'otherUser@Otherdomain.ca'
            'testpass2'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """We are going to test that a tag has been created successfully"""
        payload = {'name': 'TestTagFraggle'}
        self.client.post(TAGS_URL, payload)
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Creating a new tag that is invalid"""
        payload = {'name': ''}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

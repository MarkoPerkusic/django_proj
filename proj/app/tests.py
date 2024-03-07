from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Professor

class ProfessorRegistrationTestCase(TestCase):
    fixtures = ['professors.json']

    def setUp(self):
        super().setUp()
        self.registration_data = {
            "email": "test@example.com",
            "password": "password123"
        }

    def test_professor_registration(self):
        # Make POST request to register professor
        response = self.client.post(reverse('professor-registration'), self.registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if professor object was created in the database
        self.assertTrue(Professor.objects.filter(user__email=self.registration_data['email']).exists())

    def test_duplicate_registration(self):
        # Data for professor registration with existing email
        duplicate_data = {
            "email": "prof1@example.com",
            "password": "password123"
        }

        # Make POST request to register professor with existing email
        response = self.client.post(reverse('professor-registration'), duplicate_data, format='json')

        # Check if registration failed due to duplicate email (HTTP status code 400)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

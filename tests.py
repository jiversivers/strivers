from django.test import TestCase
from django.urls import reverse

from strivers.models import Athlete


# Create your tests here.
def IndexViewTest(TestCase):
    def test_first_time(self):
        # No cookie or session ID

        # Should return auth page
        pass
    def test_cookie(self):
        # Only cookie

        # Should return home
        pass

    def test_session(self):
        # Only session

        # Should return home
        pass

def HomeViewTest(TestCase):
    def test_first_time(self):
        # No cookie or session ID

        # Should offer auth page
        pass

    def test_cookie(self):
        # Only cookie

        # Should offer actions and logout
        pass

    def test_session(self):
        # Only session

        # Should offer actions
        pass

class SessionTestCase(TestCase):
    def test_session_with_model(self):
        # Create a sample athlete model
        athlete = Athlete.objects.create(
            id="d952744a-0ddf-441f-885b-ec058beb1a6d",
            athlete_id=1,
            username="jdoe",
            first_name="John",
            last_name="Doe",
            access_token="123abc",
            refresh_token="zyx987",
            expires_at="2025-02-15T10:47:53.292",
        )

        # Manually set session data (this is the key part for session testing)
        session = self.client.session
        session['athlete'] = {
            'id': athlete.id,
            'athlete_id': athlete.athlete_id,
            'username': athlete.username,
            'first_name': athlete.first_name,
            'last_name': athlete.last_name,
            'access_token': athlete.access_token,
            'refresh_token': athlete.refresh_token,
            'expires_at': athlete.expires_at,
        }
        session.save()

        # Send a GET request to the view (with session set)
        response = self.client.get(reverse('strivers:index'))  # Replace 'strivers:index' with your URL name

        # Check if session data is available in the response or view
        self.assertEqual(response.status_code, 200)
        self.assertIn('athlete', response.context)  # If you pass the athlete to the context
        self.assertEqual(response.context['athlete'].username, 'jdoe')

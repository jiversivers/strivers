from django.test import TestCase

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
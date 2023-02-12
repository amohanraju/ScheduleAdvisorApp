from django.test import TestCase

# Create your tests here.
class DummyTestCase(TestCase):
    def setUp(self):
        x = 2
        y = 2
    
    def test_dummy_test_case(self):
        self.assertEqual(x, y)
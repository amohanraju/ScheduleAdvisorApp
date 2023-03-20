from django.test import TestCase, Client
from django.urls import reverse



        
class TestViewRenders(TestCase):
    def setUp(self):
        self.client = Client()

    def test_profile_render(self):
        response = self.client.get(reverse("api_data"))
        self.assertTemplateUsed(response, 'myapp/courses.html')
        
    def test_shoppingCart_render(self):
        response = self.client.get(reverse('shoppingCart'))
        self.assertTemplateUsed(response, 'myapp/shoppingCart.html')
        
class Test404Error(TestCase):
    def setUp(self):
        self.client = Client()
    def test404(self):
        url = "129861yhuf.com"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
class Test200Response(TestCase):
    def setup(self):
        self.client = Client()
    def test200(self):
        url = reverse('shoppingCart')
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
            

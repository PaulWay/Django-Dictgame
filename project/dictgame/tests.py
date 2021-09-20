from django.test import TestCase
from django.urls import reverse

# Create your tests here.


class constants():
    html_content_type = 'text/html; charset=utf-8'


class EntryTestCase(TestCase):

    def test_basic_entry_page(self):
        response = self.client.get(reverse('entry'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], constants.html_content_type)
        self.assertIn('<html>', response.content.decode())

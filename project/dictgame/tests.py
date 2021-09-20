from django.test import TestCase
from django.urls import reverse

# Create your tests here.


class constants():
    html_content_type = 'text/html; charset=utf-8'


class EntryTestCase(TestCase):
    fixtures = ['basic_test_data',]

    def test_basic_entry_page(self):
        response = self.client.get(reverse('entry'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], constants.html_content_type)
        self.assertIn('<html>', response.content.decode())

    def test_entry_form(self):
        # Get an error and the form again
        response = self.client.post(
            reverse('entry'),
            data={'key': 'Nostalgic burblings'},
        )
        self.assertEqual(response.status_code, 200)  # Not a 400
        self.assertEqual(response.headers['Content-Type'], constants.html_content_type)
        content = response.content.decode()
        self.assertIn('<html>', content)  # And it starts the usual way,
        self.assertIn('<ul class="errorlist">', content)  # but it has an error message

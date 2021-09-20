from django.test import TestCase
from django.urls import reverse

# Create your tests here.


class constants():
    html_content_type = 'text/html; charset=utf-8'

    invalid_event_key = 'Nostalgic Burblings'
    event_key = 'examplicon'


class EntryTestCase(TestCase):
    fixtures = ['basic_test_data',]

    def test_basic_entry_page(self):
        response = self.client.get(reverse('entry'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], constants.html_content_type)
        self.assertIn('<html>', response.content.decode())

    def test_entry_form(self):
        # Slug too long, not a slug
        response = self.client.post(
            reverse('entry'),
            data={'key': constants.invalid_event_key},
        )
        self.assertEqual(response.status_code, 200)  # Not a 400
        self.assertEqual(response.headers['Content-Type'], constants.html_content_type)
        content = response.content.decode()
        self.assertIn('<html>', content)  # And it starts the usual way,
        self.assertIn('<ul class="errorlist">', content)  # but it has an error message

        # Valid slug gets redirected to a new page
        response = self.client.post(
            reverse('entry'),
            data={'key': constants.event_key},
        )
        # And we get redirected to the new page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('event', kwargs={'key': constants.event_key}))


class EventTestCase(TestCase):
    fixtures = ['basic_test_data', ]

    def test_no_list(self):
        response = self.client.get('/event/')
        self.assertEqual(response.status_code, 404)

    def test_basic_entry(self):
        response = self.client.get(
            reverse('event', kwargs={'key': constants.event_key})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], constants.html_content_type)
        content = response.content.decode()
        self.assertIn('<html>', content)
        self.assertIn("You're playing the 'Paul&#x27;s example dictionary game' Dictionary Game!", content)

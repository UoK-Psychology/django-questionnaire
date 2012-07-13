from django.test import TestCase
from django.utils import unittest
from django.core.urlresolvers import reverse
from questionnaire import models, views, urls

class url_test(TestCase):
    
    def test_index(self):
        resp = self.client.get('/questionnaire/')
        resp2 = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200, 'Index page should be shown')
        self.assertEqual(resp2.status_code, 200, 'Index page should be shown')

    
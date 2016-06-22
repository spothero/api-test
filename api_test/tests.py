from django.test import TestCase
from django_hosts.resolvers import reverse
from rest_framework.test import APIClient, APIRequestFactory


class TestGET(TestCase):
    def __init__(self, url):
        self.url = url
        super(TestGET, self).__init__(methodName='test_path')

    def test_path(self):
        response = reverse(self.url)
        self.assertEqual(response.status_code, 200)

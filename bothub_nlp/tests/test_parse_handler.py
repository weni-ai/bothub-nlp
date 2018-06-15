from tornado.testing import AsyncHTTPTestCase
from django.test import TestCase
from rest_framework import status


class ParseHandlerTestCase(AsyncHTTPTestCase, TestCase):
    def setUp(self):
        super().setUp()

    def get_app(self):
        from bothub_nlp.server import make_app
        return make_app()

    def test_method_get(self):
        response = self.fetch(
            '/parse/',
            method='GET',
        )
        self.assertEqual(
            response.code,
            status.HTTP_200_OK)

import unittest
from server.upload_controller import app
from unittest import TestCase

class TestIntegrations(TestCase):
    def setUp(self):
        self.app = app.test_client()  # Flask test client 

    def test_get_upload(self):
        response = self.app.get('/upload')
        assert True

    def test_post_upload_no_file:
        pass

    def post_upload_invalid_file: 
        pass

    def post_upload_valid_file:
        pass
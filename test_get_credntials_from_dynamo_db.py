import os
import unittest
import socket
from unittest import mock
from unittest.mock import Mock

from get_credentials_from_dynamo_db import GetKeysFromSite, GetCredentialsFromDynamoDB

def mock_init():
    return get_code_name()

def get_code_name():
    return "test"

class TestGetKeysFromSite(unittest.TestCase):
    def setUp(self) -> None:
        self.get_keys = GetKeysFromSite()
        self.foldername = os.path.dirname(os.path.realpath(__file__)) + "/"
        self.test_file = self.set_test_file()

    def delete_test_file(self):
        os.remove(self.test_file)

    @staticmethod
    def set_test_file():
        hostname = socket.gethostname()
        if "omer" in hostname:
            return "/tmp/test_file"
        else:
            return "/root/.aws/test_file"

    def test_get_html_page(self):
        html_page = self.get_keys.get_html_page("https://challenge.prodops.io/")
        self.assertTrue('<html>' in html_page)
        self.assertRegex(html_page, "<div(.*)+>\n")
        self.assertFalse('<xml>' in html_page)

    def test_extract_credentials(self):

        with open(self.foldername + "test_html.html") as f:
            test_html = f.read()

        test_credentials = self.get_keys.extract_credentials(test_html)
        self.assertTrue(test_credentials.get("code_name"), True)
        self.assertTrue(test_credentials["aws key"], "test_key")
        self.assertIsInstance(test_credentials["aws key"], str)

    def test_write_to_aws_directory(self):
        self.write_to_file()
        test_file = self.get_test_file()
        self.assertTrue("123456" in test_file)
        self.assertTrue("ABCDE" in test_file)
        self.assertTrue("abcde" in test_file)
        self.assertFalse("xxxx" in test_file)
        self.delete_test_file()

    def get_test_file(self):
        with open(self.test_file, "r") as f:
            return f.read()

    def write_to_file(self):
        with open(self.test_file, "w") as f:
            f.write("123456\nABCDE\nabcde")


class TestGetCredentialsFromDynamoDB(unittest.TestCase):

    def setUp(self) -> None:
        self.foldername = os.path.dirname(os.path.realpath(__file__)) + "/"
        self.write_config_file()
        self.gcfd = GetCredentialsFromDynamoDB()

    def tearDown(self) -> None:
        os.remove(self.foldername + "config")

    def write_config_file(self):
        with open(self.foldername + "config", "w") as f:
            f.write("TEST")

    def test_post_to_health(self):
        endpoint = "https://tlooihqhq5.execute-api.us-east-1.amazonaws.com/prod"

        response = self.gcfd.put_bucket_and_git_info_to_health(endpoint)
        self.assertEqual(response.status_code, 200)
        body = '{\'container\': \'https://hub.docker.com/r/omerls/get_code_from_dynamodb\', \'project\': \'https://github.com/omersi/twist\', \'status\': \'healthy\'}'
        self.assertEqual(response.request.body, body)

    def test_post_to_secret(self):
        endpoint = "https://tlooihqhq5.execute-api.us-east-1.amazonaws.com/prod"
        keys = {"secret_code": "test_code"}

        response = self.gcfd.put_secret_to_secret(keys, endpoint)
        self.assertEqual(response.status_code, 200)
        body = "{\'secret_code\': \'test_code\'}"
        self.assertEqual(response.request.body, body)

if __name__ == '__main__':
    unittest.main()

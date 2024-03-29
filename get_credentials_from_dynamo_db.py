"""Get aws keys from hiden repository and store them for accessing DynamoDB. The pushing the results to a web server"""

import base64
import os
import re

import boto3
import requests
import sys
import urllib3
from boto3.dynamodb.conditions import Key
from requests import Timeout
from retry import retry

from exception_decor import exception
from exception_logger import logger

FOLDERNAME = os.path.dirname(os.path.realpath(__file__)) + "/"

print(FOLDERNAME)


class GetKeysFromSite():

    @exception(logger)
    @retry(Timeout, tries=3, delay=2)
    def get_html_page(self, url):
        """Getting HTML page body with hidden credentials.

        :param url: html page endpoint
        :return: HTML page text.
            or
            None if error
        """
        logger.info("Getting HTML source page")
        logger.debug(url)
        http_pool = urllib3.connection_from_url(url)
        request_data = http_pool.urlopen('GET', url)

        if request_data.status == 200:
            logger.info("HTML Page collected")
            html_page = request_data.data.decode("utf-8")
            assert isinstance(html_page, str)
            return html_page
        return None

    @exception(logger)
    def extract_credentials(self, html_page):
        """Extracting credentials from HTML page.

        :param html_page:
        :return:
            credentials: dict
        """
        logger.info("Extratctin credentials")
        groups = re.search('(log\(")(.*)("\))', html_page, re.IGNORECASE)
        encoded = groups.group(2)
        credentials = {}
        credentials_from_html = base64.b64decode(encoded).decode("utf-8")
        for creds in credentials_from_html.split("\n"):
            if len(creds.split(":")) == 2:
                _creds = creds.split(":")
                credentials.setdefault(_creds[0], _creds[1].strip())
        logger.info("Credentials Extracted")
        return credentials

    @exception(logger)
    def store_to_file(self, credentials):
        """Storing recovered credentials to file for future use.

        :param credentials:
        :return: None
        """
        logger.info("Storring credentials to file")
        aws_credentials_text = "[default]\n" \
                               "aws_access_key_id = {key}\n" \
                               "aws_secret_access_key = {secret}\n" \
                               "region = {region}".format(key=credentials["aws key"],
                                                          secret=credentials["aws secret"],
                                                          region=credentials["aws region"])

        logger.info("Credentials File")
        with open("/root/.aws/credentials", "w") as f:
            f.write(aws_credentials_text.strip())
        logger.info("Config File")
        with open("/usr/src/app/config", "w") as f:
            f.write(credentials["code_name"])

    @exception(logger)
    def main(self):
        html_page = self.get_html_page("https://challenge.prodops.io/")
        credentials = self.extract_credentials(html_page)
        self.store_to_file(credentials)


class GetCredentialsFromDynamoDB(object):

    def __init__(self):
        self.code_name = self.get_code_name()

    def get_code_name(self,):
        """Getting project code_name from stored file.

        :return: project_name
        """
        logger.info("Reading config file")
        with open(FOLDERNAME + "config", "r") as f:
            return f.readlines()[0].strip()

    @exception(logger)
    def connect_to_dynamodb(self, ):
        """Connector module tp DynampDB

        :return: DynamoDB connection client
        """
        logger.info("Conneting to DynamoDB")
        client = boto3.resource("dynamodb")
        return client

    @exception(logger)
    def read_from_dynamodb(self, db_connection):
        """Read response from Dynamo DB

        :param db_connection: connector object from previous function
        :return: keys: retrieved credentials from DynamoDB
        """
        logger.info("Reading from DynamoDB")
        table = db_connection.Table("devops-challenge")
        results = table.query(KeyConditionExpression=Key("code_name").eq(self.code_name))
        keys = [x for x in results["Items"] if x["code_name"] == self.code_name][0]
        logger.info("Returning keys")
        return keys

    @exception(logger)
    @retry(Timeout, tries=3, delay=2)
    def put_secret_to_secret(self, keys, endpoint):
        """Pushing secret restored from DynamoDB to predefined endpoint.

        :param keys:
        :return: response or None
        """
        logger.info("Posting secret to container")
        url = endpoint + "/secret"
        payload_json = {
            "secret_code": keys["secret_code"]
        }
        payload = str(payload_json)
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
        }
        response = requests.request("PUT", url, data=payload, headers=headers)
        if response.status_code == 200:
            logger.info("Posting to container finished")
            return response
        return None

    @exception(logger)
    @retry(Timeout, tries=3, delay=2)
    def put_bucket_and_git_info_to_health(self, endpoint):
        """Pushing projects info (image and git) to predefined endpoint

        :return: response or None
        """
        logger.info("Posting secret to container")
        url = endpoint + "/health"
        payload_json = {
            "container": "https://hub.docker.com/r/omerls/get_code_from_dynamodb",
            "project": "https://github.com/omersi/twist",
            "status": "healthy"
        }
        payload = str(payload_json)
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
        }
        response = requests.request("PUT", url, data=payload, headers=headers)
        if response.status_code == 200:
            logger.info("Posting to container finished")
            return response
        return None

    def main(self, ):
        endpoint = "http://127.0.0.1:5000"
        db_connection = self.connect_to_dynamodb()
        keys = self.read_from_dynamodb(db_connection)
        response_secret = self.put_secret_to_secret(keys, endpoint)
        logger.info(response_secret)

        response_health = self.put_bucket_and_git_info_to_health(endpoint)
        logger.info(response_health)


if __name__ == '__main__':
    """Main module"""
    gkfs = GetKeysFromSite()
    gkfs.main()
    gcfd = GetCredentialsFromDynamoDB()
    gcfd.main()
    sys.exit(0)

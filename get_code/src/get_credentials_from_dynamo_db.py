import boto3
import urllib3
from boto3.dynamodb.conditions import Key, Attr
import requests
import os
import re
import base64
from exception_decor import exception
from exception_logger import logger

FOLDERNAME = os.path.dirname(os.path.realpath(__file__)) + "/"

print(FOLDERNAME)


class GetKeysFromSite(object):

    @exception(logger)
    def get_html_page(self):
        logger.info("Getting HTML source page")
        url = 'https://challenge.prodops.io/'
        http_pool = urllib3.connection_from_url(url)
        r = http_pool.urlopen('GET', url)

        html_page = r.data.decode("utf-8")
        logger.info("HTML Page collected")
        return html_page

    @exception(logger)
    def extract_credentials(self, html_page):
        logger.info("Extratctin credentials")
        groups = re.search('(log\(")(.*)("\))', html_page, re.IGNORECASE)
        encoded = groups.group(2)
        credentials = {}
        credentials_from_html = base64.b64decode(encoded).decode('utf-8')
        for creds in credentials_from_html.split("\n"):
            if len(creds.split(":")) == 2:
                _creds = creds.split(":")
                credentials.setdefault(_creds[0], _creds[1].strip())
        logger.info("Credentials Extracted")
        return credentials

    @exception(logger)
    def store_to_file(self, credentials):
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
        html_page = self.get_html_page()
        credentials = self.extract_credentials(html_page)
        self.store_to_file(credentials)


class GetCredentialsFromDynamoDB(object):

    def __init__(self):
        self.code_name = self.get_code_name()

    @staticmethod
    def get_code_name():
        logger.info("Reading config file")
        with open(FOLDERNAME + "config", "r") as f:
            return f.readlines()[0].strip()

    @exception(logger)
    def connect_to_dynamodb(self, ):
        logger.info("Conneting to DynamoDB")
        client = boto3.resource("dynamodb")
        return client

    @exception(logger)
    def read_from_dynamodb(self, db_connection):
        logger.info("Reading from DynamoDB")
        table = db_connection.Table("devops-challenge")
        results = table.query(KeyConditionExpression=Key("code_name").eq(self.code_name))
        keys = [x for x in results["Items"] if x["code_name"] == self.code_name][0]
        logger.info("Returning keys")
        return keys

    @exception(logger)
    def post_to_container(self, keys):
        logger.info("Posting secret to container")
        url = "http://127.0.0.1:5000/secret"
        querystring = {"secret_code": keys["secret_code"]}
        headers = {
            'cache-control': "no-cache",
        }
        response = requests.request("PUT", url, headers=headers, params=querystring)
        logger.info("Posting to container finished")
        return response

    def main(self, ):
        db_connection = self.connect_to_dynamodb()
        keys = self.read_from_dynamodb(db_connection)
        response = self.post_to_container(keys)
        print(response)


if __name__ == '__main__':
    gkfs = GetKeysFromSite()
    gkfs.main()
    gcfd = GetCredentialsFromDynamoDB()
    gcfd.main()

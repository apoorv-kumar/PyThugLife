import unittest
from crawler import Crawler
import os
import sys
from unittest.mock import patch
from io import BytesIO

class SampleCrawler(Crawler):

    @staticmethod
    def get_base_dir():
        if sys.platform == 'linux':
            return '/tmp/'
        else:
            return 'C:/Users/apoor/AppData/Local/Temp/'

    @staticmethod
    def get_image_lambda():
        return lambda link: "__isvalidpic__" in link

    @staticmethod
    def get_link_lambda():
        return lambda link: "__isvalidlink__" in link


class CrawlTest(unittest.TestCase):
    junk_files = []

    def mocked_requests_get(*args, **kwargs):
        class MockedResponse:
            def __init__(self):
                self.raw = BytesIO(b"response_content")

        return MockedResponse()

    def test_url_logger(self):
        written_urls = ['http://some_url.com', 'https://some_url.com']
        log_loc = SampleCrawler.log_urls(written_urls)
        self.junk_files.append(log_loc)

        with open(log_loc, 'r') as log_file:
            read_urls = log_file.readlines()
            read_urls = map(lambda x: x.strip(), read_urls)

        for written_url in written_urls:
            self.assertTrue(written_url in read_urls)
        self.assertTrue(len(written_urls) == len(written_urls))

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_download_pic(self, mock_get):
        img_loc = SampleCrawler.download_pic("http://test_url")
        self.junk_files.append(img_loc)
        with open(img_loc, 'r') as img_file:
            img_data = img_file.read()
        print("this", img_data)
        self.assertEqual(img_data, "response_content")


    @classmethod
    def tearDownClass(cls):
        for junk_file in cls.junk_files:
            os.remove(junk_file)

if __name__ == '__main__':
    unittest.main()

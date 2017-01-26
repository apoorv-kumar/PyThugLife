import unittest
from downloader import Downloader
from crawler import Crawler
import os
import sys
from unittest.mock import patch
from io import BytesIO


class SampleCrawler(Crawler):
    @staticmethod
    def get_image_lambda():
        return lambda page_url, img_url: "__isvalidpic__" in img_url

    @staticmethod
    def get_link_lambda():
        return lambda link: "__isvalidlink__" in link

    @staticmethod
    def get_page_text(page_url):
        return '''
        <html>
        <a   href="http://__isvalidlink__123">
            <img src="http://someinvalid_link.jpg">
        </a>
        <a href="http://_someinvalid_link"> mytext </a>
        <img src="http://__isvalidpic__111.png">
        <img src="http://__isvalidpic__333.png">
        </html>
        '''


class DownloadTest(unittest.TestCase):
    junk_files = []

    @classmethod
    def setUpClass(cls):
        if sys.platform == 'linux':
            base_dir = '/tmp/'
        else:
            base_dir = 'C:/Users/apoor/AppData/Local/Temp/'
        sample_crawler = SampleCrawler(base_dir)
        cls.downloader = Downloader(sample_crawler)

    def mocked_requests_get(*args, **kwargs):
        class MockedResponse:
            def __init__(self):
                self.raw = BytesIO(b"response_content")

        return MockedResponse()

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_download_pic(self, mock_get):
        img_loc = self.downloader.download_pic("http://test_url")
        self.junk_files.append(img_loc)
        with open(img_loc, 'r') as img_file:
            img_data = img_file.read()
        self.assertEqual(img_data, "response_content")

    @classmethod
    def tearDownClass(cls):
        for junk_file in cls.junk_files:
            os.remove(junk_file)


if __name__ == '__main__':
    unittest.main()

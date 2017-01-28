import unittest
from downloader import Downloader
import os
import sys
from unittest.mock import patch
from io import BytesIO


class DownloadTest(unittest.TestCase):
    junk_files = []

    @classmethod
    def setUpClass(cls):
        if sys.platform == 'linux':
            base_dir = '/tmp/'
        else:
            base_dir = 'C:/Users/apoor/AppData/Local/Temp/'
        cls.downloader = Downloader(base_dir)

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

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_download_batch(self, mock_get):
        images = self.downloader.download_batch(["http://pic1", "http://pic2", "http://pic3"], parallelism=3)
        self.junk_files.extend(images)
        for img_loc in images:
            with open(img_loc, 'r') as img_file:
                img_data = img_file.read()
            self.assertEqual(img_data, "response_content")

    @classmethod
    def tearDownClass(cls):
        for junk_file in cls.junk_files:
            os.remove(junk_file)


if __name__ == '__main__':
    unittest.main()

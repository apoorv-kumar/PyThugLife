import unittest
from crawl import Crawler
import os

class SampleCrawler(Crawler):

    @staticmethod
    def get_base_dir():
        return 'C:/Users/apoor/AppData/Local/Temp/'

    @staticmethod
    def get_image_lambda():
        return lambda link: "__isvalidpic__" in link

    @staticmethod
    def get_link_lambda():
        return lambda link: "__isvalidlink__" in link

class CrawlTest(unittest.TestCase):

    junk_files = []

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

    def test_get_page_links(self):
        requests.get("url1")

    def tearDown(self):
        for junk_file in self.junk_files:
            os.remove(junk_file)

if __name__ == '__main__':
    unittest.main()
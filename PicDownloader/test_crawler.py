import unittest
from crawler import Crawler
import os
import sys


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
        <a   href="__isvalidlink__123">
            <img src="http://someinvalid_link.jpg">
        </a>
        <a href="http://_someinvalid_link"> mytext </a>
        <img src="http://website/__isvalidpic__111.png">
        <img src="__isvalidpic__333.png">
        </html>
        '''


class CrawlTest(unittest.TestCase):
    junk_files = []

    @classmethod
    def setUpClass(cls):
        if sys.platform == 'linux':
            base_dir = '/tmp/'
        else:
            base_dir = 'C:/Users/apoor/AppData/Local/Temp/'
        cls.crawler = SampleCrawler(base_dir)

    def test_url_logger(self):
        written_urls = ['http://some_url.com', 'https://some_url.com']
        log_loc = self.crawler.log_urls(written_urls)
        self.junk_files.append(log_loc)

        with open(log_loc, 'r') as log_file:
            read_urls = log_file.readlines()
            read_urls = map(lambda x: x.strip(), read_urls)

        for written_url in written_urls:
            self.assertTrue(written_url in read_urls)
        self.assertTrue(len(written_urls) == len(written_urls))


    def test_get_abs_url(self):
        self.assertEqual(
            SampleCrawler.get_abs_url("/some_relative_path.blah", "http://myweb.www.x/44/abc.jpg"),
            "http://myweb.www.x/some_relative_path.blah"
        )

    def test_get_page_links(self):
        url_list = SampleCrawler.get_page_links("http://website/someurl")
        expected_urls = ["http://website/__isvalidlink__123", "http://_someinvalid_link"]
        self.assertSetEqual(set(url_list), set(expected_urls))

    def test_get_page_pics(self):
        url_list = SampleCrawler.get_page_pics("http://website/someurl")
        expected_urls = ["http://someinvalid_link.jpg",
                         "http://website/__isvalidpic__111.png",
                         "http://website/__isvalidpic__333.png"]
        self.assertSetEqual(set(url_list), set(expected_urls))

    def test_get_artifacts(self):
        valid_pics, valid_links = SampleCrawler.get_artifacts("http://website/someurl",
                                                              SampleCrawler.get_image_lambda(),
                                                              SampleCrawler.get_link_lambda())
        self.assertSetEqual(set(valid_links), set(["http://website/__isvalidlink__123"]))
        self.assertSetEqual(set(valid_pics), set(["http://website/__isvalidpic__111.png",
                                                  "http://website/__isvalidpic__333.png"]))

    def test_crawl(self):
        # terminate on images
        image_list = self.crawler.crawl("http://website/someurl", image_limit=100, link_limit=100)
        self.assertSetEqual(image_list, set(["http://website/__isvalidpic__333.png",
                                             "http://website/__isvalidpic__111.png"]))
        # terminate on links
        image_list = self.crawler.crawl("http://website/someurl", image_limit=1000, link_limit=100)
        self.assertSetEqual(image_list, set(["http://website/__isvalidpic__333.png",
                                             "http://website/__isvalidpic__111.png"]))

    @classmethod
    def tearDownClass(cls):
        for junk_file in cls.junk_files:
            os.remove(junk_file)

if __name__ == '__main__':
    unittest.main()

from crawler import Crawler
import requests
from time import time
from shutil import copyfileobj
from multiprocessing import Pool
from urllib.parse import urlparse


# Downloader accepts a crawler and uses it to
# download files.
class Downloader:
    crawler = None

    def __init__(self, _crawler):
        self.crawler = _crawler

    # TODO: use Rlock to name incrementally rather than brute hash
    def generate_pic_name(self, pic_url):
        pic_name = str(hash(pic_url)) + "_" + urlparse(pic_url).path.split('/')[-1]
        return pic_name

    def download_pic(self, pic_url):
        response = requests.get(pic_url, stream=True)
        name = self.generate_pic_name(pic_url)
        image_loc = self.crawler.base_dir + '/' + name
        with open(image_loc, 'wb') as out_file:
            copyfileobj(response.raw, out_file)
        self.crawler.log_msg("downloaded " + pic_url)
        return image_loc

    def download_batch(self, pic_urls, parallelism=4):
        downloader_pool = Pool(parallelism)
        results = downloader_pool.map(self.download_pic, pic_urls)
        self.crawler.log_urls(results, url_type="image")
        return results

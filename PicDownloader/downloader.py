from crawler import Crawler
import requests
from time import time
from shutil import copyfileobj


# Downloader accepts a crawler and uses it to
# download files.
class Downloader:
    crawler = None

    def __init__(self, _crawler):
        self.crawler = _crawler

    def download_pic(self, pic_url):
        response = requests.get(pic_url, stream=True)
        name = str(hash(pic_url + str(time()))&65535) + ".jpg"
        image_loc = self.crawler.base_dir + '/' + name
        with open(image_loc, 'wb') as out_file:
            copyfileobj(response.raw, out_file)
        return image_loc

import requests
from time import time
from shutil import copyfileobj
from multiprocessing import Pool
from urllib.parse import urlparse


# Downloader accepts a crawler and uses it to
# download files.
class Downloader:

    def __init__(self, base_dir):
        self.base_dir = base_dir

    # TODO: use Rlock to name incrementally rather than brute hash
    @staticmethod
    def generate_pic_name(pic_url):
        pic_name = str(hash(pic_url)) + "_" + urlparse(pic_url).path.split('/')[-1]
        return pic_name

    def log_urls(self, downloaded_imgs):
        log_loc = self.base_dir + "imglog_" + str(time()) + ".log"
        with open(log_loc, 'w') as log_file:
            log_file.write("\n".join(downloaded_imgs))
        return log_loc

    @staticmethod
    def log_msg(msg):
        print(msg)

    def download_pic(self, pic_url):
        try:
            response = requests.get(pic_url, stream=True)
            name = self.generate_pic_name(pic_url)
            image_loc = self.base_dir + '/' + name
            with open(image_loc, 'wb') as out_file:
                copyfileobj(response.raw, out_file)
            self.log_msg("downloaded " + pic_url)
        except:
            image_loc = ""
            self.log_msg("Failed to download image: " + pic_url)
        return image_loc

    def download_batch(self, pic_urls, parallelism=4):
        downloader_pool = Pool(parallelism)
        results = downloader_pool.map(self.download_pic, pic_urls)
        results = filter(lambda loc: loc == "", results)  # remove invalid locations
        self.log_urls(results)
        return results

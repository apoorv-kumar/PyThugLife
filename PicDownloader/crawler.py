import requests
import bs4
import os
import shutil
from abc import ABCMeta, abstractmethod
from collections import deque
from time import time

class Crawler:
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get_image_lambda():
        pass

    @staticmethod
    @abstractmethod
    def get_link_lambda():
        pass

    @staticmethod
    @abstractmethod
    def get_base_dir():
        pass

    @classmethod
    def log_urls(cls, visited_urls):
        log_loc = cls.get_base_dir() + "url_log_" + str(int(time())) + ".log"
        with open(log_loc, 'w') as log_file:
            log_file.write("\n".join(visited_urls))
            # guarantee flush to disk ( TODO: while testing only. remove it )
            log_file.flush()
            os.fsync(log_file.fileno())
        return log_loc

    # TODO: probably should be moved out of crawler into downloader
    @classmethod
    def download_pic(cls, pic_url):
        response = requests.get(pic_url, stream=True)
        name = str(hash(pic_url)&65535) + ".jpg"
        image_loc = cls.get_base_dir() + '/' + name
        with open(image_loc, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        return image_loc

    @staticmethod
    def get_page_text(page_url):
        return requests.get(page_url).text

    @classmethod
    def get_page_links(cls, page_url):
        page_text = cls.get_page_text(page_url)
        soup = bs4.BeautifulSoup(page_text, "html.parser")
        return map(lambda link: link.get("href"), soup.find_all('a') )

    @classmethod
    def get_page_pics(cls, page_url):
        page_text = cls.get_page_text(page_url)
        soup = bs4.BeautifulSoup(page_text, "html.parser")
        return map(lambda link: link.get("src"), soup.find_all('img') )

    # returns dict of images and link queue
    # image and link lambdas return true/false
    # image_lambda(link,url)
    # link_lambda(link)
    @classmethod
    def get_artifacts(cls, page_url, image_lambda, link_lambda):
        page_links = cls.get_page_links(page_url)
        page_pics = cls.get_page_pics(page_url)

        def curried_image_lambda(link):
            image_lambda(page_url, link)

        valid_links = filter(link_lambda, page_links)
        valid_pics = filter(curried_image_lambda, page_pics)
        return valid_pics, valid_links

    @classmethod
    def crawl(cls, page_url, image_limit=1000, link_limit=100):
        link_breaker_set = False
        image_breaker_set = False
        image_list = deque()
        link_list = deque([page_url])

        visited_urls = deque()

        # break if no links or too many images
        while not image_breaker_set and len(link_list) > 0:
            current_url = link_list.popleft()
            new_pics, new_links = cls.get_artifacts(current_url,
                                                    cls.get_image_lambda(),
                                                    cls.get_link_lambda())

            image_list.extend(new_pics)
            image_breaker_set = len(image_list) > image_limit
            if not link_breaker_set:
                link_list.extend(new_links)
                link_breaker_set = len(link_list) > link_limit
            # log for record
            visited_urls.append(current_url)

        cls.log_urls(visited_urls)
        print("crawl session finished")

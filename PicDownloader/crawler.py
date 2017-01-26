import requests
import bs4
import os
import shutil
from abc import ABCMeta, abstractmethod
from collections import deque
from time import time

# TODO: do we need inheritance when we can simply
#       pass along the lambda via constructor ?
class Crawler:
    __metaclass__ = ABCMeta

    def __init__(self, _base_dir):
        self.base_dir = _base_dir

    # points to the base dir
    # where logs are created.
    base_dir = str()

    @abstractmethod
    def get_image_lambda(self):
        pass

    @abstractmethod
    def get_link_lambda(self):
        pass

    def log_urls(self, visited_urls):
        log_loc = self.base_dir + "url_log_" + str(int(time())) + ".log"
        with open(log_loc, 'w') as log_file:
            log_file.write("\n".join(visited_urls))
            # guarantee flush to disk ( TODO: while testing only. remove it )
            log_file.flush()
            os.fsync(log_file.fileno())
        return log_loc

    @staticmethod
    def get_page_text(page_url):
        return requests.get(page_url).text

    @classmethod
    def get_page_links(cls, page_url):
        page_text = cls.get_page_text(page_url)
        soup = bs4.BeautifulSoup(page_text, "html.parser")
        return list(map(lambda link: link.get("href"), soup.find_all('a')))

    @classmethod
    def get_page_pics(cls, page_url):
        page_text = cls.get_page_text(page_url)
        soup = bs4.BeautifulSoup(page_text, "html.parser")
        return list(map(lambda link: link.get("src"), soup.find_all('img')))

    # returns dict of images and link queue
    # image and link lambdas return true/false
    # image_lambda(link,url)
    # link_lambda(link)
    @classmethod
    def get_artifacts(cls, page_url, image_lambda, link_lambda):
        page_links = cls.get_page_links(page_url)
        page_pics = cls.get_page_pics(page_url)

        def curried_image_lambda(link):
            return image_lambda(page_url, link)

        valid_links = list(filter(link_lambda, page_links))
        valid_pics = list(filter(curried_image_lambda, page_pics))
        return valid_pics, valid_links

    # returns list of images that the crawler crawled.
    # side effect - writes a log file listing urls visited.
    def crawl(self, page_url, image_limit=1000, link_limit=100):
        link_breaker_set = False
        image_breaker_set = False
        image_list = set()
        link_list = deque([page_url])  # for a BFS

        visited_urls = set()

        # break if no links or too many images
        while not image_breaker_set and len(link_list) > 0:
            current_url = link_list.popleft()
            new_pics, new_links = self.get_artifacts(current_url,
                                                     self.get_image_lambda(),
                                                     self.get_link_lambda())

            image_list = image_list.union(set(new_pics))
            image_breaker_set = len(image_list) > image_limit
            if not link_breaker_set:
                unvisited_links = set(new_links).difference(visited_urls)
                link_list.extend(list(unvisited_links))
            # log for record
            visited_urls.add(current_url)
            link_breaker_set = len(visited_urls) > link_limit

        self.log_urls(visited_urls)
        print("crawl session finished")
        return image_list

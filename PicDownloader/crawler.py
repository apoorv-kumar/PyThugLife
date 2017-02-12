import requests
import bs4
import os
from abc import ABCMeta, abstractmethod
from collections import deque
from time import time, clock
import re
from urllib.parse import urljoin, urlparse
from functools import reduce

# TODO: handle kill signals. Or log results periodically.
# TODO: do we need inheritance when we can simply
#       pass along the lambda via constructor ?
class Crawler:
    __metaclass__ = ABCMeta

    # TODO: base_dir + <new dir for each session>
    def __init__(self, _base_dir):
        self.base_dir = _base_dir

    # points to the base dir
    # where logs are created.
    base_dir = None

    @abstractmethod
    def get_image_lambda(self):
        pass

    @abstractmethod
    def get_link_lambda(self):
        pass

    # used to detect image links
    # can be overridden if necessary
    @staticmethod
    def is_valid_img_link(link):
        img_extensions = [".jpg", ".png", ".jpeg", ".bmp"]
        link_path = urlparse(link).path
        is_valid_vector = map(lambda ext: link_path.endswith(ext), img_extensions)
        return reduce(lambda _init, _is_valid: _is_valid or _init, is_valid_vector, False)

    # always returns absolute path
    @staticmethod
    def get_abs_url(link_url, curr_page_url):
        abs_pattern = re.compile(".*://.*")  # quite generic url
        if abs_pattern.match(link_url) is None:
            return urljoin(curr_page_url, link_url)  # make absolute
        else:
            return link_url

    @staticmethod
    def log_msg(msg):
        print(msg)

    def log_urls(self, visited_urls):
        log_loc = self.base_dir + "urllog_" + str(int(time())) + str(clock()) + ".log"
        with open(log_loc, 'w') as log_file:
            log_file.write("\n".join(visited_urls))
            # guarantee flush to disk ( TODO: while testing only. remove it )
            log_file.flush()
            os.fsync(log_file.fileno())
        return log_loc

    @staticmethod
    def get_page_text(page_url):
        return requests.get(page_url).text

    # gets all links on the page and converts them
    # to absolute paths
    @classmethod
    def get_page_links(cls, page_url):
        page_text = cls.get_page_text(page_url)
        soup = bs4.BeautifulSoup(page_text, "html.parser")
        page_links = map(lambda link: str(link.get("href")), soup.find_all('a'))
        page_links_absolute = \
            map(lambda link: cls.get_abs_url(link, page_url), page_links)
        return list(page_links_absolute)

    # gets all links on the page and converts them
    # to absolute paths
    @classmethod
    def get_page_pics(cls, page_url):
        page_text = cls.get_page_text(page_url)
        soup = bs4.BeautifulSoup(page_text, "html.parser")
        page_pics = list(map(lambda link: str(link.get("src")), soup.find_all('img')))
        page_links = map(lambda link: str(link.get("href")), soup.find_all('a'))
        page_pic_links = list(filter(cls.is_valid_img_link, page_links))
        page_pics_absolute = \
            map(lambda link: cls.get_abs_url(link, page_url), page_pics+page_pic_links)
        return list(page_pics_absolute)

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
    # periodically checks if app has exceeded max_time seconds
    # side effect - writes a log file listing urls visited.
    def crawl(self, page_url, image_limit=1000, link_limit=5000, max_time=9000):
        link_breaker_set = False
        image_breaker_set = False
        image_list = set()
        link_list = deque([page_url])  # for a BFS

        visited_links = deque()
        queued_links = set()  # links that've ever been queued
        start_time = time()
        # break if no links or too many images or time exceeded
        while not image_breaker_set and len(link_list) > 0 and time() - start_time < max_time:
            current_url = link_list.popleft()
            Crawler.log_msg("visiting: " + current_url)
            page_pics, page_links = self.get_artifacts(current_url,
                                                     self.get_image_lambda(),
                                                     self.get_link_lambda())

            # add pics
            image_list = image_list.union(set(page_pics))
            image_breaker_set = len(image_list) > image_limit

            if not link_breaker_set:
                # get new links
                new_links = set(page_links).difference(queued_links)
                queued_links = queued_links.union(new_links)
                link_list.extend(list(new_links))

            # log for record
            visited_links.append(current_url)
            link_breaker_set = len(queued_links) > link_limit
            Crawler.log_msg("images till now:: " + str(len(image_list)) + "/" + str(image_limit))
            Crawler.log_msg("links till now:: " + str(len(queued_links)) + "/" + str(link_limit))

        log_loc = self.log_urls(visited_links)
        print("crawl session finished. Urls logged at: ", log_loc)
        return image_list

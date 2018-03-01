from typing import List
from collections import namedtuple
import json
import requests
from aiohttp import ClientSession
import asyncio
from bs4 import BeautifulSoup as BS
Link = namedtuple('Link', ['title', 'href'])
reqests_sem = asyncio.BoundedSemaphore(20)

def parse_and_get(data):
    soup = BS(data, 'html.parser')
    lis = soup.findAll('li')
    lis = [l for l in lis if l.get('id', '').startswith('newslist')]
    links = [l.findAll('a')[0] for l in lis]
    return [{'title':link['title'], 'href':link['href']} for link in links]


async def get_and_store(page_no, session) -> dict:
    url = 'https://www.moneycontrol.com/news/expertadvice-250.html/page-{}/'
    url = url.format(page_no)
    async with reqests_sem, session.get(url) as response:
        data = await response.read()
        return {'page': page_no, 'data': parse_and_get(data)}


async def run(r):
    tasks = []

    async with ClientSession() as session:
        for i in range(1,r+1):
            task = asyncio.ensure_future(get_and_store(i, session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        with open('/home/apoorv/Downloads/moneyctrl/{}'.format(r), 'w') as f:
            f.write(json.dumps(responses))


loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(2536))
loop.run_until_complete(future)

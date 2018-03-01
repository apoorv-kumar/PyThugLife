from typing import List
from collections import namedtuple
import json
import requests
from aiohttp import ClientSession
import asyncio
from bs4 import BeautifulSoup as BS
Link = namedtuple('Link', ['title', 'href'])
reqests_sem = asyncio.BoundedSemaphore(40)

def parse_and_get(data):
    soup = BS(data, 'html.parser')
    content = soup.find(id='article-main')
    content = content.findAll('p') if content else []
    return [str(c) for c in content]


async def get_and_store(url, session) -> dict:
    async with reqests_sem, session.get(url) as response:
        data = await response.read()
        return {'url': url, 'data': parse_and_get(data)}

async def run(page_data):
    tasks = []
    page_no = page_data['page']
    urls = [x['href'] for x in page_data['data']]
    async with ClientSession() as session:
        for url in urls:
            task = asyncio.ensure_future(get_and_store(url, session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        with open('/home/apoorv/Downloads/moneyctrl/link_content/{}'.format(page_no), 'w') as f:
            f.write(json.dumps(responses))

with open('/home/apoorv/Downloads/moneyctrl/2536') as f:
    d = json.load(f)

loop = asyncio.get_event_loop()
for page_data in d[184:]:
    future = asyncio.ensure_future(run(page_data))
    loop.run_until_complete(future)

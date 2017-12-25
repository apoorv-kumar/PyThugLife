from bs4 import BeautifulSoup
import asyncio
from aiohttp import ClientSession
import pandas as pd

import time
time.sleep(20)


def parse_and_get(data):
    soup = BeautifulSoup(data, 'html.parser')
    tabs = soup.find_all('table')
    names = [ sp.text for sp in tabs[2].find_all('span', attrs={'class': 'comment-name'})]
    dates = [ sp.text for sp in tabs[2].find_all('span', attrs={'class': 'comment-date'})]
    comments = [ sp.text for sp in tabs[2].find_all('div', attrs={'class': 'comment-text'})]
    final_data = zip(names, dates, comments)
    return pd.DataFrame(list(final_data))


async def get_and_store(page_no, session) -> pd.DataFrame:
    url = 'http://trace.bharatiyamobile.com/showallsuggestions.php?id=tracemobile&page={}'.format(page_no)
    async with session.get(url) as response:
        data = await response.read()
        return parse_and_get(data)

async def run(r):
    tasks = []

    async with ClientSession() as session:
        for i in range(1,r+1):
            task = asyncio.ensure_future(get_and_store(i, session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        df = pd.concat(responses)
        df.to_csv('/home/apoorv/Downloads/1.csv')

loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(191))
loop.run_until_complete(future)

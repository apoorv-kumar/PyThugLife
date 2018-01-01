from string import ascii_lowercase
import json
import numpy as np
import pandas as pd
from aiohttp import ClientSession
from collections import deque
import asyncio
import time
import random
start = time.time()
incomplete_queue = deque(['ace'])
next_queue = deque()
reqests_sem = asyncio.BoundedSemaphore(5)
no_success = deque()
no_200_queue = deque()
failed_queue = deque()
def output(name):
    processed = []
    while True:
        data = yield
        processed.append(data)
        if len(processed) > 1000:
            print(
                "checkpoint " +
                name + "... sleeping.\n" +
                "remaining: " + str(len(incomplete_queue)) +
                "\nnew queue: " + str(len(next_queue))
            )
            processed = []
            time.sleep(60)

out_gen = output("success")
fail_gen = output("fail")
no_result = output('noresult')
next(out_gen)
next(fail_gen)
next(no_result)

async def get_entries(prefix, session: ClientSession):
    url = "http://www.mca.gov.in/mcafoportal/cinLookup.do"
    payload = "companyname={}".format(prefix)
    moz = int(random.random())%10
    rv = int(random.random())%58
    headers = {
        'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        'Referer': 'http://www.mca.gov.in/mcafoportal/viewCompanyMasterData.do',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/{}.0 (X11; Ubuntu_{}; Linux x86_64; rv:{}.0) Gecko/20100101 Firefox/{}.0'.format(moz, rv, prefix, rv)
    }
    async with reqests_sem:
        reqests_sem.acquire()
        try:
            async with session.post(url, headers=headers, data=payload) as response:
                status = response.status
                if status == 200:
                    raw_con = await response.read()
                    try:
                        jcontent = json.loads(raw_con)
                        if jcontent['success'] == 'true':
                            content = jcontent['companyList']
                            if len(content) >= 200:
                                next_queue.append(prefix)
                            else:
                                out_gen.send(0)
                                return content
                        else:
                            no_success.append(prefix)
                            no_result.send(0)
                    except:
                        print("failed " + prefix)
                        failed_queue.append((prefix, raw_con))
                else:
                    no_200_queue.append(prefix)
            return []
        except Exception as e:
            fail_gen.send(0)
            incomplete_queue.append(prefix)
            return []



def combine_and_write(valid_data, n):
    all_valid_data = np.concatenate(valid_data)
    df = pd.DataFrame.from_records(all_valid_data)
    df.to_csv('/home/apoorv/Downloads/mca/data{}.csv'.format(n))
    with open('/home/apoorv/Downloads/mca/no_success{}'.format(n), 'w') as f:
        f.write(str(no_success))

    with open('/home/apoorv/Downloads/mca/no_200_{}'.format(n), 'w') as f:
        f.write(str(no_200_queue))

    with open('/home/apoorv/Downloads/mca/fail{}'.format(n), 'w') as f:
        f.write(str(failed_queue))

async def query_all():
    itern = 0
    while len(incomplete_queue) > 0 or len(next_queue) > 0:
        itern += 1
        todo_next = [rem + c for rem in next_queue for c in ascii_lowercase]
        todo = list(incomplete_queue) + todo_next
        incomplete_queue.clear()
        next_queue.clear()
        print("###\niter {} - currently queued: {}\n###\n".format(itern, len(todo)))
        q_futures = []
        async with ClientSession() as session:
            for t in todo:
                q_futures.append(asyncio.ensure_future(get_entries(t, session)))
            data = await asyncio.gather(*q_futures)
            combine_and_write(data, itern)


loop = asyncio.get_event_loop()
fut = asyncio.ensure_future(query_all())
loop.run_until_complete(fut)
end = time.time()

print("total took : " + str(end - start) + " seconds")



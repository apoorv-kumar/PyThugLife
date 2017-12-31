from string import ascii_lowercase
import json
import numpy as np
import pandas as pd
from aiohttp import ClientSession
from collections import deque
import asyncio
import time
start = time.time()
incomplete_queue = deque()
with open('/home/apoorv/Downloads/mca/old/todo_files.json') as fw:
    remaining_prefixes = fw.read()
    incomplete_queue = deque(json.loads(remaining_prefixes))

reqests_sem = asyncio.BoundedSemaphore(1)
no_success = deque()
no_200_queue = deque()
failed_queue = deque()
http_fail = deque()
def output(name):
    processed = []
    while True:
        data = yield
        processed.append(data)
        if len(processed) > 1000:
            print("checkpoint " + name + "... sleeping.\n" + "remaining: " + str(len(incomplete_queue)))
            processed = []
            time.sleep(30)

out_gen = output("success")
fail_gen = output("fail")
next(out_gen)
next(fail_gen)

async def get_entries(prefix, session: ClientSession):
    url = "http://www.mca.gov.in/mcafoportal/cinLookup.do"
    payload = "companyname={}".format(prefix)
    headers = {
        'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        'Referer': 'http://www.mca.gov.in/mcafoportal/viewCompanyMasterData.do',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'
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
                                incomplete_queue.append(prefix)
                            else:
                                out_gen.send(0)
                                time.sleep(1)
                                return content
                        else:
                            no_success.append(prefix)
                    except:
                        print("failed " + prefix)
                        failed_queue.append((prefix, raw_con))
                else:
                    no_200_queue.append(prefix)
            return []
        except Exception as e:
            fail_gen.send(0)
            incomplete_queue.append(prefix)
            http_fail.append(prefix)



def combine_and_write(valid_data):
    all_valid_data = np.concatenate(valid_data)
    df = pd.DataFrame.from_records(all_valid_data)
    df.to_csv('/home/apoorv/Downloads/mca/data1.csv')

async def query_all():
    itern = 0
    while len(incomplete_queue) > 0:
        itern += 1
        todo = [rem + c for rem in incomplete_queue for c in ascii_lowercase]
        incomplete_queue.clear()
        print("###\niter {} - currently queued: {}\n###\n".format(itern, len(todo)))
        q_futures = []
        async with ClientSession() as session:
            for t in todo:
                q_futures.append(asyncio.ensure_future(get_entries(t, session)))
            data = await asyncio.gather(*q_futures)
            combine_and_write(data)


loop = asyncio.get_event_loop()
fut = asyncio.ensure_future(query_all())
loop.run_until_complete(fut)
end = time.time()

print("total took : " + str(end - start) + " seconds")

with open('/home/apoorv/Downloads/mca/no_success', 'w') as f:
    f.write(str(no_success))

with open('/home/apoorv/Downloads/mca/no_200', 'w') as f:
    f.write(str(no_200_queue))

with open('/home/apoorv/Downloads/mca/fail', 'w') as f:
    f.write(str(failed_queue))

with open('/home/apoorv/Downloads/mca/http_fail', 'w') as f:
    f.write(str(http_fail))
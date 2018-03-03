import re
import requests
from bs4 import BeautifulSoup as bs
import pprint

no_of_states = 35

states = {      
    35: "ANDAMAN & NICOBAR ISLANDS",
    28: "ANDHRA PRADESH",
    12: "ARUNACHAL PRADESH",
    18: "ASSAM",
    10: "BIHAR",
    4: "CHANDIGARH",
    22: "CHHATTISGARH",
    26: "DADRA & NAGAR HAVELI",
    25: "DAMAN AND DIU",
    30: "GOA",
    24: "GUJARAT",
    6: "HARYANA",
    2: "HIMACHAL PRADESH",
    1: "JAMMU & KASHMIR",
    20: "JHARKHAND",
    29: "KARNATAKA",
    32: "KERALA",
    31: "LAKSHADWEEP",
    23: "MADHYA PRADESH",
    27: "MAHARASHTRA",
    14: "MANIPUR",
    17: "MEGHALAYA",
    15: "MIZORAM",
    13: "NAGALAND",
    7: "NCT OF DELHI",
    21: "ODISHA",
    34: "PUDUCHERRY",
    3: "PUNJAB",
    8: "RAJASTHAN",
    11: "SIKKIM",
    33: "TAMILNADU",
    36: "TELANGANA",
    16: "TRIPURA",
    9: "UTTAR PRADESH",
    5: "UTTARAKHAND",
    19: "WEST BENGAL"
}

result = {
    10: 100289,
    11: 11,
    12: 164,
    13: 168,
    14: 1370,
    15: 18,
    16: 1814,
    17: 1274,
    18: 11393,
    19: 119122,
    20: 16385,
    21: 12367,
    22: 16362,
    23: 13386,
    24: 10421,
    27: 22285,
    28: 1413,
    29: 18638,
    30: 5,
    31: 7,
    32: 1135,
    33: 23751,
    34: 13,
    35: 70
}


def get_num_pages(html):
    page = bs(html, 'html.parser')
    links = page.findAll('a')
    pattern='pageno=([0-9]+)'
    p = re.compile(pattern)
    links_nos = [int(p.findall(link['href'])[0]) for link in links if p.findall(link['href'])]
    return max(links_nos, default=0)


url = 'https://indane.co.in/ujjwalabeneficiary.php?state_search={}'


def get_results():
    return {i: get_num_pages(requests.get(url.format(i)).content) for i in range(0, no_of_states+1)}


if not result:
    result = get_results()

pprint.pprint({state: result.get(i, 0) for i, state in states.items()}, indent=4)
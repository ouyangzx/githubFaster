import json
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import cpu_count

from bs4 import BeautifulSoup
from pip._vendor import requests


def parse_url(host):
    url = get_domain(host)

    # print(host, url)

    html_doc = requests.get(url).text

    bs = BeautifulSoup(html_doc, 'html.parser')
    scripts = bs.find_all('script', {'type': 'application/ld+json'})
    for script in scripts:

        json_loads = json.loads(script.string)

        if "mainEntity" in json_loads:
            # print(json_loads)

            main_entity_ = json_loads["mainEntity"]
            # print(main_entity_)

            for i in main_entity_:
                if str(i["name"]).__contains__("What IP address"):

                    text_ = i["acceptedAnswer"]["text"]
                    # print(text_)

                    bs = BeautifulSoup(text_, 'html.parser')
                    find = bs.find("a")

                    if find:
                        ip = find.text
                        # print(ip)
                        return f"{ip} {host}"
                    else:
                        print(host, json_loads)


def get_domain(host: str):
    flag = '.'
    r_index = host.rindex(flag)
    re0 = host[r_index + 1: len(host)]

    left = host[0: r_index]

    if left.__contains__(flag):
        re = left[left.rindex(flag) + 1: len(left)]
        return f"https://{re + flag + re0}.ipaddress.com/{host}"
    else:
        return f"https://{host}.ipaddress.com"


def find(host_list: list):
    records = []

    with ThreadPoolExecutor(max_workers=cpu_count() + 1) as pool:
        task_list = []

        for host in host_list:
            obj = pool.submit(parse_url, host.strip().replace("\n", ""))
            task_list.append(obj)

        for task in as_completed(task_list):
            print(task.result())
            records.append(task.result())


with open(r"hosts.txt") as f:
    hosts = f.readlines()

    find(hosts)
    print()

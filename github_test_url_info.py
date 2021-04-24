import requests
from bs4 import BeautifulSoup
import csv
import time
import re

start_urls = [
    'https://github.com/explosion/spaCy',
    'https://github.com/yunjey/pytorch-tutorial',
    'https://github.com/floodsung/Deep-Learning-Papers-Reading-Roadmap'
] # save urls

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    'Accept-Encoding': "gzip, deflate, br",
    'Cache-Control': 'max-age=0',
    'Connection': "keep-alive"
}

timeoutSec = 5 # setup your timeout spec(sec)

base_url = "https://github.com/topics/deep-learning?page="
allowed_domains = "https://github.com"

# for i in range(1, 2):
#     try:
#         html = requests.get(base_url+str(i), headers=headers, proxies=proxies, timeout= timeoutSec)
#     except Exception as e:
#         print(e)
#         print('fail to get request from ip via proxy')
    
#     soup = BeautifulSoup(html.text, "html.parser")
#     # print(soup.prettify())
#     # urls = soup.find_all("a", {'class': 'text-bold'})

#     for j in soup.find_all("a", {'class': 'text-bold'}):
#         start_urls.append(allowed_domains + j['href'])

    # print(urls)

print(start_urls)
print("The data length: ", len(start_urls), "\n")

result = []
labels = ['name', 'star', 'commits', 'fork', 'issues', 'pull_requests',
          'branches', 'tags']

for url in start_urls:
    try:
        html = requests.get(url, headers=headers, proxies=proxies, timeout= timeoutSec)
    except Exception as e:
        print(e)
        print('fail to get request from ip via proxy')
    # print(html)
    soup = BeautifulSoup(html.text, "html.parser")
    # star = soup.findall("a", text="starred")
    # print(soup.prettify())
    item = {}
    item['name'] = url
    print("start: ", item['name'], "\n")
    num = soup.find_all("a", {'class': 'social-count'})
    print(num)
    print('\n')
    item['star'] = num[0]
    item['fork'] = num[1]

    num = soup.find_all("span", {'class': 'd-none d-sm-inline'})
    # print('\n')
    # print(num)
    if(len(num) == 2):
        item['commits'] = num[1]
    else:
        item['commits'] = num[0]

    num = soup.find_all("span", {'class': 'Counter'})
    # print('\n')
    # print(num)

    item['issues'] = num[1]
    item['pull_requests'] = num[2]
    # item['contributors'] = num[7]
    # item['projects'] = num[4]
    # item['security'] = num[5]

    num = soup.find_all("a", {'class': 'Link--primary no-underline'})
    # print('\n')
    # print(num)
    item['branches'] = num[0]
    # item['release'] = num[1]
    # item['used_by'] = num[3]

    # num = soup.find_all("span", {'class': 'Counter'})
    # item['contributors'] = num[4]

    num = soup.find_all("a", {'class': 'ml-3 Link--primary no-underline'})
    # print('\n')
    # print(num)
    item['tags'] = num[0]

    print("end", item['name'], "\n")
    print("\n", item['commits'])
    result.append(item)
    # time.sleep(1.5)


# print(result)

# try:
#     with open('csv_dct.csv', 'w') as f:
#         writer = csv.DictWriter(f, fieldnames=labels)
#         writer.writeheader()
#         for elem in result:
#             writer.writerow(elem)
# except IOError:
#     print("I/O error")

import requests
import time
import csv
import json
from bs4 import BeautifulSoup

# request settings

token = ''

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'token {token}'.format(token = token)
}

headers_raw_page = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Authorization': 'token {token}'.format(token = token)
}

timeoutSec = 15  # setup your timeout spec(sec)


class github_grab(object):
    def __init__(self):
        self.repositories = []
        self.basic_table = []
        self.commits_table = []
        self.pull_requests_table = []
        self.forks_table = []
        self.issues_table = []
        self.base_url = [
            "https://api.github.com/search/repositories?q=language:python&sort=stars",
            "https://api.github.com/search/repositories?q=language:java&sort=stars",
            "https://api.github.com/search/repositories?q=language:c&sort=stars",
            "https://api.github.com/search/repositories?q=language:golang&sort=stars",
            "https://api.github.com/search/repositories?q=language:js&sort=stars"
        ]
        self.basic_labels = [
            'name', 'language', 'stargazers' , 'forks', 'open_issues', 'watchers', 'readme'
        ]
        # commits pull_requests forks issues_events
        self.template_labels = [
            'name',
            '2019_01', '2019_02', '2019_03', '2019_04',
            '2019_05', '2019_06', '2019_07', '2019_08',
            '2019_09', '2019_10', '2019_11', '2019_12',
            '2020_01', '2020_02', '2020_03', '2020_04',
            '2020_05', '2020_06', '2020_07', '2020_08',
            '2020_09', '2020_10', '2020_11', '2020_12',
            '2021_01', '2021_02', '2021_03'
        ]

        self.template_table = {
            'name': '',
            '2020_03': 0, '2020_04': 0, '2020_05': 0, '2020_06': 0,
            '2020_07': 0, '2020_08': 0, '2020_09': 0, '2020_10': 0,
            '2020_11': 0, '2020_12': 0, '2021_01': 0, '2021_02': 0,
            '2021_03': 0
        }

    def get_all_repositories(self):
        print("\n------------start grabbing all repositories--------------------------\n")
        index = 1
        for url in self.base_url:
            print("\nbase url : " + url + "\n")
            for i in range(1, 5):
                try:
                    req = requests.get(url + "&page=" + str(i) + "&per_page=100",
                                       headers=headers, proxies=proxies, timeout=timeoutSec)
                    if(req.status_code == 403):
                        print("Rate limit, sleep 60 sec")
                        time.sleep(60)
                        i -= 1
                        continue
                    elif(req.status_code == 404 or req.status_code == 204):
                        print('The source is not found')
                        continue
                    items = req.json()['items']
                    # temp = json.loads(req)
                    # print(type(req))
                    print("req len " + str(len(items)))
                    self.repositories += items
                    print('grab page ' + str(index) +
                          ', current repository quantity : ' + str(len(self.repositories)))
                    index += 1

                    # print(self.repositories)
                except Exception as e:
                    print(e)
                    print('fail to get request from ip via proxy')

                # sleep
                # time.sleep(2)

    def deal_with_repositories(self):
        print("-------------------start to deal with repo\'s data----------------------\n")
        i = 1
        for repo in self.repositories:
            print('deal with the ' + str(i) + ' / ' +
                  str(len(self.repositories)) + " " + repo['full_name'])
            i += 1
            # basic_table
            basic_temp = {}
            basic_temp['name'] = repo['full_name']
            basic_temp['stargazers'] = repo['stargazers_count']
            basic_temp['watchers'] = repo['watchers_count']
            basic_temp['language'] = repo['language']
            basic_temp['forks'] = repo['forks_count']
            basic_temp['open_issues'] = repo['open_issues']
            basic_temp['readme'] = self.get_repository_readme(
                repo['full_name'])
            self.basic_table.append(basic_temp)
            # commits_table
            #  init use copy
            temp = self.template_table.copy()
            # print('init temp')
            # print(temp)
            temp['name'] = repo['full_name']
            temp = self.get_repository_commits(temp)
            # print(temp)
            self.commits_table.append(temp)
            # print("-----")
            # print(self.commits_table)
            # print("----")

            # pull request
            temp = self.template_table.copy()
            temp['name'] = repo['full_name']
            temp = self.get_repository_pull_requests(temp)
            self.pull_requests_table.append(temp)

            # # forks
            # temp = self.template_table.copy()
            # temp['name'] = repo['full_name']
            # temp = self.get_repository_forks(temp)
            # self.forks_table.append(temp)

            # # issues_events
            # temp = self.template_table.copy()
            # temp['name'] = repo['full_name']
            # temp = self.get_repository_issues(temp)
            # self.issues_table.append(temp)

            print("")

    def date_classify(self, temp, date_time):
        # print(date_time)
        if("2021-03-01T00:00:00Z" <= date_time and date_time < "2021-04-01T00:00:00Z"):
            temp['2021_03'] += 1
        elif("2021-02-01T00:00:00Z" <= date_time and date_time < "2021-03-01T00:00:00Z"):
            temp['2021_02'] += 1
        elif("2021-01-01T00:00:00Z" <= date_time and date_time < "2021-02-01T00:00:00Z"):
            temp['2021_01'] += 1
        elif("2020-12-01T00:00:00Z" <= date_time and date_time < "2021-01-01T00:00:00Z"):
            temp['2020_12'] += 1
        elif("2020-11-01T00:00:00Z" <= date_time and date_time < "2020-12-01T00:00:00Z"):
            temp['2020_11'] += 1
        elif("2020-10-01T00:00:00Z" <= date_time and date_time < "2020-11-01T00:00:00Z"):
            temp['2020_10'] += 1
        elif("2020-09-01T00:00:00Z" <= date_time and date_time < "2020-10-01T00:00:00Z"):
            temp['2020_09'] += 1
        elif("2020-08-01T00:00:00Z" <= date_time and date_time < "2020-09-01T00:00:00Z"):
            temp['2020_08'] += 1
        elif("2020-07-01T00:00:00Z" <= date_time and date_time < "2020-08-01T00:00:00Z"):
            temp['2020_07'] += 1
        elif("2020-06-01T00:00:00Z" <= date_time and date_time < "2020-07-01T00:00:00Z"):
            temp['2020_06'] += 1
        elif("2020-05-01T00:00:00Z" <= date_time and date_time < "2020-06-01T00:00:00Z"):
            temp['2020_05'] += 1
        elif("2020-04-01T00:00:00Z" <= date_time and date_time < "2020-05-01T00:00:00Z"):
            temp['2020_04'] += 1
        elif("2020-03-01T00:00:00Z" <= date_time and date_time < "2020-04-01T00:00:00Z"):
            temp['2020_03'] += 1

        return temp

    def get_repository_commits(self, commits_temp):
        print("start to get " + commits_temp['name'] + " commits\' data")
        try:
            for i in range(1, 100000):
                req = requests.get("https://api.github.com/repos/" + commits_temp['name'] + "/commits?per_page=100&page=" + str(i),
                                   headers=headers, proxies=proxies, timeout=timeoutSec)
                if(req.status_code == 403):
                    print("Rate limit, sleep 60 sec")
                    time.sleep(60)
                    i -= 1
                    continue
                elif(req.status_code == 404 or req.status_code == 204):
                    print('The source is not found')
                    continue
                # print("commits times" + str(i))
                items = req.json()
                # if no data
                if len(items) == 0:
                    break
                # if the time is too older
                if(items[0]['commit']['author']['date'] < "2020-03-01T00:00:00Z"):
                    break
                if(items[-1]['commit']['author']['date'] > "2021-04-01T00:00:00Z"):
                    continue
                for date_time in items:
                    if(date_time['commit']['author']['date'] < "2020-03-01T00:00:00Z"):
                        break
                    commits_temp = self.date_classify(
                        commits_temp, date_time['commit']['author']['date'])
                # time.sleep(2)
            return commits_temp
        except Exception as e:
            print(e)
            print('fail to get request from ip via proxy')

    def get_repository_pull_requests(self, pr_temp):
        print("start to get " + pr_temp['name'] + " pull requests\' data")
        try:
            for i in range(1, 100000):
                req = requests.get("https://api.github.com/repos/" + pr_temp['name'] + "/pulls?per_page=100&page=" + str(i),
                                   headers=headers, proxies=proxies, timeout=timeoutSec)
                if(req.status_code == 403):
                    print("Rate limit, sleep 60 sec")
                    time.sleep(60)
                    i -= 1
                    continue
                elif(req.status_code == 404 or req.status_code == 204):
                    print('The source is not found')
                    continue
                items = req.json()
                # if no data
                if len(items) == 0:
                    break
                # if the time is too older
                if(items[0]['created_at'] < "2020-03-01T00:00:00Z"):
                    break
                if(items[-1]['created_at'] > "2021-04-01T00:00:00Z"):
                    continue
                for date_time in items:
                    # print(date_time['created_at'])
                    if(date_time['created_at'] < "2020-03-01T00:00:00Z"):
                        break
                    pr_temp = self.date_classify(
                        pr_temp, date_time['created_at'])
                # time.sleep(2)
            return pr_temp
        except Exception as e:
            print(e)
            print('fail to get request from ip via proxy')

    def get_repository_forks(self, forks_temp):
        print("start to get " + forks_temp['name'] + " forks\' data")
        try:
            for i in range(1, 100000):
                req = requests.get("https://api.github.com/repos/" + forks_temp['name'] + "/forks?per_page=100&page=" + str(i),
                                   headers=headers, proxies=proxies, timeout=timeoutSec)
                if(req.status_code == 403):
                    print("Rate limit, sleep 60 sec")
                    time.sleep(60)
                    i -= 1
                    continue
                elif(req.status_code == 404 or req.status_code == 204):
                    print('The source is not found')
                    continue
                items = req.json()
                # print("forks times" + str(i))
                # if no data
                if len(items) == 0:
                    break
                # if the time is too older
                if(items[0]['created_at'] < "2020-03-01T00:00:00Z"):
                    break
                if(items[-1]['created_at'] > "2021-04-01T00:00:00Z"):
                    continue
                for date_time in items:
                    # print(date_time['created_at'])
                    if(date_time['created_at'] < "2020-03-01T00:00:00Z"):
                        break
                    forks_temp = self.date_classify(
                        forks_temp, date_time['created_at'])
                # time.sleep(2)
            return forks_temp
        except Exception as e:
            print(e)
            print('fail to get request from ip via proxy')

    def get_repository_issues(self, issues_temp):
        print("start to get " + issues_temp['name'] + " issues\' data")
        try:
            for i in range(1, 100000):
                req = requests.get("https://api.github.com/repos/" + issues_temp['name'] + "/issues/events?per_page=100&page=" + str(i),
                                   headers=headers, proxies=proxies, timeout=timeoutSec)
                if(req.status_code == 403):
                    print("Rate limit, sleep 60 sec")
                    time.sleep(60)
                    i -= 1
                    continue
                elif(req.status_code == 404 or req.status_code == 204):
                    print('The source is not found')
                    continue
                items = req.json()
                # if no data
                if len(items) == 0:
                    break
                # if the time is too older
                if(items[0]['created_at'] < "2020-03-01T00:00:00Z"):
                    break
                if(items[-1]['created_at'] > "2021-04-01T00:00:00Z"):
                    continue
                for date_time in items:
                    # print(date_time['created_at'])
                    if(date_time['created_at'] < "2020-03-01T00:00:00Z"):
                        break
                    issues_temp = self.date_classify(
                        issues_temp, date_time['created_at'])
                # time.sleep(2)
            return issues_temp
        except Exception as e:
            print(e)
            print('fail to get request from ip via proxy')

    def get_repository_readme(self, url):
        print("start to get " + url + " readme")
        try:
            req = requests.get("https://github.com/" + url + "/blob/master/README.md",
                               headers=headers_raw_page, proxies=proxies, timeout=timeoutSec)
            if(req.status_code == 403):
                print("Rate limit, sleep 60 sec")
                time.sleep(60)
                req = requests.get("https://github.com/" + url + "/blob/master/README.md",
                               headers=headers_raw_page, proxies=proxies, timeout=timeoutSec)
            elif(req.status_code == 404 or req.status_code == 204):
                print('The source is not found')
            # print(type(req))
            soup = BeautifulSoup(req.text.replace('\n', ''), "html.parser")
            num = soup.find_all("div", {'id': 'readme'})
            # print(req)
            # print("req len " + str(len(req)))
            # time.sleep(2)
            return num[0] if len(num) >= 1 else ""

        except Exception as e:
            print(e)
            print('fail to get request from ip via proxy')

    def save_all_to_csv(self):
        self.save_as_csv("github_basic.csv", self.basic_labels, self.basic_table)
        self.save_as_csv("github_commits.csv", self.template_labels, self.commits_table)
        self.save_as_csv("github_pull_requests.csv", self.template_labels, self.pull_requests_table)
        # self.save_as_csv("github_forks.csv", self.template_labels, self.forks_table)
        # self.save_as_csv("github_issues.csv", self.template_labels, self.issues_table)


    def save_as_csv(self, fileName, labels, table):
        print("\n------------start saving data as csv--------------------------\n")

        # save csv
        try:
            with open(fileName, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=labels)
                writer.writeheader()
                for elem in table:
                    writer.writerow(elem)
                print("save " + fileName + " success")
        except IOError:
            print("I/O error")

if __name__ == "__main__":
    github = github_grab()
    github.get_all_repositories()
    print("repo len " + str(len(github.repositories)))
    github.deal_with_repositories()
    # print(github.basic_table)
    # print(github.commits_table)
    # print(github.pull_requests_table)
    # print(github.forks_table)
    # print(github.issues_table)
    github.save_all_to_csv()

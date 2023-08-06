from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse
import datetime

class BaiduNewsSearch:
    def __init__(self,
                 webdriver_path="browsers/chromedriver.exe",
                 ):

        # -------------设置参数-----------------
        self.webdriver_path = webdriver_path
        # -------------结束设置参数-----------------

        pass

    def get_rea_url_from_baidu(self,baidu_url):
        try:
            r = requests.get(baidu_url)
            if r.url != baidu_url:
                return r.url
            obj = BeautifulSoup(r.text, features='lxml')
            meta = obj.find("noscript").find("meta")
            real_url = meta["content"].split(";")[1].split("'")[1]
            return real_url
        except:
            return ""

    def get_search_page_model(self,baidu_search_url):

        self.driver.get(baidu_search_url)
        time.sleep(1)
        body = self.driver.find_element_by_tag_name("body")

        # print(body.get_attribute("outerHTML"))

        html_obj = BeautifulSoup(body.get_attribute("outerHTML"), features='lxml')
        result_list = html_obj.findAll("div",{"class":"result-op c-container xpath-log new-pmd"})
        # h3s = html_obj.findAll("h3")

        list_model = []
        for result in result_list:
            h3=result.find("div").find("h3")
            news_time=""

            if h3.find("a")==None:
                continue
            title = h3.find("a").text.strip()
            baidu_url = h3.find("a")["href"]
            print(title)
            print("Baidu url: ", baidu_url)

            try:

                # driver.get(baidu_url)
                # time.sleep(3)
                # real_url = driver.current_url
                real_url = baidu_url

            except:
                print("error in ", baidu_url)
                real_url = ""

            try:
                news_time = result.find("div").find("div").find("div",{"class":"c-span-last"}).find("span").text

                today = datetime.datetime.today()
                year = today.year
                month = today.month

                if '年' in news_time and '月' in news_time and '日' in news_time:
                    news_time=news_time.replace("年","-").replace("月","-").replace("日","").strip()
                if ('年' not in news_time) and '月' in news_time and '日' in news_time:
                    news_time = str(year) +"-"+ news_time.replace("月", "-").replace("日", "").strip()
                if '天前' in news_time:
                    day=news_time.replace('天前','').strip()
                    new_today=today+datetime.timedelta(days=-int(day))
                    news_time=new_today.strftime("%Y-%m-%d")
                if '小时前' in news_time or '分钟前' in news_time or '刚刚' in news_time:
                    news_time = today.strftime("%Y-%m-%d")
                if '昨天' in news_time:
                    new_today=today+datetime.timedelta(days=-1)
                    news_time=new_today.strftime("%Y-%m-%d")
                if '今天' in news_time:
                    news_time=today.strftime("%Y-%m-%d")

            except:
                news_time=""
                print("error in extracting news_time...")

            print("Real Url: ", real_url)
            print("News time: ",news_time)
            # real_url=get_rea_url_from_baidu(baidu_url)
            print()
            # print(h3.find("a").text, h3.find("a")["href"], real_url)
            model = {
                "title": title,
                "baidu_url": baidu_url,
                "real_url": real_url,
                "news_time":news_time
            }
            list_model.append(model)
        return list_model

    def fetch(self,raw_keywords,
                implicitly_wait=0.5,
                seconds_wait=10,
                func_process=None,
                silent=False,
                max_pages=100,
                save_path="",
                sleep_seconds_before_going_to_next_page=3,min_pages=0,retry_max_num=10,use_medium=False):
        keywords = urllib.parse.quote(raw_keywords)
        if silent:
            options = webdriver.ChromeOptions()
            options.add_argument("--log-level=3")
            options.headless = True
            self.driver = webdriver.Chrome(executable_path=self.webdriver_path,
                                      chrome_options=options
                                      )
        else:
            self.driver = webdriver.Chrome(executable_path=self.webdriver_path)

        self.driver.implicitly_wait(implicitly_wait)

        # 首次打开，可能需要手动验证相关，验证后，等待10s再自动获取搜索结果列表
        if use_medium:
            url = f"https://www.baidu.com/s?medium=1&tn=news&word={keywords}"
        else:
            url=f"https://www.baidu.com/s?tn=news&word={keywords}"
        self.driver.get(url)

        # body = self.driver.find_element_by_tag_name("body")

        # print(body.text)
        # print(body.get_attribute("outerHTML"))
        # print()
        print("Waiting...")
        print("若百度页面弹出验证页面，请手动通过验证，在10秒内完成！一般来说，验证一次后面就无须验证！")
        time.sleep(seconds_wait)

        # print("current url: ",driver.current_url)

        print("Start to fetch list  ...")

        field_names = ["title", "baidu_url", "real_url","news_time"]
        encoding = 'utf-8'
        if save_path!="":
            with open(save_path, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writeheader()
                pi=min_pages
                max_try=retry_max_num
                while pi<=max_pages:
                    if max_try<retry_max_num:
                        print(f"\tRetrying #{retry_max_num - max_try}...")
                    else:
                        print("Page ", pi + 1)
                    if use_medium:
                        baidu_search_url = f"https://www.baidu.com/s?ie=utf-8&medium=1&rtt=1&bsst=1&rsv_dl=news_t_sk&cl=2&wd={keywords}&tn=news&rsv_bp=1&tfflag=0&pn={10 * pi}"
                    else:
                        baidu_search_url = f"https://www.baidu.com/s?tn=news&word={keywords}&pn={10 * pi}"
                    print(baidu_search_url)
                    list_model = self.get_search_page_model(baidu_search_url)
                    if func_process != None:
                        func_process(list_model)
                    writer.writerows(list_model)
                    csvfile.flush()

                    if len(list_model)!=0 or max_try<=0:
                        time.sleep(sleep_seconds_before_going_to_next_page)
                        pi+=1
                        max_try=retry_max_num
                        print()
                    else:
                        waiting=8
                        if retry_max_num-max_try<8:
                            waiting=sleep_seconds_before_going_to_next_page*(retry_max_num-max_try+1)
                        else:
                            waiting=60*5
                        time.sleep(waiting)
                        print(f"\tWaiting: {waiting} seconds...")
                        max_try-=1
                print()
        else:
            pi = min_pages
            max_try = retry_max_num
            while pi <= max_pages:
                if max_try < retry_max_num:
                    print(f"Retrying #{retry_max_num - max_try}...")
                else:
                    print("Page ", pi + 1)
                baidu_search_url = f"https://www.baidu.com/s?tn=news&word={keywords}&pn={10 * pi}"
                list_model = self.get_search_page_model(baidu_search_url)
                if func_process != None:
                    func_process(list_model)
                time.sleep(sleep_seconds_before_going_to_next_page)
                if len(list_model) != 0 or max_try <= 0:
                    pi += 1
                    max_try = retry_max_num
                    print()
                else:
                    max_try -= 1
            print()


        self.driver.close()

class BaiduWebSearch:
    def __init__(self,
                 webdriver_path="browsers/chromedriver.exe",

                 ):

        # -------------设置参数-----------------

        self.webdriver_path = webdriver_path

        # -------------结束设置参数-----------------



        pass

    def get_rea_url_from_baidu(self, baidu_url):
        try:
            r = requests.get(baidu_url)
            if r.url != baidu_url:
                return r.url
            obj = BeautifulSoup(r.text, features='lxml')
            meta = obj.find("noscript").find("meta")
            real_url = meta["content"].split(";")[1].split("'")[1]
            return real_url
        except:
            return ""

    def get_search_page_model(self, baidu_search_url, sleep_seconds_after_visit_page=3):

        self.driver.get(baidu_search_url)
        time.sleep(1)
        body = self.driver.find_element_by_tag_name("body")

        # print(body.get_attribute("outerHTML"))

        html_obj = BeautifulSoup(body.get_attribute("outerHTML"), features='lxml')

        h3s = html_obj.findAll("h3", {"class": "t"})
        list_model = []
        for h3 in h3s:
            title = h3.find("a").text
            baidu_url = h3.find("a")["href"]
            print(title)
            print("Baidu url: ", baidu_url)
            try:
                self.driver.get(baidu_url)
                time.sleep(sleep_seconds_after_visit_page)
                real_url = self.driver.current_url
                # real_url = baidu_url
            except:
                print("error in ", baidu_url)
                real_url = ""
            print("Real Url: ", real_url)
            # real_url=get_rea_url_from_baidu(baidu_url)
            print()
            # print(h3.find("a").text, h3.find("a")["href"], real_url)
            model = {
                "title": title,
                "baidu_url": baidu_url,
                "real_url": real_url
            }
            list_model.append(model)
        return list_model

    def fetch(self, raw_keywords, implicitly_wait=0.5, seconds_wait=10, func_process=None,silent=False,
              max_pages=100,
              save_path="",
              sleep_seconds_before_going_to_next_page=5,
              sleep_seconds_after_visit_page=3
              ):
        keywords = urllib.parse.quote(raw_keywords)
        if silent:
            options = webdriver.ChromeOptions()
            options.add_argument("--log-level=3")
            options.headless = True
            self.driver = webdriver.Chrome(executable_path=self.webdriver_path,
                                           chrome_options=options
                                           )
        else:
            self.driver = webdriver.Chrome(executable_path=self.webdriver_path)


        self.driver.implicitly_wait(implicitly_wait)

        # 首次打开，可能需要手动验证相关，验证后，等待10s再自动获取搜索结果列表
        self.driver.get(f"https://www.baidu.com/s?t&wd={keywords}")

        body = self.driver.find_element_by_tag_name("body")

        # print(body.text)
        # print(body.get_attribute("outerHTML"))
        # print()
        print("Waiting...")
        print("若百度页面弹出验证页面，请手动通过验证，在10秒内完成！一般来说，验证一次后面就无须验证！")
        time.sleep(seconds_wait)

        # print("current url: ",driver.current_url)

        print("Start to fetch list  ...")

        field_names = ["title", "baidu_url", "real_url"]
        encoding = 'utf-8'
        if save_path!="":
            with open(save_path, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writeheader()
                for pi in range(0, max_pages):
                    print("Page ", pi + 1)
                    baidu_search_url = f"https://www.baidu.com/s?wd={keywords}&pn={10 * pi}"
                    list_model = self.get_search_page_model(baidu_search_url,sleep_seconds_after_visit_page)
                    if func_process != None:
                        func_process(list_model)
                    writer.writerows(list_model)
                    csvfile.flush()
                    time.sleep(sleep_seconds_before_going_to_next_page)
                print()
        else:
            for pi in range(0, max_pages):
                print("Page ", pi + 1)
                baidu_search_url = f"https://www.baidu.com/s?wd={keywords}&pn={10 * pi}"
                list_model = self.get_search_page_model(baidu_search_url)
                if func_process != None:
                    func_process(list_model)
                time.sleep(sleep_seconds_before_going_to_next_page)
            print()

        self.driver.close()


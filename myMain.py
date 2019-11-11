import requests

from bs4 import BeautifulSoup
import time,os,shutil,logging
from static_parameters import my_parameters
from getPage import get_page_info
import re
import json


# 获取cookie
BASIC_URL = 'https://kns.cnki.net/kns/brief/result.aspx'
# 利用post请求先行注册一次
SEARCH_HANDLE_URL = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
# 发送get请求获得文献列表
GET_PAGE_URL = 'http://kns.cnki.net/kns/brief/brief.aspx?pagename='
# 切换页面基础链接
CHANGE_PAGE_URL = 'http://kns.cnki.net/kns/brief/brief.aspx'

class SearchTool(object):
    def __init__(self):
        self.session = requests.Session()
        # 保持会话
        self.session.get(BASIC_URL, headers=my_parameters.headers_kns)
        self.cur_page = 1
        self.all_info = []
        self.dir_path = 'CNKI_Info/'
        self.start_page = int(input('请输入起始页码：'))
        self.end_page = int(input('请输入结束页码：'))

    def get_another_page(self):
        '''
        请求其他页面和请求第一个页面形式不同
        重新构造请求
        '''
        # time.sleep(config.crawl_stepWaitTime)
        time.sleep(0.1)
        # 搜索页面中切换页码的url，将其提取出来
        change_page_pattern_compile = re.compile(
            r'.*?pagerTitleCell.*?<a href="(.*?)".*')
        self.change_page_url = re.search(change_page_pattern_compile,
                                         self.second_get_result.text).group(1)
        # 将url中的括号进行转义  (:%28    ):%29
        self.change_page_url = re.sub(r'\(', '%28', self.change_page_url)
        self.change_page_url = re.sub(r'\)', '%29', self.change_page_url)
        #将原url中的页码替换成下一个页码，由CHANGE_PAGE_URL、替换部分、self.change_page_url三个部分组成
        curpage_pattern_compile = re.compile(r'.*?curpage=(\d+).*?')
        self.get_result_url = CHANGE_PAGE_URL + re.sub(
            curpage_pattern_compile, '?curpage=' + str(self.cur_page),
            self.change_page_url)

        #get_res = self.session.get(self.get_result_url, headers=my_parameters.headers)
        #self.parse_page(download_page_left, get_res.text)

    def search_reference(self):
        #首先创建存放数据的文件夹
        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path)
        '''
        第一次发送post请求
        再一次发送get请求,这次请求没有写文献等东西
        两次请求来获得文献列表
        '''
        first_post_res = self.session.post(SEARCH_HANDLE_URL, data=my_parameters.static_post_data, headers=my_parameters.headers_kns)
        self.get_result_url = GET_PAGE_URL + first_post_res.text + '&t=1544249384932&keyValue=' + '&S=1&sorttype=%28%e8%a2%ab%e5%bc%95%e9%a2%91%e6%ac%a1%2c%27INTEGER%27%29+desc'
        self.second_get_result = self.session.get(self.get_result_url, headers=my_parameters.headers_kns)
        time.sleep(0.1)
        #如果此文件未被保存过，则找到其内容保存下来
        if not os.path.exists(self.dir_path + 'Info' + str(self.cur_page) + '.txt'):
            #将第一页的所需内容加入列表
            dict_pre_page = get_page_info.get_Detail_Info(self.second_get_result.text,self.session)
            with open(self.dir_path + 'Info' + str(self.cur_page) + '.txt', 'w') as fp:
                json.dump(dict_pre_page, fp)
            print('第' + str(self.cur_page) + '页下载完毕！')
            # self.all_info.append(get_page_info.get_Detail_Info(self.second_get_result.text,self.session))


        for self.cur_page in range(self.start_page,self.end_page+1):
            time.sleep(0.1)
            # 如果此文件未被保存过，则找到其内容保存下来
            if not os.path.exists(self.dir_path + 'Info' + str(self.cur_page) + '.txt'):
                self.get_another_page()
                self.second_get_result = self.session.get(self.get_result_url, headers=my_parameters.headers_kns)
                dict_pre_page = get_page_info.get_Detail_Info(self.second_get_result.text, self.session)
                with open(self.dir_path + 'Info'+str(self.cur_page) + '.txt','w') as fp:
                    json.dump(dict_pre_page,fp)
                print('第' + str(self.cur_page) +'页下载完毕！')
                # self.all_info.append(dict_pre_page)

def main():
    s = SearchTool()
    s.search_reference()

if __name__ == '__main__':
    main()
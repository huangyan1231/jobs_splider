#!/usr/bin/env python
#coding:utf8
import requests
import time

class Scrapy(object):
    pages = 0

    def __init__(self, keyword):
        self.keyword = keyword

    '''fetch one info'''
    def fetch_one(self, page=0):
        url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E6%88%90%E9%83%BD&needAddtionalResult=false&isSchoolJob=0'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Referer': 'https://www.lagou.com/jobs/list_%E4%BC%9A%E8%AE%A1?labelWords=sug&fromSearch=true&suginput=%E4%BC%9A%E8%AE%A1'
        }
        params = {
            'first': False,
            'pn': str(page),
            'kd': self.keyword
        }
        time.sleep(2)
        return requests.post(url, data=params, headers=header).json()
    
    def spider(self):
        result = self.fetch_one(0)
        self.pages = result['content']['positionResult']['totalCount']
        self.parse(result['content']['positionResult']['result'])
        page_num = 0
        if self.pages % 15 == 0:
            page_num = self.pages // 15
        else:
            page_num = self.pages / 15 + 1
        for page in range(1, self.pages // 15):
            # print(self.pages, page)
            result = self.fetch_one(page+1)
            self.parse(result['content']['positionResult']['result'])
    def parse(self, jobs):
        # print(jobs)
        pass


if __name__ == '__main__':
    scrapy = Scrapy('会计')
    scrapy.spider()

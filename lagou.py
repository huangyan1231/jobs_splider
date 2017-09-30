#!/usr/bin/env python
#coding:utf8
import requests
import time
import random
from database.base_db import Session
from models.model import Company, Position
session = Session()
class Scrapy(object):
    pages = 0

    def __init__(self, keyword):
        self.keyword = keyword

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
 
        result = requests.post(url, data=params, headers=header).json()

        if result['success'] == False:
            print('抓取失败')
            print(result)
            time.sleep(120)
            return self.fetch_one(page)
        
        return result
    
    def spider(self):
        result = self.fetch_one(0)
        self.pages = result['content']['positionResult']['totalCount']
        page_num = int(self.pages / 15) + 1
        if self.pages % 15 == 0:
            page_num = self.pages // 15
        for page in range(1, page_num + 1):
            print(
                '关键字:{}, 共{}页, 正在抓取第{}页'.format(
                    self.keyword,
                    page_num,
                    page
                ),
                end=''
            )
            result = self.fetch_one(page)
            self.parse(result['content']['positionResult']['result'])
            time.sleep(random.random()+5)
        print('{}职位抓取完成.'.format(self.keyword))
    def parse(self, jobs):
        # session = Session()
        for job in jobs:
            cp = session.query(Company.id).filter_by(id=job['companyId']).first()
            ps = session.query(Position.id).filter_by(id=job['positionId']).first()
            # if position has been crawled
            if ps is None:
                position = Position(
                    id=job['positionId'],
                    company_id=job['companyId'],
                    position_name=job['positionName'],
                    work_year=job['workYear'],
                    education=job['education'],
                    job_nature=job['jobNature'],
                    create_time=job['createTime'],
                    city=job['city'],
                    industry_field=job['industryField'],
                    position_advantage=job['positionAdvantage'],
                    salary=job['salary'],
                    position_lables=job['positionLables'],
                    industry_lables=job['industryLables'],
                    district=job['district'],
                    first_type=job['firstType'],
                    second_type=job['secondType']
                )
                session.add(position)

            # if company has been crawled
            if cp is None:
                company = Company(
                    id=job['companyId'],
                    company_size=job['companySize'],
                    company_short_name=job['companyShortName'],
                    company_full_name=job['companyFullName'],
                    finance_stage=job['financeStage'],
                    company_label_list=job['companyLabelList']
                )
                session.add(company)

        session.commit()
        print(', 抓取成功')


if __name__ == '__main__':
    from models.model import Base, engine
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    pos_list = ['会计', '会计与审计', '审计', '行政']
    for pos in pos_list:
        scrapy = Scrapy(pos)
        scrapy.spider()
        time.sleep(random.random()+50)

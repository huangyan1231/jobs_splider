#!/usr/bin/env python
#coding:utf8
import requests
import time
import re
import random
from bs4 import BeautifulSoup
from database.base_db import Session
from models.model import Company, Position, Proxys
session = Session()
class Scrapy(object):
    pages = 0
    proxies = []
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Referer': 'https://www.lagou.com/jobs/list_%E4%BC%9A%E8%AE%A1?labelWords=sug&fromSearch=true&suginput=%E4%BC%9A%E8%AE%A1'
    }
    def __init__(self, keyword):
        self.keyword = keyword
        self.init_proxys()

    def init_proxys(self):
        
        proxy_list = session.query(Proxys).all()
        for proxy in proxy_list:
            self.proxies.append({
                'http': 'http://{}:{}'.format(proxy.ip, proxy.port)
            })

    def fetch_one(self, page=0):
        url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E6%88%90%E9%83%BD&needAddtionalResult=false&isSchoolJob=0'
        proxy = random.choice(self.proxies)
        params = {
            'first': False,
            'pn': str(page),
            'kd': self.keyword
        }
 
        result = requests.post(url, data=params, headers=self.header, proxies=proxy, timeout=5).json()

        if result['success'] == False:
            print(', 抓取失败')
            print(result)
            time.sleep(60)
            return self.fetch_one(page)
        
        return result
    
    def spider(self):
        result = self.fetch_one(0)
        self.pages = result['content']['positionResult']['totalCount']
        page_num = int(self.pages / 15) + 1
        if self.pages % 15 == 0:
            page_num = self.pages // 15
        print('共{}页'.format(page_num), end='')
        for page in range(1, page_num + 1):
            time.sleep(5.5)
            print(
                '正在抓取第{}页'.format(
                    page
                ),
                end=''
            )
            result = self.fetch_one(page)
            self.parse(result['content']['positionResult']['result'])
        print('{}职位抓取完成.'.format(self.keyword))
    def parse(self, jobs):
        for job in jobs:
            cp = session.query(Company.id).filter_by(id=job['companyId']).first()
            ps = session.query(Position.id).filter_by(id=job['positionId']).first()
            # if position has been crawled
            if ps is None:
                job_detail = self.parse_job_detail(job['positionId'])
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
                    second_type=job['secondType'],
                    job_advantage=job_detail['job_advantage'],
                    description=job_detail['description'],
                    location=job_detail['location'],
                    publisher_name=job_detail['publisher_name'],
                    tend_to_talk=job_detail['tend_to_talk'],
                    deal_resume=job_detail['deal_resume'],
                    active_time=job_detail['active_time']
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
    
    def parse_job_detail(self, job_id):
        fetch_url = 'https://www.lagou.com/jobs/{}.html'.format(job_id)
        html = requests.get(fetch_url, headers=self.header).text
        soup = BeautifulSoup(html,'lxml')
        job_advantage = None
        description = None
        location = None
        publisher_name = None
        tend_to_talk = None
        deal_resume = None
        active_time = None
        # 职位诱惑
        try:
            job_advantage = soup.select('#job_detail')[0].select('.job-advantage')[0].select('p')[0].text
        except IndexError:
            print('职位诱惑抓取失败')
            pass
        # 职位描述
        try:
            description_tmp = soup.select('#job_detail')[0].select('dd.job_bt div')[0].select('p')
            description = [x.text for x in description_tmp if x.text != '']
        except Exception:
            print('职位描述抓取失败')
            pass
        # 工作区域
        try:
            location = re.sub('[/\s查看地图]', '', soup.select('.work_addr')[0].text)
        except IndexError:
            print('工作区域抓取失败')
            pass
        
        # 发布者
        try:
            publisher_name = soup.select('.publisher_name .name')[0].text
        except IndexError:
            print('发布者抓取失败')
            pass
        
        # 聊天意愿
        try:
            tend_to_talk = dict()
            tend_content = soup.select('.publisher_data div')[0]
            tend_to_talk['step'] = tend_content.select('.data')[0].text
            tend_to_talk['percent'] = tend_content.select('.tip')[0].select('i')[0].text
            tend_to_talk['time'] = tend_content.select('.tip')[0].select('i')[1].text
        except IndexError:
            print('聊天意愿抓取失败')
            pass
        
        try:
            deal_resume = dict()
            resume_content = soup.select('.publisher_data div')[1]
            deal_resume['step'] = resume_content.select('.data')[0].text
            deal_resume['percent'] = resume_content.select('.tip')[0].select('i')[0].text
            deal_resume['time'] = resume_content.select('.tip')[0].select('i')[1].text
        except IndexError:
            print('简历处理速度抓取失败')
            pass
            
        # 活跃时间--上午，下午，中午
        try:
            active_time = soup.select('.publisher_data div')[1].select('.data')[0].text
        except IndexError:
            print('活跃时间抓取失败')
            pass
        
        return {
            'job_advantage': job_advantage,
            'description': description,
            'location': location,
            'publisher_name': publisher_name,
            'tend_to_talk': tend_to_talk,
            'deal_resume': deal_resume,
            'active_time': active_time
        }


if __name__ == '__main__':
    # from models.model import Base, engine
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)

    pos_list = ['前端', 'web前端', 'python', '后端']
    for pos in pos_list:
        print('关键字{}, '.format(pos), end='')
        scrapy = Scrapy(pos)
        scrapy.spider()
        time.sleep(70)

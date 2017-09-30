import requests
import os
from bs4 import BeautifulSoup
from database.base_db import Session
from models.model import Proxys
session = Session()
def test_ip(ip, port, protocal):
    url = 'http://ip138.com/'
    if protocal == 'https':
        return
    proxy = {
        'http': 'http://{}:{}'.format(ip, port)
    }
    try:
        result = requests.get(url, headers=headers, proxies=proxy, timeout=5)
    except Exception as e:
        return 
    if result.status_code == 200:
        print(ip, port, protocal)
        p = Proxys(
            ip=ip,
            port=port,
            protocal=protocal
        )
        try:
            session.add(p)
            session.commit()
        except Exception as e:
            print('插入失败')
            print(e)
            exit()

def fetch(page):
    global headers
    headers = {'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'}
    url = 'http://www.xicidaili.com/nn/{}'.format(page)
    s = requests.get(url,headers = headers)
    soup = BeautifulSoup(s.text,'lxml')
    ips = soup.select('#ip_list tr')
    for i in ips:
        try:
            ipp = i.select('td')
            ip = ipp[1].text
            port = ipp[2].text
            protocal = ipp[5].text.lower()
            test_ip(ip, port, protocal)
        except Exception as e :
            # print (e)
            pass

if __name__ == '__main__':
    for i in range(1, 10):
        fetch(i)
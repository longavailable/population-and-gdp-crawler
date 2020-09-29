# -*- coding: utf-8 -*-
'''
* Updated on 2020/09/29
* python3
**
* crawl / download poplation and gdp for cities in YDM
* features:
* - data source: 'https://www.gotohui.com/' (聚汇数据),
* - access the webpage by requests,
* - parse data / conten with lxml, 
* - export in csv format.
'''

import requests
from lxml import html
import pandas as pd
import pathlib, time, re
import numpy as np
from pypinyin import lazy_pinyin, Style

headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
								'Chrome/85.0.4183.83 YaBrowser/20.9.0.933 Yowser/2.5 Safari/537.3 ',
	}

urls_area = [
	'https://www.gotohui.com/category/search.html?word={}',
	'http://{}.gotohui.com/',
	'http://{}.gotohui.com/'
	]

urls = {
	'population': 'http://population.gotohui.com/pdata-{}',
	'gdp': 'http://gdp.gotohui.com/data-{}'
	}

s = requests.Session()
s.headers = headers

'''
not success
#login
#extract apikey
url_login = 'https://www.gotohui.com/user/login.html'
re01 = s.get(url_login)
content = html.fromstring(re01.content)
apikey = content.xpath('//*[@id="tokenkey"]/@value')[0]
print(apikey)
#post to login
url = 'https://www.gotohui.com//?api_user/loginapi'
data = {'uname':'longavailable', 'upwd':'UjE-vFC-jGZ-KCg', 'apikey':apikey}
re02 = s.post(url=url, data=data)
'''

#list of cities
cities = pd.read_csv('data/ydm-city-list.csv', names=['cities'])['cities'].to_list()
for area in cities:
	area_full_pinyin = ''.join(lazy_pinyin(area))	#pinyin
	area_initials_pinyin = ''.join(lazy_pinyin(area, style=Style.FIRST_LETTER))	#first letter of pinyin
	#3 possibilites to get the correct url
	attempts = [area, area_full_pinyin, area_initials_pinyin]
	for i, area_str in enumerate(attempts):
		url_area = urls_area[i].format(area_str)
		page_area = s.get(url_area)
		#check if the page is correct by title. The right format of title starts with 'area name'+'房价', eg: '上海房价', '浙江房价'， '镇江房价'...
		if page_area.ok:
			content = html.fromstring(page_area.content)
			suffix = content.xpath('/html/head/title')[0].text[len(area):len(area)+2]	#
			if suffix=='房价': break
	
	#parse the code of area (district / city / province)
	code = re.findall(r'\d+', content.xpath('/html/head/meta[@name="mobile-agent"]')[0].get('content'))[-1]
	print(area, code)
	
	#access pop and gdp pages, get data by 'pandas.read_html', then join them
	for index, key in enumerate(urls):
		url = urls[key].format(code)
		subdata = pd.read_html(io=url, match='时间', index_col=0)[0]	#note that 'read_html' return a list of DataFrames
		if index==0:
			data = subdata
		else:
			data = data.join(subdata, how='outer')
	#replace '登录查看' label
	data = data.replace('登录查看', np.nan)
	
	filename = pathlib.Path('data/{}.csv'.format(area))
	filename.parent.mkdir(parents=True, exist_ok=True)
	data.to_csv(filename)
	print('Done - %s' % area)

print('Done')

'''
#by lxml
#access population page
pop_page = s.get(pop.format(code))
#parse the population table
content = html.fromstring(pop_page.content)
pop = content.xpath('//div[contains(@class,"listcontent")]/table[contains(@class,"ntable")]')[0]
#convert to pandas.DataFrame
temp = pd.read_html(html.tostring(pop))
'''


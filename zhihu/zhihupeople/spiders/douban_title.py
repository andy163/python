# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.http import FormRequest
from zhihupeople.items import DoubanItem
from bs4 import BeautifulSoup
import txt_dict

class DoubanTitleSpider(scrapy.Spider):
    name = "zhihupeople"
    allowed_domains = ["zhihu.com"]
    """
    start_urls = (
        'http://www.zhihu.com',
    )
    """
    def start_requests(self):
        cookies = txt_dict.txt_dict()
        yield scrapy.Request(url='http://www.zhihu.com/', cookies=cookies, callback=self.parse)


    def parse(self, response):
        html_doc = response.body
        soup = BeautifulSoup(html_doc, "lxml")
        filename = "zhihupeople.title"
        with open(filename, 'wb') as f:
            f.write(response.body)
        item = DoubanItem()
        item['title'] = soup.title.string
        item['name'] = soup.find_all('span', class_="name")
        item['corp'] = soup.find_all('span', class_="corp")
        return item 

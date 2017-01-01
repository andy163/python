# -*- coding: utf-8 -*-
import json
import os
import re
from urllib import urlencode
import urlparse
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request
from scrapy.selector import Selector
from zhihuitems import MyZhihuPeopleItem
from zhihuitems import ZhihuRelationItem
from constants import Gender, People,HEADER
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor as sle
import zhihu.txt_dict

class ZhihuPeopleSpider(scrapy.Spider):

    name = "zhihupeople"
    allowed_domains = ["www.zhihu.com"]
    cookies = zhihu.txt_dict.txt_dict()
    start_url = (
        "https://www.zhihu.com/people/weizhi-xiazhi"
    )
    def start_requests(self):

        yield scrapy.Request(url=self.start_url,
                             cookies=self.cookies,
                             headers=HEADER,
                             callback=self.parse_people)


    def parse(self, response):
        html_doc = response.body
        soup = BeautifulSoup(html_doc, "lxml")
        filename = "zhihupeople.title"
        with open(filename, 'wb') as f:
            f.write(response.body)
        return ""

    def parse_err(self, response):
        self.log('crawl {} failed'.format(response.url))

    def parse_people(self, response):

        html_doc = response.body
        soup = BeautifulSoup(html_doc, "lxml")

        """
        解析用户主页
        """
        selector = Selector(response)
        nickname = selector.xpath(
            '//span[@class="ProfileHeader-name"]/text()'
        ).extract_first()
        zhihu_id = os.path.split(response.url)[-1]
        location = selector.xpath(
            '//span[@class="location item"]/@title'
        ).extract_first()
        business = selector.xpath(
            '//span[@class="business item"]/@title'
        ).extract_first()
        gender = selector.xpath(
            '//span[@class="item gender"]/i/@class'
        ).extract_first()
        if gender is not None:
            gender = Gender.FEMALE if u'female' in gender else Gender.MALE

        position = selector.xpath(
            '//span[@class="position item"]/@title'
        ).extract_first()
        list = tuple(selector.xpath(
            '//div[@class="ProfileHeader-infoItem"]/text()'
        ).extract())

        if len(list) > 0:
            employment = list[0]
        else:
            employment = ''

        if len(list) > 1:
            education = list[1]
        else:
            education = ''
        followee_count, follower_count = tuple(selector.xpath(
            '//div[@class="NumberBoard-value"]/text()'
        ).extract())
        followee_count, follower_count = int(followee_count), int(follower_count)
        image_url = selector.xpath(
            '//div[@class="UserAvatar ProfileHeader-avatar"]/img/@srcset'
        ).extract_first('')[0:-3]

        follow_urls = selector.xpath(
            '//div[@class="NumberBoard FollowshipCard-counts"]/a[@class="Button NumberBoard-item Button--plain"]/@href'
        ).extract()
        print (follow_urls)
        for url in follow_urls:
            for x in range(1, 5):
                complete_url = 'https://{}{}'.format(self.allowed_domains[0], url)+'?page='+ str(x)
                print (complete_url)
                yield Request(complete_url,
                              cookies=self.cookies,
                              callback=self.parse_follow,
                              headers=HEADER,
                              errback=self.parse_err)

        item = MyZhihuPeopleItem(
            nickname=nickname,
            zhihu_id=zhihu_id,
            location=location,
            business=business,
            gender=gender,
            employment=employment,
            position=position,
            education=education,
            followee_count=followee_count,
            follower_count=follower_count,
            image_url=image_url,
        )
        yield item

    def parse_follow(self, response):
        """
        解析follow数据
        """
        selector = Selector(response)
        people_links = selector.xpath('//span[@class="UserLink UserItem-name"]/div/div/a[@class="UserLink-link"]/@href').extract()

        # 请求所有的人
        zhihu_ids = []
        print (people_links)
        for people_url in people_links:
            zhihu_ids.append(os.path.split(people_url)[-1])
            complete_url = 'https://{}{}'.format(self.allowed_domains[0], people_url)
            print (complete_url)
            yield Request(complete_url,
                          headers=HEADER,
                          cookies=self.cookies,
                          callback=self.parse_people)

        # 返回数据
        url, user_type = os.path.split(response.url)
        user_type = People.Follower if user_type == u'followers' else People.Followee
        item = ZhihuRelationItem(
            zhihu_id=os.path.split(url)[-1],
            user_type=user_type,
            user_list=zhihu_ids
        )
        yield item


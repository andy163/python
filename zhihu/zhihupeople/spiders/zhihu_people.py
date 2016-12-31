# -*- coding: utf-8 -*-
import json
import os
import re
from urllib import urlencode

import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request
from scrapy.selector import Selector
from zhihuitems import MyZhihuPeopleItem, ZhihuRelationItem
from constants import Gender, People,HEADER
import zhihu.txt_dict


class ZhihuPeopleSpider(scrapy.Spider):
    name = "zhihupeople"
    allowed_domains = ["zhihu.com"]
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
        self.log.ERROR('crawl {} failed'.format(response.url))

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
        employment, education = tuple(selector.xpath(
            '//div[@class="ProfileHeader-infoItem"]/text()'
        ).extract())
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
        for url in follow_urls:
            complete_url = 'https://{}{}'.format(self.allowed_domains[0], url)
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
        if isinstance(item, MyZhihuPeopleItem):
            print ("true")
        yield item

    def parse_follow(self, response):
        """
        解析follow数据
        """
        selector = Selector(response)
        people_links = selector.xpath('//a[@class="zg-link"]/@href').extract()
        people_info = selector.xpath(
            '//span[@class="zm-profile-section-name"]/text()').extract_first()
        people_param = selector.xpath(
            '//div[@class="zh-general-list clearfix"]/@data-init').extract_first()

        re_result = re.search(r'\d+', people_info) if people_info else None
        people_count = int(re_result.group()) if re_result else len(people_links)
        if not people_count:
            return

        people_param = json.loads(people_param)
        post_url = 'https://{}/node/{}'.format(
            self.allowed_domains[0], people_param['nodename'])

        # 去请求所有的用户数据
        start = 20
        while start < people_count:
            payload = {
                u'method': u'next',
                u'_xsrf': self.xsrf,
                u'params': people_param[u'params']
            }
            payload[u'params'][u'offset'] = start
            payload[u'params'] = json.dumps(payload[u'params'])
            HEADER.update({'Referer': response.url})
            start += 20

            yield Request(post_url,
                          method='POST',
                          cookies=self.cookies,
                          headers=HEADER,
                          body=urlencode(payload),
                          priority=100,
                          callback=self.parse_post_follow)

        # 请求所有的人
        zhihu_ids = []
        for people_url in people_links:
            zhihu_ids.append(os.path.split(people_url)[-1])
            yield Request(people_url,
                          headers=HEADER,
                          cookies=self.cookies,
                          callback=self.parse_people,
                          errback=self.parse_err)

        # 返回数据
        url, user_type = os.path.split(response.url)
        user_type = People.Follower if user_type == u'followers' else People.Followee
        item = ZhihuRelationItem(
            zhihu_id=os.path.split(url)[-1],
            user_type=user_type,
            user_list=zhihu_ids
        )
        yield item

    def parse_post_follow(self, response):
        """
        获取动态请求拿到的人员
        """
        body = json.loads(response.body)
        people_divs = body.get('msg', [])

        # 请求所有的人
        zhihu_ids = []
        for div in people_divs:
            selector = Selector(text=div)
            link = selector.xpath('//a[@class="zg-link"]/@href').extract_first()
            if not link:
                continue

            zhihu_ids.append(os.path.split(link)[-1])
            yield Request(link,
                          headers=HEADER,
                          cookies=self.cookies,
                          callback=self.parse_people,
                          errback=self.parse_err)

        url, user_type = os.path.split(response.request.headers['Referer'])
        user_type = People.Follower if user_type == u'followers' else People.Followee
        zhihu_id = os.path.split(url)[-1]
        yield ZhihuRelationItem(
            zhihu_id=zhihu_id,
            user_type=user_type,
            user_list=zhihu_ids,
        )
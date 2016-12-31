# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class DoubanPipeline(object):
        
    def process_item(self, item, spider):
        with open('JobTitle.txt', 'w+') as file:
            title = item['title']
            name = item['name']
            file.write("title:" + str(title) + '\n\n')
            for i, tag in enumerate(name):
                file.write("JobTitle" + str(i+1) + ":" + str(tag.get_text()) + '\n\n')
        return item
       
        
        

#coding=utf-8
#-*- coding: UTF-8 -*-

import re
import requests
import datetime
import hashlib
import lib_mysql_query;
import os


mysqlServer = lib_mysql_query.lib_mysql_query()

class Spider:
    def __init__(self):
        self.site = [];
        
        ifengName='凤凰资讯'
        ifengUrl = 'http://news.ifeng.com/listpage/11574/0/1/rtlist.shtml';
        ifengListRegular='<li><h4>(.*?)</h4><a href="(.*?)".*?>(.*?)</a>'
        ifengContentRegular='<div id="main_content".*?<p.*?>(.*?)<span class="ifengLogo">';
        self.site.append([ifengName,ifengUrl,ifengListRegular,ifengContentRegular]);
        
        
        self.imgDir=r'g:\img\\'
        self.source='凤凰资讯'
        self.imgUrl='http://localhost:8080/img/'
        self.patt="/";
    def getPage(self,url):
#        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' 
#        headers = { 'User-Agent' : user_agent }
        r = requests.get(url)
        return r.content
    
    def getContent(self,contentUrl,contentRegular):
        content = self.getPage(contentUrl)
        pattern = re.compile(contentRegular,re.S)
        items = re.findall(pattern,content)
        return items[0];
#        print items[0].decode("utf8","ignore").encode("gbk","ignore")
    
    def getContents(self,url,listRegular):
        page = self.getPage(url)
        pattern = re.compile(listRegular,re.S)
        items = re.findall(pattern,page)
        contents = []
        for item in items:
            contents.append([item[0],item[1],item[2]])
        return contents
    
    def getUrlMd5(self,url):
        m = hashlib.md5();
        m.update(url)
        return m.hexdigest();
    
    def checkDBUrl(self,md5):
        selectMD5='select count(1) from td_url_md5 where url_md5=\'%s\'' % md5;
        result = mysqlServer.mysql_query_count(selectMD5);
        return result
    #info.title,info.content,info.source,info.source,info.publish_time,info.publish_time,info.link,info.link_md5
    def saveContent(self,title,content,source,publish_time,link,link_md5):
        saveSql='insert into td_news_info(title,content,publisher,source,publish_time,link,link_md5,state) values(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')'% (title,content,source,source,publish_time,link,link_md5,'prehandler');
        mysqlServer.mysql_insert(saveSql);
        
    def saveUrlMd5(self,md5):
        saveMD5='insert into td_url_md5(url_md5) values(\'%s\')'%md5;
        mysqlServer.mysql_insert(saveMD5);
        
    def getAllImg(self,content):
        patternImg = re.compile('<img.*?src="(.*?)"',re.S)
        images = re.findall(patternImg,content)
        return images
    
    def saveImg(self,imageURL,fileName,imgPath):
        print "Download Image File=", fileName
        r = requests.get(imageURL, stream=True) # here we need to set stream = True parameter
        with open(imgPath+self.patt+fileName, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            f.close()

    def mkdir(self,path):
        path = path.strip()
        isExists=os.path.exists(path)
        if not isExists:
            print u"not the ",path,u'will create'
            os.makedirs(path)
            return True
        else:
            print u"have the path",path
            return False
    def saveAllImgs(self,content):
        now_year_month_day = str(datetime.datetime.now().strftime("%Y%m%d"));
        imgPath = self.imgDir+now_year_month_day
        self.mkdir(imgPath);
        images = self.getAllImg(content)
        for imgurl in images:
            fileName = imgurl.split('/')[-1]
            self.saveImg(imgurl,fileName,imgPath);
            content = content.replace(imgurl,self.imgUrl+now_year_month_day+'/'+fileName);
        return content;
            
            
    def savePageInfo(self,url,listRegular,contentRegular,sourceName):
        contents = self.getContents(url,listRegular);
        today = datetime.datetime.now()
        current_year = today.strftime('%Y');
        print current_year
        for item in contents:
            print '------ fetch  ------ '+item[2]
            print u"date:",item[0].decode("utf8","ignore").encode("gbk","ignore")
            print u" url:",item[1].decode("utf8","ignore").encode("gbk","ignore")
            print u" title:",item[2]
            article_date = datetime.datetime.strptime(current_year+'/'+item[0],'%Y/%m/%d %H:%M');
            delta =today - article_date;
            title=item[2]
            link = item[1];
            urlMd5=self.getUrlMd5(link);
            if (delta.days < 1) and (self.checkDBUrl(urlMd5)<1):
                content = self.getContent(link,contentRegular);
                content = self.saveAllImgs(content);
                self.saveContent(title,content,sourceName,article_date.strftime("%Y-%m-%d %H:%M:%S"),link,urlMd5);
                self.saveUrlMd5(urlMd5);
            else:
                print 'the info is had'
            print '----- end fetch  ------' + item[2]
    def beginFetchPage(self):
        for item in self.site:
            print 'begin fetch ' + item[0]
            sourceName = item[0]
            url = item[1]
            listRegular = item[2]
            contentRegular = item[3]
            self.savePageInfo(url,listRegular,contentRegular,sourceName);
            print 'end fetch '+ item[0]
            
spider = Spider()
content = spider.beginFetchPage();
print 'down load end';



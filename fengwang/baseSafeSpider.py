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
        ifengUrl = 'http://cs.mfa.gov.cn/zggmcg/ljmdd/';
        ifengListRegular='.*?<li><a href="(.*?)".*?><img src="(.*?)".*?>.*?<a.*?>(.*?)</a></p></li>'
        ifengContentRegular='<div class="list m_mt20">.*?社会治安.*?<div class="chnlnamecon">(.*?)</div>.*?<div class="list m_mt20">';
        self.site.append([ifengName,ifengUrl,ifengListRegular,ifengContentRegular]);
        
        
        self.imgDir=r'g:\img\\'
        self.source='凤凰资讯'
        self.imgUrl='http://localhost:8080/img/'
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
        pattern = re.compile('<div class="country_list".*?<ul>(.*?)<div class="clear">',re.S)
        mainContent = re.search(pattern,page)
        pattern = re.compile(listRegular,re.S)
        items = re.findall(pattern,mainContent.group(1))
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
        with open(imgPath+r'\\'+fileName, 'wb') as f:
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
    
    def saveCountry(self,countryId,countryName,safeInfo,flagUrl):
        saveSql='insert into td_country_info(country_id,ch_name,is_hot,flag_url,safe_info,create_time) values(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')'% (countryId,countryName,1,flagUrl,safeInfo,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"));
        mysqlServer.mysql_insert(saveSql);
            
    def savePageInfo(self,url,listRegular,contentRegular,sourceName):
        contents = self.getContents(url,listRegular);
        today = datetime.datetime.now()
        current_year = today.strftime('%Y');
        imgName='img';
        print current_year
        id = 10000;
        for item in contents:
            try:
                id = id +1;
                idStr = 'C'+str(id);
                content_url = url+item[0].replace('./','');
                country_img='http://cs.mfa.gov.cn/'+item[1].replace('../../','');
                country_name=item[2];
                print '------ fetch  ------ '+country_name
                content = self.getContent(content_url,contentRegular);
                fileName = country_img.split('/')[-1]
                self.saveImg(country_img,fileName,self.imgDir+'flag');
                imgUrl=self.imgUrl+'flag/'+fileName;
                print imgUrl,country_name,content
                self.saveCountry(idStr,country_name,content,imgUrl);
                print '----- end fetch  ------' + country_name
            except Exception,ex:
                 print Exception,":",ex
            
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



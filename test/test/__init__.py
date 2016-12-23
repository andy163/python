#!user/bin/python# 
# -*- coding: utf-8 -*-
import json
import requests
import xlwt
import importlib

#解决编码问题
import sys
reload(sys)

#获取存储了职位信息的json对象，遍历获得公司名、职位、待遇等信息
def get_json(url,page): 
  datas = {"first": "true", "pn": page,"kd": "HR" }
  s = requests.post(url, data=datas).json()    #reqquests获得json对象
  print (s)
  info_list = []    
  jcontent = s["content"]["positionResult"]["result"]    
  for i in jcontent:        
    info = []        
    info.append(i["companyFullName"])        
    info.append(i['companySize'])        
    info.append(i['positionName'])        
    info.append(i['education'])        
    info.append(i['financeStage'])        
    info.append(i['salary'])        
    info.append(i['city'])        
    info.append(i['district'])        
    info.append(i['positionAdvantage'])        
    info.append(i['workYear'])        
    info_list.append(info)    
    print
    json.dumps(info_list, ensure_ascii=False, indent=2);
    return info_list

#实现翻页，结果写入excel文件
def main():    
   url="https://www.lagou.com/jobs/positionAjax.json"
   page=1    
   info_result=[]    
   title = ['公司全名', '公司规模', '职位名称', '教育程度', '融资情况', "薪资水平", "城市", "区域", "优势", "工作经验"]    
   info_result.append(title)    
   while page < 31:        
      info=get_json(url,page)        
      info_result=info_result+info
      page+=1        
      workbook = xlwt.Workbook(encoding="utf-8")        
      booksheet = workbook.add_sheet('HR', cell_overwrite_ok=True)        
      for i, row in enumerate(info_result):            
           for j, col in enumerate(row):
               booksheet.write(i, j, col)
               workbook.save('HR.xls')

if __name__=="__main__":
    main()
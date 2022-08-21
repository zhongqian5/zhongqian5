# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 16:30:40 2022

@author: zhongqian5
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Dec 30 16:02:23 2021

@author: zhongqian5
"""

import time
import random
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

level_list = ['provincetr','citytr','countytr','towntr','villagetr']
driver_path = r'chromedriver.exe'
app_get_data_url = r'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2021/index.html'
timeout = 2
result_position =  './data/'+'national_area_result.csv'
position = './province_link.txt'

def read_position():
    
    province_link_list = []
    province_link_pd =  pd.read_csv(position,header=0,usecols=['url'])    
    province_link_list = [x for x in province_link_pd['url']]
    
    return province_link_list
    
def dict2file(res_dict):

    if not os.path.exists(result_position):
        res_pd = pd.DataFrame(res_dict,index=[0],dtype = str)
        res_pd.to_csv(result_position,encoding='utf_8_sig',mode='a',index=False,index_label=False)
    else:
        res_pd = pd.DataFrame(res_dict,index=[0],dtype = str)
        res_pd.to_csv(result_position,encoding='utf_8_sig', mode='a',index=False, index_label=False,header=False)
    
def get_random_time_sleep_click(driver, button):
    time.sleep(random.random()+0.3)
    webdriver.ActionChains(driver).move_to_element(button).click(button).perform()
    time.sleep(2)


def get_content_detail(driver,level):
    
    '''
    获取对应级别的行政区划信息
    '''
    division_level = ".//tr[@class='%s']"%(level)
    division_link_list = []
    
    for division in driver.find_elements(By.XPATH,division_level):
        division_content={}
        
        if  level != 'villagetr':#获取市区县乡镇街道的信息
            try:
                division_detail = division.find_elements(By.XPATH,".//td/a") 
                division_link = division_detail[0].get_attribute('href')
                division_content['code'] = division_detail[0].text
                division_content['name'] = division_detail[1].text
                division_content['url']  = division_link
                division_content['urban_rural_class_code'] = ''
                division_link_list.append(division_link)
                
            except:#处理市辖区这种情况,没有下属街道
                division_detail = division.find_elements(By.XPATH,".//td") 
                division_content['code'] = division_detail[0].text
                division_content['name'] = division_detail[1].text
                division_content['url']  = ''
                division_content['urban_rural_class_code'] = ''                
            
        else:#获取社区的信息
            division_detail = division.find_elements(By.XPATH,".//td") 
            division_content['code'] = division_detail[0].text
            division_content['name'] = division_detail[2].text
            division_content['url']  = ''
            division_content['urban_rural_class_code'] = division_detail[1].text
        
        division_content['type']=level[:-2]
        dict2file(division_content)
     
    return division_link_list

def open_html(driver,division_link,level):
    
    '''
    打开浏览器,防止加载缓慢
    '''
    p_d = 1
    while p_d:
        try:
            driver.get(division_link)
            driver.set_page_load_timeout(3)
            WebDriverWait(driver, timeout=timeout).until(EC.presence_of_element_located((By.XPATH, "//*[@class='%s']"%level)))
            p_d = 0
        
        except:
            p_d = 1
     
    return driver       

def get_content(driver,mode_1): 
    
    '''
    获取省份的链接与信息
    '''
    province_link_list = []
    
    if mode_1 == 'w':
        for row in driver.find_elements(By.XPATH,".//tr[@class='provincetr']"):
            for province in row.find_elements(By.XPATH,".//td/a"):
                division_content = {}
                province_link = province.get_attribute('href')
                division_content['code'] = province_link[-7:-5]+'0000000000'
                division_content['name'] = province.text
                division_content['url'] =  province_link
                division_content['urban_rural_class_code'] = ''
                division_content['type'] = 'provincet'
                province_link_list.append(province_link)#获取页面元素的href属性
                dict2file(division_content)
    
    elif mode_1 == 'a':
        province_link_list = read_position()   
        
    '''
    获取市县(区)乡镇(街道)社区一级的信息流程
    '''
    for province_link in province_link_list:
        driver = open_html(driver,province_link,'citytr')
        city_link_list = get_content_detail(driver,'citytr')

        for city_link in city_link_list:
            driver = open_html(driver,city_link,'countytr')
            county_link_list = get_content_detail(driver,'countytr')
            
            for county_link in  county_link_list:
                driver = open_html(driver,county_link,'towntr')
                town_link_list = get_content_detail(driver,'towntr')
                
                for town_link in town_link_list:
                    driver = open_html(driver,town_link,'villagetr')
                    get_content_detail(driver,'villagetr')
  
        
def fetch_data(driver,mode_1):
    
    try: 
        driver.get(app_get_data_url)
        driver.set_page_load_timeout(3)
        WebDriverWait(driver, timeout=timeout).until(EC.presence_of_element_located((By.XPATH, "//*[@class='provincetr']")))
        get_content(driver,mode_1)
        #for open_btn in  driver.find_element(By.CLASS_NAME,'openlist'):
        
    except Exception as e:
        print(e)
        print('打开网站失败，请检测网络环境！')
        

if __name__ == '__main__':
    
    chrome_opt =webdriver.ChromeOptions()
    prefs ={'profile.managed_default_content_setting.images':2} #不加载图片
    chrome_opt.add_experimental_option('prefs',prefs)
    chrome_opt.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    s = Service(driver_path)
    with webdriver.Chrome(service=s,options=chrome_opt) as driver:
        mode_1 = ''
        while mode_1 not in ['w','a','n']:
            mode_1 = input('是否打开指定网页, 开始获取数据? w(重新写入)a(追加写入)n(不获取数据)')
        
        if mode_1 in ('w','a'):
            
            try:
                fetch_data(driver,mode_1)
                print('数据获取完成')
            except Exception as e:
                print(e)
        input('按回车键退出！')








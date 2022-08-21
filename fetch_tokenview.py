# -*- coding: utf-8 -*-
"""
Created on Thu Dec 30 16:02:23 2021

@author: zhongqian5
"""

import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

driver_path = r'chromedriver.exe'
app_get_data_url = r'https://trx.tokenview.com/cn/tokentxns/'
timeout = 5
position = './tmp.txt'
result_position = './data/'+str(int(time.time()))+'tikenview_result.csv'
#writer = pd.ExcelWriter(result_position,mode='a')


def get_random_time_sleep_click(driver, button):
    time.sleep(random.random()+0.3)
    webdriver.ActionChains(driver).move_to_element(button).click(button).perform()
    time.sleep(2)

def open_html(driver,app_get_data_url,account):
    
    '''
    打开浏览器,防止加载缓慢
    '''
    division_link = app_get_data_url+account
    p_d = 1
    while p_d<=3 and p_d != 0:
        try:
            driver.get(division_link)
            driver.set_page_load_timeout(3)
            WebDriverWait(driver, timeout=timeout).until(EC.presence_of_element_located((By.XPATH, "//*[@class='openlist']")))
            p_d = 0
            print(p_d)
        
        except Exception as e:
 
            if p_d == 3:
                try:
                    driver.find_element(By.CLASS_NAME,'nodata')
                    print(account+'没有数据')
                    break
                except:
                    p_d = 1
            else:
                p_d = p_d+1
                
                
    return driver 

def get_content_detail(item,account,people):

    for row in item.find_elements(By.XPATH,".//div[@class='tablecolumn']"):
         data_map={}
         data_map['人员']=people
         data_map['账号']=account
         data_map['交易哈希']=row.find_element(By.XPATH,".//div[@class='hash']").text
         data_map['从']=row.find_element(By.XPATH,".//div[@class='from']/div").text
         data_map['方向']=row.find_element(By.XPATH,".//div[contains(@class,'direction')]").text
         data_map['到']=row.find_element(By.XPATH,".//div[@class='to']/div").text
         data_map['金额']=row.find_element(By.XPATH,".//div[@class='mount']").text
         data_map['时间']=row.find_element(By.XPATH,".//div[@class='time']").text
         pd.DataFrame(data_map,index=[0]).to_csv(result_position,index=False,header=None,mode='a+') 


def get_content(driver,item,account,people):
    
    get_content_detail(item,account,people)#获取内容
    
    try:
        next_page_btn = item.find_element(By.CLASS_NAME,'next_page')
        while next_page_btn.get_attribute('style') != 'cursor: text;':
            get_random_time_sleep_click(driver, next_page_btn)
            WebDriverWait(driver, timeout=timeout).until(EC.presence_of_element_located((By.XPATH, ".//div[@class='childtable']")))
            get_content_detail(item,account,people)
            next_page_btn = item.find_element(By.CLASS_NAME,'next_page')
    except Exception as e:
        print(e)

def fetch_data(driver):
    
    ori_search_pd = pd.read_csv(position,header=None,encoding='utf-8',sep='\t')
    pd.DataFrame(columns=['人员','账号','交易哈希','从','方向','到','金额','时间']).to_csv(result_position,index=False,encoding='gbk') 
    for i in range(0,len(ori_search_pd)):
        try:
            account = str(ori_search_pd.iloc[i,0]) 
            people  = str(ori_search_pd.iloc[i,1]) 
            driver = open_html(driver,app_get_data_url,account)
            item_list = driver.find_elements(By.XPATH,"//div[@class = 'inner']")
            m = 0
            for item in item_list:
                if  'USDT' in item.find_element(By.XPATH,"./div[@class='item']/div[@class='balance']/a").text:
                    get_random_time_sleep_click(driver, item.find_element(By.CLASS_NAME,'openlist'))#点击第一个展开
                    WebDriverWait(driver, timeout=timeout).until(EC.presence_of_element_located((By.XPATH, ".//div[@class='childtable']")))
                    get_content(driver,item,account,people)
                    m = m+1
                    print(account+str(m)+'完成')
        except Exception as e:
            print('打开网站失败，请检测网络环境！')
        

if __name__ == '__main__':
    
    chrome_opt =webdriver.ChromeOptions()
    prefs ={'profile.managed_default_content_setting.images':2} #不加载图片
    chrome_opt.add_experimental_option('prefs',prefs)
    chrome_opt.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    s = Service(driver_path)
    with webdriver.Chrome(service=s,options=chrome_opt) as driver:
        input_data = ''
        while input_data not in ['y', 'n']:
            input_data = input('是否打开指定网页, 开始获取数据? y/n:')
        
        if input_data == 'y':
            
            try:
                fetch_data(driver)
                print('数据获取完成')
            except Exception as e:
                print(e)
        input('按回车键退出！')








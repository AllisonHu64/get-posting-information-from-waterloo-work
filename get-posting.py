#!/usr/bin/env python
# coding: utf-8

# In[232]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import pandas as pd
import math

waterlooWorkUrl = "https://waterlooworks.uwaterloo.ca/myAccount/co-op/coop-postings.htm"
waterlooNotLoggedInUrl = "https://waterlooworks.uwaterloo.ca/notLoggedIn.htm"
waterlooWorkDashBoard = "https://waterlooworks.uwaterloo.ca/myAccount/dashboard.htm"


# In[233]:


# login 
try:
    browser = webdriver.Chrome()
    browser.get("https://waterlooworks.uwaterloo.ca/myAccount/co-op/coop-postings.htm")    # open waterloo work website 
    element = WebDriverWait(browser,10).until(
        EC.url_to_be(waterlooNotLoggedInUrl)
    )
    print('please log in manually in the next 60s')
    try:
        element = WebDriverWait(browser,60).until(
            EC.url_to_be(waterlooWorkDashBoard)
        )
    except TimeoutException:
        print('Time Out. Please rerun the script')
        exit
    print('Successfully logged in. Redirecting to coop postings url')
    browser.get("https://waterlooworks.uwaterloo.ca/myAccount/co-op/coop-postings.htm")
    try:
        element = WebDriverWait(browser,10).until(
            EC.url_to_be(waterlooWorkUrl)
        )
    except TimeoutException:
        print('Time Out. Please rerun the script. Please check your internect connection')
        exit
except TimeoutException:
        print('You already loggined in to Waterloo Work. Please Proceed')


# In[5]:


# find the for my program link
try:
    forMyProgram = browser.find_element_by_link_text('For My Program')
    try:
        forMyProgram.click()
        element = WebDriverWait(browser,10).until(
            EC.presence_of_element_located((By.XPATH,"//h1[contains(text(),'Search Results - For My Program')]"))
        )
    except TimeoutException:
        print('Time Out. Please check your internet connection or manually click For My Program.')
        print('Please manually click For My Program Link in the next 60s')
except NoSuchElementException:
    print('Can not find the element For My Program. Please check the website.')
    print('Please manually click For My Program Link in the next 60s')


# In[6]:


try:
    element = WebDriverWait(browser,60).until(
        EC.presence_of_element_located((By.XPATH,"//h1[contains(text(),'Search Results - For My Program')]"))
    )
except TimeoutException:
    print('Time Out. Redirecting to For My Program Failed')
    exit
    


# In[9]:


## get info header
postingHeader = browser.find_elements(By.XPATH,"//thead/tr/th")
postingShortInfoHeader = [list(map(lambda x: x.text ,postingHeader))]


# In[7]:


# get number of posts 
postingNum = browser.find_elements(By.XPATH,"//strong[text()='TOTAL RESULTS:']");
postingNum = int(postingNum[0].find_elements(By.XPATH,"../span")[0].text);


# In[10]:


def getShortInfo(shortInfo, firstLine):
    newShortInfoList = []
    for index,value in enumerate(shortInfo):
        if(firstLine and index >= 4 and index < 15):
            newShortInfoList.append(value.text)
        elif((not firstLine) and index >=1 and index < 12):
            newShortInfoList.append(value.text)
    return newShortInfoList


# In[61]:


postingShortInfoData = []
for pageNum in range(0, math.floor(postingNum/100)):
    for index in range(1,min(postingNum - (pageNum+1)*100 + 1,101)):
        shortInfo = browser.find_elements(By.XPATH,"//tr["+str(index)+"]/td");
        postingShortInfoData.append(getShortInfo(shortInfo, index == 1))
    ## open next Page
    print('copying items from page ' + str(pageNum + 1))
    nextPage = browser.find_elements(By.XPATH,"//div[@class='pagination pagination'][1]/ul[1]/li["+
                                                str(pageNum+4)+"]/a")
    try:
        nextPage[0].click()
        element = WebDriverWait(browser,10).until(
            EC.presence_of_element_located((By.XPATH,"//span[@id='totalOverAllDocs' and text()="
                                            +str((pageNum+1)*100+1)+"]"))
        )
    except TimeoutException:
        print('Time Out. Please check your internet connection or manually click For My Program.')
        break


# In[63]:


postingShortInfo = pd.DataFrame(postingShortInfoData,columns=postingShortInfoHeader)


# In[65]:


## save to local files
postingShortInfo.to_csv('/Users/allisonhu/Desktop/waterloo_work_short_info.csv',index=False)


# In[20]:


## go back to first page and start getting long posting info
try:
    firstPage =  browser.find_elements(By.XPATH,"//div[@class='pagination pagination'][1]/ul[1]/li["+
                                                str(3)+"]/a")
    firstPage[0].click()
    element = WebDriverWait(browser,10).until(
        EC.presence_of_element_located((By.XPATH,"//span[@id='totalOverAllDocs' and text()="
                                        +str(1)+"]"))
    )
except TimeoutException:
    print('Time Out. Please check your internet connection or manually click For My Program.')


# In[214]:


postingLongInfoHeader = [
 'Work Term:',
 'Job Type:',
 'Job Title:',
 'Number of Job Openings:',
 'Job Category (NOC):',
 'Level:',
 'Region:',
 'Job - Address Line One:',
 'Job - City:',
 'Job - Province / State:',
 'Job - Postal Code / Zip Code (X#X #X#):',
 'Job - Country:',
 'Job Location (if exact address unknown or multiple locations):',
 'Work Term Duration:',
 'Special Job Requirements:',
 'Job Summary:',
 'Job Responsibilities:',
 'Required Skills:',
 'Transportation and Housing:',
 'Compensation and Benefits Information:',
 'Targeted Degrees and Disciplines:']


# In[225]:


## open each posting and get their info
postingLongInfoData = []
browser.switch_to.window(browser.window_handles[0])
for pageNum in range(0, math.ceil(postingNum/100)):
    postingLongInfoData = []
    postingLinks = browser.find_elements(By.XPATH,"//a[contains(text(),'new tab')]")
    viewButtons = browser.find_elements(By.XPATH,"//a[contains(text(),'View')]")
    for index in range(0,min(postingNum - (pageNum)*100,100)):
        ## open job posting detail page
        try:
            ## scroll into view
            browser.execute_script("arguments[0].scrollIntoView(false);",viewButtons[index])
            viewButtons[index].click()
            postingLinks[index].click()
            ## switch tabs
            browser.switch_to.window(browser.window_handles[1])
            element = WebDriverWait(browser,10).until(
                EC.presence_of_element_located((By.XPATH,"//h1[contains(text(),'Job ID:')]"))
            )
            element = WebDriverWait(browser,10).until(
                EC.presence_of_element_located((By.XPATH,"//h1[contains(text(),'Job ID:')]"))
            )
        except TimeoutException:
            print('Time Out. Please check your internet connection or manually click For My Program.')
            break
        ## get posting long info
        print('recording info from ',browser.find_elements(By.XPATH,"//h1[contains(text(),'Job ID:')]")[0].text)
        header = []
        data = []
        for column in postingLongInfoHeader:
            columnData = browser.find_elements(By.XPATH,"//strong[contains(text(),'"+column+"')][1]/../../td[2]")
            if (len(columnData) == 0):
                data.append('')
            else:
                data.append(columnData[0].text)
        postingLongInfoData.append(data)
        ## close and switch tab
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
    ## save longInFo to csv
    postingLongInfo = pd.DataFrame(postingLongInfoData,columns=postingLongInfoHeader)
    postingLongInfo.to_csv('/Users/allisonhu/Desktop/waterloo_work_ling_info_page'+
                           str(pageNum+1)+'.csv',index=False)
    postingLongInfoData = []
    
    ## open next Page
    print('copying items from page ' + str(pageNum + 1))
    nextPage = browser.find_elements(By.XPATH,"//div[@class='pagination pagination'][1]/ul[1]/li["+
                                                str(pageNum+4)+"]/a")
    try:
        nextPage[1].click()
        element = WebDriverWait(browser,10).until(
            EC.presence_of_element_located((By.XPATH,"//span[@id='totalOverAllDocs' and text()="
                                            +str((pageNum+1)*100+1)+"]"))
        )
        element = WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.XPATH,"//a[contains(text(),'View')][1]")))
    except TimeoutException:
        print('Time Out. Please check your internet connection or manually click For My Program.')
        break


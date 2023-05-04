# Import libraries
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import re
import numpy as np

# URL used for job finding
url = "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22102257491%22%5D&keywords=product%20analyst&origin=FACETED_SEARCH&sid=f*l"


# Set up chromedriver
#driver = webdriver.Chrome(ChromeDriverManager().install())
wd_path = "C:\\Users\\calmp\\AppData\\Local\\Temp\\Temp1_chromedriver_win32.zip\\chromedriver.exe"
wd = webdriver.Chrome(executable_path = wd_path)
wd.get(url)

# Log in details
passw = 'Jobby6@!'
user = 'calmpg.spam@gmail.com'

# Click on sign in
wd.find_element_by_xpath('/html/body/div[2]/main/p[1]/a').click()

# Enter username
u = wd.find_element_by_xpath('//*[@id="username"]')
u.click()
time.sleep(2)
u.send_keys(user)

# Enter password
u = wd.find_element_by_xpath('//*[@id="password"]')
u.click()
time.sleep(2)
u.send_keys(passw)
u.send_keys(Keys.RETURN)

# Give time for page to load
time.sleep(5)


# Pull data from each page
page = 0
scope = 100 # total pages to search
jobs = []
    
while page <= scope:

    # Get all the people on the page
    p_list = wd.find_element_by_class_name("search-results-container")
    people = p_list.find_elements_by_tag_name("li") # return a list  
    
    
    # Get Job titles
    for i in people:
        try:
            job = i.find_element_by_tag_name('p').get_attribute("innerText")
            jobs.append(job)
        except:
            next
    
    # Scroll to bottom (Selenium needs to see the next button)
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # Move to next page
    time.sleep(1)
    if page == 0:
        path = '/html/body/div[6]/div[3]/div[2]/div/div[1]/main/div/div/div[5]/div/div/button[2]'
    else:
        path = '/html/body/div[6]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/div[2]/div/button[2]'
    u = wd.find_element_by_xpath(path)
    u.click()
    time.sleep(5)

    # Countdown pages
    page = page+1
    print(page)
    

# Export dataframe
df = pd.DataFrame(jobs)
path = 'C:\\Users\\calmp\\OneDrive\\0 - Job Applications\\Job Apps\\Portfolio\\LinkedIn job analysis\\LI_Companies.csv'
df.to_csv(path, index = False)
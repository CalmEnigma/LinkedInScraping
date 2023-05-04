# https://maoviola.medium.com/a-complete-guide-to-web-scraping-linkedin-job-postings-ad290fcaa97f

# Import libraries
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import re
import numpy as np

# URL used for job finding
url = "https://www.linkedin.com/jobs/search/?currentJobId=3176601534&distance=25&geoId=102257491&keywords=data%20product%20analyst"


# Set up chromedriver
#driver = webdriver.Chrome(ChromeDriverManager().install())
wd_path = "C:\\Users\\calmp\\AppData\\Local\\Temp\\Temp1_chromedriver_win32.zip\\chromedriver.exe"
wd = webdriver.Chrome(executable_path = wd_path)
wd.get(url)

# See number of jobs
no_of_jobs = str(wd.find_element_by_css_selector("h1>span").get_attribute("innerText"))

# Convert number of jobs to integer
## If over 3000, assume it is 3000
n = []
for i in no_of_jobs:
    try:
        int(i)
        n.append(i)
    except: ValueError
no_of_jobs = int("".join(n))


# Browse all the jobs
## 40 pages, 25 results per page = 1000 jobs
## The sleep timer helps prevent being locked out by LinkedIn for too many requests
i = 2
while i <= 40:
    
    # Scroll down the list of jobs
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    i = i + 1
    
    # If the page requires a click at the bottom
    try:
        wd.find_element_by_xpath("/html/body/div[3]/div/main/section[2]/button").click()
        time.sleep(5)
    except:
        pass
        time.sleep(1)
         

# Find all the jobs
job_lists = wd.find_element_by_class_name("jobs-search__results-list")
jobs = job_lists.find_elements_by_tag_name("li") # return a list         
len(jobs) # number of jobs


# Extract data from job card
job_id= []
job_title = []
company_name = []
location = []
date = []
job_link = []

for job in jobs:
 job_id0 = job.find_element_by_css_selector("div").get_attribute("data-entity-urn")
 job_id.append(job_id0)
 
 job_title0 = job.find_element_by_css_selector("h3").get_attribute("innerText")
 job_title.append(job_title0)
 
 company_name0 = job.find_element_by_css_selector("h4").get_attribute("innerText")
 company_name.append(company_name0)
 
 location0 = job.find_element_by_class_name("base-search-card__metadata").find_element_by_class_name("job-search-card__location").get_attribute("innerText")
 location.append(location0)
 
 date0 = job.find_element_by_css_selector("div>div>time").get_attribute("datetime")
 date.append(date0)
 
 job_link0 = job.find_element_by_css_selector("a").get_attribute("href")
 job_link.append(job_link0)


                           

# Get more detailed job descriptions and other data
jd = []
applicants = []
oth_cri = []
#seniority = []
#emp_type = []
#job_func = []
#industries = []


n = 0
for link in job_link:
    
    # Reset wd after some scrapes to prevent blocking by LinkedIn
    if n==1:
        wd.close()
        wd = webdriver.Chrome(executable_path = wd_path)        
    
    # Navigate to job page
    wd.get(link)
    
    # Get job description
    jd_path = "/html/body/main/section[1]/div/div[1]/section[1]/div/div/section/div"
    jd0 = wd.find_element_by_xpath(jd_path).get_attribute("innerText")
    jd.append(jd0)
    
    # Get number of applicants
    data = wd.find_element_by_class_name("num-applicants__caption").get_attribute("innerText")
    applicants.append(data)
    
    # Get other job criteria items
    # To be cleaned later because the HTML locations often vary for these criteria
    data = wd.find_element_by_class_name("description__job-criteria-list").get_attribute("innerText")
    oth_cri.append(data)
    
    # Pause before next page to avoid being locked out by LinkedIn
    time.sleep(5.5)
    
    # Add to count
    n = n+1
 

# Keep results with data for both datasets
n = len(applicants)
job_id = job_id[:n]
job_title = job_title[:n]
company_name = company_name[:n]
location = location[:n]
date = date[:n]
job_link = job_link[:n]    
 
# Create dataframe
df = pd.DataFrame({"ID": job_id,
                        "Date": date,
                        "Company": company_name,
                        "Title": job_title,
                        "Location": location,
                        "Description": jd,
                        "Applicants": applicants,
                        "Other criteria": oth_cri,
                        "Link": job_link
                        })   
    


# Export dataframe
path = 'C:\\Users\\calmp\\OneDrive\\0 - Job Applications\\Job Apps\\Portfolio\\LinkedIn job analysis\\LI_Data.csv'
df.to_csv(path, index = False)


# =============================================================================
#     # Get seniority
#     data = wd.find_element_by_xpath("/html/body/main/section[1]/div/div/section[1]/div/ul/li[1]/span").get_attribute("innerText")
#     seniority.append(data)
#     
#     # Get employment type
#     data = wd.find_element_by_xpath("/html/body/main/section[1]/div/div/section[1]/div/ul/li[3]/span").get_attribute("innerText")
#     emp_type.append(data)
#     
#     # Get job function
#     data = wd.find_elements_by_xpath("/html/body/main/section[1]/div/div/section[1]/div/ul/li[3]/span")
#     job_func0=[]
#     for element in data:
#         job_func0.append(element.get_attribute("innerText"))
#         job_func_final = ", ".join(job_func0)
#         job_func.append(job_func_final)
#     
#     # Get industries
#     data = wd.find_elements_by_xpath("/html/body/main/section[1]/div/div/section[1]/div/ul/li[4]/span")
#     industries0=[]
#     for element in data:
#         industries0.append(element.get_attribute("innerText"))
#         industries_final = ", ".join(industries0)
#         industries.append(industries_final)
#         
#     
# =============================================================================




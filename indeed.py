from bs4 import BeautifulSoup 
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import json
import random
import time
import re

def load_config():
    with open('config.json') as file:
        config = json.load(file)
        queries = config["queries"]
        locations = config["locations"]
        include = config["includes"]
        must_include = config["must_include"]
        exclude = config["excludes"]
        age_limit = config["age_limit"]
        distance = config["distance"]

    return queries, locations, include, must_include, exclude, age_limit, distance

def get_titles(soup, includes, must_include, excludes):
    filtered_titles = []
    titles = soup.select('span[title]')
    for title in titles:
        title_text = title.get_text().strip().lower()
        title_text = title_text.replace('/', ' ')
        title_words = title_text.split()
        includes_matches = any(include in title_words for include in includes)
        must_include_matches = any(must in title_words for must in must_include)
        excludes_matches = any(exclude in title_words for exclude in excludes)
        if includes_matches and must_include_matches and not excludes_matches:
            filtered_titles.append(title)

    return filtered_titles

def get_links(titles):
    links = []
    for title in titles:
        if title.parent.has_attr('href'):
            link = title.parent['href']
            links.append(f'https://ca.indeed.com{link}')
    return links

def get_locations(titles):
    locations = []
    for title in titles:
        parent = title.find_parent('td', {'class': 'resultContent css-lf1alc eu4oa1w0'})
        child = parent.find('div', {'class': 'company_location css-i375s1 e37uo190'})
        location = child.find('div', {'class': 'css-1restlb eu4oa1w0'}).text
        locations.append(location)
    return locations

def get_dates(titles):
    dates = []
    date_format = '%Y-%m-%d'
    for title in titles:
        today = datetime.today()
        parent = title.find_parent('td', {'class': 'resultContent css-lf1alc eu4oa1w0'})
        job_seen_beacon = parent.find_parent('div', {'class': "job_seen_beacon"})
        date_info = job_seen_beacon.find('span', {'class': 'css-1yxm164 eu4oa1w0'}).text.replace('+', '')
        days_info = re.sub('\D', '', date_info)
        if days_info.isdigit() and len(days_info) > 0:
            date_t = timedelta(days=int(days_info))
            final_date = (today - date_t).strftime(date_format)
        else: 
            print(f"failed to get date for {title.get_text().strip()}: defaulting to today's date")
            final_date = today.strftime(date_format) 
        
        dates.append(final_date)

    return dates

def clear_old_jobs(jobs, age_limit):
    jobs_to_delete = []
    today = datetime.today()
    for title, details in jobs['jobs'].items():
        if details["date"] != 'failed to fetch date':
            date = datetime.strptime(details["date"], '%Y-%m-%d')
            difference = (today - date).days
            if difference > age_limit:
                jobs_to_delete.append(title)
    
    for title in jobs_to_delete:
        del jobs['jobs'][title]

    return jobs

def write_jobs(jobs, old_jobs):
    for job_title, job_info in jobs["jobs"].items():
        if job_title in old_jobs["jobs"]:
            job_info["new"] = False
    
    if len(jobs["jobs"]) > 0:
        with open('jobs.json', 'w') as job_json:
            json.dump(jobs, job_json, indent=4)

def merge_jobs(linkedin_jobs, indeed_jobs):
    all_jobs = {"jobs": {}}
    if linkedin_jobs:
        if len(linkedin_jobs) > 0: all_jobs["jobs"].update(linkedin_jobs["jobs"])
    if indeed_jobs:
        if len(indeed_jobs) > 0: all_jobs["jobs"].update(indeed_jobs["jobs"])
    return all_jobs

def scrape_indeed(result):
    queries, locations, include, must_include, exclude, age_limit, distance = load_config()
    options = Options()     
    options.headless = True
    driver = webdriver.Firefox(options=options)
    # load old jobs
    with open('jobs.json', 'r') as job_json:
        jobs = json.load(job_json)

    jobs = clear_old_jobs(jobs, age_limit)
    old_count = len(jobs["jobs"])
    try:
        for query in queries:
            for location in locations:
                print(f'query: {query}, location: {location} (Indeed)')
                page = 0
                driver.get(f'https://ca.indeed.com/jobs?q={query}&l={location}&radius={distance}&start={page}')
                total_height = int(driver.execute_script("return document.body.scrollHeight"))
                driver.implicitly_wait(3)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                for i in range(1, total_height, random.randint(30, 250)):
                    driver.execute_script("window.scrollTo(0, {});".format(i))                
                    time.sleep(random.randint(1,3))

                while True:
                    titles = get_titles(soup, include, must_include, exclude)
                    links = get_links(titles)
                    locations = get_locations(titles)
                    dates = get_dates(titles)
                    page += 10
                    if page % 50 == 0:
                        print(f'page: {page//10} (Indeed)')

                    for i in range(len(titles)):
                        new_job = {
                            titles[i].get_text().strip(): {
                                "link": links[i],
                                "location": locations[i],
                                "date": dates[i],
                                "new": True
                            }
                        }
                        # only add jobs within the age limit
                        if new_job[titles[i].get_text().strip()]["date"] != 'failed to fetch date':
                            if (datetime.today() - datetime.strptime((new_job[titles[i].get_text().strip()])["date"], '%Y-%m-%d')).days < age_limit: 
                                jobs['jobs'].update(new_job) 
                                print(f'{titles[i].get_text().strip()} (Indeed)')

                    # if no next page
                    time.sleep(random.randint(2,6))
                    if not driver.find_elements(By.XPATH, '/html/body/main/div/div[2]/div/div[5]/div/div[1]/nav/ul/li[6]/a'):
                        break
            
                    driver.get(f'https://ca.indeed.com/jobs?q={query}&l={location}&radius={distance}&start={page}')
                    driver.implicitly_wait(3)
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
    except Exception as e:
        print(f'Error: {e} (Indeed)')

    driver.quit()
    
    new_count = len(jobs["jobs"])
    print(f'Found {abs(old_count - new_count)} new jobs on Indeed')

    result[0] = jobs
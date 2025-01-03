from bs4 import BeautifulSoup 
from datetime import datetime
import requests
import time
import random
import json

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
    titles = soup.find_all("span", {"class": "sr-only"})
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
            links.append(link)
    return links

def get_locations(titles):
    locations = []
    for title in titles:
        location = title.parent.parent.find(class_='job-search-card__location')
        locations.append(location.get_text().strip())
    return locations

def get_dates(titles):
    dates = []
    for title in titles:
        try:
            date = title.parent.parent.find(class_='job-search-card__listdate')
            dates.append(date['datetime'])
        except Exception as e:
            today = datetime.today().strftime('%Y-%m-%d')
            print(f'Error adding date: {e}')
            dates.append(today) # default to today's date 

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

def scrape_linkedin(result):
    queries, query_locations, include, must_include, exclude, age_limit, distance = load_config()
    
    with open('cookies.json', 'r') as cookie_file:
        cookies_data = json.load(cookie_file)
    cookies = {}
    for cookie in cookies_data:
        cookies[cookie['name']] = cookie['value']

    jobs = json.load(open("jobs.json"))
    
    jobs = clear_old_jobs(jobs, age_limit)
    old_count = len(jobs["jobs"])
    try:
        for query in queries:
            time.sleep(random.randint(2,4))
            for q_location in query_locations:
                print(f'query: {query}, location: {q_location} (LinkedIn)')
                page = 0
                html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={q_location}&distance={distance}&start=0', cookies=cookies, headers=requests.utils.default_headers())
                soup = BeautifulSoup(html.text, 'html.parser')
                links = soup.find_all('a')
                while len(links) > 0:
                    time.sleep(random.randint(2,4))
                    titles = get_titles(soup, include, must_include, exclude)
                    links = get_links(titles)
                    locations = get_locations(titles)
                    dates = get_dates(titles)
                    page += 1
                    if page % 100 == 0:
                        print(f'page: {page} (LinkedIn)')
                    
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
                        # don't add if it already exists
                        if new_job[titles[i].get_text().strip()]["date"] != 'failed to fetch date':
                            if (datetime.today() - datetime.strptime((new_job[titles[i].get_text().strip()])["date"], '%Y-%m-%d')).days < age_limit: 
                                jobs['jobs'].update(new_job) 
                                print(f'{titles[i].get_text().strip()} (LinkedIn)')

                    html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={q_location}&distance={distance}&start={page}', cookies=cookies, headers=requests.utils.default_headers())
                    soup = BeautifulSoup(html.text, 'html.parser')
                    links = soup.find_all('a')
        
    except Exception as e:
        print(f'Error: {e} (LinkedIn)')
    new_count = len(jobs["jobs"])
    print(f'Found {abs(old_count - new_count)} new jobs on LinkedIn')

    result[0] = jobs

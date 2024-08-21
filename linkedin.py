from bs4 import BeautifulSoup 
from datetime import datetime
import requests
import time
import random
import json
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
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

def count_jobs(jobs):
    count = 0
    for title, details in jobs['jobs'].items():
        count += 1
    return count

def scrape_linkedin(result):
    queries, locations, include, must_include, exclude, age_limit, distance = load_config()

    # load old jobs
    with open('jobs.json', 'r') as job_json:
        jobs = json.load(job_json)

    jobs = clear_old_jobs(jobs, age_limit)
    old_count = count_jobs(jobs)
    for query in queries:
        time.sleep(random.randint(2,5))
        for location in locations:
            print(f'query: {query}, location: {location}')
            page = 0
            html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={location}&distance={distance}&start=0', headers=headers)
            soup = BeautifulSoup(html.text, 'html.parser')
            links = soup.find_all('a')
            while len(links) > 0:
                time.sleep(random.randint(6,15))
                titles = get_titles(soup, include, must_include, exclude)
                links = get_links(titles)
                locations = get_locations(titles)
                dates = get_dates(titles)
                page += 1
                
                for i in range(len(titles)):
                    new_job = {
                        titles[i].get_text().strip(): {
                            "link": links[i],
                            "location": locations[i],
                            "date": dates[i],
                        }
                    }
                    # only add jobs within the age limit
                    # don't add if it already exists
                    if new_job[titles[i].get_text().strip()]["date"] != 'failed to fetch date':
                        if (datetime.today() - datetime.strptime((new_job[titles[i].get_text().strip()])["date"], '%Y-%m-%d')).days < age_limit: 
                            jobs['jobs'].update(new_job) 
                            print(f'{titles[i].get_text().strip()} (LinkedIn)')

                html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={location}&distance={distance}&start={page}', headers=headers)
                soup = BeautifulSoup(html.text, 'html.parser')
                links = soup.find_all('a')

    new_count = count_jobs(jobs)
    print(f'Found {abs(old_count - new_count)} new jobs on LinkedIn')

    result[0] = jobs

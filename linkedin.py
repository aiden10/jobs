from bs4 import BeautifulSoup 
from datetime import datetime
import requests
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
        if (any(include in title.get_text().strip().lower() for include in includes) 
            and any(must in title.get_text().strip().lower() for must in must_include) 
            and not any(exclude in title.get_text().strip().lower() for exclude in excludes)):
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
            print(f'Error adding date: {e}')
            dates.append('failed to fetch date')

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

def scrape_linkedin():
    queries, locations, include, must_include, exclude, age_limit, distance = load_config()

    # load old jobs
    with open('jobs.json', 'r') as job_json:
        jobs = json.load(job_json)

    jobs = clear_old_jobs(jobs, age_limit)

    for query in queries:
        for location in locations:
            page = 0
            html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={location}&distance={distance}&start=0')
            soup = BeautifulSoup(html.text, 'html.parser')
            while len(soup.find_all('li')) > 0:
                titles = get_titles(soup, include, must_include, exclude)
                links = get_links(titles)
                locations = get_locations(titles)
                dates = get_dates(titles)
                page += 1
                
                for i in range(len(titles)):
                    print(titles[i].get_text().strip())
                    new_job = {
                        titles[i].get_text().strip(): {
                            "link": links[i],
                            "location": locations[i],
                            "date": dates[i],
                        }
                    }
                    # only add jobs within the age limit
                    if new_job[titles[i].get_text().strip()]["date"] != 'failed to fetch date':
                        if (datetime.today() - datetime.strptime((new_job[titles[i].get_text().strip()])["date"], '%Y-%m-%d')).days < age_limit: 
                            jobs['jobs'].update(new_job) 
                            
                html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={location}&distance={distance}&start={page}')
                soup = BeautifulSoup(html.text, 'html.parser')

    # write new job
    with open('jobs.json', 'w') as job_json:
        json.dump(jobs, job_json, indent=4)

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
        title_text = title.get_text().strip().lower()
        includes_matches = [include for include in includes if include in title_text]
        must_include_matches = [must for must in must_include if must in title_text]
        excludes_matches = [exclude for exclude in excludes if exclude in title_text]
        if len(includes_matches) > 0 and len(must_include_matches) > 0 and len(excludes_matches) == 0:
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

def count_jobs(jobs):
    count = 0
    for title, details in jobs['jobs'].items():
        count += 1
    return count

def scrape_linkedin():
    queries, locations, include, must_include, exclude, age_limit, distance = load_config()

    # load old jobs
    with open('jobs.json', 'r') as job_json:
        jobs = json.load(job_json)

    old_count = count_jobs(jobs)

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
                            print(f'{titles[i].get_text().strip()} (LinkedIn)')

                html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={location}&distance={distance}&start={page}')
                soup = BeautifulSoup(html.text, 'html.parser')

    # write new job
    with open('jobs.json', 'w') as job_json:
        json.dump(jobs, job_json, indent=4)

    new_count = count_jobs(jobs)
    print(f'Found {abs(old_count - new_count)} new jobs on LinkedIn')


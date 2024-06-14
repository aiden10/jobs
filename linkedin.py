from bs4 import BeautifulSoup 
import requests
# https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=intern&location=markham,%20on&start=100
LINKEDIN_API = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?'
title_include = ['intern', 'co-op', 'coop'] 
title_exclude = ['marketing', 'hr', 'business', 'investment']
locations = []

"""
TODO
- job titles x
- job links x
- job locations x
- job dates x
- load main function parameters from config file
- refactor main function to use parameters
- save results to json
- delete old jobs from file
"""

def get_titles(soup):
    filtered_titles = []
    titles = soup.find_all("span", {"class": "sr-only"})
    for title in titles:
        if any(include in title.get_text().lower() for include in title_include) and not any(exclude in title.get_text().lower() for exclude in title_exclude):
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
        date = title.parent.parent.find(class_='job-search-card__listdate')
        dates.append(date['datetime'])
    return dates

def scrape():
    html = requests.get('https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=intern&location=markham,%20on&start=0')
    soup = BeautifulSoup(html.text, 'html.parser')
    titles = get_titles(soup)
    links = get_links(titles)
    locations = get_locations(titles)
    dates = get_dates(titles)
scrape()
import requests
from bs4 import BeautifulSoup 
import time
import random
"""
Get html of followers and following 
Parse them
Get names in lists for both
See which names are in following and not in followers
"""
# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
# html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=student&location=Waterloo, ON&distance=50&start=0', headers=headers)
# soup = BeautifulSoup(html.text, 'html.parser')
# links = soup.find_all('a')
# page = 0
# print(f'{len(links)} links found on page {page}')

# while len(links) > 0:
#     wait = random.randint(8, 20)
#     print(f'waiting for {wait} seconds')
#     page+=1
#     time.sleep(wait)
#     print(f'{len(links)} links found on page {page}')
#     html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=student&location=Waterloo, ON&distance=50&start={page}', headers=headers)
#     soup = BeautifulSoup(html.text, 'html.parser')
#     links = soup.find_all('a')

followers = []
following = []
with open('followers.html', encoding='utf8') as html:
    soup = BeautifulSoup(html.read(), 'html.parser')
    f = soup.find_all("span", {"class": "_ap3a _aaco _aacw _aacx _aad7 _aade"})
    for fo in f:
        followers.append(fo.get_text())

with open('following.html', encoding='utf8') as html:
    soup = BeautifulSoup(html.read(), 'html.parser')
    f = soup.find_all("span", {"class": "_ap3a _aaco _aacw _aacx _aad7 _aade"})
    for fo in f:
        following.append(fo.get_text())

for follow in following:
    if follow not in followers:
        print(follow)

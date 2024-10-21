# from bs4 import BeautifulSoup 
# from datetime import datetime, timedelta
# import re
import requests
import json

# date_format = '%Y-%m-%d'
# today = datetime.today()
# with open("testpage.htm", "r", encoding="utf-8") as file:
#     soup = BeautifulSoup(file.read(), "html.parser")
#     titles = soup.select("span[title]")
#     for title in titles:
#         if "Software Developer Student - 4 or 8 Month Winter Term" in title:
#             parent = title.find_parent('td', {'class': 'resultContent css-lf1alc eu4oa1w0'})
#             job_seen_beacon = parent.find_parent('div', {'class': "job_seen_beacon"})
#             date_info = job_seen_beacon.find('span', {'class': 'css-1yxm164 eu4oa1w0'}).text.replace('+', '')
#             days_info = re.sub('\D', '', date_info)
#             if days_info.isdigit() and len(days_info) > 0:
#                 date_t = timedelta(days=int(days_info))
#                 final_date = (today - date_t).strftime(date_format)
#             else: 
#                 print(f"failed to get date for {title.get_text().strip()}: defaulting to today's date")
#                 final_date = today.strftime(date_format) 

with open('cookies.json', 'r') as cookie_file:
    cookies_data = json.load(cookie_file)
cookies = {}
for cookie in cookies_data:
    cookies[cookie['name']] = cookie['value']

url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=intern&location=markham,on&start=2"
response = requests.get(url, cookies=cookies)
print(response.status_code)
print(response.text)
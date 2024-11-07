from linkedin import scrape_linkedin
from indeed import scrape_indeed, write_jobs, merge_jobs
import threading
import json
with open('jobs.json', 'r') as job_json:
    old_jobs = json.load(job_json)

indeed_input = input("Scrape Indeed? (y/n) ")
if indeed_input == 'y': indeed_input = True
else: indeed_input = False

linkedin_input = input("Scrape LinkedIn? (y/n) ")
if linkedin_input == 'y': linkedin_input = True
else: linkedin_input = False

linkedin_jobs = [None]
indeed_jobs = [None]
threads = []

if linkedin_input:
    print("scraping LinkedIn...")
    t1 = threading.Thread(target=scrape_linkedin, args=(linkedin_jobs,))
    t1.start()
    threads.append(t1)

if indeed_input:
    print("scraping Indeed...")
    t2 = threading.Thread(target=scrape_indeed, args=(indeed_jobs,))
    t2.start()
    threads.append(t2)

for thread in threads:
    thread.join()

if linkedin_input or indeed_input:
    all_jobs = merge_jobs(linkedin_jobs[0], indeed_jobs[0])
    write_jobs(all_jobs, old_jobs)

input("Press enter to exit...")

from linkedin import scrape_linkedin
from indeed import scrape_indeed, write_jobs, merge_jobs
import threading

linkedin_jobs = [None]
indeed_jobs = [None]
t1 = threading.Thread(target=scrape_linkedin, args=(linkedin_jobs,))
t2 = threading.Thread(target=scrape_indeed, args=(indeed_jobs,))
t1.start()
t2.start()
t1.join()
t2.join()
all_jobs = merge_jobs(linkedin_jobs[0], indeed_jobs[0])
write_jobs(all_jobs)

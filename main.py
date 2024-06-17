from linkedin import scrape_linkedin
from indeed import scrape_indeed
import time

"""
This isn't really necessary and you could just call scrape_linkedin() directly. 
The loop is just for if you leave it running on some device indefinitely.
"""
scrape_linkedin()
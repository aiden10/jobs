# LinkedIn and Indeed Job Scraper

## Usage
Install the required packages by typing the following command into your terminal: `pip install -r requirements.txt`

Modify the `config.json` file to your liking.

- **queries**: what you want to search 

- **locations**: where you want to search

- **includes**: string that the job title must include (at least one string must be in job title)

- **must_include**: kind of a misnomer since it's the same as 'includes' (at least one string must be in job title)

- **exlcudes**: excludes jobs if the title contains any of the strings in the list

- **age_limit** (days): jobs older than this are not added and once jobs in `jobs.json` become older than this, they are removed

- **distance**: not really sure if this is miles or kilometres, but it's the distance from the location  

Then run the `jobs.bat` file or call the main function directly. And for added convenience you could also add the `jobs.bat` to your start menu or desktop.

After the script finishes, you can open the `index.html` file and view the jobs that have been scraped in your browser. 

![scroll-ezgif com-video-to-gif-converter](https://github.com/aiden10/jobs/assets/51337166/65ca110f-abfa-43d8-8bd0-264eb793d7f9)

Example:
```
{
    "queries": [
        "student",
        "co-op",
        "intern"
    ],
    
    "locations": [
        "Whitby, ON",
        "Markham, ON",
        "Waterloo, ON",
        "Toronto, ON",
        "Ottawa, ON"
    ],
    "includes": [
        "software engineering",
        "software engineer",
        "software",
        "technology",
        "computer", 
        "full stack",
        "full-stack",
        "backend",
        "frontend",
        "qa",
        "automation",
        "data",
        "developer",
        "mobile",
        "web",
        "it",
        "quality assurance"
    ],
    "must_include": [
        "intern",
        "co-op",
        "student",
        "coop"
    ],
    "excludes": [
        "marketing",
        "business",
        "administrative",
        "sales",
        "economics",
        "writer",
        "finance",
        "marketeer",
        "civil",
        "mechanical",
        "accounting",
        "accountant"
    ],
    "age_limit": 14,
    "distance": 25
}
```

## Note
- Adding too many locations and queries will greatly increase the time it takes to run because they're in a nested loop (depending on the amount of jobs/pages), so try not to add too many. 
- Indeed might block the script if it makes too many visits since I'm sure they have countermeasures to prevent scraping even though I haven't noticed any so far.
- The LinkedIn API might also stop working at some point in the near future.

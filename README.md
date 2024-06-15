# LinkedIn Job Scraper
plan to also scrape indeed but that's a bit tougher

## Usage
Modify the `config.json` file to your liking.

- **queries**: what you want to search 

- **locations**: where you want to search

- **includes**: string that the job title must include (at least one string must be in job title)

- **must_include**: kind of a misnomer since it's the same as 'includes' (at least one string must be in job title)

- **exlcudes**: excludes jobs if the title contains any of the strings in the list

- **age_limit** (days): jobs older than this are not added and once jobs in `jobs.json` become older than this, they are removed

- **distance**: not really sure if this is miles or kilometres, but it's the distance from the location  

Then run the main file or call the `scrape_linkedin` function directly. 

After, you can open the `index.html` file and view the jobs that have been scraped in your browser. 

![jobs-ezgif com-video-to-gif-converter](https://github.com/aiden10/jobs/assets/51337166/d304ff80-28f4-46f2-ba24-1f6ec0fd2b85)

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

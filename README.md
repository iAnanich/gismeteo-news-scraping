# gismeteo-news-scraping

scrapinghub project for scraping news from https://www.gismeteo.ua/news/

## Usage

Project is writen on Python 3 (tested on 3.5).

It have two spiders:
* `news-list` - scrapes only new news from news' list (with urls) and saves their urls
* `event` - scrapes full articles, which urls was scraped by `news-list` on latest job

`event` spider saves items into Google Drive Sheet

#### Google API key

Follow steps [from this page](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html)
to generate `.json` key and save it to `gismeteo` folder with `client-secret.json` name.

#### Deploying

Connection to Scrapy Cloud via GitHub mustn't work because it doesn't support Python 3.
So you need to use `shub` command line tool.

Define your project id for each `shub deploy` call, or edit `scrapinghub.yml`.

#### Running

When editing job on Scrapy Cloud, you need to define some arguments:
* `API_KEY` - your ScrapingHub API key (used to access ScrapyCloud API)
* `FORCE` - set `True` to get error message when other arguments missed
(it exist because `shub` runs spiders without arguments when deploying them to cloud)
* `SPREADSHEET_TITTLE` - name of your Google Drive Sheet
* `PROJECT_ID` - id of ScrapingHub project from what your spiders will take latest job's data

To run spiders locally, define those arguments as for spider:
```
scrapy crawl <spider> -a <key>=<value> ...
```

#### Storage

`event` spider (I mean Pipeline, when EventSpider runs) appends (adds new row, so in scratch Google Drive Sheet
it will have 1000+ index, so it is recomended to remove first 999 rows)
url, header, tags and body of article to **second** worksheet (so it
must be created before, or spider will raise an RuntimeError), and when
all items where added, spider ends his work with a row that contains
url to job, CPU datetime and two '-----' strings.

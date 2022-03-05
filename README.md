# Simple Universal Scraper
[![Python package](https://github.com/ResupinePuma/SUS/actions/workflows/python-package.yml/badge.svg)](https://github.com/ResupinePuma/SUS/actions/workflows/python-package.yml) 

Scrape Telegram, Reddit and Rss by link. This is demo project.

## Install

```
git clone https://github.com/ResupinePuma/SUS.git
cd SUS && pip install . 
```


## Usage

```
from SUS.sus import Scraper

urls = ["https://t.me/<some channel>","https://reddit.com/r/<some thread>,"<some rss url>"]

s = Scraper()
results = s.parse(urls)
```

Output example
```
{
    "https://some_url" : Publication(title, content, url, media)
}
```

## To-Do

- Async support
- Media scraping
- More engines

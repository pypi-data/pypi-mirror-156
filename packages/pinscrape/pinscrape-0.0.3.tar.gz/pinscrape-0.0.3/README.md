# pinscrape
[![built with Python3](https://img.shields.io/badge/built%20with-Python3.x-red.svg)](https://www.python.org/)

### This package can be use to scrape images from pinterest just by using any search keywords. Install it just by using <br><br>
`pip install pinscrape`
### How to use?
```
from pinscrape import pinscrape
is_downloaded = pinscrape.scraper.scrape("messi", "output", {}, 10) 

if is_downloaded:
    print("\nDownloading completed !!")
else:
    print("\nNothing to download !!")
```

#### scrape("messi", "output", {}, 10) here `"messi"` is keyword, `"output"` is path to a folder where you want to save images, `{}` is proxy if you want to add and finally `10` is a number of threads you want to use for downloading those images

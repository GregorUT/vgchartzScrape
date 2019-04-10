
vgchartzfull is a python script with multiprocessing based on BeautifulSoup.
proxies are implemented in the script but it is disabled due to free proxies are unreliable and could results in running the program longer. It can be enabled by changing it to True

It creates a dataset based on data from 
http://www.vgchartz.com/gamedb/

The dataset is saved as vgsales-%Y-%m-%d_%H_%M_%S.csv.

You will need to have the following dependencies installed:
```
BeautifulSoup4 
pandas
numpy
requests
unidecode
user_agent
```

Thanks to Chris Albon.
http://chrisalbon.com/python/beautiful_soup_scrape_table.html
https://www.kdnuggets.com/2018/02/web-scraping-tutorial-python.html

vgchartzfull is a python script with multiprocessing based on BeautifulSoup.
proxies are implemented in the script, it can be disabled by changing it to False

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

Thanks to:
- https://www.kdnuggets.com/2018/02/web-scraping-tutorial-python.html
- http://python.omics.wiki/multiprocessing_map/multiprocessing_partial_function_multiple_arguments
- https://medium.com/datadriveninvestor/speed-up-web-scraping-using-multiprocessing-in-python-af434ff310c5


Free proxies:
[1](https://proxyscrape.com/free-proxy-list)
[2](http://multiproxy.org/txt_all/proxy.txt)
[3](https://proxy.rudnkh.me/txt)
[4](https://www.us-proxy.org/)

- [x] added multiprocessing for faster results with a maximum of 24 workers.
- [x] added proxies to avoid being blocked 
- [x] handling couple of exceptions
- [x] scraped data gets saved before raising an unexpected error
- [x] add the option to continue where we left off due to an unexpected error
- [x] clean version removes the print statements, should results in better performance!
- [ ] optimize it
- [ ] create a log file
- [ ] convert the script to a class or use scrapy, reference
    - https://edmundmartin.com/multi-threaded-crawler-in-python/
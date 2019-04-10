
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

Thanks to:
- https://www.kdnuggets.com/2018/02/web-scraping-tutorial-python.html
- http://python.omics.wiki/multiprocessing_map/multiprocessing_partial_function_multiple_arguments
- https://medium.com/datadriveninvestor/speed-up-web-scraping-using-multiprocessing-in-python-af434ff310c5


Free proxies:
[1](https://proxyscrape.com/free-proxy-list)
[2](http://multiproxy.org/txt_all/proxy.txt)
[3](https://proxy.rudnkh.me/txt)
[4](https://www.us-proxy.org/)

- [ ] convert the script to a class or use scrapy, reference
https://edmundmartin.com/multi-threaded-crawler-in-python/
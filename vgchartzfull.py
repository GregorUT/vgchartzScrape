from bs4 import BeautifulSoup
import urllib
import pandas as pd

pages = 18
rec_count = 0
rank = []
gname = []
platform = []
year = []
genre = []
publisher = []
sales_na = []
sales_eu = []
sales_jp = []
sales_ot = []
sales_gl = []

urlhead = 'http://www.vgchartz.com/gamedb/?page='
urltail = '&results=1000&name=&platform=&minSales=0.01&publisher=&genre=&sort=GL'

for page in range(1,pages):
	surl = urlhead + str(page) + urltail	
	r = urllib.urlopen(surl).read()
	soup = BeautifulSoup(r)
	print page
	chart = soup.find("table", class_="chart")
	for row in chart.find_all('tr')[1:]:
		try: 
			col = row.find_all('td')
		
			#extract data into column data
			column_1 = col[0].string.strip()
			column_2 = col[1].string.strip()		
			column_3 = col[2].string.strip()		
			column_4 = col[3].string.strip()		
			column_5 = col[4].string.strip()	
			column_6 = col[5].string.strip()
			column_7 = col[6].string.strip()		
			column_8 = col[7].string.strip()		
			column_9 = col[8].string.strip()		
			column_10 = col[9].string.strip()		
			column_11 = col[10].string.strip()

			#Add Data to columns
			#Adding data only if able to read all of the columns
			rank.append(column_1)
			gname.append(column_2)
			platform.append(column_3)
			year.append(column_4)
			genre.append(column_5)
			publisher.append(column_6)
			sales_na.append(column_7)
			sales_eu.append(column_8)
			sales_jp.append(column_9)
			sales_ot.append(column_10)
			sales_gl.append(column_11)
		
			rec_count += 1
	
		except:
			continue

columns = {'rank': rank, 'name': gname, 'platform': platform, 'year': year, 'genre': genre, 'publisher': publisher, 'NA_Sales':sales_na, 'EU_Sales': sales_eu,'JP_Sales': sales_jp,'Other_Sales':sales_ot, 'Global_Sales':sales_gl }
print rec_count
df = pd.DataFrame(columns)
df = df[['Rank','Name','Platform','Year','Genre','Publisher','NA_Sales','EU_Sales','JP_Sales','Other_Sales','Global_Sales']]
del df.index.name
df.to_csv("vgsales.csv",sep=",",encoding='utf-8')



from bs4 import BeautifulSoup   #for web scraping
import urllib                   #for opening urls
import pandas as pd             # for data frames
import time                     # for time
import datetime                 # for dates

#global constants
gc_dflt_max_time = 300 # seconds
gc_output_filename ='vgsales'
gc_output_filetype ='csv'

#global variables
dflt_max_rec = 10
data_list = []
pages = 0
items_scraped = 0
data_exists = True

class NotPositiveError(UserWarning):
	pass

# Define a function row of type game 
# Argument passed in must be of type BeautifulSoup row
def vgchartz_parse(row):
        game = {}
        #get columns from the row we passed in
        cols = row.find_all("td")
        if cols:
                # Start to build our data grid, defining appropriate names
                game["rank"]            =cols[0].string.strip()
                game["gname"]           =cols[2].text.strip()
                game["platform"]        =cols[3].find('img').get('alt')
                game["developer"]       =cols[4].string.strip()
                game["publisher"]       =cols[5].string.strip()
                game["criticscore"]     =cols[6].string.strip()
                game["userscore"]       =cols[7].string.strip()
                game["sales_tot"]       =cols[8].string.strip()
                game["sales_na"]        =cols[9].string.strip() 
                game["sales_eu"]        =cols[10].string.strip() 
                game["sales_jp"]        =cols[11].string.strip() 
                game["sales_ot"]        =cols[12].string.strip() 
                game["year"]            =cols[13].string.strip() 
                game["lst_update"]      =cols[14].string.strip() 
                        
        return game               

#Get maximum number of records from the user.
#Try-Except conditions to ensure that
#       i) Figure is a number
#       ii) Figure is Positive
#       iii) If no entry is made (use to revert to our default in dflt_max_rec)
while True:
        try:
                print('Enter the maximum number of records to scrape')
                in_max = input()
                if (in_max.strip() == ""):
                        print('Running for maximum '+str(dflt_max_rec)+' records')
                        break
                elif int(in_max) <= 0:
                        #make sure value is positive, otherwise raise user defined error
                        raise NotPositiveError
                        break
                elif int(in_max) > 0:
                        #update variable with new value
                        dflt_max_rec = in_max
                        print('Running for '+str(in_max)+' records')
                        break
                
        except ValueError:
                print("This was not a number, please try again.")
        except NotPositiveError:
                print("The number was not positive, please try again.")
                
start_time = time.time()
print('Starting scrape...')

while data_exists:

        #This is the page number used in the url query. 
        pages +=1
                
        #concat url to include page number
        url = 'http://www.vgchartz.com/gamedb/?page=' + str(pages) + '&results=1000&name=&console=&keyword=&publisher=&genre=&order=Sales&ownership=Both&boxart=Both&showdeleted=&region=All&developer=&goty_year=&alphasort=&showtotalsales=1&shownasales=1&showpalsales=1&showjapansales=1&showothersales=1&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1&showvgchartzscore=0&showcriticscore=1&showuserscore=1'
        #url='file:GameDataScrape/vgchartz.htm'#save the site locally first for development purposes instead of hitting the site
        #open url
        r = urllib.request.urlopen(url).read()
         
        #use beautiful soup
        soup = BeautifulSoup(r, "html.parser")
        
        divparent = soup.find('div', id = 'generalBody')

        table = divparent.find('table', width = '968')

        #Skipping to 3rd row from VGChartz to avoid menu rows and increment max_dat
        for row in table.find_all('tr')[3:]:

                #create a row of the type we desire
                vg_game_info = vgchartz_parse(row)
                
                #Gets values in named columns                      
                columns = {'Rank': vg_game_info['rank'], 'Name': vg_game_info['gname'], \
                           'Platform': vg_game_info['platform'], 'Developer': vg_game_info['developer'],\
                           'Publisher': vg_game_info['publisher'], 'Critic_Score': vg_game_info['criticscore'],\
                           'User_Score': vg_game_info['userscore'],'Global_Sales':vg_game_info['sales_tot'],\
                           'NA_Sales':vg_game_info['sales_na'], 'EU_Sales': vg_game_info['sales_eu'],\
                           'JP_Sales': vg_game_info['sales_jp'],'Other_Sales':vg_game_info['sales_ot'], \
                           'Year': vg_game_info['year']}
        
                items_scraped +=1

                #What are our end conditions to break out the loop??
                #1. End if the maximum number of records is reached which is determined by
                # i) global constant default value in 'dflt_max_rec'
                # ii) over-ridden 'gc_default_max' with new max
                if (int(dflt_max_rec) == items_scraped):
                                print('***Reached max data limit, ending scrape process...')
                                data_exists = False
                                break
                                      
                #2. End of we've been running for too long, arbitrary number stored in max_time_limit
                elif (round(time.time() - start_time, 2)>gc_dflt_max_time):
                                print('***Reached max time limit, ending scrape process...')
                                data_exists = False
                                break
                        
                #3. End if games do not have any sale data, not interested otherwise
                # i) Bespoke to your purpose, update or remove
                if (vg_game_info["sales_tot"] == "0.00" or vg_game_info["sales_tot"] == "0.00m"):
                                print('***No more relvent data available, ending scrape process...')
                                data_exists = False
                                break
                        
                #append to a list of data so we can save this row for later
                data_list.append(columns)

print('...Scrape completed')
print()
print('Now writing to file')

#Use pandas create data frame from our games list                
df = pd.DataFrame(data_list)

#list of columns
df = df[['Rank','Name','Platform','Publisher','Developer','Critic_Score','User_Score','Global_Sales','NA_Sales','EU_Sales','JP_Sales','Other_Sales','Year']]

del df.index.name

#write out to file
filename = gc_output_filename+'-' + datetime.datetime.now().strftime("%Y%m%d-%H_%M_%S") + '.'+gc_output_filetype
df.to_csv(filename,sep=",",encoding='utf-8')
print ('Writing scraped data to', filename)

elapsed_time = time.time() - start_time
print()
print('Filewrite completed')
print()
print('Record Count: '+str(items_scraped))
print()
print( 'Scraped', items_scraped, 'records over',pages, 'pages in', round(elapsed_time, 2), 'seconds.')
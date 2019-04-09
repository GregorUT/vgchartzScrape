from bs4 import BeautifulSoup, element
import pandas as pd
import numpy as np
import requests
import time
import unidecode
from user_agent import generate_user_agent
from proxies_gen import get_proxies
from itertools import cycle
from lxml.html import fromstring
# import threading
from multiprocessing import Pool  # This is a thread-based Pool
from multiprocessing import cpu_count


rec_count = 0
thread_counter = 0
start_time = time.time()
current_time = time.time()
csvfilename = "vgsales-" + time.strftime("%Y-%m-%d_%H_%M_%S") + ".csv"


# initialize a panda dataframe to store all games with the following columns:
# rank, name, img-url, vgchartz score, genre, ESRB rating, platform, developer,
# publisher, release year, critic score, user score, na sales, pal sales,
# jp sales, other sales, total sales, total shipped, last update, url, status
# last two columns for debugging

df = pd.DataFrame(columns=[
    'Rank', 'Name', 'basename', 'Genre', 'ESRB_Rating', 'Platform', 'Publisher',
    'Developer', 'VGChartz_Score', 'Critic_Score', 'User_Score',
    'Total_Shipped', 'Global_Sales', 'NA_Sales', 'PAL_Sales', 'JP_Sales',
    'Other_Sales', 'Year', 'Last_Update', 'url', 'status'])

urlhead = 'http://www.vgchartz.com/games/games.php?page='
urltail = '&results=20&name=&console=&keyword=&publisher=&genre=&order=Sales&ownership=Both'
urltail += '&banner=Both&showdeleted=&region=All&goty_year=&developer='
urltail += '&direction=DESC&showtotalsales=1&shownasales=1&showpalsales=1&showjapansales=1'
urltail += '&showothersales=1&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1'
urltail += '&showvgchartzscore=1&showcriticscore=1&showuserscore=1&showshipped=1&alphasort=&showmultiplat=Yes&showgenre=1'


def parse_games(game_tags):
    """
    parse the games table on current page
    parameters:
    game_tags: games tags after reading the html page
    df: the dataframe where we will store the games
    """
    global rec_count
    global df
    for tag in game_tags:
        game = {}
        game["Name"] = " ".join(tag.string.split())
        # print(f"{rec_count + 1} Fetch data for game {game['Name']}")
        print(rec_count+1, 'Fetch Data for game', unidecode.unidecode(game['Name']))

        data = tag.parent.parent.find_all("td")
        if data:
            game["Rank"] = np.int32(data[0].string)
            game["img_url"] = data[1].a.img.get('src')
            game["url"] = data[2].a.get('href')
            if len(game["Name"].split("/")) > 1:
                # replace accented chars with ascii
                game["basename"] = unidecode.unidecode(
                    game['Name'].strip().split('/')[0].strip().replace(' ', '-'))
            else:
                game["basename"] = game["url"].rsplit('/', 2)[1]
            game["Platform"] = data[3].img.get('alt')
            game["Publisher"] = data[4].get_text().strip()
            game["Developer"] = data[5].get_text().strip()
            game["Vgchartzscore"] = data[6].get_text().strip()
            game["Critic_Score"] = float(
                data[7].string) if not data[7].string.startswith("N/A") else np.nan
            game["User_Score"] = float(
                data[8].string) if not data[8].string.startswith("N/A") else np.nan
            game["Total_Shipped"] = float(
                data[9].string[:-1]) if not data[9].string.startswith("N/A") else np.nan
            game["Global_Sales"] = float(
                data[10].string[:-1]) if not data[10].string.startswith("N/A") else np.nan
            game["NA_Sales"] = float(
                data[11].string[:-1]) if not data[11].string.startswith("N/A") else np.nan
            game["PAL_Sales"] = float(
                data[12].string[:-1]) if not data[12].string.startswith("N/A") else np.nan
            game["JP_Sales"] = float(
                data[13].string[:-1]) if not data[13].string.startswith("N/A") else np.nan
            game["Other_Sales"] = float(
                data[14].string[:-1]) if not data[14].string.startswith("N/A") else np.nan
            year = data[15].string.split()[-1]
            if year.startswith('N/A'):
                game["Year"] = 'N/A'
            else:
                if int(year) >= 80:
                    year_to_add = np.int32("19" + year)
                else:
                    year_to_add = np.int32("20" + year)
            game["Year"] = year_to_add
            game["Last_Update"] = data[16].get_text().strip()
            game['Genre'] = 'N/A'
            game['ESRB_Rating'] = 'N/A'
            game['status'] = 0
            df = df.append(game, ignore_index=True)
        rec_count += 1


def parse_genre_esrb(df):
    """
    loads every game's url to get genre and esrb rating
    """
    count = 0
    # global thread_counter
    # thread_counter += 1

    headers = {'User-Agent': generate_user_agent(
        device_type='desktop', os=('mac', 'linux'))}
    
    proxies = get_proxies()
    proxy = cycle(proxies)

    for index, row in df.loc[df['status'] == 0].iterrows():
        # we only want to scrape 200 games at a time.
        if count == 200:
            break
        try:
            # uses global headers and proxies
            game_page = requests.get(
                df.at[index, 'url'], headers=headers, proxies={"http": proxy, "https": proxy})
            if game_page.status_code == 200:
                sub_soup = BeautifulSoup(game_page.text, "lxml")
                # again, the info box is inconsistent among games so we
                # have to find all the h2 and traverse from that to the genre
                gamebox = sub_soup.find("div", {"id": "gameGenInfoBox"})
                h2s = gamebox.find_all('h2')
                # make a temporary tag here to search for the one that contains
                # the word "Genre"
                temp_tag = element.Tag
                for h2 in h2s:
                    if h2.string == 'Genre':
                        temp_tag = h2
                df.at[index, 'Genre'] = temp_tag.next_sibling.string

                # find the ESRB rating
                game_rating = gamebox.find('img').get('src')
                if 'esrb' in game_rating:
                    df.at[index, 'ESRB_Rating'] = game_rating.split(
                        '_')[1].split('.')[0].upper()

                # we successfuly got the genre and rating if available
                df.at[index, 'status'] = 1
                print('Successfully scraped genre and rating for :', df.at[index, 'Name'])
        except:
            print('Something went wrong while connecting to', df.at[index, 'Name'], 'url, will try again later')
            # probably something went wrong the proxy?
            proxy = next(proxies)

        # wait for 2 seconds between every call
        time.sleep(2)
        count += 1


# def retry_games():
#     """try to scrape the missing data again"""
#     global df
#     # run every 5 minutes
#     t = threading.Timer(300.0, retry_games)
#     t.start()
#     print("Starting to scrape missing data")
#     if len(df[df['status'] == 0]) == 0:
#         t.cancel()
#     else:
#         parse_genre_esrb()


# get the number of pages
page = requests.get('http://www.vgchartz.com/gamedb/').text
x = fromstring(page).xpath("//th[@colspan='3']/text()")[0].split('(', 1)[1].split(')')[0]
pages = np.ceil(int(x.replace(',', ""))/1000)

pages = 2
for page in range(1, pages):  # pages = 2 for debugging!
    surl = urlhead + str(page) + urltail
    r = requests.get(surl).text
    soup = BeautifulSoup(r, 'lxml')
    print('Scraping page:', page)

    # vgchartz website is really weird so we have to search for
    # <a> tags with game urls
    game_tags = list(filter(
        lambda x: x.attrs['href'].startswith('http://www.vgchartz.com/game/'),
        # discard the first 10 elements because those
        # links are in the navigation bar
        soup.find_all("a")
    ))[10:]
    parse_games(game_tags)


# # this should repeatedly try scrape genre and rating until it reaches this number of calls

NUM_WORKERS = cpu_count() * 2
while len(df.loc[df['status'] == 0]) > 0:
    chunks = NUM_WORKERS // len(df.loc[df['status'] == 0])
    df_subsets = np.array_split(
        df, chunks) if chunks != 0 else np.array_split(df, 1)
    if __name__ == "__main__":
        with Pool(NUM_WORKERS) as p:
            p.map(parse_genre_esrb, df_subsets)
    
    ## add sleep, maybe proxies and headers here? better right?


# chunk_size = int(df.shape[0] / 4)
# for start in range(0, df.shape[0], chunk_size):
#     df_subset = df.iloc[start:start + chunk_size]
#     process_data(df_subset)

# select only these columns in the final dataset
df_final = df[[
    'Rank', 'Name', 'Platform', 'Year', 'Genre', 'ESRB_Rating',
    'Publisher', 'Developer', 'Critic_Score', 'User_Score',
    'Global_Sales', 'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales']]
df_final.to_csv(csvfilename, sep=",", encoding='utf-8', index=False)

elapsed_time = time.time() - start_time
print("Scraped", rec_count, "games in", round(elapsed_time, 2), "seconds.")
print("Wrote scraper data to", csvfilename)

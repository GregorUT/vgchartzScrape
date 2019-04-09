from bs4 import BeautifulSoup, element
import pandas as pd
import numpy as np
import requests
import time
import unidecode
from user_agent import generate_user_agent
from proxies_gen import get_proxies, test_proxies
from itertools import cycle
from lxml.html import fromstring
from multiprocessing import Pool  # This is a thread-based Pool
from requests.exceptions import ConnectionError, Timeout, ProxyError
import sys
sys.setrecursionlimit(10000) # need to optimize code.

rec_count = 0
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

    headers = {'User-Agent': generate_user_agent(
        device_type='desktop', os=('mac', 'linux'))}  

    print("'\n'******getting list of proxies and testing them******'\n'")
    #proxies = set(requests.get('https://proxy.rudnkh.me/txt').text.split())
    #proxies = get_proxies()
    # proxies = test_proxies(proxies)
    #proxy = cycle(proxies)
    print('******begin scraping for Genre and Rating******')

    for index, row in df.iterrows():
        try:
            #game_page = requests.get(df.at[index, 'url'], headers=headers, proxies={"http": proxy, "https": proxy})
            game_page = requests.get(df.at[index, 'url'])
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
                df.loc[index, 'Genre'] = temp_tag.next_sibling.string

                # find the ESRB rating
                game_rating = gamebox.find('img').get('src')
                if 'esrb' in game_rating:
                    df.loc[index, 'ESRB_Rating'] = game_rating.split(
                        '_')[1].split('.')[0].upper()
                # we successfuly got the genre and rating
                df.loc[index, 'status'] = 1
                print('Successfully scraped genre and rating for :', df.at[index, 'Name'])
            #else:
                #proxies.remove(proxy)
                #proxy = next(proxies)

        except (ConnectionError, Timeout):
            print('Something went wrong while connecting to', df.at[index, 'Name'], 'url, will try again later')

        #except(ProxyError):
            #proxies.remove(proxy)
            #proxy = next(proxies)

        # wait for 2 seconds between every call,
        # we do not want to get blocked or abuse the server
        time.sleep(2)
    return df

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


def retry_game():
    """try to scrape the missing data again"""
    global df
    failed_games = len(df['status'] == 0)
    # every worker can have 100 games at max
    NUM_WORKERS = int(np.ceil(failed_games/100))
    df_subsets = np.array_split(df, NUM_WORKERS)
    print(df_subsets)
    pool = Pool(processes=NUM_WORKERS)
    result = pool.map(parse_genre_esrb, df_subsets)
    updated_df = pd.concat([i for i in result if not i.empty])
    pool.close()
    pool.join()
    return updated_df if len(updated_df) > 0 else df


if __name__ == "__main__":
    while len(df['status']) > 0 or time.time() - start_time >= 300: # change to one day
        df = retry_game()
    #df = retry_game()
    elapsed_time = time.time() - start_time
    print("Scraped", rec_count, "games in", round(elapsed_time, 2), "seconds.")

    # select only these columns in the final dataset
    df_final = df[[
        'Rank', 'Name', 'Platform', 'Year', 'Genre', 'ESRB_Rating',
        'Publisher', 'Developer', 'Critic_Score', 'User_Score',
        'Global_Sales', 'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales']]

    df_final.to_csv(csvfilename, sep=",", encoding='utf-8', index=False)
    print("Wrote scraper data to", csvfilename)

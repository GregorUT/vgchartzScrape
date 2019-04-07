from bs4 import BeautifulSoup, element
import urllib
import pandas as pd
import numpy as np
import requests
import time 
from user_agent import generate_user_agent

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv: 12.0) Gecko/20100101 Firefox/12.0'}
# generate a new header for every new page
headers = {'User-Agent': generate_user_agent(device_type = 'desktop', os=('mac', 'linux'))}

pages = 56
rec_count = 0
rank = []
gname = []
platform = []
year = []
genre = []
critic_score = []
user_score = []
publisher = []
developer = []
sales_na = []
sales_pal = []
sales_jp = []
sales_ot = []
sales_gl = []
rating = []

urlhead = 'http://www.vgchartz.com/games/games.php?page='
urltail = '&results=200&name=&console=&keyword=&publisher=&genre=&order=Sales&ownership=Both'
urltail += '&banner=Both&showdeleted=&region=All&goty_year=&developer='
urltail += '&direction=DESC&showtotalsales=1&shownasales=1&showpalsales=1&showjapansales=1'
urltail += '&showothersales=1&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1'
urltail += '&showvgchartzscore=1&showcriticscore=1&showuserscore=1&showshipped=1&alphasort=&showmultiplat=Yes&showgenre=1'

for page in range(1, pages):
    surl = urlhead + str(page) + urltail
    r = urllib.request.urlopen(surl).read()
    soup = BeautifulSoup(r)
    print(f"Page: {page}")

    # vgchartz website is really weird so we have to search for
    # <a> tags with game urls
    game_tags = list(filter(
        lambda x: x.attrs['href'].startswith('http://www.vgchartz.com/game/'),
        # discard the first 10 elements because those
        # links are in the navigation bar
        soup.find_all("a")
    ))[10:]

    for tag in game_tags:

        # add name to list
        gname.append(" ".join(tag.string.split()))
        print(f"{rec_count + 1} Fetch data for game {gname[-1]}")

        # get different attributes
        # traverse up the DOM tree
        data = tag.parent.parent.find_all("td")
        rank.append(np.int32(data[0].string))
        platform.append(data[3].find('img').attrs['alt'])
        publisher.append(data[4].string)
        developer.append(data[5].string)
        critic_score.append(
            float(data[7].string) if
            not data[7].string.startswith("N/A") else np.nan)
        user_score.append(
            float(data[8].string) if
            not data[8].string.startswith("N/A") else np.nan)
        sales_na.append(
            float(data[11].string[:-1]) if
            not data[11].string.startswith("N/A") else np.nan)
        sales_pal.append(
            float(data[12].string[:-1]) if
            not data[12].string.startswith("N/A") else np.nan)
        sales_jp.append(
            float(data[13].string[:-1]) if
            not data[13].string.startswith("N/A") else np.nan)
        sales_ot.append(
            float(data[14].string[:-1]) if
            not data[14].string.startswith("N/A") else np.nan)
        sales_gl.append(
            float(data[10].string[:-1]) if
            not data[10].string.startswith("N/A") else np.nan)
        release_year = data[15].string.split()[-1]
        # different format for year
        if release_year.startswith('N/A'):
            year.append('N/A')
        else:
            if int(release_year) >= 80:
                year_to_add = np.int32("19" + release_year)
            else:
                year_to_add = np.int32("20" + release_year)
            year.append(year_to_add)

        # go to every individual website to get genre info
        url_to_game = tag.attrs['href']
        try:
            #site_raw = urllib.request.urlopen(url_to_game).read()
            site_raw = requests.get(url_to_game, headers=headers)
            sub_soup = BeautifulSoup(site_raw.text, "lxml")
            # again, the info box is inconsistent among games so we
            # have to find all the h2 and traverse from that to the genre name
            gamebox = sub_soup.find("div", {"id": "gameGenInfoBox"})
            h2s = gamebox.find_all('h2')
            # make a temporary tag here to search for the one that contains
            # the word "Genre"
            temp_tag = element.Tag
            for h2 in h2s:
                if h2.string == 'Genre':
                    temp_tag = h2
            genre.append(temp_tag.next_sibling.string)
            #find the ESRB rating
            game_rating = gamebox.find('img').get('src')
            if 'esrb' in game_rating:
                rating.append(game_rating[game_rating.index('esrb'):])
        except:
            print('something wrong with game url:', url_to_game, 'code:', site_raw.status_code)
            genre.append(np.nan)
            rating.append(np.nan)

        time.sleep(5)
        rec_count += 1

columns = {
    'Rank': rank,
    'Name': gname,
    'Platform': platform,
    'Year': year,
    'Genre': genre,
    'Critic_Score': critic_score,
    'User_Score': user_score,
    'Publisher': publisher,
    'Developer': developer,
    'NA_Sales': sales_na,
    'PAL_Sales': sales_pal,
    'JP_Sales': sales_jp,
    'Other_Sales': sales_ot,
    'Global_Sales': sales_gl
}
print(rec_count)
df = pd.DataFrame(columns)
print(df.columns)
df = df[[
    'Rank', 'Name', 'Platform', 'Year', 'Genre',
    'Publisher', 'Developer', 'Critic_Score', 'User_Score',
    'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']]
df.to_csv("vgsales.csv", sep=",", encoding='utf-8', index=False)

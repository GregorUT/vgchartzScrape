from bs4 import BeautifulSoup, element
import urllib
import pandas as pd
import numpy as np
import datetime
import time

# Environment & buffers
rec_count = 0
page_size = 10
pages = 4          # 57,453 / 1000 = 58 (At the time of this writing)

rank = []
game_name = []
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

def main ():
    """
    Main Crawler Loop

    :return: a csv file :)
    """

    for page in range(1, pages):

        try:
            surl = generate_uri(page_number=str(page), page_size=page_size)
            r = urllib.request.urlopen(surl).read()
            soup = BeautifulSoup(r, features="html.parser")
            print(f"Crawling page: {page} of {pages}")

            # We locate the game from <a> tags with game urls
            game_tags = list(filter(
                lambda x: x.attrs['href'].startswith('http://www.vgchartz.com/game/'),
                # discard the first 10 elements because those links are in the navigation bar
                soup.find_all("a")
            ))[10:]

            # Loop for each line received
            for tag in game_tags:
                parse_game(tag=tag)

        except urllib.error.HTTPError as e:
            print("Unexpected error:", sys.exc_info()[0])
            print(e.code)
            print(e.read())

            time.sleep(15)

        finally:
            # Crawlers: The Friend Nobody Likes
            time.sleep(60)

    # Generate and export to CSV
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    df.to_csv(f"vgsales-{timestamp}.csv", sep=",", encoding='utf-8', index=False)


def generate_uri(*, page_number, page_size):
    """

    Generate the uri from page number

    :param page_number:
    :return:
    """

    urlhead = 'http://www.vgchartz.com/gamedb/?page='
    # page_number... <= here comes the param received
    urltail = f'&results={page_size}'
    urltail += '&order=Sales'
    urltail += '&region=All'
    urltail += '&boxart=Both'
    urltail += '&banner=Both'
    urltail += '&ownership=Both'
    urltail += '&keyword='
    urltail += '&console='
    urltail += '&developer='
    urltail += '&publisher='
    urltail += '&goty_year='
    urltail += '&genre='
    urltail += '&showmultiplat=No'
    urltail += '&showtotalsales=0'
    urltail += '&showtotalsales=1'
    urltail += '&showpublisher=0'
    urltail += '&showpublisher=1'
    urltail += '&showvgchartzscore=0'
    urltail += '&showvgchartzscore=1'
    urltail += '&shownasales=0'
    urltail += '&shownasales=1'
    urltail += '&showdeveloper=0'
    urltail += '&showdeveloper=1'
    urltail += '&showcriticscore=0'
    urltail += '&showcriticscore=1'
    urltail += '&showpalsales=0'
    urltail += '&showpalsales=1'
    urltail += '&showreleasedate=0'
    urltail += '&showreleasedate=1'
    urltail += '&showuserscore=0'
    urltail += '&showuserscore=1'
    urltail += '&showjapansales=0'
    urltail += '&showjapansales=1'
    urltail += '&showlastupdate=0'
    urltail += '&showlastupdate=1'
    urltail += '&showothersales=0'
    urltail += '&showothersales=1'
    urltail += '&showshipped=0'
    urltail += '&showshipped=1'

    return urlhead + str(page_number) + urltail

def parse_game(*, tag):
    """
    Parse a game and navigate to its particular url to grab its data

    :param tag:
    :return:
    """

    # Add name to list
    game_name.append(" ".join(tag.string.split()))
    print(f"{rec_count + 1} Fetch data for game {game_name[-1]}")

    # Get different attributes traverse up the DOM tree
    data = tag.parent.parent.find_all("td")
    rank.append(np.int32(data[0].string))
    platform.append(data[3].find('img').attrs['alt'])
    publisher.append(data[4].string)
    developer.append(data[5].string)

    critic_score.append(float(data[6].string) if
        not data[6].string.startswith("N/A") else np.nan)

    user_score.append(
        float(data[7].string) if
        not data[7].string.startswith("N/A") else np.nan)

    sales_na.append(
        float(data[9].string[:-1]) if
        not data[9].string.startswith("N/A") else np.nan)

    sales_pal.append(
        float(data[10].string[:-1]) if
        not data[10].string.startswith("N/A") else np.nan)

    sales_jp.append(
        float(data[11].string[:-1]) if
        not data[11].string.startswith("N/A") else np.nan)

    sales_ot.append(
        float(data[12].string[:-1]) if
        not data[12].string.startswith("N/A") else np.nan)

    sales_gl.append(
        float(data[8].string[:-1]) if
        not data[8].string.startswith("N/A") else np.nan)

    release_year = data[13].string.split()[-1]

    # different format for year i.e. 2K year effect XD
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
    site_raw = urllib.request.urlopen(url_to_game).read()
    sub_soup = BeautifulSoup(site_raw, "html.parser")

    # again, the info box is inconsistent among games so we
    # have to find all the h2 and traverse from that to the genre name
    h2s = sub_soup.find("div", {"id": "gameGenInfoBox"}).find_all('h2')

    # make a temporary tag here to search for the one that contains
    # the word "Genre"
    temp_tag = element.Tag

    for h2 in h2s:
        if h2.string == 'Genre':
            temp_tag = h2
    genre.append(temp_tag.next_sibling.string)

    rec_count += 1

    # Crawlers: The Friend Nobody Likes
    time.sleep(10)


def assemble_response(*, rank, game_name, platform, year, genre, critic_score, user_score, publisher, developer, sales_na, sales_pal, sales_jp, sales_ot, sales_gl):
    """
    
    Assemble from buffers to a Panda DataFrame
    
    :param rank: 
    :param game_name:
    :param platform: 
    :param year: 
    :param genre: 
    :param critic_score: 
    :param user_score: 
    :param publisher: 
    :param developer: 
    :param sales_na: 
    :param sales_pal: 
    :param sales_jp: 
    :param sales_ot: 
    :param sales_gl: 
    :return: 
    """

    # Assembler
    columns = {
        'Rank': rank,
        'Name': game_name,
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

    # Final Report
    print(rec_count)
    df = pd.DataFrame(columns)
    print(df.columns)
    df = df[[
        'Rank', 'Name', 'Platform', 'Year', 'Genre',
        'Publisher', 'Developer', 'Critic_Score', 'User_Score',
        'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']]

    return df

main()

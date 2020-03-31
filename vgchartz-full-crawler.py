from bs4 import BeautifulSoup, element
from random import randint, choice
import urllib
import urllib.request
import pandas as pd
import numpy as np
import logging
import sys
import time
import json

def create_random_header():
    """
    Create a random user agent in order to better mimic user behaviour.
    :return JSON with User-Agent as key and random browser-os combo as value
    """
    logging.info("create_random_header >>>")
    browsers = ["Mozilla", "Chrome"]
    os_list = ["Windows NT 6.1; Win64; x64", "X11; Linux x86_64"]
    major_version = randint(properties['minimum_major_version'], properties['maximum_major_version'])
    minor_version = randint(properties['minimum_minor_version'], properties['maximum_minor_version'])
    chosen_browser = choice(browsers)
    chosen_os = choice(os_list)

    user_agent = '{}/{}.{} ({})'.format(
        chosen_browser,
        major_version,
        minor_version,
        chosen_os)
    header = {'User-Agent': user_agent}
    logging.debug("Current user_agent: {}".format(header))
    logging.info("create_random_header <<<")
    return header

def generate_remaining_url(*, query_parameters):
    """
    Generate an url with a list of videogames from the query params configured at resources.json
    :return: Url with page number
    """
    logging.info("generate_remaining_url >>>")
    reply=''
    for param in query_parameters:
        value=query_parameters.get(param, None)
        reply += f"&{param}={value}" if value is not None else f"&{param}="
    logging.debug(f"Url Generated: {base_url}N{reply}")
    logging.info("generate_remaining_url <<<")
    return reply

def get_page(*, url):
    """
    Perform a GET request to the given URL and return results.
    Add a wait logic that, combined with random header, will help avoiding
    HTTP 429 error.
    :param url: webpage URL
    :return: HTML page's body
    """
    logging.info("get_page >>>")
    logging.debug("Current URL: {}".format(url))
    header = create_random_header()
    request = urllib.request.Request(url, headers=header)
    result = urllib.request.urlopen(request).read()
    time.sleep(randint(properties['minimum_sleep_time'], properties['maximum_sleep_time']))
    logging.info("get_page <<<")
    return result


def get_genre(*, game_url):
    """
    Return the game genre retrieved from the given url
    (It involves another http request)
    :param game_url:
    :return: Genre of the input game
    """
    logging.info("get_genre >>>")
    logging.debug("Page to download: {}".format(game_url))
    site_raw = get_page(url=game_url)
    sub_soup = BeautifulSoup(site_raw, "html.parser")

    # Eventually the info box is inconsistent among games so we
    # have to find all the h2 and traverse from that to the genre name
    # and make a temporary tag here to search
    # for the one that contains the word "Genre"
    h2s = sub_soup.find("div", {"id": "gameGenInfoBox"}).find_all('h2')
    temp_tag = element.Tag

    for h2 in h2s:
        if h2.string == 'Genre':
            temp_tag = h2

    genre_value = temp_tag.next_sibling.string
    logging.debug("Game genre: {}".format(genre_value))
    logging.info("get_genre <<<")
    return genre_value

def parse_number(*, number_string):
    """
    Return string parsed to float with custom format for millions (m)
    :param number_string:
    :return: a float number right parsed
    """
    logging.info("parse_number >>>")
    print(number_string)
    if "m" in number_string:
        reply = number_string.strip('m')
        reply = str(float(reply) * 1000000)
    else:
        reply=number_string

    logging.info("parse_number <<<")
    return float(reply) if not reply.startswith("N/A") else np.nan

def parse_date(*, date_string):
    """
    Return the date received as string onto timestamp or N/A.
    :param date_string:
    :return: A timestamp in panda date format
    """
    logging.info("parse_date >>>")
    if date_string.startswith('N/A'):
        date_formatted = 'N/A'
    else:
        #i.e. date_string = '18th Feb 20'
        date_formatted = pd.to_datetime(date_string)

    logging.debug("Date parsed: {}".format(date_formatted))
    logging.info("parse_date <<<")
    return date_formatted

def add_current_game_data(*,
                          current_rank,
                          current_game_name,
                          current_game_genre,
                          current_platform,
                          current_publisher,
                          current_developer,
                          current_vgchartz_score,
                          current_critic_score,
                          current_user_score,
                          current_total_shipped,
                          current_total_sales,
                          current_sales_na,
                          current_sales_pal,
                          current_sales_jp,
                          current_sales_ot,
                          current_release_date,
                          current_last_update):
    """
    Add all the game data to the related lists
    """
    logging.info("add_current_game_data >>>")
    game_name.append(current_game_name)
    rank.append(current_rank)
    platform.append(current_platform)
    genre.append(current_game_genre)
    publisher.append(current_publisher.strip())
    developer.append(current_developer.strip())
    vgchartz_score.append(current_vgchartz_score)
    critic_score.append(current_critic_score)
    user_score.append(current_user_score)
    total_shipped.append(current_total_shipped)
    total_sales.append(current_total_sales)
    sales_na.append(current_sales_na)
    sales_pal.append(current_sales_pal)
    sales_jp.append(current_sales_jp)
    sales_ot.append(current_sales_ot)
    release_date.append(current_release_date)
    last_update.append(current_last_update)
    logging.info("add_current_game_data <<<")


def download_data(*, start_page, end_page, include_genre):
    """
    Download games data from vgchartz: only data whose pages are in the range (start_page, end_page) will be downloaded
    :param start_page:
    :param end_page:
    :param include_genre:
    :return:
    """
    logging.info("download_data >>>")
    downloaded_games = 0  # Results are decreasingly ordered according to Shipped units
    for page in range(start_page, end_page + 1):
        page_url = "{}{}{}".format(base_url, str(page), remaining_url)
        current_page = get_page(url=page_url)
        soup = BeautifulSoup(current_page, features="html.parser")
        logging.info("Downloaded page {}".format(page))

        # We locate the game through search <a> tags with game urls in the main table
        game_tags = list(filter(
            lambda x: x.attrs['href'].startswith('https://www.vgchartz.com/game/'),
            # discard the first 10 elements because those
            # links are in the navigation bar
            soup.find_all("a")
        ))[10:]

        for tag in game_tags:

            current_game_name = " ".join(tag.string.split())
            data = tag.parent.parent.find_all("td")

            logging.debug("Downloaded game: {}. Name: {}".format(downloaded_games + 1, current_game_name))

            # Get the resto of attributes traverse up the DOM tree looking for the cells in results' table
            current_rank = np.int32(data[0].string)
            current_platform = data[3].find('img').attrs['alt']
            current_publisher = data[4].string
            current_developer = data[5].string
            current_vgchartz_score = parse_number(number_string=data[6].string)
            current_critic_score = parse_number(number_string=data[7].string)
            current_user_score = parse_number(number_string=data[8].string)
            current_total_shipped = parse_number(number_string=data[9].string)
            current_total_sales = parse_number(number_string=data[10].string)
            current_sales_na = parse_number(number_string=data[11].string)
            current_sales_pal = parse_number(number_string=data[12].string)
            current_sales_jp = parse_number(number_string=data[13].string)
            current_sales_ot = parse_number(number_string=data[14].string)
            current_release_date = parse_date(date_string=data[15].string)
            current_last_update = parse_date(date_string=data[16].string)

            # The genre requires another HTTP Request, so it's made at the end
            game_url = tag.attrs['href']
            current_game_genre = ""
            if include_genre:
                current_game_genre = get_genre(game_url=game_url)

            add_current_game_data(
                current_rank=current_rank,
                current_game_name=current_game_name,
                current_game_genre=current_game_genre,
                current_platform=current_platform,
                current_publisher=current_publisher,
                current_developer=current_developer,
                current_vgchartz_score=current_vgchartz_score,
                current_critic_score=current_critic_score,
                current_user_score=current_user_score,
                current_total_shipped=current_total_shipped,
                current_total_sales=current_total_sales,
                current_sales_na=current_sales_na,
                current_sales_pal=current_sales_pal,
                current_sales_jp=current_sales_jp,
                current_sales_ot=current_sales_ot,
                current_release_date=current_release_date,
                current_last_update=current_last_update)

            downloaded_games += 1

    logging.info("Number of downloaded resources: {}".format(downloaded_games))
    logging.info("download_data <<<")


def save_games_data(*, filename, separator, enc):
    """
    Save all the downloaded data into the specified file
    :param filename
    :param separator
    :param enc
    """
    logging.info("save_games_data >>>")
    columns = {
        'Rank': rank,
        'Name': game_name,
        'Genre': genre,
        'Platform': platform,
        'Publisher': publisher,
        'Developer': developer,
        'Vgchartz_Score': vgchartz_score,
        'Critic_Score': critic_score,
        'User_Score': user_score,
        'Total_Shipped': total_shipped,
        'Total_Sales': total_sales,
        'NA_Sales': sales_na,
        'PAL_Sales': sales_pal,
        'JP_Sales': sales_jp,
        'Other_Sales': sales_ot,
        'Release_Date': release_date,
        'Last_Update': last_update
    }

    df = pd.DataFrame(columns)
    logging.debug("Dataframe column name: {}".format(df.columns))
    df = df[[ 'Rank', 'Name', 'Genre', 'Platform', 'Publisher', 'Developer',
              'Vgchartz_Score', 'Critic_Score', 'User_Score', 'Total_Shipped',
              'Total_Sales', 'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales',
              'Release_Date', 'Last_Update' ]]

    df.to_csv(filename, sep=separator, encoding=enc, index=False)
    logging.info("save_games_data <<<")

if __name__ == "__main__":

    # Buffers
    rank = []
    game_name = []
    genre = []
    platform = []
    publisher, developer = [], []
    critic_score, user_score, vgchartz_score = [], [], []
    total_shipped = []
    total_sales, sales_na, sales_pal, sales_jp, sales_ot = [], [], [], [], []
    release_date, last_update = [], []

    properties = None

    with open("cfg/resources.json") as file:
        properties = json.load(file)

    logging.root.handlers = []
    logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s| %(message)s',
                        level=logging.DEBUG,
                        filename=properties["application_log_filename"])

    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)

    # set a format which is simpler for console use
    formatter = logging.Formatter(fmt='%(asctime)s|%(name)s|%(levelname)s| %(message)s',
                                  datefmt="%d-%m-%Y %H:%M:%S")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    try:
        logging.info('Application started')
        base_url = properties['base_page_url']
        remaining_url=generate_remaining_url(query_parameters=properties['query_parameters'])

        download_data(
            start_page=properties['start_page'],
            end_page=properties['end_page'],
            include_genre=properties['include_genre'])

        save_games_data(
            filename=properties['output_filename'],
            separator=properties['separator'],
            enc=properties['encoding'])

    except:
        print("Global exception")
        print("Unexpected error:", sys.exc_info())
        pass

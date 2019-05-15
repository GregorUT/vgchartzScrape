from bs4 import BeautifulSoup, element
import urllib
import pandas as pd
import numpy as np
from random import randint, choice
import time
import json
import logging


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


def get_page(url):
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


def get_genre(game_url):
    """
    Return the game genre retrieved from the given url
    :param game_url:
    :return: Genre of the input game
    """
    logging.info("get_genre >>>")
    logging.debug("Page to download: {}".format(game_url))
    site_raw = get_page(game_url)
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

    genre_value = temp_tag.next_sibling.string
    logging.debug("Game genre: {}".format(genre_value))
    logging.info("get_genre <<<")
    return genre_value


def get_release_year(raw_year):
    """
    Return the release year of the given game in a 4 digit format or N/A.
    :param raw_year:
    :return: Game Release year
    """
    logging.info("get_release_year >>>")
    if raw_year.startswith('N/A'):
        final_year = 'N/A'
    elif int(raw_year) >= 80:
        final_year = np.int32("19" + raw_year)
    else:
        final_year = np.int32("20" + raw_year)
    logging.debug("Release Year: {}".format(final_year))
    logging.info("get_release_year <<<")
    return final_year


def add_current_game_data(current_critic_score,
                          current_developer,
                          current_game_name,
                          current_platform,
                          current_publisher,
                          current_rank,
                          current_release_year,
                          current_sales_gl,
                          current_sales_jp,
                          current_sales_na,
                          current_sales_ot,
                          current_sales_pal,
                          current_user_score):
    """
    Add all the game data to the related lists

    :param current_critic_score:
    :param current_developer:
    :param current_game_name:
    :param current_platform:
    :param current_publisher:
    :param current_rank:
    :param current_release_year:
    :param current_sales_gl:
    :param current_sales_jp:
    :param current_sales_na:
    :param current_sales_ot:
    :param current_sales_pal:
    :param current_user_score:
    :return:
    """
    logging.info("add_current_game_data >>>")
    game_name.append(current_game_name)
    rank.append(current_rank)
    platform.append(current_platform)
    publisher.append(current_publisher)
    developer.append(current_developer)
    critic_score.append(current_critic_score)
    user_score.append(current_user_score)
    sales_na.append(current_sales_na)
    sales_pal.append(current_sales_pal)
    sales_jp.append(current_sales_jp)
    sales_ot.append(current_sales_ot)
    sales_gl.append(current_sales_gl)
    year.append(current_release_year)
    logging.info("add_current_game_data <<<")


def download_data(start_page, end_page, include_genre):
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
        current_page = get_page(page_url)
        soup = BeautifulSoup(current_page)
        logging.info("Downloaded page {}".format(page))

        # vgchartz website is really weird so we have to search for
        # <a> tags with game urls
        game_tags = list(filter(
            lambda x: x.attrs['href'].startswith('http://www.vgchartz.com/game/'),
            # discard the first 10 elements because those
            # links are in the navigation bar
            soup.find_all("a")
        ))[10:]

        for tag in game_tags:

            current_gname = " ".join(tag.string.split())  # add game name to list
            logging.debug("Downloaded game: {}. Name: {}".format(downloaded_games + 1, current_gname))

            # Get different attributes
            # traverse up the DOM tree
            data = tag.parent.parent.find_all("td")
            current_rank = np.int32(data[0].string)
            current_platform = data[3].find('img').attrs['alt']
            current_publisher = data[4].string
            current_developer = data[5].string
            current_critic_score = float(data[6].string) if not data[6].string.startswith("N/A") else np.nan
            current_user_score = float(data[7].string) if not data[7].string.startswith("N/A") else np.nan
            current_sales_na = float(data[9].string[:-1]) if not data[9].string.startswith("N/A") else np.nan
            current_sales_pal = float(data[10].string[:-1]) if not data[10].string.startswith("N/A") else np.nan
            current_sales_jp = float(data[11].string[:-1]) if not data[11].string.startswith("N/A") else np.nan
            current_sales_ot = float(data[12].string[:-1]) if not data[12].string.startswith("N/A") else np.nan
            current_sales_gl = float(data[8].string[:-1]) if not data[8].string.startswith("N/A") else np.nan
            current_release_year = get_release_year(data[13].string.split()[-1])

            add_current_game_data(current_critic_score, current_developer, current_gname, current_platform,
                                  current_publisher, current_rank, current_release_year, current_sales_gl,
                                  current_sales_jp, current_sales_na, current_sales_ot, current_sales_pal,
                                  current_user_score)

            game_url = tag.attrs['href']
            game_genre = ""
            if include_genre:
                game_genre = get_genre(game_url)
            genre.append(game_genre)

            downloaded_games += 1

    logging.info("Number of downloaded resources: {}".format(downloaded_games))
    logging.info("download_data <<<")


def save_games_data(filename, separator, enc):
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
    df = pd.DataFrame(columns)
    logging.debug("Dataframe column name: {}".format(df.columns))
    df = df[[
        'Rank', 'Name', 'Platform', 'Year', 'Genre',
        'Publisher', 'Developer', 'Critic_Score', 'User_Score',
        'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']]
    df.to_csv(filename, sep=separator, encoding=enc, index=False)
    logging.info("save_games_data <<<")


if __name__ == "__main__":
    rank = []
    game_name = []
    platform = []
    year = []
    genre = []
    critic_score, user_score = [], []
    publisher = []
    developer = []
    sales_na, sales_pal, sales_jp, sales_ot, sales_gl = [], [], [], [], []

    properties = None

    with open("resources.json") as file:
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

    logging.info('Application started')
    base_url = properties['base_page_url']
    remaining_url = properties['remaining_url']
    download_data(properties['start_page'], properties['end_page'], properties['include_genre'])
    save_games_data(properties['output_filename'], properties['separator'], properties['encoding'])

from bs4 import BeautifulSoup, element
#import urllib.request
import requests


# link = "https://pythonprogramming.net/parsememcparseface/"
# sauce = urllib.request.urlopen(link).read()
# soup = bs.BeautifulSoup(sauce, 'lxml')

# #print(soup.title.text)

# # for paragraph in soup.find_all("p"):
# #     print(paragraph.string)

# pages = 56
# rec_count = 0
# rank = []
# gname = []
# platform = []
# year = []
# genre = []
# critic_score = []
# user_score = []
# publisher = []
# developer = []
# sales_na = []
# sales_pal = []
# sales_jp = []
# sales_ot = []
# sales_gl = []
# rating = []

# urlhead = 'http://www.vgchartz.com/games/games.php?page='
# urltail = '&results=200&name=&console=&keyword=&publisher=&genre=&order=Sales&ownership=Both'
# urltail += '&banner=Both&showdeleted=&region=All&goty_year=&developer='
# urltail += '&direction=DESC&showtotalsales=1&shownasales=1&showpalsales=1&showjapansales=1'
# urltail += '&showothersales=1&showpublisher=1&showdeveloper=1&showreleasedate=1&showlastupdate=1'
# urltail += '&showvgchartzscore=1&showcriticscore=1&showuserscore=1&showshipped=1&alphasort=&showmultiplat=Yes&showgenre=1'

# for page in range(1, 3):
#     surl = urlhead + str(page) + urltail
#     r = urllib.request.urlopen(surl).read()
#     soup = bs.BeautifulSoup(r)
#     print(f"Page: {page}")

#     # vgchartz website is really weird so we have to search for
#     # <a> tags with game urls
#     game_tags = list(filter(
#         lambda x: x.attrs['href'].startswith('http://www.vgchartz.com/game/'),
#         # discard the first 10 elements because those
#         # links are in the navigation bar
#         soup.find_all("a")
#     ))[10:]

#     print(game_tags)


rating = []
genre = []
url_to_game = "http://www.vgchartz.com/game/6968/mario-kart-wii/?region=All"
site_raw = requests.get(url_to_game, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv: 12.0) Gecko/20100101 Firefox/12.0'}).text
sub_soup = BeautifulSoup(site_raw, "lxml")
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

print(rating)
print(genre)

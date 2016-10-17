import urllib2
import cookielib
from bs4 import BeautifulSoup
f = open("E:/Temp/N64.csv","w+")
f.write("Game;URL\n")
nb_pages = 13
counter = 0
gamelist = "http://www.giantbomb.com/nintendo-64/3045-43/games/"
cj = cookielib.MozillaCookieJar('cookies.txt')
cj.load()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36')]
for page in range(1,nb_pages+1):
    html = opener.open(gamelist + "?page=" + str(page))
    soup = BeautifulSoup(html,'html.parser')
    all_games = soup.find_all('li',class_='related-game')
    for game in all_games:
        line = game.a.h3.text + ";" + game.a.get('href')
        f.write(line.encode('utf8') + "\n")
        counter+=1
        print str(counter) + ": " + game.a.h3.text + "\n"
f.close()

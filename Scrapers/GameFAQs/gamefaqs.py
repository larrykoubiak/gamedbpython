import urllib2
import cookielib
import os
import sys
import re
from bs4 import BeautifulSoup
from xml.sax.saxutils import escape, unescape
import codecs

def ScrapeAllSystems():
    siteurl = "http://www.gamefaqs.com/games/systems"
    cj = cookielib.MozillaCookieJar('cookies.txt')
    cj.load()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36')]

    html = opener.open(siteurl)
    soup = BeautifulSoup(html,'html.parser')

    f = open('gameFAQsSystem.csv','w')

    for link in soup.find_all('a', href=True):
        if not "games/" in link['href'] and not "http" in link['href'] and not "/user" in link['href']:
            f.write ("http://www.gamefaqs.com" + link['href'] +'\n')
    f.close()

def ScrapeAllGamesURLPerSystem():

    print " *** Scraping all games from GameFAQs *** \n"

    with open('gameFAQsSystem.csv','r') as gameFAQsSystemFile:
        gamefaqsFile = codecs.open('gameFAQsURL.csv','w', encoding='utf-8')
        for systemLine in gameFAQsSystemFile:

            row = systemLine.split(";")
            baseURL = str(row[1])+'/'+str(row[5])

            siteurl = baseURL[:-1] + "/category/999-all"
            print siteurl + '\n'
            cj = cookielib.MozillaCookieJar('cookies.txt')
            cj.load()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36')]

            html = opener.open(siteurl)
            soup = BeautifulSoup(html,'html.parser')

            gametable = soup.findAll("td", {"class" : "rtitle"})
            for game in gametable:
                gamefaqsFile.write(row[0]+';'+row[3]+';'+game.a.text + ';' + game.a.get('href')+'\n')

            footer = soup.find('div',{'class':'post_content row'})
            paginate = footer.find('ul',{'class':'paginate'})

            if paginate is not None:
                pgtext = re.sub('\t','',paginate.find_next('li').text)
                pgtext = re.sub('[\r\n]',' ',pgtext)

                result = re.search('Page\s*(\d+)(?:\s+\d+|\s+\.\.\.)*\s+of (\d+)',pgtext)
                totalPage = int(result.group(2))
                for pageNumber in range (1,totalPage):
                    html = opener.open(siteurl+'?page='+str(pageNumber))
                    soup = BeautifulSoup(html,'html.parser')
                    gametable = soup.findAll("td", {"class" : "rtitle"})
                    for game in gametable:
                        lineToWrite = row[0]+';'+row[3]+';'+game.a.text + ';' + game.a.get('href')+'\n'
                        gamefaqsFile.write(escape(lineToWrite))
            
        gameFAQsSystemFile.close()
        gamefaqsFile.close()
    print " *** Scraping done *** "

def ScrapeAGame(gameURL,gameFAQsMetaDataFile):
    print " *** http://www.gamefaqs.com"+gameURL
    siteurl = "http://www.gamefaqs.com"+gameURL[:-1]

    cj = cookielib.MozillaCookieJar('cookies.txt')
    cj.load()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36')]

    html = opener.open(siteurl)
    soup = BeautifulSoup(html,'html.parser')

    print "Page Title : " + soup.title.text

    print "Descriptio : " + soup.find("div", {"class": "body game_desc"}).text
    gameFAQsMetaDataFile.write("\t\t<Description>" + escape(soup.find("div", {"class": "body game_desc"}).text.encode('utf-8')) + "</Description>\n")

    try:
        print "Usr Rating : " + soup.find("div", {"class": "mygames_stats_rate"}).find_next('a').text
        gameFAQsMetaDataFile.write("\t\t<UserRating>" + escape(soup.find("div", {"class": "mygames_stats_rate"}).find_next('a').text.encode('utf-8')) + "</UserRating>\n")
    except:
        pass
    try:
        print "Difficulty : " + soup.find("div", {"class": "mygames_stats_diff"}).find_next('a').text
        gameFAQsMetaDataFile.write("\t\t<Difficulty>" + escape(soup.find("div", {"class": "mygames_stats_diff"}).find_next('a').text.encode('utf-8')) + "</Difficulty>\n")
    except:
        pass
    try:
        print "Length : " + soup.find("div", {"class": "mygames_stats_time"}).find_next('a').text
        gameFAQsMetaDataFile.write("\t\t<Length>" + escape(soup.find("div", {"class": "mygames_stats_time"}).find_next('a').text.encode('utf-8')) + "</Length>\n")
    except:
        pass
    
    
    gameInfo = soup.find("div", {"class": "pod pod_gameinfo"})

    try:
        print "Platform : " + gameInfo.find("li", {"class": "core-platform"}).b.text
        systemName = gameInfo.find("li", {"class": "core-platform"}).b.text
        systemName = re.sub('["<>:;/\|?$*]', '', systemName)
        #gameFAQsMetaDataFile.write("\t\t<System>" + escape(str(systemName)) + "</System>\n")
    except:
        pass

    try:
        print "A.K.A.: " + gameInfo.find(string='Also Known As:').find_next('i').text
        gameFAQsMetaDataFile.write("\t\t<AKA>" + escape(gameInfo.find(string='Also Known As:').find_next('i').text.encode('utf-8')) + "</AKA>\n")
    except:
        pass

    try:
        print "Developer : " + gameInfo.find('a', href=re.compile(r'\/company')).text
        gameFAQsMetaDataFile.write("\t\t<Developer>" + escape(gameInfo.find('a', href=re.compile(r'\/company')).text.encode('utf-8')) + "</Developer>\n")
    except:
        pass

    try:
        print "ReleaseDate : " + gameInfo.find('a', href=re.compile(r'\/data')).text
        #gameFAQsMetaDataFile.write("\t\t<ReleaseDate>" + escape(str(gameInfo.find('a', href=re.compile(r'\/data')).text)) + "</ReleaseDate>\n")
    except:
        pass

    try:
        print "Franchise : " + gameInfo.find('a', href=re.compile(r'\/franchise')).text
        gameFAQsMetaDataFile.write("\t\t<Franchise>" + escape(gameInfo.find('a', href=re.compile(r'\/franchise')).text.encode('utf-8')) + "</Franchise>\n")
    except:
        pass

    html = opener.open(siteurl+ "/data")
    soup = BeautifulSoup(html,'html.parser')
    gameInfo = soup.find("div", {"class": "pod_titledata"})
    try:
        print "Genre : " + gameInfo.find(string='Genre:').next.text
        gameFAQsMetaDataFile.write("\t\t<Genre>" + escape(gameInfo.find(string='Genre:').next.text.encode('utf-8')) + "</Genre>\n")
    except:
        pass


    gameInfo = soup.find(string="Release Data").find_next('table')

    rows = gameInfo.find_all('tr')
    x = 2
    while x < len(rows):

        cols = rows[x].find_all('td')
        if "Virtual Console" not in rows[x+1].find_all('td')[3].text:
            
            releaseName = u""
            releaseRegion = u""
            try:
                imageURL = "http://www.gamefaqs.com" + cols[0].a['href']
            except:
                pass
            
            try:
                releaseName = cols[1].b.text
                print "ReleaseN : " + releaseName
            except:
                pass

            imageAlt = cols[1].b.text
            cols = rows[x+1].find_all('td')
            try:
                releaseRegion = cols[0].text
                print "Region : " + releaseRegion
                imageAlt += ' (' + cols[0].text +')'
            except:
                pass
            gameFAQsMetaDataFile.write(u'\t\t<Release name="{0}" region="{1}">\n'.format(escape(releaseName),escape(releaseRegion)))
            try:
                print "Publisher : " + cols[1].a.text
                gameFAQsMetaDataFile.write("\t\t\t<ReleasePublisher>" + escape(cols[1].a.text.encode('utf-8')) + "</ReleasePublisher>\n")
            except:
                pass

            try:
                print "Product ID : "+ cols[2].text
                gameFAQsMetaDataFile.write("\t\t\t<ReleaseProductID>" + escape(cols[2].text.encode('utf-8')) + "</ReleaseProductID>\n")
            except:
                pass

            try:
                print "BarCode : " +cols[3].text
                gameFAQsMetaDataFile.write("\t\t\t<ReleaseBarCode>" + escape(cols[3].text.encode('utf-8')) + "</ReleaseBarCode>\n")
            except:
                pass
            
            try:
                print "ReleaseDate : " + cols[4].text
                gameFAQsMetaDataFile.write("\t\t\t<ReleaseDate>" + escape(cols[4].text.encode('utf-8')) + "</ReleaseDate>\n")
            except:
                pass
                    
            try:
                print "ESRB : " + cols[5].text
                gameFAQsMetaDataFile.write("\t\t\t<ReleaseESRB>" + escape(row.text.encode('utf-8')) + "</ReleaseESRB>\n")
            except:
                pass

            try:
                html = opener.open(imageURL)
                soup = BeautifulSoup(html,'html.parser')
                gameImages = soup.find("div", {"class": "game_imgs"}).find_all("div", {"class": "boxshot"})

                image = next(i for i in gameImages if i.img['alt']==imageAlt)

                boxURL = image.a['href']

                print image.img['alt'] + ' ' + boxURL

                html = opener.open("http://www.gamefaqs.com"+ boxURL)
                soup = BeautifulSoup(html,'html.parser')
                gameBoxartDiv = soup.find("div", {"class": "game_imgs"})

                gameFAQsMetaDataFile.write("\t\t\t<ReleaseImages>\n")
                for boxArt in gameBoxartDiv.find_all('a'):
                    r = urllib2.urlopen(boxArt['href'])
                    regExp = re.compile("(\d*)_(\w*)\.")
                    imgResult = regExp.search(boxArt['href'])
                    if not os.path.exists("images/" + str(systemName)):
                        os.makedirs("images/" + str(systemName))
                    fileName = image.img['alt'] + "-" + imgResult.group(1) + "_" + imgResult.group(2)+ ".jpg"
                    fileName = re.sub('["<>:;/\|?$*]', '', fileName)
                    gameFAQsMetaDataFile.write("\t\t\t\t<Image>" + escape(str(fileName)) + "</Image>\n")
                    print fileName
                    f = open("images/"+systemName + "/" + fileName, 'wb')
                    f.write(r.read())
                    f.close()
                gameFAQsMetaDataFile.write("\t\t\t</ReleaseImages>\n")
            except:
                pass
                
            gameFAQsMetaDataFile.write("\t\t</Release>\n")
        x+=2
       
    print "\n *** Game Parsing Done \n"
    
def ScrapeAllGames():
    with open('gameFAQsURL.csv','r') as gameFAQsFile:
        gameFAQsMetaDataFile = codecs.open('gameMASTA_FILE.xml','w', encoding='utf-8')
        gameFAQsMetaDataFile.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
        gameFAQsMetaDataFile.write('<softwarelist>\n')
        #for x in range (0,xxxxxx):
        #    gameFAQsFile.readline()
        for x in range (0,87942):
            gameLine = gameFAQsFile.readline()[:-1].split(";")
            gameFAQsMetaDataFile.write('\t<software scraper="{0}" system="{1}" name="{2}" URL="{3}">\n'.format(escape(gameLine[0].encode('utf-8')),escape(gameLine[1].encode('utf-8')),escape(gameLine[2].encode('utf-8')),escape(gameLine[3].encode('utf-8'))))
            
            ScrapeAGame(gameLine[3],gameFAQsMetaDataFile)
            gameFAQsMetaDataFile.write("\t</software>\n")
        gameFAQsMetaDataFile.write('</softwarelist>\n')    
        gameFAQsMetaDataFile.close()
    gameFAQsFile.close()

ScrapeAllGames()
#ScrapeAllGamesURLPerSystem()

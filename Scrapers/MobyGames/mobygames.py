import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
import http.cookiejar
import os
import sys
import unicodedata
import re
from bs4 import BeautifulSoup

def ScrapeAllSystems():
    siteurl = "http://www.mobygames.com/browse/games/full,1/"
    cj = http.cookiejar.MozillaCookieJar('cookies.txt')
    cj.load()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36')]

    html = opener.open(siteurl)
    soup = BeautifulSoup(html,'html.parser')

    f = open('MobyGamesSystem.csv','w')

    soup = soup.find("div", {"class": "browseTable"})
    
    for link in soup.find_all('a', href=True):
        f.write ("http://www.mobygames.com" + link['href'] +'\n')
    f.close()

def ScrapeAllGamesURLPerSystem():

    print(" *** Scraping all games from GameFAQs *** \n")

    with open('MobyGamesSystem.csv','r') as MobyGamesSystemFile:
        MobyGamesURLFile = open('MobyGamesURL.csv','w')
        for systemLine in MobyGamesSystemFile:

            row = systemLine.split(";")
            
            baseURL = str(row[1])+'/browse/games/offset,0/so,0a/'+str(row[5])[:-1]+"/list-games/"

            siteurl = baseURL
            print(siteurl + '\n')
            cj = http.cookiejar.MozillaCookieJar('cookies.txt')
            cj.load()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36')]

            html = opener.open(siteurl)
            soup = BeautifulSoup(html,'html.parser')

            #MobyGames;System;GameName;URL
            footer = soup.find("div",{"class": "mobFooter"})
            try:
                for link in footer.find_all('a', href=True):
                    html = opener.open('http://www.mobygames.com/'+link['href'])
                    soup = BeautifulSoup(html,'html.parser')

                    gametable = soup.find("table", id="mof_object_list")
                    for game in gametable.find_all("tr"):
                        try:
                            if "/game/" in game.td.a['href']:
                                lineToWrite = row[0]+';'+row[3]+';' + game.a.text + ';' + game.td.a['href'] +'\n'
                                MobyGamesURLFile.write(unicodedata.normalize('NFKD',lineToWrite).encode('ascii','ignore'))
                        except:
                            pass
            except:
                gametable = soup.find("table", id="mof_object_list")
                for game in gametable.find_all("tr"):
                    try:
                        if "/game/" in game.td.a['href']:
                            lineToWrite = row[0]+';'+row[3]+';' + game.a.text + ';' + game.td.a['href'] +'\n'
                            MobyGamesURLFile.write(unicodedata.normalize('NFKD',lineToWrite).encode('ascii','ignore'))
                    except:
                        pass
                    
        MobyGamesSystemFile.close()
        MobyGamesURLFile.close()
    print(" *** Scraping done *** ")

def ScrapeAGame(gameURL):
    print(" *** http://www.mobygames.com"+gameURL)
    #siteurl = "http://www.mobygames.com"+gameURL[:-1]
    siteurl = "http://www.mobygames.com"+gameURL

    cj = http.cookiejar.MozillaCookieJar('cookies.txt')
    cj.load()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36')]

    html = opener.open(siteurl)
    soup = BeautifulSoup(html,'html.parser')

    texts = soup.findAll(text=True)
    str = ""
    check = False
    for text in texts:
        if check:
            str +=text
        if text == "Description":
            check = True
        if text == "edit description":
            check = False

    print("Description : " + str[:-17])

    data = soup.find("table",{"class": "pct100"})
    try :
        print("Published by: " + data.find(string="Published by").next.text)
    except:
        pass
    
    try :
        print("Developed by: " + data.find(string="Developed by").next.text)
    except:
        pass

    try :
        print("Released: " + data.find(string="Released").next.text)
    except:
        pass

    try :
        print("Genre: " + data.find(string="Genre").next.text)
    except:
        pass

    try :
        print("Perspective: " + data.find(string="Perspective").next.text)
    except:
        pass    

    try :
        print("Art: " + data.find(string="Art").next.text)
    except:
        pass        

    try :
        print("Gameplay: " + data.find(string="Gameplay").next.text)
    except:
        pass        

    try :
        print("Setting: " + data.find(string="Setting").next.text)
    except:
        pass        
            
    
    print("\n *** Game Parsing Done \n")
    
def ScrapeAllGames():
    with open('MobyGamesURL.csv','r') as MobyGamesFile:
        #for w in range (0,36090):
        #    gameLine = gameFAQsFile.readline()
        for x in range (0,1):
            gameLine = MobyGamesFile.readline().split(";")
            ScrapeAGame(gameLine[3])
    MobyGamesFile.close()

ScrapeAllGames()
#ScrapeAllGamesURLPerSystem()

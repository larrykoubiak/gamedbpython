import urllib2
import cookielib
from bs4 import BeautifulSoup
import codecs

class Scraper:

    def __init__(self):
        self.name = ""
        self.url = ""
        self.systems = []
        self.urls = []

    def __init__(self,name,url):
        self.name = name
        self.url = url
        self.systems = []
        self.urls = []
        self.getSystems()
        self.getURLs()

    def getSystems(self):
        self.systems = []
        systemsfile = codecs.open('Scrapers/' + self.name + '/' + self.name + "System.csv",'r',encoding='utf8')
        for systemLine in systemsfile:
            systemDic = {}
            systemrow = systemLine.split(";")
            systemDic['name'] = systemrow[0]
            systemDic['url'] = systemrow[1]
            systemDic['systemId'] = systemrow[2]
            systemDic['systemName'] = systemrow[3]
            systemDic['systemAcronym'] = systemrow[4]
            systemDic['systemURL'] = systemrow[5].replace('\r\n','')
            self.systems.append(systemDic)
        systemsfile.close()

    def getURLs(self):
        self.urls = []
        urlsfile = codecs.open('Scrapers/' + self.name + '/' + self.name + "URL.csv",'r',encoding='utf8')
        for urlline in urlsfile:
            urlDic = {}
            urlrow = urlline.split(";")
            urlDic['name'] = urlrow[0]
            urlDic['systemName'] = urlrow[1]
            urlDic['gameName'] = urlrow[2]
            urlDic['gameUrl'] = urlrow[3]
            self.urls.append(urlDic)

if __name__ == '__main__':
    gf = Scraper('GameFAQs','http://www.gamefaqs.com')
    gf.getSystems()
    gf.getURLs()
    for system in gf.systems:
        print system
    print "Done."
        
            

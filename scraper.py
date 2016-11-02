import urllib2
import cookielib
from bs4 import BeautifulSoup
import codecs
import os
import xml.etree.ElementTree as ET
import regex as re

class Scraper:

    def __init__(self):
        self.name = ""
        self.url = ""
        self.systems = {}

    def __init__(self,name,url):
        self.name = name
        self.url = url
        self.systems = {}
        self.getSystems()
        self.getGames()
        self.getGameData()

    def getSystems(self):
        self.systems = {}
        systemsfile = codecs.open('Scrapers/' + self.name + '/' + self.name + "System.csv",'r',encoding='utf8')
        for systemLine in systemsfile:
            systemDic = {}
            systemrow = systemLine.split(";")
            systemDic['systemName'] = systemrow[3]
            systemDic['systemAcronym'] = systemrow[4]
            systemDic['systemURL'] = systemrow[5].replace('\r\n','')
            systemDic['systemGames'] = {}
            self.systems[systemDic['systemName']] = systemDic
        systemsfile.close()

    def getGames(self):
        urlsfile = codecs.open('Scrapers/' + self.name + '/' + self.name + "URL.csv",'r',encoding='utf8')
        for urlline in urlsfile:
            urlDic = {}
            urlrow = urlline.split(";")
            urlDic['gameName'] = urlrow[2]
            urlDic['gameUrl'] = urlrow[3].replace('\r\n','')
            urlDic['gameParsed'] = 'No'
            self.systems[urlrow[1]]['systemGames'][urlDic['gameUrl']] = urlDic

    def getGameData(self):
        xmlpath = 'Scrapers/' + self.name + '/xml'
        if os.path.exists(xmlpath):
            for xmlfile in os.listdir(xmlpath):
                print "Parsing game data from " + xmlfile
                tree = ET.parse(os.path.join(xmlpath,xmlfile))
                root = tree.getroot()
                for softnode in root.findall('software'):
                    systemname = softnode.get('system')
                    url = softnode.get('URL')
                    gameDic = self.systems[systemname]['systemGames'][url]
                    gameDic['gameParsed'] = 'Yes'
                    gameDic['softwareFlags'] = []
                    gameDic['releases'] = []
                    for flag in [flag for flag in list(softnode) if flag.tag !='Release']:
                        if(len(flag.text)>0):
                            flagDic = {}
                            flagDic['name'] = flag.tag
                            flagDic['value'] = flag.text
                            gameDic['softwareFlags'].append(flagDic)
                    for release in softnode.findall('Release'):
                        releaseDic = {}
                        releaseDic['name'] = release.get('name')
                        releaseDic['region'] = release.get('region')
                        releaseDic['releaseFlags'] = []
                        releaseDic['releaseImages'] = []
                        for flag in [flag for flag in list(release) if flag.tag !='ReleaseImages']:
                            if(flag.text is not None):
                                if(len(flag.text)>1):
                                    flagDic = {}
                                    flagDic['name'] = flag.tag
                                    flagDic['value'] = flag.text
                                    releaseDic['releaseFlags'].append(flagDic)
                        images = release.find('ReleaseImages')
                        if(images is not None):
                            for img in images.findall('Image'):
                                imageDic = {}
                                imageDic['name'] = img.text
                                imageDic['type'] = re.search("_([a-z]+)\.",img.text,re.IGNORECASE).group(1)
                                releaseDic['releaseImages'].append(imageDic)
                        gameDic['releases'].append(releaseDic)
                  
if __name__ == '__main__':
    gf = Scraper('GameFAQs','http://www.gamefaqs.com')
    gf.getSystems()
    gf.getGames()
    gf.getGameData()
    for key,system in gf.systems.items():
        print system['systemGames'].itervalues().next()
    print "Done."
        
            

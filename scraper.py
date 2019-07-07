# import urllib.request
# import urllib.error
# import urllib.parse
# import http.cookiejar
# from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET
import re


class Scraper:
    def __init__(self, name="", url=""):
        self.name = name
        self.url = url
        self.systems = {}
        self.getSystems()
        self.getGames()
        self.getGameData()

    def getSystems(self):
        self.systems = {}
        systemsfile = open(
            'Scrapers/' + self.name +
            '/' + self.name +
            "System.csv", 'r')
        for systemLine in systemsfile:
            systemDic = {}
            systemrow = systemLine.split(";")
            systemDic['systemName'] = systemrow[3]
            systemDic['systemAcronym'] = systemrow[4]
            systemDic['systemURL'] = systemrow[5].rstrip()
            systemDic['systemGames'] = {}
            self.systems[systemDic['systemName']] = systemDic
        systemsfile.close()

    def getGames(self):
        urlsfile = open(
            'Scrapers/' + self.name +
            '/' + self.name +
            "URL.csv", 'r')
        for urlline in urlsfile:
            urlDic = {}
            urlrow = urlline.split(";")
            urlDic['gameName'] = urlrow[2]
            urlDic['gameUrl'] = urlrow[3].rstrip()
            urlDic['gameParsed'] = 'No'
            self.systems[urlrow[1]]['systemGames'][urlDic['gameUrl']] = urlDic

    def getGameData(self):
        xmlpath = 'Scrapers/' + self.name + '/xml'
        if os.path.exists(xmlpath):
            for xmlfile in os.listdir(xmlpath):
                print("Parsing game data from " + xmlfile)
                tree = ET.parse(os.path.join(xmlpath, xmlfile))
                root = tree.getroot()
                for softnode in root.findall('software'):
                    systemname = softnode.get('system')
                    url = softnode.get('URL')
                    gameDic = self.systems[systemname]['systemGames'][url]
                    gameDic['gameParsed'] = 'Yes'
                    gameDic['softwareFlags'] = []
                    gameDic['releases'] = []
                    for flag in [
                         flag for flag in list(softnode)
                         if flag.tag != 'Release']:
                        if(len(flag.text) > 0):
                            flagDic = {}
                            flagDic['name'] = flag.tag
                            flagDic['value'] = flag.text
                            gameDic['softwareFlags'].append(flagDic)
                    for release in softnode.findall('Release'):
                        releaseDic = {}
                        releaseDic['name'] = release.get('name')
                        releaseDic['region'] = release.get('region')
                        releaseDic['type'] = 'Standard'
                        releaseDic['releaseFlags'] = []
                        releaseDic['releaseImages'] = []
                        for flag in [
                             flag for flag in list(release)
                             if flag.tag != 'ReleaseImages']:
                            if(flag.text is not None and len(flag.text) > 1):
                                flagDic = {}
                                # handle barcodes containing text
                                # (PSN, Nintendo Power, etc...)
                                if flag.tag == "ReleaseBarCode" and \
                                   not flag.text.strip().isdigit():
                                    releaseDic['type'] = flag.text
                                    flagDic['name'] = flag.tag
                                    flagDic['value'] = ''
                                else:
                                    flagDic['name'] = flag.tag
                                    flagDic['value'] = flag.text
                                releaseDic['releaseFlags'].append(flagDic)
                        images = release.find('ReleaseImages')
                        if(images is not None):
                            for img in images.findall('Image'):
                                imageDic = {}
                                imageDic['name'] = img.text
                                imageDic['type'] = re.search(
                                    "_([a-z]+)\\.",
                                    img.text,
                                    re.IGNORECASE).group(1)
                                releaseDic['releaseImages'].append(imageDic)
                        gameDic['releases'].append(releaseDic)


if __name__ == '__main__':
    gf = Scraper('GameFAQs', 'http://www.gamefaqs.com')
    system = gf.systems['PSP']
    for key, game in system['systemGames'].items():
        for release in game['releases']:
            print('name :"' + release['name'] + '" type: ' + release['type'])
    print("Done.")

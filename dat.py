from collections import OrderedDict
import xml.etree.ElementTree as ET
import ntpath
import re

class DAT:

    def __init__(self):
        self.header = {}
        self.filename = ""
        self.softwares=OrderedDict()
        self.releaseGroup = None

    def getReleaseGroup(self):
        self.releaseGroup = None
        if('comment' in self.header):
            if(self.header['comment'] == "no-intro | www.no-intro.org"):
                self.releaseGroup = "No-Intro"
        elif('url' in self.header):
            if(self.header['url'] == "www.no-intro.org"):
                self.releaseGroup = "No-Intro"
            elif(self.header['url'] == "http://www.fbalpha.com/"):
                self.releaseGroup = "FBA"
        else:
            if('homepage' in self.header):
                if(self.header['homepage'] == "TOSEC"):
                    self.releaseGroup = "TOSEC"
                elif(self.header['homepage'] == "redump.org"):
                    self.releaseGroup = "Redump"

    def import_old_dat(self,datfile):
        line = datfile.readline()
        self.header = {}
        datexp = re.compile("\t*(.+?) \"?(.+?)\"?$")
        romexp = re.compile("\( (?:name \"(?P<name>.*)\" )?(?:size (?P<size>.+?) )?(?:crc (?P<crc>.+?) )?(?:md5 (?P<md5>.+?) )?(?:sha1 (?P<sha1>.+?) )?(?:status (?P<status>.+?) )?\)")
        #import header
        while(line !=")\n"):
            result = datexp.search(line)
            self.header[result.group(1)] = result.group(2)
            line = datfile.readline()
        #import software
        self.softwares = OrderedDict()
        while(line != ''):
            line = datfile.readline() #skip line
            line = datfile.readline() #read game
            if(line == "game (\n"):
                game = {}
                game['Roms'] = []
                line = datfile.readline()
                while(line !=")\n"):
                    result = datexp.search(line)
                    if result.group(1)=="rom":
                        rom = OrderedDict()
                        romresult = romexp.search(result.group(2))
                        for key,val in romresult.groupdict().items():
                            rom[key] = val
                        game['Roms'].append(rom)
                    else:
                        game[result.group(1).capitalize()] = result.group(2)
                    line = datfile.readline()
            self.softwares[game['Name']] = game

    def import_metadat_dat(self,path):
        datfile = open(path,"r")
        line = datfile.readline()
        self.header = {}
        datexp = re.compile('\t*(.+?) \"?([^\"\n]*)\"?$')
        romexp = re.compile('([a-z|1]+?) \"?([^"| ]*)\"?')
        #import header
        while(line !=")\n"):
            result = datexp.search(line)
            self.header[result.group(1)] = result.group(2)
            line = datfile.readline()
        #import software
        self.softwares = OrderedDict()
        while(line != ''):
            line = datfile.readline() #skip line
            line = datfile.readline() #read game
            if(line == "game (\n"):
                game = OrderedDict()
                game['romtags'] = {}
                line = datfile.readline()
                nameresult = datexp.search(line)
                game['Name'] = nameresult.group(2)
                line = datfile.readline()
                tagresult = datexp.search(line)
                game['Tag'] = tagresult.group(1)
                game['TagValue'] = tagresult.group(2)
                line = datfile.readline() # rom (
                if line=="\trom (\n":
                    line = datfile.readline()
                    while line != "\t)\n":
                        romresult = datexp.search(line)
                        game['romtags'][romresult.group(1)] = '' if romresult.group(2) is None else romresult.group(2)
                        line = datfile.readline()                   
                    line = datfile.readline() # \)
                else:
                    romresult = datexp.search(line)
                    tagresults = romexp.finditer(romresult.group(2))
                    for tagresult in tagresults:
                        game['romtags'][tagresult.group(1)] = tagresult.group(2)
                    line = datfile.readline() # \)                    
                self.softwares[game['Name']] = game
        datfile.close()
            
    def import_xml_dat(self,datfile):
        datfile.seek(0)
        tree = ET.parse(datfile)
        root = tree.getroot()
        #import header
        headernode = root.find('header')
        self.header = {}
        for field in list(headernode):
            self.header[field.tag] = field.text
        #extract softwares
        self.softwares = OrderedDict()
        for gamenode in root.findall('game'):
            game = OrderedDict()
            game['Name'] = gamenode.get('name')
            game['CloneOf'] = '' if gamenode.get('cloneof') is None else gamenode.get('cloneof')
            game['RomOf'] = '' if gamenode.get('romof') is None else gamenode.get('romof')
            game['Description'] = gamenode.find('description').text
            game['Roms'] = []
            for romnode in gamenode.findall('rom'):
                rom = {}
                for key,val in romnode.attrib.items():
                    rom[key] = '' if val is None else val
                if 'merge' not in rom:
                    rom['merge'] = ''
                game['Roms'].append(rom)
            self.softwares[game['Name']] = game

    def read_dat(self,path):
        datfile = open(path,"r")
        self.filename = ntpath.basename(path)
        line = datfile.readline()
        if(line=="clrmamepro (\n"):
            self.import_old_dat(datfile)
        else:
            self.import_xml_dat(datfile)
        self.getReleaseGroup()

if __name__ == '__main__':
    from dicttoxml import dicttoxml
    from xml.dom.minidom import parseString
    import os
    output = open("old/releaseyear.csv","w")
    for datfile in os.listdir("old/metadat/releaseyear"):
        dat = DAT()
        dat.import_metadat_dat(os.path.join("old/metadat/releaseyear",datfile))
        for soft in dat.softwares.itervalues():
            baseline = datfile + '\t' + '\t'.join(value for key,value in soft.iteritems() if key !='romtags')
            line = baseline + '\t' + '\t'.join('' if value is None else key + '\t' + str(value) for key,value in soft['romtags'].iteritems())
            output.write(line + "\n")
    output.close()

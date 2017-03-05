# -*- coding: cp1252 -*-
from collections import OrderedDict
import xml.etree.ElementTree as ET
import shlex
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
            elif(self.header['url']=="http://redump.org/"
                 self.releaseGroup = "No-Intro"
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
        romexp = re.compile("\( (?:name \"(?P<name>.*)\" )?(?:size (?P<size>.+?) )?(?:crc (?P<crc>.+?) )?(?:md5 (?P<md5>.+?) )?(?:sha1 (?P<sha1>.+?) )?(?:status (?P<status>.+?) )?(?:flags (?P<flags>.+?) )?\)")
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

    def import_metadat_dat(self,datfile,debug=False):
        data = datfile.read()
        lexer = shlex.shlex(data)
        lexer.quotes = '"'
        lexer.wordchars += '\'\.\-öäå'
        tokens = list(lexer)
        if debug==True:
            log = open('old/log.txt','w')
            log.write("\n".join(token for token in tokens))
            log.close()
        tokidx = 0
        while tokidx < len(tokens):
            token = tokens[tokidx]
            if token=="clrmamepro": #header
                tokidx += 1
                if tokens[tokidx] == "(":
                    tokidx +=1
                else:
                    print "incorrect format (header)"
                while tokens[tokidx] != ")":
                    key = tokens[tokidx]
                    value = tokens[tokidx +1]
                    self.header[key] = value
                    tokidx += 2
            elif token=="game": #header
                tokidx +=1
                if tokens[tokidx] == "(":
                    game = {}
                    gamename = ""
                    game['gametags'] = []
                    game['Roms'] = [] 
                    tokidx += 1
                else:
                    print "incorrect format (game)"
                while tokens[tokidx] != ")":
                    key = tokens[tokidx]
                    if key == "rom":
                        tokidx +=1
                        if tokens[tokidx]== "(":
                            tokidx += 1
                            rom = OrderedDict()
                        else:
                            print "incorrect format (rom)"
                        while tokens[tokidx] != ")":
                            key = tokens[tokidx]
                            value = tokens[tokidx+1]
                            rom[key] = value
                            tokidx += 2
                        tokidx +=1
                        game['Roms'].append(rom)
                    else:
                        value = tokens[tokidx+1]
                        if key=="name":
                            gamename = value
                        game['gametags'].append((key,value))
                        tokidx += 2
                self.softwares[gamename] = game
            else:
                tokidx +=1
        #self.softwares = OrderedDict(sorted(self.softwares.iteritems(),key=lambda s: s[0].lower()))
        self.softwares = OrderedDict(sorted(self.softwares.iteritems()))
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
        self.softwares = {}
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

    def write_sorted_dat(self,path):
        output = open(path,"wb")
        output.write("clrmamepro (\n")
        for key,value in self.header.iteritems():
            output.write("\t{0} {1}\n".format(key,value))
        output.write(")\n")
        for softkey,softvalue in self.softwares.iteritems():
            output.write("\ngame (")
            for tag in softvalue['gametags']:
                output.write("\n\t{0} {1}".format(tag[0],tag[1]))
            flagtag = False
            for rom in softvalue['Roms']:
                output.write("\n\trom (")
                for romkey,romvalue in rom.iteritems():
                    if romkey in ('name','size','crc','md5','sha1','status','flags') and romvalue !=None:
                        output.write(" {0} {1}".format(romkey,romvalue))                            
                    elif romvalue != None:
                        if len(rom) == 1:
                            output.write(" {0} {1}".format(romkey,romvalue))
                        else:
                            output.write("\n\t\t{0} {1}".format(romkey,romvalue))
                            flagtag = True
                if flagtag == True:
                    output.write("\n\t)\n")
                else:
                    output.write(" )")
            output.write("\n)\n")
        output.close()


if __name__ == '__main__':
    import os
    for (dirpath, dirnames, filenames) in os.walk('libretro-database/metadat'):
        for filename in filenames:
            path =  os.path.join(dirpath,filename)
            datfile = open(path,"rb")
            line = datfile.readline()
            if(line!="clrmamepro (\n"):
                print line
                print "wrong format: " + path
                datfile.close()
            else:
                #import dat
                print path
                dat = DAT()
                datfile.seek(0,0)
                dat.import_metadat_dat(datfile)
                datfile.close()
                dat.write_sorted_dat(path)

        
    datfile.close()
##    dat = DAT()
##    path = r"libretro-database/metadat/no-intro/Tiger - Gizmondo.dat"
##    datfile = open(path,'rb')
##    dat.import_metadat_dat(datfile,True)
##    datfile.close()
##    dat.write_sorted_dat(r'old/sorted/no-intro/Tiger - Gizmondo.dat')

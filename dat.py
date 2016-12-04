from collections import OrderedDict
import xml.etree.ElementTree as ET
import ntpath
import re

class DAT:

    def __init__(self):
        self.header = {}
        self.filename = ""
        self.softwares=OrderedDict()

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
            game = {}
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

if __name__ == '__main__':
    from dicttoxml import dicttoxml
    from xml.dom.minidom import parseString
    output = open("old/nes.csv","w")
    dat = DAT()
    dat.read_dat('libretro-database/metadat/goodtools/Nintendo - Nintendo Entertainment System.dat')
    for soft in dat.softwares.itervalues():
        baseline = ';'.join(value for key,value in soft.items() if key !='Roms')
        for rom in soft['Roms']:
            line = baseline + ';'.join('' if value is None else str(value) for value in rom.itervalues())
            output.write(line + '\n')
    output.close()

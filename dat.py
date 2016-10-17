from collections import OrderedDict
import xml.etree.ElementTree as ET
import ntpath

class DAT:

    def __init__(self):
        self.header = {}
        self.filename = ""
        self.softwares=OrderedDict()
   
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

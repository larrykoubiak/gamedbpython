import regex as re
from datetime import datetime
from collections import namedtuple, OrderedDict
import xml.etree.ElementTree as ET
import sqlite3 as lite
import ntpath
import os

class DAT:
    regexes = {}
    rom = namedtuple('Rom',['name','size','crc','md5','sha1','status'])
    flag = namedtuple('Flag',['name','value'])
    dat = namedtuple('DAT',['header','softwares'])
    system = namedtuple('System',['name','manufacturer'])

def init_regexes(releaseGroup):
    global regexes
    regexes = {}
    tree = ET.parse("regexes.xml")
    groupNode = tree.find("//ReleaseGroup[@name='" + releaseGroup+ "']")
    for regex in groupNode.findall("Regex"):
        namenode = regex.find("Name")
        patternnode = regex.find("Pattern")
        regexes[namenode.text] = re.compile(patternnode.text)
        
def get_regex_result(regname,value):
    global regexes
    return regexes[regname].search(value)

def get_regex_results(regname,value):
    global regexes
    return regexes[regname].finditer(value)

def getDATReleaseGroup(header):
    relGroup = None
    if('comment' in header):
        if(header['comment'] == "no-intro | www.no-intro.org"):
            relGroup = "No-Intro"
    elif('url' in header):
        if(header['url'] == "www.no-intro.org"):
            relGroup = "No-Intro"
    else:
        if(header['homepage'] is not None):
            if(header['homepage'] == "TOSEC"):
                relGroup = "TOSEC"
            elif(header['homepage'] == "redump.org"):
                relGroup = "Redump"
    return relGroup

def getDATDate(header):
    datDate = None
    if(header['version'] is not None or header['date'] is not None):
        dateResult = get_regex_result("DatDate",header['version'] if header['version'] is not None else header['date'])
        if(match is not None):
            year = int(dateResult.group('Year'))
            month = int(dateResult.group('Month'))
            day = int(dateResult.group('Day'))
            hour = int(dateResult.group('Hour'))
            minute = int(dateResult.group('Minute'))
            second = int(dateResult.group('Second'))
            datDate = datetime(year,month,day,hour,minute,second)
    return datDate

def getDATSystem(header):
    system = None
    
    return system

def import_xml_dat(datfile):

    datfile.seek(0)
    tree = ET.parse(datfile)
    root = tree.getroot()
    #import header
    headernode = root.find('header')
    header = {}
    for field in list(headernode):
        header[field.tag] = field.text
    softwares=OrderedDict()
    for gamenode in root.findall('game'):
        game = {}
        game['Name'] = gamenode.get('name')
        game['Description'] = gamenode.find('description').text
        game['Roms'] = []
        for romnode in gamenode.findall('rom'):
            rom = {}
            for key,val in romnode.attrib.items():
                rom[key] = val
            game['Roms'].append(rom)
        softwares[game['Name']] = game
    return dat(header,softwares)

def parse_header(datheader):
    header = {}
    #extract dat Release Group
    header['ReleaseGroup'] = getDATReleaseGroup(datheader)
    init_regexes(header['ReleaseGroup'])
    #extract dat Date
    header['Date'] = getDATDate(datheader)
    #extract dat System 
    sysresult = get_regex_result("System",datheader["name"])
    header['Manufacturer'] = sysresult.group('Manufacturer')
    header['System'] = sysresult.group('Name')
    header['DatType'] = 'Standard' if sysresult.group('DatType') == None else sysresult.group('DatType')

def read_dat(path,cur):
    datfile = open(path,"r")
    line = datfile.readline()
    if(line=="clrmamepro (\n"):
        dat = import_old_dat(datfile)
    else:
        dat = import_xml_dat(datfile)
    datfile.close()

def import_folder(path):
    con = lite.connect('sqlite/GameDB.db')
    cur = con.cursor()
    for xmlfile in os.listdir(path):
        read_dat(os.path.join(path,xmlfile),cur)

    con.close()

if __name__ == '__main__':
    import_folder('./DAT')

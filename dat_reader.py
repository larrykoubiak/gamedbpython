import regex as re
from collections import namedtuple, OrderedDict
import xml.etree.ElementTree as ET
import sqlite3 as lite
import ntpath
import os

regexes = {}
rom = namedtuple('Rom',['name','size','crc','md5','sha1','status'])
flag = namedtuple('Flag',['name','value'])
dat = namedtuple('DAT',['header','softwares'])

def init_database(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS tblDATs (datId INTEGER PRIMARY KEY,datFileName TEXT, systemName TEXT, systemManufacturer TEXT, datType TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblSoftwares (softwareId INTEGER PRIMARY KEY, softwareName TEXT, softwareType TEXT, datId INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblReleases (releaseId INTEGER PRIMARY KEY, releaseName TEXT, releaseType TEXT, softwareId INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblReleaseFlags (releaseFlagId INTEGER PRIMARY KEY, releaseFlagName TEXT, releaseFlagValue TEXT, releaseId INTEGER)")

def init_regexes():
    global regexes
    regexes["System"] = re.compile("^(?P<Manufacturer>.+?)\s-\s(?P<Name>.+?)(?:\s\((?P<Format>.+?)\))?(?:\s(?P<DatType>Parent-Clone)|$)")
    regexes["Software"] = re.compile("^(?:\[(?P<BIOS>BIOS)\]\s)?(?P<Name>[^\(]+)\s(?:.+?)(?:\((?P<Type>Addon|Coverdisk|Diskmag|Program).*\)|\)$|\]$)")
    regexes["DatTuple"] = re.compile("\t*(.+?) \"?(.+?)\"?$")
    regexes["Rom"] = re.compile("\( (?:name \"(?P<name>.*)\" )?(?:size (?P<size>.+?) )?(?:crc (?P<crc>.+?) )?(?:md5 (?P<md5>.+?) )?(?:sha1 (?P<sha1>.+?) )?(?:status (?P<status>.+?) )?\)")
    regexes["DevStatus"] = re.compile("\(.+?(?P<DevStatus>Beta|Proto|Sample)(?:\s\d)?\)")
    regexes["Demo"] = re.compile("(?:\((?=[^\(]*(?:, [^\(]*)*\))|(?<=, )\G|[\(]*)(?P<Demo>Demo|Promo|Budget)(?:, |[^\(]*\))")
    regexes["Region"] = re.compile("(?:\((?=[^,|\)]+(?:, [^,|\)]+)*\))|(?<=, )\G)(?P<Region>Australia|Brazil|Canada|China|France|Germany|Greece|Hong Kong|Italy|Japan|Korea|Netherlands|Norway|Russia|Spain|Sweden|USA|United Kingdom|Unknown|Asia|Europe|World)(?:, |\))")
    regexes["Compilation"] = re.compile("\((?:[^\)]*?)?\s?(?P<Compilation>Compilation)(?: - )?(?:[^\)]*?)?\)")
    regexes["Language"] = re.compile("(?:\((?=\w+(?:,\w+)*\))|(?<=,)\G)(?P<Language>En|Ja|Fr|De|Es|It|Nl|Pt|Sv|No|Da|Fi|Zh|Ko|Pl|Ru|,)(?:,|\))")
    regexes["Version"] = re.compile("\(.*?v(?P<Version>[\d|\.]+\w?)\s?(?:[^\)]*)\)")
    regexes["Revision"] = re.compile("\(.*?Rev (?P<Revision>[\d|\w|\.]+)(?:[^\)]*)?\)")
    regexes["License"] = re.compile("\((?P<License>Unl)\)")
    regexes["DumpStatus"] = re.compile("\[(?<BadDump>b)\]")

def get_regex_result(regname,value):
    global regexes
    return regexes[regname].search(value)

def get_regex_results(regname,value):
    global regexes
    return regexes[regname].finditer(value)

def import_old_dat(datfile):
    line = datfile.readline()
    header = {} 
    while(line !=")\n"):
        result = get_regex_result("DatTuple",line)
        if(result.group(1)=="name"):
            sysresult = get_regex_result("System",result.group(2))
            header['Manufacturer'] = sysresult.group('Manufacturer')
            header['Name'] = sysresult.group('Name')
            header['DatType'] = 'Standard' if sysresult.group('DatType') == None else sysresult.group('DatType')
        else:
            header[result.group(1)] = result.group(2)
        line = datfile.readline()
    softwares=OrderedDict()
    while(line != ''):
        line = datfile.readline() #skip line
        line = datfile.readline() #read game
        if(line == "game (\n"):
            line = datfile.readline()
            software = {}
            release = {}
            releaseflags = []
            datroms = []
            while(line !=")\n"):
                result = get_regex_result("DatTuple",line)
                if(result.group(1)=="name"):
                    #parse software
                    softresult = get_regex_result("Software",result.group(2))
                    software['Name'] = softresult.group('Name')
                    software['Type'] = 'BIOS' if softresult.group('BIOS') is not None else softresult.group('Type') if softresult.group('Type') is not None else 'Game'
                    software['Releases'] = []
                    release['Name'] = result.group(2)
                elif(result.group(1)=="description"):
                    release['Description'] = result.group(2)
                    #parse release
                    compilresult = get_regex_result("Compilation",release['Name'])
                    devstatusresult = get_regex_result("DevStatus",release['Name'])
                    demoresult = get_regex_result("Demo",release['Name'])
                    release['Type'] = compilresult.group('Compilation') if compilresult is not None else devstatusresult.group('DevStatus') if devstatusresult is not None else demoresult.group('Demo') if demoresult is not None else 'Commercial'
                    for regionresult in get_regex_results("Region",release['Name']):
                        releaseflags.append(flag('Region',regionresult.group('Region')))                    
                    for languageresult in get_regex_results("Language",release['Name']):
                        releaseflags.append(flag('Language',languageresult.group('Language')))
                    versionresult = get_regex_result("Version",release['Name'])
                    if(versionresult):
                        releaseflags.append(flag('Version',versionresult.group('Version')))
                    revisionresult = get_regex_result("Revision",release['Name'])
                    if(revisionresult):
                        releaseflags.append(flag('Revision',revisionresult.group('Revision')))
                    licenseresult = get_regex_result("License",release['Name'])
                    if(licenseresult):
                        releaseflags.append(flag('License',licenseresult.group('License')))
                    baddumpresult = get_regex_result("DumpStatus",release['Name'])
                    if(baddumpresult):
                        releaseflags.append(flag('BadDump',baddumpresult.group('BadDump')))
                elif(result.group(1)=="rom"):
                    #parse rom
                    romresult = result = get_regex_result("Rom",result.group(2))
                    datrom = rom(romresult.group('name'),romresult.group('size'), romresult.group('crc'),romresult.group('md5'),romresult.group('sha1'),romresult.group('status'))
                    datroms.append(datrom)
                line = datfile.readline()
            release['flags'] = releaseflags
            release['roms'] = datroms
            software['Releases'].append(release)
        softwares[software['Name']] = software
    return dat(header,softwares)
    
def import_xml_dat(datfile):
    datfile.seek(0)
    tree = ET.parse(datfile)
    root = tree.getroot()
    headernode = root.find('header')
    header = {}
    for field in list(headernode):
        if(field.tag=="name"):
            sysresult = get_regex_result("System",field.text)
            header['Manufacturer'] = sysresult.group('Manufacturer')
            header['Name'] = sysresult.group('Name')
            header['DatType'] = 'Standard' if sysresult.group('DatType') == None else sysresult.group('DatType')
        else:
            header[field.tag] = field.text
    print header['Name']
    softwares=OrderedDict()
    for gamenode in root.findall('game'):
        software = {}
        release = {}
        #software insert or select
        print '\t' + gamenode.get('name')
        if(gamenode.get('cloneof') is None):
            softresult = get_regex_result("Software",gamenode.get('name'))
        else:
            softresult = get_regex_result("Software",gamenode.get('cloneof'))
        if(softresult.group('Name') in softwares.keys()):
            software = softwares[softresult.group('Name')]
        else:
            software['Name'] = softresult.group('Name')
            software['Type'] = 'BIOS' if softresult.group('BIOS') is not None else softresult.group('Type') if softresult.group('Type') is not None else 'Game'
            software['Releases'] = []
            softwares[software['Name']] = software
        #releases
        release['Name'] = gamenode.get('name')
        releaseflags = []
        #release type
        compilresult = get_regex_result("Compilation",release['Name'])
        devstatusresult = get_regex_result("DevStatus",release['Name'])
        demoresult = get_regex_result("Demo",release['Name'])
        release['Type'] = compilresult.group('Compilation') if compilresult is not None else devstatusresult.group('DevStatus') if devstatusresult is not None else demoresult.group('Demo') if demoresult is not None else 'Commercial'
        #release flags
        release['Description'] = gamenode.find('description').text
        for regionresult in get_regex_results("Region",release['Name']):
            releaseflags.append(flag('Region',regionresult.group('Region')))
        for languageresult in get_regex_results("Language",release['Name']):
            releaseflags.append(flag('Language',languageresult.group('Language')))
        versionresult = get_regex_result("Version",release['Name'])
        if(versionresult):
            releaseflags.append(flag('Version',versionresult.group('Version')))
        revisionresult = get_regex_result("Revision",release['Name'])
        if(revisionresult):
            releaseflags.append(flag('Revision',revisionresult.group('Revision')))
        licenseresult = get_regex_result("License",release['Name'])
        if(licenseresult):
            releaseflags.append(flag('License',licenseresult.group('License')))
        baddumpresult = get_regex_result("DumpStatus",release['Name'])
        if(baddumpresult):
            releaseflags.append(flag('BadDump',baddumpresult.group('BadDump')))
        roms = []
        for romnode in gamenode.findall('rom'):
            datrom = rom(romnode.get('name'),romnode.get('size'),romnode.get('crc'),romnode.get('md5'),romnode.get('sha1'),romnode.get('status'))
            roms.append(datrom)
        release['roms'] = roms
        release['flags'] = releaseflags
        software['Releases'].append(release)
    return dat(header,softwares)

def read_dat(path,cur):
    datfile = open(path,"r")
    line = datfile.readline()
    if(line=="clrmamepro (\n"):
        dat = import_old_dat(datfile)
    else:
        dat = import_xml_dat(datfile)
    #import dat header
    cur.execute("INSERT INTO tblDATs (datFileName,systemName,systemManufacturer,datType) VALUES (?,?,?,?)",(ntpath.basename(path),dat.header['Manufacturer'],dat.header['Name'],dat.header['DatType']))
    datid = cur.lastrowid
    for softkey,softvalue in dat.softwares.iteritems():
        cur.execute("INSERT INTO tblSoftwares (softwareName,softwareType,datId) VALUES (?,?,?)",(softkey,softvalue['Type'],datid))
        softid = cur.lastrowid
        for release in softvalue['Releases']:
            cur.execute("INSERT INTO tblReleases (releaseName,releaseType,softwareId) VALUES (?,?,?)",(release['Name'],release['Type'],softid))
            relid = cur.lastrowid
            for flag in release['flags']:
                cur.execute("INSERT INTO tblReleaseFlags (releaseFlagName,releaseFlagValue,releaseId) VALUES (?,?,?)",(flag.name,flag.value,relid))
    datfile.close()

def import_folder(path):
    con = lite.connect('sqlite/GameFAQs.db')
    cur = con.cursor()
    init_database(cur)
    for xmlfile in os.listdir(path):
        read_dat(os.path.join(path,xmlfile),cur)
    #fix software types for unpublished games
    sql = """UPDATE tblSoftwares SET softwareType = 'Unpublished' WHERE softwareId IN
            (SELECT s.softwareId FROM tblSoftwares s INNER JOIN tblDATs d On d.datId = s.datId
            INNER JOIN (SELECT s2.softwareId FROM tblSoftwares s2 INNER JOIN tblReleases r ON r.softwareId = s2.softwareId
            GROUP BY s2.softwareId HAVING SUM(CASE WHEN r.releaseType = 'Commercial' THEN 1 ELSE 0 END) = 0
            ) sub ON sub.softwareId = s.softwareId)"""
    cur.execute(sql)
    con.commit()
    con.close()

if __name__ == '__main__':
    init_regexes()
    import_folder('./DAT')

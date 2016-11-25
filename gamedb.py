import sqlite3 as lite
import os
from datetime import datetime
from collections import namedtuple
import io

from dat import DAT
from regexes import GameDBRegex
from scraper import Scraper
from matcher import Matcher
from exporter import Exporter

flag = namedtuple('Flag',['name','value'])

class GameDB:
    def __init__(self):
        self.regexes = GameDBRegex()
        if not os.path.exists('sqlite'):
            os.makedirs('sqlite')
        self.con = lite.connect('sqlite/GameDB.db')
        self.cur = self.con.cursor()
        self.dats = []
        self.scrapers = []
        self.exporter = Exporter()
        self.matcher = Matcher()
        self.init_database()

    def init_database(self):
        sqlfile = io.open('create_db.sql','r',encoding='utf-8').read()
        self.cur.executescript(sqlfile)
        self.con.commit()
        
    def getSystem(self,manufacturer,systemName):
        system = {}
        systemId = None
        query = "SELECT systemId FROM tblSystems WHERE systemName = ? AND systemManufacturer = ?"
        self.cur.execute(query,(systemName,manufacturer))
        systemrow = self.cur.fetchone()
        if systemrow is None:
             query = "INSERT INTO tblSystems (systemName, systemManufacturer) VALUES (?,?)"
             self.cur.execute(query,(systemName,manufacturer))
             systemId = self.cur.lastrowid
        else:
            systemId = systemrow[0]
        return systemId

    def getSystemName(self,systemId):
        systemName = ""
        query = "SELECT systemManufacturer || ' - ' || systemName FROM tblSystems WHERE systemId = " + systemId
        self.cur.execute(query)
        systemrow = self.cur.fetchone()
        if systemrow is not None:
            systemName = systemrow[0]
        return systemName
    
    def getDATReleaseGroup(self,dat):
        releaseGroup = None
        if('comment' in dat.header):
            if(header['comment'] == "no-intro | www.no-intro.org"):
                releaseGroup = "No-Intro"
        elif('url' in dat.header):
            if(dat.header['url'] == "www.no-intro.org"):
                releaseGroup = "No-Intro"
            elif(dat.header['url'] == "http://www.fbalpha.com/"):
                releaseGroup = "FBA"
        else:
            if(dat.header['homepage'] is not None):
                if(dat.header['homepage'] == "TOSEC"):
                    releaseGroup = "TOSEC"
                elif(dat.header['homepage'] == "redump.org"):
                    releaseGroup = "Redump"
        return releaseGroup
    
    def getDATDate(self,dat):
        datDate = None
        if(dat.header['version'] is not None or dat.header['date'] is not None):
            dateResult = self.regexes.get_regex_result("DatDate",dat.header['version'] if dat.header['version'] is not None else dat.header['date'])
            if(dateResult is not None):
                year = int(dateResult.group('Year'))
                month = int(dateResult.group('Month'))
                day = int(dateResult.group('Day'))
                hour = int(dateResult.group('Hour'))
                minute = int(dateResult.group('Minute'))
                second = int(dateResult.group('Second'))
                datDate = datetime(year,month,day,hour,minute,second)
        return datDate

    def getDATFile(self,dat):
        datfile = {}
        datFileId = None
        releaseGroup = self.getDATReleaseGroup(dat)
        self.regexes.init_regexes(releaseGroup)
        #fill dictionary 
        sysresult = self.regexes.get_regex_result("System",dat.header["name"])
        datfile["systemId"] = self.getSystem(sysresult.group('Manufacturer'),sysresult.group('Name'))
        datfile["datFileName"] = dat.filename
        datfile["datType"] = 'Standard' if sysresult.group('DatType') == None else sysresult.group('DatType')
        datfile["datReleaseGroup"] = releaseGroup
        datfile['datDate'] = self.getDATDate(dat)
        #check in DB
        query = "SELECT datFileId FROM tblDatFiles WHERE systemId = :systemId AND datFileName = :datFileName AND datType = :datType AND datReleaseGroup = :datReleaseGroup AND datDate = :datDate"
        self.cur.execute(query,datfile)
        datfilerow = self.cur.fetchone()
        if datfilerow is None:
            sql = "INSERT INTO tblDATFiles (systemId,datFileName,datType,datReleaseGroup, datDate) VALUES (:systemId,:datFileName,:datType,:datReleaseGroup,:datDate)"
            self.cur.execute(sql,datfile)
            datFileId = self.cur.lastrowid
        else:
            datFileId = datfilerow[0]
        return datFileId

    def getDATGame(self,game,datFileId):
        datsoft = {}
        datGameId = None
        datsoft['datFileId'] = datFileId
        datsoft['datGameName'] = game['Name']
        datsoft['datCloneOf'] = game['CloneOf']
        datsoft['datRomOf'] = game['RomOf']
        query = "SELECT datGameId FROM tblDatGames WHERE datFileId = :datFileId AND datGameName = :datGameName AND datCloneOf = :datCloneOf AND datRomOf = :datRomOf"
        self.cur.execute(query,datsoft)
        datgamerow = self.cur.fetchone()
        if datgamerow is None:
            sql = "INSERT INTO tblDatGames (datFileId,datGameName,datCloneOf,datRomOf) VALUES (:datFileId,:datGameName,:datCloneOf,:datRomOf)"
            self.cur.execute(sql,datsoft)
            datGameId = self.cur.lastrowid
        else:
            datGameId = datgamerow[0]
        return datGameId

    def getDATROM(self,rom,datFileId,datGameId):
        datrom = {}
        datROMId = None
        datrom['datFileId'] = datFileId
        datrom['datGameId'] = datGameId
        datrom['datROMName'] = rom['name']
        datrom['datROMMerge'] = rom['merge']
        datrom['datROMSize'] = rom['size']
        datrom['datROMCRC'] = rom['crc']
        datrom['datROMMD5'] = rom['md5']
        datrom['datROMSHA1'] = rom['sha1']
        query = """SELECT datRomId FROM tblDatRoms WHERE datFileId = :datFileId AND datGameId = :datGameId AND datROMName = :datROMName AND datROMMerge = :datROMMerge AND
                    datROMSize = :datROMSize AND datROMCRC = :datROMCRC AND datROMMD5 = :datROMMD5 AND datROMSHA1 = :datROMSHA1"""
        self.cur.execute(query,datrom)
        datromrow = self.cur.fetchone()
        if datromrow is None:
            sql = "INSERT INTO tblDatRoms (datFileId,datGameId,datROMName,datROMMerge,datROMSize,datROMCRC,datROMMD5,datROMSHA1) VALUES (:datFileId,:datGameId,:datROMName,:datROMMerge,:datROMSize,:datROMCRC,:datROMMD5,:datROMSHA1)"
            self.cur.execute(sql,datrom)
            datROMId = self.cur.lastrowid
        else:
            datROMId = datromrow[0]
        return datROMId
                             
    def getSoftware(self,gameName,systemId):
        software = {}
        softwareId = None
        softresult = self.regexes.get_regex_result("Software",gameName)
        software['softwareName'] = softresult.group('Name')
        software['softwareType'] = 'BIOS' if softresult.group('BIOS') is not None else softresult.group('Type') if softresult.group('Type') is not None else 'Game'
        software['systemId'] = systemId
        query = "SELECT softwareId FROM tblSoftwares WHERE softwareName = :softwareName AND softwareType = :softwareType AND systemId = :systemId"
        self.cur.execute(query,software)
        softwarerow = self.cur.fetchone()
        if softwarerow is None:
            query = "INSERT INTO tblSoftwares (softwareName,softwareType,systemId) VALUES (:softwareName,:softwareType,:systemId)"
            self.cur.execute(query,software)
            softwareId = self.cur.lastrowid
        else:
            softwareId = softwarerow[0]
        return softwareId

    def getReleaseFlag(self,flagName):
        flagId = None
        query = "SELECT releaseFlagId FROM tblReleaseFlags WHERE releaseFlagName = '" + flagName + "'"
        self.cur.execute(query)
        flagrow = self.cur.fetchone()
        if flagrow is None:
            query = "INSERT INTO tblReleaseFlags (releaseFlagName) VALUES ('" + flagName + "')"
            self.cur.execute(query)
            flagId = self.cur.lastrowid
        else:
            flagId = flagrow[0]
        return flagId

    def getRelease(self,releaseName,softwareId):
        release = {}
        releaseId = None
        release['releaseName'] = releaseName
        compresult = self.regexes.get_regex_result("Compilation",releaseName)
        devstatusresult = self.regexes.get_regex_result("DevStatus",releaseName)
        demoresult = self.regexes.get_regex_result("Demo",releaseName)
        licenseresult = self.regexes.get_regex_result("License",releaseName)
        if compresult is not None:
            release['releaseType'] = compresult.group('Compilation')
        elif devstatusresult is not None:
            release['releaseType'] = devstatusresult.group('DevStatus')
        elif demoresult is not None:
            release['releaseType'] = demoresult.group('Demo')
        elif licenseresult is not None:
            release['releaseType'] = licenseresult.group('License')
        else:
            release['releaseType'] = 'Commercial'
        release['softwareId'] = softwareId
        query = "SELECT releaseId FROM tblReleases WHERE releaseName = :releaseName AND releaseType = :releaseType AND softwareId = :softwareId"
        self.cur.execute(query,release)
        releaserow = self.cur.fetchone()
        if releaserow is None:
            query = "INSERT INTO tblReleases (releaseName,releaseType,softwareId) VALUES (:releaseName,:releaseType,:softwareId)"
            self.cur.execute(query,release)
            releaseId = self.cur.lastrowid
        else:
            releaseId = releaserow[0]
        #release flags
        releaseflags = []
        for regionresult in self.regexes.get_regex_results("Region",releaseName):
            releaseflags.append([releaseId,self.getReleaseFlag('Region'),regionresult.group('Region')])
        for languageresult in self.regexes.get_regex_results("Language",releaseName):
            releaseflags.append([releaseId,self.getReleaseFlag('Language'),languageresult.group('Language')])
        versionresult = self.regexes.get_regex_result("Version",releaseName)
        if(versionresult):
            releaseflags.append([releaseId,self.getReleaseFlag('Version'),versionresult.group('Version')])
        revisionresult = self.regexes.get_regex_result("Revision",releaseName)
        if(revisionresult):
            releaseflags.append([releaseId,self.getReleaseFlag('Revision'),revisionresult.group('Revision')])
        baddumpresult = self.regexes.get_regex_result("DumpStatus",releaseName)
        if(baddumpresult):
            releaseflags.append([releaseId,self.getReleaseFlag('BadDump'),baddumpresult.group('BadDump')])
        for flag in releaseflags:
            query = "SELECT 1 FROM tblReleaseFlagValues WHERE releaseId = ? AND releaseFlagId = ? AND releaseFlagValue = ?"
            self.cur.execute(query,flag)
            flagrow = self.cur.fetchone()
            if flagrow is None:
                query = "INSERT INTO tblReleaseFlagValues (releaseId,releaseFlagId,releaseFlagValue) VALUES (?,?,?)"
                self.cur.execute(query,flag)
        return releaseId

    def getROM(self,releaseId,romsize,romcrc,rommd5,romsha1):
        rom = {}
        romId = None
        rom['releaseId'] = releaseId
        rom['crc32'] = romcrc
        rom['md5'] = rommd5
        rom['sha1'] = romsha1
        rom['size'] = romsize
        query = "SELECT romId FROM tblROMs WHERE releaseId = :releaseId AND crc32 = :crc32 AND md5 = :md5 AND sha1 = :sha1 AND size = :size"
        self.cur.execute(query,rom)
        romrow = self.cur.fetchone()
        if romrow is None:
            query = "INSERT INTO tblROMs (releaseId,crc32,md5,sha1,size) VALUES (:releaseId,:crc32,:md5,:sha1,:size)"
            self.cur.execute(query,rom)
            romId = self.cur.lastrowid
        else:
            romId = romrow[0]
        return romId

    def getScraper(self,name,url):
        scraperId = None
        scraperDic = {}
        scraperDic['Name'] = name
        scraperDic['URL'] = url
        query = "SELECT scraperId FROM tblScrapers WHERE scraperName=:Name AND scraperURL=:URL"
        self.cur.execute(query,scraperDic)
        scraperrow = self.cur.fetchone()
        if scraperrow is None:
            query = "INSERT INTO tblScrapers (scraperName, scraperURL) VALUES (:Name,:URL)"
            self.cur.execute(query,scraperDic)
            scraperId = self.cur.lastrowid
        else:
            scraperId = scraperrow[0]
        return scraperId

    def getScraperSystem(self,scraperId,systemname,systemacronym,systemurl):
        scraperSystemId = None
        scraperSystemDic = {}
        scraperSystemDic['scraperId'] = scraperId
        scraperSystemDic['scraperSystemName'] = systemname
        scraperSystemDic['scraperSystemAcronym'] = systemacronym
        scraperSystemDic['scraperSystemURL'] = systemurl
        query = "SELECT scraperSystemId FROM tblScraperSystems WHERE scraperId=:scraperId AND scraperSystemName=:scraperSystemName AND scraperSystemAcronym=:scraperSystemAcronym AND scraperSystemURL=:scraperSystemURL"
        self.cur.execute(query,scraperSystemDic)
        scraperSystemrow = self.cur.fetchone()
        if scraperSystemrow is None:
            query = "INSERT INTO tblScraperSystems (scraperId,scraperSystemName,scraperSystemAcronym,scraperSystemURL) VALUES (:scraperId,:scraperSystemName,:scraperSystemAcronym,:scraperSystemURL)"
            self.cur.execute(query,scraperSystemDic)
            scraperSystemId = self.cur.lastrowid
        else:
            scraperSystemId = scraperSystemrow[0]
        return scraperSystemId

    def getScraperGame(self,systemid,gamename,gameurl):
        scraperGameId = None
        scraperGameDic = {}
        scraperGameDic['scraperSystemId'] = systemid
        scraperGameDic['scraperGameName'] = gamename
        scraperGameDic['scraperGameURL'] = gameurl
        query = "SELECT scraperGameId FROM tblScraperGames WHERE scraperSystemId=:scraperSystemId AND scraperGameName=:scraperGameName AND scraperGameURL=:scraperGameURL"
        self.cur.execute(query,scraperGameDic)
        scraperGamerow = self.cur.fetchone()
        if scraperGamerow is None:
            query = "INSERT INTO tblScraperGames (scraperSystemId,scraperGameName,scraperGameURL) VALUES (:scraperSystemId,:scraperGameName,:scraperGameURL)"
            self.cur.execute(query,scraperGameDic)
            scraperGameId = self.cur.lastrowid
        else:
            scraperGameId = scraperGamerow[0]
        return scraperGameId

    def getScraperRelease(self,gameid,name,region):
        scraperReleaseId = None
        scraperReleaseDic = {}
        scraperReleaseDic['scraperGameId'] = gameid
        scraperReleaseDic['scraperReleaseName'] = name
        scraperReleaseDic['scraperReleaseRegion'] = region
        query = "SELECT scraperReleaseId FROM tblScraperReleases WHERE scraperGameId=:scraperGameId AND scraperReleaseName=:scraperReleaseName AND scraperReleaseRegion=:scraperReleaseRegion"
        self.cur.execute(query,scraperReleaseDic)
        scraperReleaserow = self.cur.fetchone()
        if scraperReleaserow is None:
            query = "INSERT INTO tblScraperReleases (scraperGameId,scraperReleaseName,scraperReleaseRegion) VALUES (:scraperGameId,:scraperReleaseName,:scraperReleaseRegion)"
            self.cur.execute(query,scraperReleaseDic)
            scraperReleaseId = self.cur.lastrowid
        else:
            scraperReleaseId = scraperReleaserow[0]
        return scraperReleaseId

    def getScraperReleaseImage(self,releaseid,name,imagetype):
        scraperReleaseImageId = None
        scraperReleaseImageDic = {}
        scraperReleaseImageDic['scraperReleaseId'] = releaseid
        scraperReleaseImageDic['scraperReleaseImageName'] = name
        scraperReleaseImageDic['scraperReleaseImageType'] = imagetype
        query = "SELECT scraperReleaseImageId FROM tblScraperReleaseImages WHERE scraperReleaseId=:scraperReleaseId AND scraperReleaseImageName=:scraperReleaseImageName AND scraperReleaseImageType=:scraperReleaseImageType"
        self.cur.execute(query,scraperReleaseImageDic)
        scraperReleaseImagerow = self.cur.fetchone()
        if scraperReleaseImagerow is None:
            query = "INSERT INTO tblScraperReleaseImages (scraperReleaseId,scraperReleaseImageName,scraperReleaseImageType) VALUES (:scraperReleaseId,:scraperReleaseImageName,:scraperReleaseImageType)"
            self.cur.execute(query,scraperReleaseImageDic)
            scraperReleaseImageId = self.cur.lastrowid
        else:
            scraperReleaseImageId = scraperReleaseImagerow[0]
        return scraperReleaseImageId

    def getSynonym(self,synonymDic):
        synonymId = None
        query = "SELECT key, value, type FROM tblSynonyms WHERE key=:key AND value=:value AND type=:type"
        self.cur.execute(query,synonymDic)
        synonymrow = self.cur.fetchone()
        if synonymrow is None:
            query = "INSERT INTO tblSynonyms (key,value,type) VALUES (:key,:value,:type)"
            self.cur.execute(query,synonymDic)

    def getSystemMatch(self,systemId,scraperSystemId):
        systemMatchDic = {}
        systemMatchDic['systemId'] = systemId
        systemMatchDic['scraperSystemId'] = scraperSystemId
        query = "SELECT 1 FROM tblSystemMap WHERE systemId = :systemId AND scraperSystemId = :scraperSystemId"
        self.cur.execute(query,systemMatchDic)
        systemMatchrow = self.cur.fetchone()
        if systemMatchrow is None:
            query = "INSERT INTO tblSystemMap (systemId, scraperSystemId) VALUES (:systemId,:scraperSystemId)"
            self.cur.execute(query,systemMatchDic)
        else:
            pass

    def getSoftwareMatch(self,softwareId,scraperGameId):
        softwareMatchDic = {}
        softwareMatchDic['softwareId'] = softwareId
        softwareMatchDic['scraperGameId'] = 0 if scraperGameId is None else scraperGameId
        query = "SELECT 1 FROM tblSoftwareMap WHERE softwareId = :softwareId AND scraperGameId = IFNULL(:scraperGameId,0)"
        self.cur.execute(query,softwareMatchDic)
        softwareMatchrow = self.cur.fetchone()
        if softwareMatchrow is None:
            query = "INSERT INTO tblSoftwareMap (softwareId, scraperGameId) VALUES (:softwareId,:scraperGameId)"
            self.cur.execute(query,softwareMatchDic)
        else:
            pass

    def getReleaseMatch(self,releaseId,scraperReleaseId):
        releaseMatchDic = {}
        releaseMatchDic['releaseId'] = releaseId
        releaseMatchDic['scraperReleaseId'] = scraperReleaseId
        query = "SELECT 1 FROM tblReleaseMap WHERE releaseId = :releaseId AND scraperReleaseId = :scraperReleaseId"
        self.cur.execute(query,releaseMatchDic)
        releaseMatchrow = self.cur.fetchone()
        if releaseMatchrow is None:
            query = "INSERT INTO tblReleaseMap (releaseId, scraperReleaseId) VALUES (:releaseId, :scraperReleaseId)"
            self.cur.execute(query,releaseMatchDic)
        else:
            pass
        
    def import_dat(self,dat):
        datGameId = None
        datRomId = None
        datFileId = self.getDATFile(dat)
        for gamekey,gamevalue in dat.softwares.iteritems():
            datGameId = self.getDATGame(gamevalue,datFileId)
            for rom in gamevalue['Roms']:
                datRomId = self.getDATROM(rom,datFileId,datGameId)
        self.con.commit()
                             
    def import_new_ROMS(self):
        romId = None
        releaseId = None
        softwareId = None
        releaseGroup = None
        systemId = None
        query = """SELECT df.systemId, df.datReleaseGroup, dg.datGameName, dg.datCloneOf, dr.datGameId, dr.datROMSize, dr.datROMCRC,dr.datROMMD5,dr.datROMSHA1 
                    FROM tblDatRoms dr INNER JOIN tblDatFiles df ON df.datFileId = dr.datFileId INNER JOIN tblDatGames dg ON dg.datGameId = dr.datGameId 
                    LEFT JOIN tblROMs r ON r.crc32 = dr.datROMCRC AND r.md5 = dr.datROMMD5 AND r.sha1 = dr.datROMSHA1 WHERE r.romID IS NULL"""
        self.cur.execute(query)
        datRoms = self.cur.fetchall()
        for datRom in datRoms:
            #get releaseGroup regexes
            if releaseGroup != datRom[1]:
                releaseGroup = datRom[1]
                self.regexes.init_regexes(releaseGroup)
            #get system
            if systemId != datRom[0]:
                systemId = datRom[0]
                print "exporting new roms for " + self.getSystemName(systemId)
            #get software
            gameName = datRom[2] if datRom[3] == '' else datRom[3]
            softwareId = self.getSoftware(gameName,datRom[0])
            #get release
            releaseName = datRom[2]
            releaseId = self.getRelease(releaseName,softwareId)
            #get rom
            romId = self.getROM(releaseId,*datRom[5:])
        self.con.commit()

    def import_dats(self):
        self.dats = []
        for xmlfile in os.listdir("DAT"):
            dat = DAT()
            dat.read_dat(os.path.join("DAT",xmlfile))
            self.dats.append(dat)
        for dat in self.dats:
            print "parsing " + dat.filename
            self.import_dat(dat)
        self.dats = None
        self.import_new_ROMS()
        

    def import_scrapers(self):
        self.scrapers = []
        scrapersfile = io.open('Scrapers/scrapers.csv','r',encoding='utf-8')
        for scraperline in scrapersfile:
            scraperCols = scraperline.split(';')
            scraperId = self.getScraper(*scraperCols)
            scraper = Scraper(*scraperCols)
            for scraperSystemKey,scraperSystem in scraper.systems.items():
                print "exporting game data for " + scraper.name + " - " + scraperSystemKey
                scraperSystemId = self.getScraperSystem(scraperId,scraperSystem['systemName'],scraperSystem['systemAcronym'],scraperSystem['systemURL'])
                for scraperGameKey,scraperGame in scraperSystem['systemGames'].items():
                    scraperGameId = self.getScraperGame(scraperSystemId,scraperGame['gameName'],scraperGame['gameUrl'])
                    if scraperGame['gameParsed']=='Yes':
                        for flag in scraperGame['softwareFlags']:
                            query = "SELECT 1 FROM tblScraperGameFlags WHERE scraperGameId = ? AND scraperGameFlagName = ? AND scraperGameFlagValue = ?"
                            self.cur.execute(query,(scraperGameId,flag['name'],flag['value']))
                            flagrow = self.cur.fetchone()
                            if flagrow is None:
                                query = "INSERT INTO tblScraperGameFlags (scraperGameId,scraperGameFlagName,scraperGameFlagValue) VALUES (?,?,?)"
                                self.cur.execute(query,(scraperGameId,flag['name'],flag['value']))
                        for scraperRelease in scraperGame['releases']:
                            scraperReleaseId = self.getScraperRelease(scraperGameId,scraperRelease['name'],scraperRelease['region'])
                            for flag in scraperRelease['releaseFlags']:
                                query = "SELECT 1 FROM tblScraperReleaseFlags WHERE scraperReleaseId = ? AND scraperReleaseFlagName = ? AND scraperReleaseFlagValue = ?"
                                self.cur.execute(query,(scraperReleaseId,flag['name'],flag['value']))
                                flagrow = self.cur.fetchone()
                                if flagrow is None:
                                    query = "INSERT INTO tblScraperReleaseFlags (scraperReleaseId,scraperReleaseFlagName,scraperReleaseFlagValue) VALUES (?,?,?)"
                                    self.cur.execute(query,(scraperReleaseId,flag['name'],flag['value']))
                            for scraperReleaseImage in scraperRelease['releaseImages']:
                                scraperReleaseImageId = self.getScraperReleaseImage(scraperReleaseId,scraperReleaseImage['name'],scraperReleaseImage['type'])                            
        self.con.commit()

    def match_systems(self):
        systemDic = {}
        for synonym in self.matcher.synonyms:
            self.getSynonym(synonym)
        query = "SELECT systemId, systemName FROM tblSystems"
        self.cur.execute(query)
        for row in self.cur:
            systemDic[row[0]] = row[1]
        query = "SELECT scraperSystemId, scraperSystemName FROM tblScraperSystems"
        self.cur.execute(query)
        scraperSystems = self.cur.fetchall()
        #create fuzzy matches for system
        for scraperSystem in scraperSystems:
            print "Matching System : " + scraperSystem[1]
            #use synonym table to find match
            query = "SELECT s.systemId FROM tblSystems s INNER JOIN tblSynonyms sn ON sn.key = s.systemName AND sn.type = 'System' INNER JOIN tblScraperSystems ss ON ss.scraperSystemName = sn.value WHERE ss.scraperSystemId = " + str(scraperSystem[0])
            self.cur.execute(query)
            systemrows = self.cur.fetchall()
            for systemrow in systemrows:
                self.getSystemMatch(systemrow[0],scraperSystem[0])
        self.con.commit()

    def match_softwares(self):
        scrapedGamesDic = {}
        query = """SELECT s.systemId, s.systemName, ss.scraperSystemId FROM tblSystems s INNER JOIN tblSystemMap sm on s.systemId = sm.systemId INNER JOIN
                tblScraperSystems ss on sm.scraperSystemId = ss.scraperSystemId WHERE ss.scraperId = 1"""
        self.cur.execute(query)
        systems = self.cur.fetchall()
        for system in systems:
            print "Matching Softwares for System : " + system[1]
            releaseDic = {}
            gameDic = {}
            query = """SELECT DISTINCT sr.scraperReleaseId, sr.scraperReleaseName, sr.scraperGameId FROM tblScraperReleases
                    sr INNER JOIN tblScraperGames sg ON sg.scraperGameId = sr.scraperGameId WHERE sg.scraperSystemId = ?"""
            self.cur.execute(query,(system[2],))
            for row in self.cur:
                releaseDic[row[0]] = row[1]
                gameDic[row[0]] = row[2]

            query = "SELECT softwareId, softwareName FROM tblSoftwares s WHERE s.systemId = ? AND NOT EXISTS (SELECT 1 FROM tblSoftwareMap WHERE softwareId = s.softwareId AND scraperGameId IS NOT NULL)"
            self.cur.execute(query,(system[0],))
            softwares = self.cur.fetchall()
            for software in softwares:
                scraperReleaseId = self.matcher.match_fuzzy(releaseDic,software[1],"Full",80)
                if scraperReleaseId == None:
                    scraperReleaseId = self.matcher.match_fuzzy(releaseDic,software[1],"Partial",86)
                self.getSoftwareMatch(software[0],None if scraperReleaseId is None else gameDic[scraperReleaseId])
        self.con.commit()

    def match_releases(self):
        query = """SELECT s.systemId, s.systemName, ss.scraperSystemId FROM tblSystems s INNER JOIN tblSystemMap sm on s.systemId = sm.systemId INNER JOIN
                tblScraperSystems ss on sm.scraperSystemId = ss.scraperSystemId WHERE ss.scraperId = 1"""
        self.cur.execute(query)
        systems = self.cur.fetchall()
        for system in systems:
            print "Matching Releases for System : " + system[1]
            query = """SELECT r.releaseId, r.releaseName, r.releaseType, 
                    GROUP_CONCAT(CASE WHEN rf.releaseFlagName = 'Region' THEN sy.value END) Region,
                    so.softwareId, s.systemManufacturer || ' - ' || s.systemName systemName,sm.scraperGameId,sg.scraperGameName
                    FROM 
                    tblReleases r INNER JOIN
                    tblReleaseFlagValues rfv On rfv.releaseId = r.releaseId INNER JOIN
                    tblReleaseFlags rf ON rf.releaseFlagId = rfv.releaseFlagId INNER JOIN
                    tblSynonyms sy ON sy.key = rfv.releaseFlagValue AND sy.type = 'Region' INNER JOIN
                    tblSoftwares so ON r.softwareId = so.softwareId INNER JOIN
                    tblSystems s ON s.systemId = so.systemId INNER JOIN
                    tblSoftwareMap sm ON sm.softwareId = so.softwareId INNER JOIN
                    tblScraperGames sg ON sg.scraperGameId = sm.scraperGameId
                    WHERE r.releaseType = 'Commercial' AND s.systemId = ?
                    GROUP BY r.releaseId, r.releaseName, so.softwareId, sm.scraperGameId,sg.scraperGameName,s.systemManufacturer || ' - ' || s.systemName"""
            self.cur.execute(query,(system[0],))
            releaserows = self.cur.fetchall()
            for releaserow in releaserows:
                scraperReleaseDic = {}
                scraperReleaseDic['scraperGameId'] = releaserow[6]
                scraperReleaseDic['scraperReleaseRegion'] = releaserow[3]
                query = """SELECT sr.scraperReleaseId,sr.scraperReleaseName
                    FROM tblScraperReleases sr 
                    WHERE sr.scraperGameId = :scraperGameId AND sr.scraperReleaseRegion = :scraperReleaseRegion"""
                self.cur.execute(query,scraperReleaseDic)
                matches = self.cur.fetchall()
                if len(matches) == 1:
                    self.getReleaseMatch(releaserow[0],matches[0][0])
                elif len(matches) > 1:
                    releaseDic = {}
                    for match in matches:
                        releaseDic[match[0]] = match[1]
                    scraperReleaseId = self.matcher.match_fuzzy(releaseDic,releaserow[1],"Full",80)
                    self.getReleaseMatch(releaserow[0],scraperReleaseId)
        self.con.commit()
        
    def export_releaseflags(self):
        for flagname in ['origin']:
            flag = {}
            flag['name'] = flagname
            if flagname == 'origin':
                flag['releaseFlagName'] = 'Region'
            flag['systems'] = []
            query ="""SELECT DISTINCT rf.releaseFlagName, s.systemManufacturer || ' - ' || s.systemName systemName, s.systemId
                    FROM tblReleaseFlags rf INNER JOIN
                    tblReleaseFlagValues rfv ON rfv.releaseFlagId = rf.releaseFlagId INNER JOIN
                    tblReleases r ON r.releaseId = rfv.releaseId INNER JOIN
                    tblSoftwares so ON so.softwareId = r.softwareId INNER JOIN 
                    tblSystems s ON s.systemId = so.systemId
                    WHERE rf.releaseFlagName = ?"""
            self.cur.execute(query,(flag['releaseFlagName'],))
            systemrows = self.cur.fetchall()
            for systemrow in systemrows:
                system = {}
                system['name'] = systemrow[1]
                system['roms'] = []
                query = """SELECT ro.crc32, r.releaseName, GROUP_CONCAT(DISTINCT rfv.releaseFlagValue) flagValue
                        FROM tblROMs ro INNER JOIN 
                        tblReleases r ON r.releaseId = ro.releaseId INNER JOIN
                        tblSoftwares so ON so.softwareId = r.softwareId INNER JOIN
                        tblReleaseFlagValues rfv ON rfv.releaseId = r.releaseId INNER JOIN
                        tblReleaseFlags rf ON rf.releaseFlagId = rfv.releaseFlagId
                        WHERE so.systemId = ? AND rf.releaseFlagName = ?
                        GROUP BY ro.crc32, r.releaseName"""
                self.cur.execute(query,(systemrow[2],flag['releaseFlagName']))
                romrows = self.cur.fetchall()
                for romrow in romrows:
                    rom = {}
                    rom['name'] = romrow[1]
                    rom['flagvalue'] = romrow[2]
                    rom['crc'] = romrow[0]
                    system['roms'].append(rom)
                flag['systems'].append(system)
            print "Exporting release flag " + flagname
            self.exporter.export_rdb_dat(flag)

    def export_scraperSoftwareFlags(self):
        for flagname in ['developer','franchise','genre']:
            flag = {}
            flag['name'] = flagname
            if flagname == "developer":
                flag['scraperGameFlagName'] = "Developer"
            elif flagname == "franchise":
                flag['scraperGameFlagName'] = "Franchise"
            elif flagname == "genre":
                flag['scraperGameFlagName'] = "Genre"
            else:
                pass
            flag['systems'] = []
            query = """SELECT DISTINCT sgf.scraperGameFlagName, s.systemManufacturer || ' - ' || s.systemName systemName, s.systemId
                    FROM tblScraperGameFlags sgf INNER JOIN
                    tblScraperGames sg ON sg.scraperGameId = sgf.scraperGameId INNER JOIN
                    tblScraperSystems ss ON ss.scraperSystemId = sg.scraperSystemId INNER JOIN
                    tblSystemMap sm ON sm.scraperSystemId = ss.scraperSystemId INNER JOIN
                    tblSystems s ON s.systemId = sm.systemId
                    WHERE scraperGameFlagName = ?"""
            self.cur.execute(query,(flag['scraperGameFlagName'],))
            systemrows = self.cur.fetchall()
            for systemrow in systemrows:
                system = {}
                system['name'] = systemrow[1]
                system['roms'] = []
                query = """SELECT ro.crc32, r.releaseName, sgf.scraperGameFlagValue
                        FROM tblROMs ro INNER JOIN 
                        tblReleases r ON r.releaseId = ro.releaseId INNER JOIN
                        tblSoftwares so ON so.softwareId = r.softwareId INNER JOIN
                        tblSoftwareMap sm ON sm.softwareId = so.softwareId INNER JOIN
                        tblScraperGameFlags sgf ON sgf.scraperGameId = sm.scraperGameId
                        WHERE so.systemId = ? AND sgf.scraperGameFlagName = ?"""
                self.cur.execute(query,(systemrow[2],flag['scraperGameFlagName']))
                romrows = self.cur.fetchall()
                for romrow in romrows:
                    rom = {}
                    rom['name'] = romrow[1]
                    rom['flagvalue'] = romrow[2]
                    rom['crc'] = romrow[0]
                    system['roms'].append(rom)
                flag['systems'].append(system)
            print "Exporting sraped software flag " + flagname
            self.exporter.export_rdb_dat(flag)

    def export_scraperReleaseFlags(self):
        for flagname in ['publisher','serial','releasemonth','releaseyear']:
            flag = {}
            flag['name'] = flagname
            if flagname == "publisher":
                flag['scraperReleaseFlagName'] = "ReleasePublisher"
            elif flagname == "serial":
                flag['scraperReleaseFlagName'] = "ReleaseProductID"
            elif flagname == "releasemonth":
                flag['scraperReleaseFlagName'] = "ReleaseDate"
            elif flagname == "releaseyear":
                flag['scraperReleaseFlagName'] = "ReleaseDate"
            else:
                pass
            flag['systems'] = []
            query = """SELECT DISTINCT srf.scraperReleaseFlagName, s.systemManufacturer || ' - ' || s.systemName systemName, s.systemId
                    FROM tblScraperReleaseFlags srf INNER JOIN
                    tblScraperReleases sr ON sr.scraperReleaseId = srf.scraperReleaseId INNER JOIN
                    tblScraperGames sg ON sg.scraperGameId = sr.scraperReleaseId INNER JOIN
                    tblScraperSystems ss ON ss.scraperSystemId = sg.scraperSystemId INNER JOIN
                    tblSystemMap sm ON sm.scraperSystemId = ss.scraperSystemId INNER JOIN
                    tblSystems s ON s.systemId = sm.systemId
                    WHERE srf.scraperReleaseFlagName = ?"""
            self.cur.execute(query,(flag['scraperReleaseFlagName'],))
            systemrows = self.cur.fetchall()
            for systemrow in systemrows:
                system = {}
                system['name'] = systemrow[1]
                system['roms'] = []
                query = """SELECT ro.crc32, r.releaseName, srf.scraperReleaseFlagValue
                        FROM tblROMs ro INNER JOIN 
                        tblReleases r ON r.releaseId = ro.releaseId INNER JOIN
                        tblSoftwares so ON so.softwareId = r.softwareId INNER JOIN
                        tblReleaseMap rm ON rm.releaseId = r.releaseId INNER JOIN
                        tblScraperReleaseFlags srf ON srf.scraperReleaseId = rm.scraperReleaseId
                        WHERE so.systemId = ? AND srf.scraperReleaseFlagName = ?"""
                self.cur.execute(query,(systemrow[2],flag['scraperReleaseFlagName']))
                romrows = self.cur.fetchall()
                for romrow in romrows:
                    if flagname == "releasemonth":
                        releasedate = self.regexes.get_cleaned_date(romrow[2])
                        if releasedate is not None:                       
                            rom = {}
                            rom['name'] = romrow[1]
                            rom['flagvalue'] = str(self.regexes.get_cleaned_date(romrow[2]).month)
                            rom['crc'] = romrow[0]
                            system['roms'].append(rom)
                    elif flagname == "releaseyear":
                        releasedate = self.regexes.get_cleaned_date(romrow[2])
                        if releasedate is not None:
                            rom = {}
                            rom['name'] = romrow[1]
                            rom['flagvalue'] = str(self.regexes.get_cleaned_date(romrow[2]).year)
                            rom['crc'] = romrow[0]
                            system['roms'].append(rom)
                    else:
                        rom = {}
                        rom['name'] = romrow[1]
                        rom['flagvalue'] = romrow[2]
                        rom['crc'] = romrow[0]
                        system['roms'].append(rom)
                flag['systems'].append(system)
            print "Exporting scraped release flag " + flagname
            self.exporter.export_rdb_dat(flag)
            
    def export_rdbs(self):
        query = "SELECT systemManufacturer || ' - ' || systemName systemName FROM tblSystems"
        self.cur.execute(query)
        systemrows = self.cur.fetchall()
        for systemrow in systemrows:
            self.exporter.create_rdb(systemrow[0])
            
            
if __name__ == '__main__':
    gamedb = GameDB()
##    gamedb.import_dats()
##    gamedb.import_scrapers()
##    gamedb.match_systems()
    gamedb.match_softwares()
    gamedb.match_releases()
    gamedb.export_releaseflags()
    gamedb.export_scraperSoftwareFlags()
    gamedb.export_scraperReleaseFlags()
    gamedb.export_rdbs()
    gamedb.con.close()
    print "\nJob done."

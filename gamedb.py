import sqlite3 as lite
import os
from datetime import datetime
from collections import namedtuple
import codecs

from dat import DAT
from regexes import GameDBRegex
from scraper import Scraper

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
        self.init_database()

    def init_database(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblDatFiles (datFileId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, systemId TEXT, datFileName TEXT, datType TEXT, datReleaseGroup TEXT, datDate TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblDatGames (datGameId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, datFileId INTEGER, datGameName TEXT, datCloneOf TEXT, datRomOf TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblDatRoms (datROMId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, datFileId INTEGER, datGameId INTEGER, datROMName TEXT, datROMMerge TEXT, datROMSize INTEGER, datROMCRC TEXT, datROMMD5 TEXT, datROMSHA1 TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblSystems (systemId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, systemName TEXT, systemManufacturer TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblSoftwares (softwareId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, softwareName TEXT, softwareType TEXT, systemId INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblReleases (releaseId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseName TEXT, releaseType TEXT, softwareId INTEGER )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblROMs (romId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseId INTEGER, crc32 TEXT, md5 TEXT, sha1 TEXT, size INTEGER )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblReleaseFlags (releaseFlagId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseFlagName TEXT )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblReleaseFlagValues (releaseId INTEGER, releaseFlagId INTEGER, releaseFlagValue TEXT )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblScrapers (scraperId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperName TEXT, scraperURL TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblScraperSystems (scraperSystemId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperId INTEGER, scraperSystemName TEXT, scraperSystemAcronym TEXT, scraperSystemURL TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblScraperGames (scraperGameId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperSystemId INTEGER, scraperGameName TEXT, scraperGameURL TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblScraperGameFlags (scraperGameId INTEGER, scraperGameFlagName TEXT, scraperGameFlagValue TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblScraperReleases (scraperReleaseId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperGameId INTEGER, scraperReleaseName TEXT, scraperReleaseRegion TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblScraperReleaseFlags (scraperReleaseId INTEGER, scraperReleaseFlagName TEXT, scraperReleaseFlagValue TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblScraperReleaseImages (scraperReleaseImageId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperReleaseId INTEGER, scraperReleaseImageName TEXT, scraperReleaseImageType TEXT)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxDatGame_fileId ON tblDatGames (datFileId ASC)")
        self.cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idxDatGame_gameName ON tblDatGames (datFileId ASC,datGameName ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxDatRom_fileId ON tblDatRoms (datFileId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxDatRom_gameId ON tblDatRoms (datGameId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxROM_releaseId ON tblROMs (releaseId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxROM_hashes ON tblROMs (crc32 ASC,md5 ASC,sha1 ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxRelease_softwareId ON tblReleases (softwareId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxSoftware_systemId ON tblSoftwares (systemId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxreleaseflagvalue_releaseId_releaseFlagId ON tblReleaseFlagValues (releaseId ASC,releaseFlagId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxscrapersystem_scraperId ON tblScraperSystems (scraperId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxScraperGame_systemId ON tblScraperGames (scraperSystemId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxscrapergameflag_gameid ON tblScraperGameFlags (scraperGameId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxScraperRelease_gameid ON tblScraperReleases (scraperGameId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxscraperreleaseflag_releaseid ON tblScraperReleaseFlags (scraperReleaseId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxscraperreleaseimage_releaseid ON tblScraperReleaseImages (scraperReleaseId ASC)")
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
        release['releaseType'] = compresult.group('Compilation') if compresult is not None else devstatusresult.group('DevStatus') if devstatusresult is not None else demoresult.group('Demo') if demoresult is not None else 'Commercial'
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
        licenseresult = self.regexes.get_regex_result("License",releaseName)
        if(licenseresult):
            releaseflags.append([releaseId,self.getReleaseFlag('License'),licenseresult.group('License')])
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
        scrapersfile = codecs.open('Scrapers/scrapers.csv')
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
if __name__ == '__main__':
    gamedb = GameDB()
    gamedb.import_dats()
    gamedb.import_scrapers()
    gamedb.con.close()
    print "\nJob done."

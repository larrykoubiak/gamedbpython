import sqlite3 as lite
import os
from datetime import datetime
from dat import DAT
from regexes import GameDBRegex
from collections import namedtuple

flag = namedtuple('Flag',['name','value'])

class GameDB:
    def __init__(self):
        self.regexes = GameDBRegex()
        self.con = lite.connect('sqlite/GameDB.db')
        self.cur = self.con.cursor()
        self.dats = []
        self.init_database()

    def init_database(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblDatFiles (datFileId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, systemId TEXT, datFileName TEXT, datType TEXT, datReleaseGroup TEXT, datDate TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblDatGames (datGameId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, datFileId INTEGER, datGameName TEXT, datCloneOf TEXT, datRomOf TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblDatRoms (datROMId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, datFileId INTEGER, datGameId INTEGER, datROMName TEXT, datROMMerge TEXT, datROMSize INTEGER, datROMCRC TEXT, datROMMD5 TEXT, datROMSHA1 TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblSoftwares (softwareId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, softwareName TEXT, softwareType TEXT, systemId INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblReleases (releaseId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseName TEXT, releaseType TEXT, softwareId INTEGER )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblROMs (romId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseId INTEGER, crc32 TEXT, md5 TEXT, sha1 TEXT, size INTEGER )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS tblReleaseFlagValues (releaseId INTEGER, releaseFlagId INTEGER, releaseFlagValue TEXT )")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxDatGame_fileId ON tblDatGames (datFileId ASC)")
        self.cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idxDatGame_gameName ON tblDatGames (datFileId ASC,datGameName ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxDatRom_fileId ON tblDatRoms (datFileId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxDatRom_gameId ON tblDatRoms (datGameId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxROM_releaseId ON tblROMs (releaseId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxRelease_softwareId ON tblReleases (softwareId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxSoftware_systemId ON tblSoftwares (systemId ASC)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idxreleaseflagvalue_releaseId_releaseFlagId ON tblReleaseFlagValues (releaseId ASC,releaseFlagId ASC)")
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

    def getDATReleaseGroup(self,dat):
        releaseGroup = None
        if('comment' in dat.header):
            if(header['comment'] == "no-intro | www.no-intro.org"):
                releaseGroup = "No-Intro"
        elif('url' in dat.header):
            if(dat.header['url'] == "www.no-intro.org"):
                releaseGroup = "No-Intro"
        else:
            if(dat.header['homepage'] is not None):
                if(dat.header['homepage'] == "TOSEC"):
                    releaseGroup = "TOSEC"
                elif(self.header['homepage'] == "redump.org"):
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
            query = "INSERT INTO tblReleaseFlagValues (releaseId,releaseFlagId,releaseFlagValue) VALUES (?,?,?)"
            self.cur.execute(query,flag)

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
        query = """SELECT df.systemId, df.datReleaseGroup, dg.datGameName, dg.datCloneOf, dr.datGameId, dr.datROMSize, dr.datROMCRC,dr.datROMMD5,dr.datROMSHA1 
                    FROM tblDatRoms dr INNER JOIN tblDatFiles df ON df.datFileId = dr.datFileId INNER JOIN tblDatGames dg ON dg.datGameId = dr.datGameId
                    WHERE NOT EXISTS (SELECT 1 FROM tblROMs r WHERE r.crc32 = dr.datROMCRC OR r.md5 = dr.datROMMD5 OR r.sha1 = dr.datROMSHA1)"""
        self.cur.execute(query)
        datRoms = self.cur.fetchall()
        for datRom in datRoms:
            #get releaseGroup regexes
            if releaseGroup != datRom[1]:
                releaseGroup = datRom[1]
                self.regexes.init_regexes(releaseGroup)
            #get software
            gameName = datRom[2] if datRom[3] == '' else datRom[3]
            softwareId = self.getSoftware(gameName,datRom[0]) 
            #get release
            releaseName = datRom[2]
            releaseId = self.getRelease(releaseName,softwareId)
            #get rom
            romId = self.getROM(releaseId,*datRom[5:])
        self.con.commit()

    def import_folder(self,path):
        self.dats = []
        for xmlfile in os.listdir(path):
            dat = DAT()
            dat.read_dat(os.path.join(path,xmlfile))
            self.dats.append(dat)
        for dat in self.dats:
            print "importing " + dat.filename
            self.import_dat(dat)
        self.import_new_ROMS()
        self.con.close()

if __name__ == '__main__':
    gamedb = GameDB()
    gamedb.import_folder("DAT")
    print gamedb

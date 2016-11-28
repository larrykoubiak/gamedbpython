import sqlite3 as lite
import io
import os

class Database:

    def __init__(self):
        if not os.path.exists('sqlite'):
            os.makedirs('sqlite')
        self.con = lite.connect('sqlite/GameDB.db')
        self.cur = self.con.cursor()
        self.run_script('create_db.sql')

    def run_script(self,path):
        sqlfile = io.open(path,'r',encoding='utf-8').read()
        self.cur.executescript(sqlfile)
        self.con.commit()

    def save(self):
        self.con.commit()

    def close(self):
        self.con.close()

    #################
    # DAT functions #
    #################
    
    def getDATFile(self,systemId,datFileName,datType,datReleaseGroup,datDate):
        datfileDic = {}
        datFileId = None
        datfileDic["systemId"] = systemId
        datfileDic["datFileName"] = datFileName
        datfileDic["datType"] = datType
        datfileDic["datReleaseGroup"] = datReleaseGroup
        datfileDic['datDate'] = datDate
        query = "SELECT datFileId FROM tblDatFiles WHERE systemId = :systemId AND datFileName = :datFileName AND datType = :datType AND datReleaseGroup = :datReleaseGroup AND datDate = :datDate"
        self.cur.execute(query,datfileDic)
        datfilerow = self.cur.fetchone()
        if datfilerow is None:
            sql = "INSERT INTO tblDATFiles (systemId,datFileName,datType,datReleaseGroup, datDate) VALUES (:systemId,:datFileName,:datType,:datReleaseGroup,:datDate)"
            self.cur.execute(sql,datfileDic)
            datFileId = self.cur.lastrowid
        else:
            datFileId = datfilerow[0]
        return datFileId

    def getDATGame(self,datFileId,gamename,cloneof,romof):
        datgameDic = {}
        datGameId = None
        datgameDic['datFileId'] = datFileId
        datgameDic['datGameName'] = gamename
        datgameDic['datCloneOf'] = cloneof
        datgameDic['datRomOf'] = romof
        query = "SELECT datGameId FROM tblDatGames WHERE datFileId = :datFileId AND datGameName = :datGameName AND datCloneOf = :datCloneOf AND datRomOf = :datRomOf"
        self.cur.execute(query,datgameDic)
        datgamerow = self.cur.fetchone()
        if datgamerow is None:
            sql = "INSERT INTO tblDatGames (datFileId,datGameName,datCloneOf,datRomOf) VALUES (:datFileId,:datGameName,:datCloneOf,:datRomOf)"
            self.cur.execute(sql,datgameDic)
            datGameId = self.cur.lastrowid
        else:
            datGameId = datgamerow[0]
        return datGameId

    def getDATROM(self,datFileId,datGameId,romname,rommerge,romsize,romcrc,rommd5,romsha1):
        datromDic = {}
        datROMId = None
        datromDic['datFileId'] = datFileId
        datromDic['datGameId'] = datGameId
        datromDic['datROMName'] = romname
        datromDic['datROMMerge'] = rommerge
        datromDic['datROMSize'] = romsize
        datromDic['datROMCRC'] = romcrc
        datromDic['datROMMD5'] = rommd5
        datromDic['datROMSHA1'] = romsha1
        query = """SELECT datRomId FROM tblDatRoms WHERE datFileId = :datFileId AND datGameId = :datGameId AND datROMName = :datROMName AND datROMMerge = :datROMMerge AND
                    datROMSize = :datROMSize AND datROMCRC = :datROMCRC AND datROMMD5 = :datROMMD5 AND datROMSHA1 = :datROMSHA1"""
        self.cur.execute(query,datromDic)
        datromrow = self.cur.fetchone()
        if datromrow is None:
            sql = "INSERT INTO tblDatRoms (datFileId,datGameId,datROMName,datROMMerge,datROMSize,datROMCRC,datROMMD5,datROMSHA1) VALUES (:datFileId,:datGameId,:datROMName,:datROMMerge,:datROMSize,:datROMCRC,:datROMMD5,:datROMSHA1)"
            self.cur.execute(sql,datromDic)
            datROMId = self.cur.lastrowid
        else:
            datROMId = datromrow[0]
        return datROMId

    def getNewRoms(self):
        query = """SELECT df.systemId, df.datReleaseGroup, dg.datGameName, dg.datCloneOf, dr.datGameId, dr.datROMSize, dr.datROMCRC,dr.datROMMD5,dr.datROMSHA1 
                    FROM tblDatRoms dr INNER JOIN tblDatFiles df ON df.datFileId = dr.datFileId INNER JOIN tblDatGames dg ON dg.datGameId = dr.datGameId 
                    LEFT JOIN tblROMs r ON r.crc32 = dr.datROMCRC AND r.md5 = dr.datROMMD5 AND r.sha1 = dr.datROMSHA1 WHERE r.romID IS NULL"""
        self.cur.execute(query)
        datRoms = self.cur.fetchall()
        return datRoms
    
    ####################
    # GameDB functions #
    ####################

    def getSystem(self,manufacturer,systemName):
        systemDic = {}
        systemId = None
        systemDic['systemName'] = systemName
        systemDic['systemManufacturer'] = manufacturer
        query = "SELECT systemId FROM tblSystems WHERE systemName=:systemName AND systemManufacturer=:systemManufacturer"
        self.cur.execute(query,(systemName,manufacturer))
        systemrow = self.cur.fetchone()
        if systemrow is None:
             query = "INSERT INTO tblSystems (systemName, systemManufacturer) VALUES (:systemName,:systemManufacturer)"
             self.cur.execute(query,systemDic)
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

    def getSoftware(self,systemId,softwarename,softwaretype):
        softwareDic = {}
        softwareId = None
        softwareDic['softwareName'] = softwarename
        softwareDic['softwareType'] = softwaretype
        softwareDic['systemId'] = systemId
        query = "SELECT softwareId FROM tblSoftwares WHERE softwareName = :softwareName AND softwareType = :softwareType AND systemId = :systemId"
        self.cur.execute(query,softwareDic)
        softwarerow = self.cur.fetchone()
        if softwarerow is None:
            query = "INSERT INTO tblSoftwares (softwareName,softwareType,systemId) VALUES (:softwareName,:softwareType,:systemId)"
            self.cur.execute(query,softwareDic)
            softwareId = self.cur.lastrowid
        else:
            softwareId = softwarerow[0]
        return softwareId

    def getRelease(self,releaseName,releaseType,softwareId):
        releaseDic = {}
        releaseId = None
        releaseDic['releaseName'] = releaseName
        releaseDic['releaseType'] = releaseType
        releaseDic['softwareId'] = softwareId
        query = "SELECT releaseId FROM tblReleases WHERE releaseName = :releaseName AND releaseType = :releaseType AND softwareId = :softwareId"
        self.cur.execute(query,releaseDic)
        releaserow = self.cur.fetchone()
        if releaserow is None:
            query = "INSERT INTO tblReleases (releaseName,releaseType,softwareId) VALUES (:releaseName,:releaseType,:softwareId)"
            self.cur.execute(query,releaseDic)
            releaseId = self.cur.lastrowid
        else:
            releaseId = releaserow[0]
        return releaseId

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

    def addReleaseFlagValue(self,releaseid,flagid,flagvalue):
        releaseflagDic = {}
        releaseflagDic['releaseId'] = releaseid
        releaseflagDic['releaseFlagId'] = flagid
        releaseflagDic['releaseFlagValue'] = flagvalue
        query = "SELECT 1 FROM tblReleaseFlagValues WHERE releaseId=:releaseId AND releaseFlagId=:releaseFlagId AND releaseFlagValue=:releaseFlagValue"
        self.cur.execute(query,releaseflagDic)
        flagrow = self.cur.fetchone()
        if flagrow is None:
            query = "INSERT INTO tblReleaseFlagValues (releaseId,releaseFlagId,releaseFlagValue) VALUES (:releaseId,:releaseFlagId,:releaseFlagValue)"
            self.cur.execute(query,releaseflagDic)

    def getROM(self,releaseId,romsize,romcrc,rommd5,romsha1):
        romDic = {}
        romId = None
        romDic['releaseId'] = releaseId
        romDic['crc32'] = romcrc
        romDic['md5'] = rommd5
        romDic['sha1'] = romsha1
        romDic['size'] = romsize
        query = "SELECT romId FROM tblROMs WHERE releaseId = :releaseId AND crc32 = :crc32 AND md5 = :md5 AND sha1 = :sha1 AND size = :size"
        self.cur.execute(query,romDic)
        romrow = self.cur.fetchone()
        if romrow is None:
            query = "INSERT INTO tblROMs (releaseId,crc32,md5,sha1,size) VALUES (:releaseId,:crc32,:md5,:sha1,:size)"
            self.cur.execute(query,romDic)
            romId = self.cur.lastrowid
        else:
            romId = romrow[0]
        return romId

    def getSystemDic(self):
        systemDic = {}
        query = "SELECT systemId, systemName FROM tblSystems"
        self.cur.execute(query)
        for row in self.cur:
            systemDic[row[0]] = row[1]
        return systemDic

    def getSoftwareList(self,systemId):
        query = "SELECT softwareId, softwareName FROM tblSoftwares s WHERE s.systemId = ? AND NOT EXISTS (SELECT 1 FROM tblSoftwareMap WHERE softwareId = s.softwareId AND scraperGameId IS NOT NULL)"
        self.cur.execute(query,(systemId,))
        return self.cur.fetchall()

    #####################
    # Scraper functions #
    #####################

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

    def addScraperGameFlagValue(self,scraperGameId,flagname,flagvalue):
        softwareflagDic = {}
        softwareflagDic['scraperGameId'] = scraperGameId
        softwareflagDic['scraperGameFlagName'] = flagname
        softwareflagDic['scraperGameFlagValue'] = flagvalue        
        query = "SELECT 1 FROM tblScraperGameFlags WHERE scraperGameId=:scraperGameId AND scraperGameFlagName=:scraperGameFlagName AND scraperGameFlagValue=:scraperGameFlagValue"
        self.cur.execute(query,softwareflagDic)
        flagrow = self.cur.fetchone()
        if flagrow is None:
            query = "INSERT INTO tblScraperGameFlags (scraperGameId,scraperGameFlagName,scraperGameFlagValue) VALUES (:scraperGameId,:scraperGameFlagName,:scraperGameFlagValue)"
            self.cur.execute(query,softwareflagDic)


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

    def addScraperReleaseFlagValue(self,releaseid,flagname,flagvalue):
        releaseflagDic = {}
        releaseflagDic['scraperReleaseId'] = releaseid
        releaseflagDic['scraperReleaseFlagName'] = flagname
        releaseflagDic['scraperReleaseFlagValue'] = flagvalue
        query = "SELECT 1 FROM tblScraperReleaseFlags WHERE scraperReleaseId=:scraperReleaseId AND scraperReleaseFlagName=:scraperReleaseFlagName AND scraperReleaseFlagValue=:scraperReleaseFlagValue"
        self.cur.execute(query,releaseflagDic)
        flagrow = self.cur.fetchone()
        if flagrow is None:
            query = "INSERT INTO tblScraperReleaseFlags (scraperReleaseId,scraperReleaseFlagName,scraperReleaseFlagValue) VALUES (:scraperReleaseId,:scraperReleaseFlagName,:scraperReleaseFlagValue)"
            self.cur.execute(query,releaseflagDic)

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

    #####################
    # Matcher functions #
    #####################

    def addSynonym(self,synonymkey,synonymvalue,synonymtype):
        synonymDic = {}
        synonymDic['key'] = synonymkey
        synonymDic['value'] = synonymvalue
        synonymDic['type'] = synonymtype
        query = "SELECT key, value, type FROM tblSynonyms WHERE key=:key AND value=:value AND type=:type"
        self.cur.execute(query,synonymDic)
        synonymrow = self.cur.fetchone()
        if synonymrow is None:
            query = "INSERT INTO tblSynonyms (key,value,type) VALUES (:key,:value,:type)"
            self.cur.execute(query,synonymDic)

    def addSystemMatch(self,systemId,scraperSystemId):
        systemMatchDic = {}
        systemMatchDic['systemId'] = systemId
        systemMatchDic['scraperSystemId'] = scraperSystemId
        query = "SELECT 1 FROM tblSystemMap WHERE systemId = :systemId AND scraperSystemId = :scraperSystemId"
        self.cur.execute(query,systemMatchDic)
        systemMatchrow = self.cur.fetchone()
        if systemMatchrow is None:
            query = "INSERT INTO tblSystemMap (systemId, scraperSystemId) VALUES (:systemId,:scraperSystemId)"
            self.cur.execute(query,systemMatchDic)

    def addSoftwareMatch(self,softwareId,scraperGameId):
        softwareMatchDic = {}
        softwareMatchDic['softwareId'] = softwareId
        softwareMatchDic['scraperGameId'] = 0 if scraperGameId is None else scraperGameId
        query = "SELECT 1 FROM tblSoftwareMap WHERE softwareId = :softwareId AND scraperGameId = IFNULL(:scraperGameId,0)"
        self.cur.execute(query,softwareMatchDic)
        softwareMatchrow = self.cur.fetchone()
        if softwareMatchrow is None:
            query = "INSERT INTO tblSoftwareMap (softwareId, scraperGameId) VALUES (:softwareId,:scraperGameId)"
            self.cur.execute(query,softwareMatchDic)

    def addReleaseMatch(self,releaseId,scraperReleaseId):
        releaseMatchDic = {}
        releaseMatchDic['releaseId'] = releaseId
        releaseMatchDic['scraperReleaseId'] = scraperReleaseId
        query = "SELECT 1 FROM tblReleaseMap WHERE releaseId = :releaseId AND scraperReleaseId = :scraperReleaseId"
        self.cur.execute(query,releaseMatchDic)
        releaseMatchrow = self.cur.fetchone()
        if releaseMatchrow is None:
            query = "INSERT INTO tblReleaseMap (releaseId, scraperReleaseId) VALUES (:releaseId, :scraperReleaseId)"
            self.cur.execute(query,releaseMatchDic)

    def matchSystemScraperSystem(self):
        #use synonym table to find match
        query = """INSERT INTO tblSystemMap
                SELECT s.systemId,ss.scraperSystemId
                FROM tblSystems s INNER JOIN
                tblSynonyms sn ON sn.key = s.systemName AND sn.type = 'System' INNER JOIN
                tblScraperSystems ss ON ss.scraperSystemName = sn.value
                WHERE NOT EXISTS (SELECT 1 FROM tblSystemMap WHERE systemId=s.systemId AND scraperSystemId = ss.scraperSystemId)"""
        self.cur.execute(query)

    def getMappedSystems(self,scraperId):
        query = """SELECT s.systemId, s.systemName, ss.scraperSystemId FROM tblSystems s INNER JOIN tblSystemMap sm on s.systemId = sm.systemId INNER JOIN
                tblScraperSystems ss on sm.scraperSystemId = ss.scraperSystemId WHERE ss.scraperId = ?"""
        self.cur.execute(query,(scraperId,))
        return self.cur.fetchall()

    def getScraperReleaseGameList(self,scraperSystemId):
        query = """SELECT DISTINCT sr.scraperReleaseId, sr.scraperReleaseName, sr.scraperGameId FROM tblScraperReleases
                sr INNER JOIN tblScraperGames sg ON sg.scraperGameId = sr.scraperGameId WHERE sg.scraperSystemId = ?"""
        self.cur.execute(query,(scraperSystemId,))
        return self.cur.fetchall()

    def getScraperReleaseList(self,systemId):
        query = """SELECT r.releaseId, r.releaseName,sm.scraperGameId,GROUP_CONCAT(CASE WHEN rf.releaseFlagName = 'Region' THEN sy.value END) Region
                FROM tblReleases r INNER JOIN
                tblReleaseFlagValues rfv On rfv.releaseId = r.releaseId INNER JOIN
                tblReleaseFlags rf ON rf.releaseFlagId = rfv.releaseFlagId INNER JOIN
                tblSynonyms sy ON sy.key = rfv.releaseFlagValue AND sy.type = 'Region' INNER JOIN
                tblSoftwares so ON r.softwareId = so.softwareId INNER JOIN
                tblSystems s ON s.systemId = so.systemId INNER JOIN
                tblSoftwareMap sm ON sm.softwareId = so.softwareId INNER JOIN
                tblScraperGames sg ON sg.scraperGameId = sm.scraperGameId
                WHERE r.releaseType = 'Commercial' AND s.systemId = ?
                GROUP BY r.releaseId, r.releaseName, so.softwareId, sm.scraperGameId,sg.scraperGameName,s.systemManufacturer || ' - ' || s.systemName"""
        self.cur.execute(query,(systemId,))
        return self.cur.fetchall()

    def getScraperGameReleaseList(self,scraperGameId,scraperReleaseRegion):
        scraperReleaseDic = {}
        scraperReleaseDic['scraperGameId'] = scraperGameId
        scraperReleaseDic['scraperReleaseRegion'] = scraperReleaseRegion
        query = """SELECT sr.scraperReleaseId,sr.scraperReleaseName
            FROM tblScraperReleases sr 
            WHERE sr.scraperGameId = :scraperGameId AND sr.scraperReleaseRegion = :scraperReleaseRegion"""
        self.cur.execute(query,scraperReleaseDic)
        return self.cur.fetchall()

    ######################
    # Exporter functions #
    ######################

    def getExportSystems(self):
        query = "SELECT systemManufacturer || ' - ' || systemName systemName FROM tblSystems"
        self.cur.execute(query)
        return self.cur.fetchall()

    def getReleaseFlagSystem(self,releaseFlagName):
        query ="""SELECT DISTINCT rf.releaseFlagName, s.systemManufacturer || ' - ' || s.systemName systemName, s.systemId
                FROM tblReleaseFlags rf INNER JOIN
                tblReleaseFlagValues rfv ON rfv.releaseFlagId = rf.releaseFlagId INNER JOIN
                tblReleases r ON r.releaseId = rfv.releaseId INNER JOIN
                tblSoftwares so ON so.softwareId = r.softwareId INNER JOIN 
                tblSystems s ON s.systemId = so.systemId
                WHERE rf.releaseFlagName = ?"""
        self.cur.execute(query,(releaseFlagName,))
        return self.cur.fetchall()

    def getReleaseFlagSystemValue(self,systemId,releaseFlagName):
        releaseflagDic = {}
        releaseflagDic['systemId'] = systemId
        releaseflagDic['releaseFlagName'] = releaseFlagName
        query = """SELECT ro.crc32, r.releaseName, GROUP_CONCAT(DISTINCT rfv.releaseFlagValue) flagValue
                FROM tblROMs ro INNER JOIN 
                tblReleases r ON r.releaseId = ro.releaseId INNER JOIN
                tblSoftwares so ON so.softwareId = r.softwareId INNER JOIN
                tblReleaseFlagValues rfv ON rfv.releaseId = r.releaseId INNER JOIN
                tblReleaseFlags rf ON rf.releaseFlagId = rfv.releaseFlagId
                WHERE so.systemId = ? AND rf.releaseFlagName = ?
                GROUP BY ro.crc32, r.releaseName"""
        self.cur.execute(query,releaseflagDic)
        return self.cur.fetchall()

    def getSoftwareFlagSystem(self,scraperGameFlagName):
        query = """SELECT DISTINCT sgf.scraperGameFlagName, s.systemManufacturer || ' - ' || s.systemName systemName, s.systemId
                FROM tblScraperGameFlags sgf INNER JOIN
                tblScraperGames sg ON sg.scraperGameId = sgf.scraperGameId INNER JOIN
                tblScraperSystems ss ON ss.scraperSystemId = sg.scraperSystemId INNER JOIN
                tblSystemMap sm ON sm.scraperSystemId = ss.scraperSystemId INNER JOIN
                tblSystems s ON s.systemId = sm.systemId
                WHERE scraperGameFlagName = ?"""
        self.cur.execute(query,(scraperGameFlagName,))
        return self.cur.fetchall()

    def getSoftwareFlagSystemValue(self,systemId,scraperGameFlagName):
        softwareflagDic = {}
        softwareflagDic['systemId'] = systemId
        softwareflagDic['scraperGameFlagName'] = scraperGameFlagName
        query = """SELECT ro.crc32, r.releaseName, sgf.scraperGameFlagValue
                FROM tblROMs ro INNER JOIN 
                tblReleases r ON r.releaseId = ro.releaseId INNER JOIN
                tblSoftwares so ON so.softwareId = r.softwareId INNER JOIN
                tblSoftwareMap sm ON sm.softwareId = so.softwareId INNER JOIN
                tblScraperGameFlags sgf ON sgf.scraperGameId = sm.scraperGameId
                WHERE so.systemId = :systemId AND sgf.scraperGameFlagName = :scraperGameFlagName"""
        self.cur.execute(query,softwareflagDic)
        return self.cur.fetchall()

    def getScraperReleaseFlagSystem(self,scraperReleaseFlagName):
        query = """SELECT DISTINCT srf.scraperReleaseFlagName, s.systemManufacturer || ' - ' || s.systemName systemName, s.systemId
                FROM tblScraperReleaseFlags srf INNER JOIN
                tblScraperReleases sr ON sr.scraperReleaseId = srf.scraperReleaseId INNER JOIN
                tblScraperGames sg ON sg.scraperGameId = sr.scraperReleaseId INNER JOIN
                tblScraperSystems ss ON ss.scraperSystemId = sg.scraperSystemId INNER JOIN
                tblSystemMap sm ON sm.scraperSystemId = ss.scraperSystemId INNER JOIN
                tblSystems s ON s.systemId = sm.systemId
                WHERE srf.scraperReleaseFlagName = ?"""
        self.cur.execute(query,(scraperReleaseFlagName,))
        return self.cur.fetchall()

    def getScraperReleaseFlagSystemValue(self,systemId,scraperReleaseFlagName):
        releaseflagDic = {}
        releaseflagDic['systemId'] = systemId
        releaseflagDic['scraperReleaseFlagName'] = scraperReleaseFlagName
        query = """SELECT ro.crc32, r.releaseName, srf.scraperReleaseFlagValue
                FROM tblROMs ro INNER JOIN 
                tblReleases r ON r.releaseId = ro.releaseId INNER JOIN
                tblSoftwares so ON so.softwareId = r.softwareId INNER JOIN
                tblReleaseMap rm ON rm.releaseId = r.releaseId INNER JOIN
                tblScraperReleaseFlags srf ON srf.scraperReleaseId = rm.scraperReleaseId
                WHERE so.systemId=:systemId AND srf.scraperReleaseFlagName=:scraperReleaseFlagName"""
        self.cur.execute(query,releaseflagDic)
        return self.cur.fetchall()

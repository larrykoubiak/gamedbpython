import os
import io
from datetime import datetime

from dat import DAT
from regexes import GameDBRegex
from scraper import Scraper
from matcher import Matcher
from exporter import Exporter
from patcher import Patcher
from database import Database

class GameDB:
    def __init__(self):
        self.regexes = GameDBRegex()
        self.dats = []
        self.scrapers = []
        self.exporter = Exporter()
        self.matcher = Matcher()
        self.patcher = Patcher()
        self.database = Database()
    
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
        
    def import_dat(self,dat):
        datFileId = None
        datGameId = None
        datRomId = None
        self.regexes.init_regexes(dat.releaseGroup)
        sysresult = self.regexes.get_regex_result("System",dat.header["name"])
        systemId = self.database.getSystem(sysresult.group('Manufacturer'),sysresult.group('Name'))
        datType = 'Standard' if sysresult.group('DatType') == None else sysresult.group('DatType')
        datVersion = dat.header['version'] if dat.header['version'] is not None else dat.header['date']
        #check if version is a date
        datDate = self.regexes.get_cleaned_date(datVersion)
        if datDate is not None:
            datVersion = datDate
        datFileId = self.database.getDATFile(systemId,dat.filename,datType,dat.releaseGroup,datVersion)
        for gamekey,gamevalue in dat.softwares.iteritems():
            datGameId = self.database.getDATGame(datFileId,gamevalue['Name'],gamevalue['CloneOf'],gamevalue['RomOf'])
            for rom in gamevalue['Roms']:
                datRomId = self.database.getDATROM(datFileId,datGameId,rom['name'],rom['merge'],rom['size'],rom['crc'],rom['md5'],rom['sha1'])
        self.database.save()
                             
    def import_new_ROMS(self):
        systemId = None
        releaseGroup = None
        softwareId = None
        releaseId = None
        romId = None
        datRoms = self.database.getNewRoms()
        for datRom in datRoms:
            #get releaseGroup regexes
            if releaseGroup != datRom[1]:
                releaseGroup = datRom[1]
                self.regexes.init_regexes(releaseGroup)
            #get system
            if systemId != datRom[0]:
                systemId = datRom[0]
                print "exporting new roms for " + self.database.getSystemName(systemId)
            #get software
            gameName = datRom[2] if datRom[3] == '' else datRom[3]
            softwareId = self.import_software(gameName,systemId)
            #get release
            releaseName = datRom[2]
            releaseId = self.import_release(releaseName,softwareId)
            #release flags
            self.import_releaseflags(releaseName,releaseId)
            romId = self.database.getROM(releaseId,*datRom[5:])
        self.database.save()
        
    def import_software(self,gameName,systemId):
        softresult = self.regexes.get_regex_result("Software",gameName)
        softwarename = softresult.group('Name')
        softwaretype = 'BIOS' if softresult.group('BIOS') is not None else softresult.group('Type') if softresult.group('Type') is not None else 'Game'
        return self.database.getSoftware(systemId,softwarename,softwaretype)

    def import_release(self,releaseName,softwareId):
        compresult = self.regexes.get_regex_result("Compilation",releaseName)
        devstatusresult = self.regexes.get_regex_result("DevStatus",releaseName)
        demoresult = self.regexes.get_regex_result("Demo",releaseName)
        licenseresult = self.regexes.get_regex_result("License",releaseName)
        if compresult is not None:
            releaseType = compresult.group('Compilation')
        elif devstatusresult is not None:
            releaseType = devstatusresult.group('DevStatus')
        elif demoresult is not None:
            releaseType = demoresult.group('Demo')
        elif licenseresult is not None:
            releaseType = licenseresult.group('License')
        else:
            releaseType = 'Commercial'
        return self.database.getRelease(releaseName,releaseType,softwareId)

    def import_releaseflags(self,releaseName,releaseId):
        for regionresult in self.regexes.get_regex_results("Region",releaseName):
            self.database.addReleaseFlagValue(releaseId,self.database.getReleaseFlag('Region'),regionresult.group('Region'))
        for languageresult in self.regexes.get_regex_results("Language",releaseName):
            self.database.addReleaseFlagValue(releaseId,self.database.getReleaseFlag('Language'),languageresult.group('Language'))
        versionresult = self.regexes.get_regex_result("Version",releaseName)
        if(versionresult):
            self.database.addReleaseFlagValue(releaseId,self.database.getReleaseFlag('Version'),versionresult.group('Version'))
        revisionresult = self.regexes.get_regex_result("Revision",releaseName)
        if(revisionresult):
            self.database.addReleaseFlagValue(releaseId,self.database.getReleaseFlag('Revision'),revisionresult.group('Revision'))
        baddumpresult = self.regexes.get_regex_result("DumpStatus",releaseName)
        if(baddumpresult):
            self.database.addReleaseFlagValue(releaseId,self.database.getReleaseFlag('BadDump'),baddumpresult.group('BadDump'))

    def import_scrapers(self):
        self.scrapers = []
        scrapersfile = io.open('Scrapers/scrapers.csv','r',encoding='utf-8')
        for scraperline in scrapersfile:
            scraperCols = scraperline.split(';')
            scraperId = self.database.getScraper(*scraperCols)
            scraper = Scraper(*scraperCols)
            for scraperSystemKey,scraperSystem in scraper.systems.items():
                print "exporting game data for " + scraper.name + " - " + scraperSystemKey
                scraperSystemId = self.database.getScraperSystem(scraperId,scraperSystem['systemName'],scraperSystem['systemAcronym'],scraperSystem['systemURL'])
                for game in scraperSystem['systemGames'].itervalues():
                    scraperGameId = self.database.getScraperGame(scraperSystemId,game['gameName'],game['gameUrl'])
                    if game['gameParsed']=='Yes':
                        for flag in game['softwareFlags']:
                            self.database.addScraperGameFlagValue(scraperGameId,flag['name'],flag['value'])
                        for release in game['releases']:
                            scraperReleaseId = self.database.getScraperRelease(scraperGameId,release['name'],release['region'])
                            for flag in release['releaseFlags']:
                                self.database.addScraperReleaseFlagValue(scraperReleaseId,flag['name'],flag['value'])
                            for image in release['releaseImages']:
                                scraperReleaseImageId = self.database.getScraperReleaseImage(scraperReleaseId,image['name'],image['type'])                            
        self.database.save()

    def match_systems(self):
        for synonym in self.matcher.synonyms:
            self.database.addSynonym(synonym['key'],synonym['value'],synonym['type'])
        self.database.matchSystemScraperSystem()
        self.database.save()

    def match_softwares(self):
        systems = self.database.getMappedSystems(1) ## scraperId 1 - GameFaqs
        for system in systems:
            print "Matching Softwares for System : " + system[1]
            releasegamelist = self.database.getScraperReleaseGameList(system[2])
            releaseDic = {r[0]:r[1] for r in releasegamelist}
            gameDic = {r[0]:r[2] for r in releasegamelist}
            softwares = self.database.getSoftwareList(system[0])
            for software in softwares:
                scraperReleaseId = self.matcher.match_fuzzy(releaseDic,software[1],"Full",80)
                if scraperReleaseId == None:
                    scraperReleaseId = self.matcher.match_fuzzy(releaseDic,software[1],"Partial",86)
                self.database.addSoftwareMatch(software[0],None if scraperReleaseId is None else gameDic[scraperReleaseId])
        self.database.save()

    def match_releases(self):
        systems = self.database.getMappedSystems(1) ## scraperId 1 - GameFaqs
        for system in systems:
            print "Matching Releases for System : " + system[1]
            releaserows = self.database.getScraperReleaseList(system[0])
            for releaserow in releaserows:
                matches = self.database.getScraperGameReleaseList(releaserow[2],releaserow[3])
                if len(matches) == 1:
                    self.database.addSoftwareMatch(releaserow[0],matches[0][0])
                elif len(matches) > 1:
                    releaseDic = {m[0]:m[1] for m in matches}
                    scraperReleaseId = self.matcher.match_fuzzy(releaseDic,releaserow[1],"Full",80)
                    self.database.addReleaseMatch(releaserow[0],scraperReleaseId)
        self.database.save()
        
    def export_releaseflags(self):
        for flagname in ['origin']:
            flag = {}
            flag['name'] = flagname
            if flagname == 'origin':
                flag['releaseFlagName'] = 'Region'
            flag['systems'] = []
            systemrows = self.database.getReleaseFlagSystem(flag['releaseFlagName'])
            for systemrow in systemrows:
                system = {}
                system['name'] = systemrow[1]
                system['roms'] = []
                romrows = self.database.getReleaseFlagSystemValue(systemrow[2],flag['releaseFlagName'])
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
            systemrows = self.database.getSoftwareFlagSystem(flag['scraperGameFlagName'])
            for systemrow in systemrows:
                system = {}
                system['name'] = systemrow[1]
                system['roms'] = []
                romrows = self.database.getSoftwareFlagSystemValue(systemrow[2],flag['scraperGameFlagName'])
                for romrow in romrows:
                    rom = {}
                    rom['name'] = romrow[1]
                    rom['crc'] = romrow[0]
                    if flagname=="developer":
                        rom['flagvalue'] = self.regexes.get_cleaned_developer(romrow[2])
                    else:
                        rom['flagvalue'] = romrow[2]
                    system['roms'].append(rom)
                flag['systems'].append(system)
            print "Exporting scraped software flag " + flagname
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
            systemrows = self.database.getScraperReleaseFlagSystem(flag['scraperReleaseFlagName'])
            for systemrow in systemrows:
                system = {}
                system['name'] = systemrow[1]
                system['roms'] = []
                romrows = self.database.getScraperReleaseFlagSystemValue(systemrow[2],flag['scraperReleaseFlagName'])
                for romrow in romrows:
                    rom = {}
                    rom['name'] = romrow[1]
                    rom['crc'] = romrow[0]
                    if flagname == "releasemonth":
                        releasedate = self.regexes.get_cleaned_date(romrow[2])              
                        rom['flagvalue'] = '' if releasedate is None else str(self.regexes.get_cleaned_date(romrow[2]).month)                        
                    elif flagname == "releaseyear":
                        releasedate = self.regexes.get_cleaned_date(romrow[2])
                        rom['flagvalue'] = '' if releasedate is None else str(self.regexes.get_cleaned_date(romrow[2]).year)
                    elif flagname=="publisher":
                        rom['flagvalue'] = self.regexes.get_cleaned_developer(romrow[2])
                    else:
                        rom['flagvalue'] = romrow[2]
                    system['roms'].append(rom)
                flag['systems'].append(system)
            print "Exporting scraped release flag " + flagname
            self.exporter.export_rdb_dat(flag)
            
    def export_rdbs(self):
        systemrows = self.database.getExportSystems()
        for systemrow in systemrows:
            print "Exporting rdb for " + systemrow[0]
            self.exporter.create_rdb(systemrow[0])

    def apply_patches(self):
        self.patcher.LoadFile("patches.xlsx")
        self.patcher.GenerateScript("patches.sql")
        self.database.run_script('patches.sql')
        print "Patches applied"
            
if __name__ == '__main__':
    gamedb = GameDB()
    gamedb.import_dats()
    gamedb.import_scrapers()
    gamedb.match_systems()
    gamedb.match_softwares()
    gamedb.apply_patches()
    gamedb.match_releases()
    gamedb.export_releaseflags()
    gamedb.export_scraperSoftwareFlags()
    gamedb.export_scraperReleaseFlags()
    gamedb.export_rdbs()
    gamedb.database.close()
    print "\nJob done."

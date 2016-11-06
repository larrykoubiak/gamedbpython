/*-------------*/
/*   Tables    */
/*-------------*/
--Dat Tables
CREATE TABLE IF NOT EXISTS tblDatFiles (datFileId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, systemId TEXT, datFileName TEXT, datType TEXT, datReleaseGroup TEXT, datDate TEXT)
CREATE TABLE IF NOT EXISTS tblDatGames (datGameId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, datFileId INTEGER, datGameName TEXT, datCloneOf TEXT, datRomOf TEXT)
CREATE TABLE IF NOT EXISTS tblDatRoms (datROMId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, datFileId INTEGER, datGameId INTEGER, datROMName TEXT, datROMMerge TEXT, datROMSize INTEGER, datROMCRC TEXT, datROMMD5 TEXT, datROMSHA1 TEXT)
--GameDb tables
CREATE TABLE IF NOT EXISTS tblSystems (systemId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, systemName TEXT, systemManufacturer TEXT)
CREATE TABLE IF NOT EXISTS tblSoftwares (softwareId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, softwareName TEXT, softwareType TEXT, systemId INTEGER)
CREATE TABLE IF NOT EXISTS tblReleases (releaseId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseName TEXT, releaseType TEXT, softwareId INTEGER )
CREATE TABLE IF NOT EXISTS tblROMs (romId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseId INTEGER, crc32 TEXT, md5 TEXT, sha1 TEXT, size INTEGER )
CREATE TABLE IF NOT EXISTS tblReleaseFlags (releaseFlagId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseFlagName TEXT )
CREATE TABLE IF NOT EXISTS tblReleaseFlagValues (releaseId INTEGER, releaseFlagId INTEGER, releaseFlagValue TEXT )
CREATE TABLE IF NOT EXISTS tblScrapers (scraperId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperName TEXT, scraperURL TEXT)
--Scraper tables
CREATE TABLE IF NOT EXISTS tblScraperSystems (scraperSystemId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperId INTEGER, scraperSystemName TEXT, scraperSystemAcronym TEXT, scraperSystemURL TEXT)
CREATE TABLE IF NOT EXISTS tblScraperGames (scraperGameId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperSystemId INTEGER, scraperGameName TEXT, scraperGameURL TEXT)
CREATE TABLE IF NOT EXISTS tblScraperGameFlags (scraperGameId INTEGER, scraperGameFlagName TEXT, scraperGameFlagValue TEXT)
CREATE TABLE IF NOT EXISTS tblScraperReleases (scraperReleaseId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperGameId INTEGER, scraperReleaseName TEXT, scraperReleaseRegion TEXT)
CREATE TABLE IF NOT EXISTS tblScraperReleaseFlags (scraperReleaseId INTEGER, scraperReleaseFlagName TEXT, scraperReleaseFlagValue TEXT)
CREATE TABLE IF NOT EXISTS tblScraperReleaseImages (scraperReleaseImageId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperReleaseId INTEGER, scraperReleaseImageName TEXT, scraperReleaseImageType TEXT)
--Matcher tables
CREATE TABLE IF NOT EXISTS tblSynonyms (key TEXT, value TEXT)
CREATE TABLE IF NOT EXISTS tblSystemMap(systemId INTEGER, scraperSystemId INTEGER)

/*-------------*/
/*   Indexes   */
/*-------------*/
--Dat indexes
CREATE INDEX IF NOT EXISTS idxDatGame_fileId ON tblDatGames (datFileId ASC)
CREATE UNIQUE INDEX IF NOT EXISTS idxDatGame_gameName ON tblDatGames (datFileId ASC,datGameName ASC)
CREATE INDEX IF NOT EXISTS idxDatRom_fileId ON tblDatRoms (datFileId ASC)
CREATE INDEX IF NOT EXISTS idxDatRom_gameId ON tblDatRoms (datGameId ASC)
--GameDb indexes
CREATE INDEX IF NOT EXISTS idxROM_releaseId ON tblROMs (releaseId ASC)
CREATE INDEX IF NOT EXISTS idxROM_hashes ON tblROMs (crc32 ASC,md5 ASC,sha1 ASC)
CREATE INDEX IF NOT EXISTS idxRelease_softwareId ON tblReleases (softwareId ASC)
CREATE INDEX IF NOT EXISTS idxSoftware_systemId ON tblSoftwares (systemId ASC)
CREATE INDEX IF NOT EXISTS idxreleaseflagvalue_releaseId_releaseFlagId ON tblReleaseFlagValues (releaseId ASC,releaseFlagId ASC)
--Scraper indexes
CREATE INDEX IF NOT EXISTS idxscrapersystem_scraperId ON tblScraperSystems (scraperId ASC)
CREATE INDEX IF NOT EXISTS idxScraperGame_systemId ON tblScraperGames (scraperSystemId ASC)
CREATE INDEX IF NOT EXISTS idxscrapergameflag_gameid ON tblScraperGameFlags (scraperGameId ASC)
CREATE INDEX IF NOT EXISTS idxScraperRelease_gameid ON tblScraperReleases (scraperGameId ASC)
CREATE INDEX IF NOT EXISTS idxscraperreleaseflag_releaseid ON tblScraperReleaseFlags (scraperReleaseId ASC)
CREATE INDEX IF NOT EXISTS idxscraperreleaseimage_releaseid ON tblScraperReleaseImages (scraperReleaseId ASC)
--Matcher indexes
CREATE INDEX IF NOT EXISTS idxsynonym_key ON tblSynonyms (key ASC)
/*-------------*/
/*   Tables    */
/*-------------*/
--Dat Tables
CREATE TABLE IF NOT EXISTS tblDatFiles (datFileId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, systemId TEXT, datFileName TEXT, datType TEXT, datReleaseGroup TEXT, datDate TEXT);
CREATE TABLE IF NOT EXISTS tblDatGames (datGameId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, datFileId INTEGER, datGameName TEXT, datCloneOf TEXT, datRomOf TEXT);
CREATE TABLE IF NOT EXISTS tblDatRoms (datROMId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, datFileId INTEGER, datGameId INTEGER, datROMName TEXT, datROMMerge TEXT, datROMSize INTEGER, datROMCRC TEXT, datROMMD5 TEXT, datROMSHA1 TEXT);
--GameDb tables
CREATE TABLE IF NOT EXISTS tblSystems (systemId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, systemName TEXT, systemManufacturer TEXT);
CREATE TABLE IF NOT EXISTS tblSoftwares (softwareId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, softwareName TEXT, softwareType TEXT, systemId INTEGER);
CREATE TABLE IF NOT EXISTS tblReleases (releaseId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseName TEXT, releaseType TEXT, softwareId INTEGER);
CREATE TABLE IF NOT EXISTS tblROMs (romId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseId INTEGER, crc32 TEXT, md5 TEXT, sha1 TEXT, size INTEGER);
CREATE TABLE IF NOT EXISTS tblReleaseFlags (releaseFlagId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, releaseFlagName TEXT);
CREATE TABLE IF NOT EXISTS tblReleaseFlagValues (releaseId INTEGER, releaseFlagId INTEGER, releaseFlagValue TEXT);
CREATE TABLE IF NOT EXISTS tblScrapers (scraperId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperName TEXT, scraperURL TEXT);
--Scraper tables
CREATE TABLE IF NOT EXISTS tblScraperSystems (scraperSystemId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperId INTEGER, scraperSystemName TEXT, scraperSystemAcronym TEXT, scraperSystemURL TEXT);
CREATE TABLE IF NOT EXISTS tblScraperGames (scraperGameId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperSystemId INTEGER, scraperGameName TEXT, scraperGameURL TEXT);
CREATE TABLE IF NOT EXISTS tblScraperGameFlags (scraperGameId INTEGER, scraperGameFlagName TEXT, scraperGameFlagValue TEXT);
CREATE TABLE IF NOT EXISTS tblScraperReleases (scraperReleaseId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperGameId INTEGER, scraperReleaseName TEXT, scraperReleaseRegion TEXT);
CREATE TABLE IF NOT EXISTS tblScraperReleaseFlags (scraperReleaseId INTEGER, scraperReleaseFlagName TEXT, scraperReleaseFlagValue TEXT);
CREATE TABLE IF NOT EXISTS tblScraperReleaseImages (scraperReleaseImageId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, scraperReleaseId INTEGER, scraperReleaseImageName TEXT, scraperReleaseImageType TEXT);
--Matcher tables
CREATE TABLE IF NOT EXISTS tblSynonyms (key TEXT, value TEXT, type TEXT);
CREATE TABLE IF NOT EXISTS tblSystemMap(systemId INTEGER, scraperSystemId INTEGER);
CREATE TABLE IF NOT EXISTS tblSoftwareMap(softwareId INTEGER, scraperGameId INTEGER);
CREATE TABLE IF NOT EXISTS tblReleaseMap(releaseId INTEGER, scraperReleaseId INTEGER);
--View
CREATE VIEW IF NOT EXISTS v_match AS
SELECT 
d.datFileName, 
s.systemManufacturer || " - " || s.systemName systemName,
so.softwareId,
so.softwareName,
so.softwareType,
r.releaseId,
r.releaseName,
r.releaseType,
ro.crc32,
ro.md5,
ro.sha1,
ro.size,
sr.scraperName,
sg.scraperGameName,
sg.scraperGameURL,
GROUP_CONCAT(DISTINCT (CASE WHEN rf.releaseFlagName = 'Region' THEN rfv.releaseFlagValue END)) [Region],
GROUP_CONCAT(DISTINCT (CASE WHEN rf.releaseFlagName = 'Version' THEN rfv.releaseFlagValue END)) [Version],
GROUP_CONCAT(DISTINCT (CASE WHEN rf.releaseFlagName = 'License' THEN rfv.releaseFlagValue END)) [License],
GROUP_CONCAT(DISTINCT (CASE WHEN rf.releaseFlagName = 'Revision' THEN rfv.releaseFlagValue END)) [Revision],
GROUP_CONCAT(DISTINCT (CASE WHEN rf.releaseFlagName = 'Language' THEN rfv.releaseFlagValue END)) [Language],
GROUP_CONCAT(DISTINCT (CASE WHEN rf.releaseFlagName = 'BadDump' THEN rfv.releaseFlagValue END)) [BadDump],
GROUP_CONCAT(CASE WHEN sgf.scraperGameFlagName = 'Description' THEN sgf.scraperGameFlagValue END,';') [Description],
GROUP_CONCAT(CASE WHEN sgf.scraperGameFlagName = 'UserRating' THEN sgf.scraperGameFlagValue END,';') [UserRating],
GROUP_CONCAT(CASE WHEN sgf.scraperGameFlagName = 'Difficulty' THEN sgf.scraperGameFlagValue END,';') [Difficulty],
GROUP_CONCAT(CASE WHEN sgf.scraperGameFlagName = 'Length' THEN sgf.scraperGameFlagValue END,';') [Length],
GROUP_CONCAT(CASE WHEN sgf.scraperGameFlagName = 'Developer' THEN sgf.scraperGameFlagValue END,';') [Developer],
GROUP_CONCAT(CASE WHEN sgf.scraperGameFlagName = 'Genre' THEN sgf.scraperGameFlagValue END,';') [Genre],
GROUP_CONCAT(CASE WHEN sgf.scraperGameFlagName = 'Franchise' THEN sgf.scraperGameFlagValue END,';') [Franchise],
GROUP_CONCAT(CASE WHEN sgf.scraperGameFlagName = 'AKA' THEN sgf.scraperGameFlagValue END,';') [AKA]
FROM
tblDatFiles d INNER JOIN
tblSystems s ON s.systemId = d.systemId INNER JOIN
tblSoftwares so ON so.systemId = s.systemId INNER JOIN
tblReleases r ON r.softwareId = so.softwareId INNER JOIN
tblROMs ro ON ro.releaseId = r.releaseId INNER JOIN
tblReleaseFlagValues rfv ON rfv.releaseId = r.releaseId INNER JOIN
tblReleaseFlags rf ON rf.releaseFlagId = rfv.releaseFlagId LEFT JOIN
tblSoftwareMap sm ON sm.softwareId = so.softwareId LEFT JOIN
tblScraperGames sg ON sg.scraperGameId = sm.scraperGameId LEFT JOIN
tblScraperSystems ss ON ss.scraperSystemId = sg.scraperSystemId LEFT JOIN
tblScrapers sr ON sr.scraperId = ss.scraperId LEFT JOIN
tblScraperGameFlags sgf ON sgf.scraperGameId = sg.scraperGameId
GROUP BY 
d.datFileName, 
s.systemManufacturer || " - " || s.systemName,
so.softwareId,
so.softwareName,
so.softwareType,
r.releaseId,
r.releaseName,
r.releaseType,
ro.crc32,
ro.md5,
ro.sha1,
ro.size,
sr.scraperName,
sg.scraperGameName,
sg.scraperGameURL;
/*-------------*/
/*   Indexes   */
/*-------------*/
--Dat indexes
CREATE INDEX IF NOT EXISTS idxDatGame_fileId ON tblDatGames (datFileId ASC);
CREATE UNIQUE INDEX IF NOT EXISTS idxDatGame_gameName ON tblDatGames (datFileId ASC,datGameName ASC);
CREATE INDEX IF NOT EXISTS idxDatRom_fileId ON tblDatRoms (datFileId ASC);
CREATE INDEX IF NOT EXISTS idxDatRom_gameId ON tblDatRoms (datGameId ASC);
--GameDb indexes
CREATE INDEX IF NOT EXISTS idxROM_releaseId ON tblROMs (releaseId ASC);
CREATE INDEX IF NOT EXISTS idxROM_hashes ON tblROMs (crc32 ASC,md5 ASC,sha1 ASC);
CREATE INDEX IF NOT EXISTS idxRelease_softwareId ON tblReleases (softwareId ASC);
CREATE INDEX IF NOT EXISTS idxSoftware_systemId ON tblSoftwares (systemId ASC);
CREATE INDEX IF NOT EXISTS idxReleaseFlagValue_releaseId_releaseFlagId ON tblReleaseFlagValues (releaseId ASC,releaseFlagId ASC);
--Scraper indexes
CREATE INDEX IF NOT EXISTS idxScraperSystem_scraperId ON tblScraperSystems (scraperId ASC);
CREATE INDEX IF NOT EXISTS idxScraperGame_systemId ON tblScraperGames (scraperSystemId ASC);
CREATE INDEX IF NOT EXISTS idxScraperGameFlag_gameid ON tblScraperGameFlags (scraperGameId ASC,scraperGameFlagName ASC);
CREATE INDEX IF NOT EXISTS idxScraperRelease_gameid ON tblScraperReleases (scraperGameId ASC);
CREATE INDEX IF NOT EXISTS idxScraperReleaseFlag_releaseid ON tblScraperReleaseFlags (scraperReleaseId ASC);
CREATE INDEX IF NOT EXISTS idxScraperReleaseImage_releaseid ON tblScraperReleaseImages (scraperReleaseId ASC);
--Matcher indexes
CREATE INDEX IF NOT EXISTS idxSynonym_key ON tblSynonyms (key ASC);
CREATE INDEX IF NOT EXISTS idxSoftwareMap_sofwareId ON tblSoftwareMap (softwareId ASC, scraperGameId ASC);
CREATE INDEX IF NOT EXISTS idxReleaseMap_releaseId ON tblReleaseMap (releaseId ASC, scraperReleaseId ASC);

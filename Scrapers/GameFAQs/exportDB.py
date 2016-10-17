import sqlite3 as lite
import xml.etree.ElementTree as ET
import re
import os

def init_database(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS tblScraper (scraperId INTEGER PRIMARY KEY,scraperName TEXT, scraperURL TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblScrapedSoftwares (scrapedSoftwareId INTEGER PRIMARY KEY, scrapedSoftwareName TEXT, scrapedSoftwareURL TEXT, scrapedSoftwareSystem TEXT, scraperId INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblScrapedReleases (scrapedReleaseId INTEGER PRIMARY KEY, scrapedReleaseName TEXT, scrapedReleaseRegion TEXT, scrapedSoftwareId INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblScrapedSoftwareFlags (scrapedSoftwareFlagId INTEGER PRIMARY KEY, scrapedSoftwareFlagName TEXT, scrapedSoftwareFlagValue TEXT, scrapedSoftwareId INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblScrapedReleaseFlags (scrapedReleaseFlagId INTEGER PRIMARY KEY, scrapedReleaseFlagName TEXT, scrapedReleaseFlagValue TEXT, scrapedReleaseId INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblScrapedReleaseImages (scrapedReleaseImageId INTEGER PRIMARY KEY, scrapedReleaseImageName TEXT, scrapedReleaseImageType TEXT, scrapedReleaseId INTEGER)")

def export_xml(path):
    con = lite.connect('../../sqlite/GameFAQs.db')
    cur = con.cursor()
    init_database(cur)
    tree = ET.parse(path)
    root = tree.getroot()
    cur.execute("SELECT scraperId FROM tblScraper WHERE scraperName = 'GameFAQS'")
    result = cur.fetchone()
    if result is None:
        cur.execute("INSERT INTO tblScraper (scraperName,scraperURL) VALUES (?,?)",("GameFAQS","http://www.gamefaqs.com"))
        scraperId = cur.lastrowid
    else:
        scraperId = result[0]
        
    for soft in root.findall('software'):
        cur.execute("INSERT INTO tblScrapedSoftwares (scrapedSoftwareName,scrapedSoftwareURL,scrapedSoftwareSystem,scraperId) VALUES (?,?,?,?)",(soft.get('name'),soft.get('URL'),soft.get('system'),scraperId))
        softId = cur.lastrowid
        for flag in [flag for flag in list(soft) if flag.tag !='Release']:
            if(len(flag.text)>0):
                cur.execute("INSERT INTO tblScrapedSoftwareFlags (scrapedSoftwareFlagName,scrapedSoftwareFlagValue,scrapedSoftwareId) VALUES (?,?,?)",(flag.tag,flag.text,softId))
        for release in soft.findall('Release'):
            cur.execute("INSERT INTO tblScrapedReleases (scrapedReleaseName,scrapedReleaseRegion,scrapedSoftwareId) VALUES (?,?,?)",(release.get('name'),release.get('region'),softId))
            relId = cur.lastrowid
            for flag in [flag for flag in list(release) if flag.tag !='ReleaseImages']:
                if(flag.text is not None):
                    if(len(flag.text)>1):
                        cur.execute("INSERT INTO tblScrapedReleaseFlags (scrapedReleaseFlagName,scrapedReleaseFlagValue,scrapedReleaseId) VALUES (?,?,?)",(flag.tag,flag.text,softId))
            images = release.find('ReleaseImages')
            if(images is not None):
                for img in images.findall('Image'):
                    cur.execute("INSERT INTO tblScrapedReleaseImages (scrapedReleaseImageName,scrapedReleaseImageType,scrapedReleaseId) VALUES (?,?,?)",(img.text,re.search("_([a-z]+)\.",img.text,re.IGNORECASE).group(1),softId))
        print soft.get('name')
    con.commit()
    con.close()

def import_folder(path):
    for xmlfile in os.listdir(path):
        export_xml(os.path.join(path,xmlfile))

#export_xml("xml/gameFAQsNintendoGameCube.xml")
import_folder('./xml')

from datetime import datetime
import hashlib
import os
import zipfile
import binascii
import sqlite3 as lite
import xml.etree.ElementTree as ET
import regex as re

def init_database(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS tblRomFiles (filename TEXT, size INT, crc32 TEXT, md5 TEXT, sha1 TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblRomInfos (name TEXT, description TEXT, year TEXT, manufacturer TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblRomPictures (name TEXT, type TEXT)")
    
def getsha1(filepath):
    sha1 = hashlib.sha1()
    ##f = zipfile.ZipFile(filepath, 'r')
    ##try:
    ##   sha1.update(f.read(f.namelist()[0]))
    ##finally:
    ##    f.close()
    f = open(filepath,"rb")
    sha1.update(f.read())
    f.close()
    return sha1.hexdigest()

def getmd5(filepath):
    md5 = hashlib.md5()
    ##f = zipfile.ZipFile(filepath, 'r')
    ##try:
    ##    md5.update(f.read(f.namelist()[0]))
    ##finally:
    ##    f.close()
    f = open(filepath,"rb")
    md5.update(f.read())
    f.close()
    return md5.hexdigest()

def getcrc32(filepath):
    f = open(filepath,"rb")
    crc32 = binascii.crc32(f.read()) & 0xFFFFFFFF
    return "%08X" % crc32
    ##f = zipfile.ZipFile(filepath, 'r')
    ##info = f.getinfo(f.namelist()[0])
    ##f.close()
    ##return hex(info.CRC)[2:-1]

def getChecksums(filepath):
    f = open(filepath,"rb")
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    buff = f.read()
    size = len(buff)
    tmp = binascii.crc32(buff) & 0xFFFFFFFF
    crc32 = "%08x" % tmp
    md5.update(buff)
    sha1.update(buff)
    return size,crc32, md5.hexdigest(), sha1.hexdigest()

def scan_folder(path,cursor):
    for filename in os.listdir(path):
        if filename.endswith("zip"):
            size, crc32, md5, sha1 = getChecksums(os.path.join(path, filename))
            cursor.execute("INSERT INTO tblRomFiles (filename, size, crc32, md5, sha1) VALUES (?,?,?,?,?)",(filename,size,crc32,md5,sha1))
            print filename + " : " + crc32 + " " + md5 + " " + sha1
        if filename.endswith("png"):
            cursor.execute("INSERT INTO tblRomPictures (name, type) VALUES (?,?)",(filename[:-4],os.path.basename(path)))

def import_FBA(path,cur):
    datfile = open(path,"r")
    datfile.seek(0)
    tree = ET.parse(datfile)
    root = tree.getroot()
    headernode = root.find('header')
    for gamenode in root.findall('game'):
        softname = gamenode.get('name')
        softdesc = re.sub('[\/<>&*?"|:]',"_",gamenode.find('description').text)
        softyear = gamenode.find('year').text
        softmanu = gamenode.find('manufacturer').text
        print softname + " " + softdesc + " " + softyear + " " + softmanu
        cur.execute("INSERT INTO tblRomInfos (name,description,year,manufacturer) VALUES (?,?,?,?)",(softname,softdesc,softyear,softmanu))
  
def export_dat(path, cur):
    f = open(path,"wb")
    f.write("clrmamepro (\n")
    f.write("\tname \"FB Alpha - Arcade Games\"\n")
    f.write("\tname \"FB Alpha v0.2.97.38 Arcade Games\"\n")
    f.write("\tversion 0.2.97.38\n")
    f.write(")\n")
    f.write("\n")
    sql = """SELECT i.name, i.description, i.year, i.manufacturer, f.filename, f.size, f.crc32, f.md5, f.sha1
            FROM tblRomFiles f LEFT JOIN tblRomInfos i ON i.name || '.zip' = f.filename"""
    cursor.execute(sql)
    for game in cursor:
        f.write("game (\n")
        f.write("\tname \"" + game[1] + "\"\n")
        f.write("\tyear " + game[2] + "\n")
        f.write("\tmanufacturer \"" + game[3] + "\"\n")
        f.write("\trom ( name {0} size {1} crc32 {2} sha1 {3} )\n".format(game[4],game[5],game[6],game[8]))
        f.write(")\n\n")
    f.close()



starttime = datetime.now()
con = lite.connect('sqlite/GameFAQs.db')
cursor = con.cursor()
init_database(cursor)
con.commit()
cursor.execute("DELETE FROM tblRomInfos")
import_FBA(r'FB Alpha v0.2.97.38 (ClrMame Pro XML).dat',cursor)
con.commit()
## cursor.execute("DELETE FROM tblRomFiles")
## scan_folder(r"F:/GameDB/Roms/fba",cursor)
## con.commit()
cursor.execute("DELETE FROM tblRomPictures")
scan_folder(r"D:/Emu/RetroArch/thumbnails/FB Alpha - Arcade Games/Named_Snaps",cursor)
scan_folder(r"D:/Emu/RetroArch/thumbnails/FB Alpha - Arcade Games/Named_Titles",cursor)
con.commit()
export_dat(r"FB Alpha - Arcade Games.dat",cursor)
con.close()
print datetime.now()-starttime

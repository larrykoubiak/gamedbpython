from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import sqlite3 as lite
import re
import os



numeral_map = zip(
    (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
    ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
)

def roman_to_int(n):
    n = unicode(n).upper()

    i = result = 0
    for integer, numeral in numeral_map:
        while n[i:i + len(numeral)] == numeral:
            result += integer
            i += len(numeral)
    return result

def normalize(s):
    s = re.sub(":","",s) # subtitle :
    s = re.sub("-","",s) # subtitle -
    s = re.sub("  "," ",s) # remove double space
    s = re.sub("The ","",s) # remove prefix The      
    s = re.sub(", The","",s) # remove suffix ,The
    return s

def init_database(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS datSystem (datId INTEGER, scrapedSoftwareSystem TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tblFuzzy (datId INTEGER, softwareId INTEGER, scrapedReleaseName TEXT, matchScore INTEGER)")
    f = open('datSystem.csv','r')
    line = f.readline()
    cursor.execute("DELETE FROM datSystem")
    for line in f:
        fields =line[:-1].split(';')
        cursor.execute("INSERT INTO datSystem (datId, scrapedSoftwareSystem) VALUES (?,?)",(fields[0],fields[1]))
    f.close()

def match_releases():
    con = lite.connect('sqlite/GameFAQs.db')
    cursor = con.cursor()
    init_database(cursor)
    con.commit()
    query = "SELECT * FROM datSystem ORDER BY 1"
    cursor.execute(query)
    systems = cursor.fetchall()

    for sys in systems:
        cursor.execute("DELETE FROM tblFuzzy WHERE datId=" + str(sys[0]))
        query = """SELECT DISTINCT r.scrapedReleaseName
                FROM tblScrapedReleases r INNER JOIN
                tblScrapedSoftwares s on s.scrapedSoftwareId = r.scrapedSoftwareId
                WHERE s.scrapedSoftwaresystem = '""" + sys[1] + """'
                ORDER BY 1"""
        cursor.execute(query)
        print sys[1]
        releases=[]
        for row in cursor:
            strGame = normalize(row[0])
            releases.append(strGame)
        query = "SELECT softwareId,softwareName FROM tblSoftwares WHERE datId = " + str(sys[0]) + " AND softwareType='Game'"
        cursor.execute(query)
        softwares = cursor.fetchall()
        for soft in softwares:
            strGame = normalize(soft[1])
            match = process.extractOne(strGame,releases,scorer=fuzz.partial_ratio)
            print '\t' + strGame
            cursor.execute("INSERT INTO tblFuzzy (datId,softwareId, scrapedReleaseName, matchScore) VALUES(?,?,?,?)",(sys[0],soft[0],match[0],match[1]))
        con.commit()
    con.close()

if __name__ == '__main__':
    match_releases()

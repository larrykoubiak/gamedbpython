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
    s = re.sub("\s|-|:|!|'|")

con = lite.connect('sqlite/GameFAQs.db')
cursor = con.cursor()

query = "SELECT * FROM datSystem WHERE datId IN (4,33) ORDER BY 1"
cursor.execute(query)
systems = cursor.fetchall()

for sys in systems:
    cursor.execute("DELETE FROM tblFuzzy WHERE datId=" + str(sys[0]))
    query = """SELECT DISTINCT r.scrapedReleaseName
            FROM tblScrapedReleases r INNER JOIN
            tblScrapedSoftwares s on s.scrapedSoftwareId = r.scrapedSoftwareId
            WHERE s.scrapedSoftwaresystem = '""" + sys[1] + """' AND s.softwareType = 'Commercial'
            ORDER BY 1"""
    cursor.execute(query)
    print sys[1]
    releases=[]
    for row in cursor:
        strGame = row[0]
        strGame = re.sub(":","",strGame) # subtitle :
        strGame = re.sub("-","",strGame) # subtitle -
        strGame = re.sub("  ","",strGame) # remove double space
        strGame = re.sub("The ","",strGame) # remove prefix The      
        strGame = re.sub(", The","",strGame) # remove suffix ,The      
        releases.append(strGame)
    query = "SELECT softwareId,softwareName FROM tblSoftwares WHERE datId = " + str(sys[0]) + " AND softwareType='Game'"
    cursor.execute(query)
    softwares = cursor.fetchall()
    for soft in softwares:
        strGame = soft[1]
        strGame = re.sub(":","",strGame) # subtitle :
        strGame = re.sub("-","",strGame) # subtitle -
        strGame = re.sub("  ","",strGame) # remove double space
        strGame = re.sub("The ","",strGame) # remove prefix The      
        strGame = re.sub(", The","",strGame) # remove suffix ,The      
        match = process.extractOne(strGame,releases,scorer=fuzz.QRatio)
        print '\t' + strGame
        cursor.execute("INSERT INTO tblFuzzy (datId,softwareId, scrapedReleaseName, matchScore) VALUES(?,?,?,?)",(sys[0],soft[0],match[0],match[1]))
    con.commit()
con.close()

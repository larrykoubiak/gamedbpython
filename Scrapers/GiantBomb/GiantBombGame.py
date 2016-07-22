import urllib2
import cookielib
import sqlite3 as lite
import sys
from bs4 import BeautifulSoup
con = lite.connect('GiantBomb.db')
cur = con.cursor()
cj = cookielib.MozillaCookieJar('cookies.txt')
cj.load()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36')]
siteurl = "http://www.giantbomb.com"
systemId = 18
cur.execute ("""SELECT gu.* FROM tblGameURL gu
                INNER JOIN tblSoftwares s ON s.softwareId = gu.softwareID
                INNER JOIN tblSystems sy ON sy.systemId = s.systemId
                WHERE sy.systemID = ? AND gu.softwareId >=? AND gu.softwareId<=?""",(str(systemId),str(12770),str(12957)))
print "Fetching games"
listGames = cur.fetchall()
print "Parsing games"
for game in listGames:
    gameurl = siteurl + game[2]  
    html = opener.open(gameurl)
    soup = BeautifulSoup(html,'html.parser')
    print 'Parsing ' + soup.find('h1',class_='instapaper_title entry-title').a.text
    details = soup.find('div',class_='wiki-details')
    rows = details.table.find_all('tr')
    for row in rows:
        cur.execute("INSERT INTO softwareData(softwareId,tagSource,tagName,tagValue) VALUES (?,?,?,?)",(game[0],'GiantBomb',row.th.text,row.td.text.strip().replace('\n','|')))
    con.commit()
print "Parsing done"

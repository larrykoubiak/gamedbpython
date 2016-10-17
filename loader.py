from rdb import *
import sys, getopt
from xml.sax.saxutils import escape, unescape
import xml.etree.ElementTree as ET
from mysql.connector import connection, FieldType
import os

def xstr(s):
    if s is None:
        return ''
    return str(s)

def import_rdb_xml(input_filename,output_filename):
    tree = ET.parse(input_filename)
    root = tree.getroot()
    db = []
    for soft in root.findall("software"):
        record = []
        for col in list(soft):
            field = rfield(col.tag, col.text)
            record.append(field)
        db.append(record)
    write_rdb(output_filename,db)

def import_rdb_mysql():
    cnx =connection.MySQLConnection(user='d_idea', password='idea1234', host='db.larrykoubiak.com', database='gamedbprod')
    cursor = cnx.cursor()
    query = "SELECT systemId, systemManufacturer, systemName FROM tblSystems WHERE systemId != 18"
    cursor.execute(query)
    systems = cursor.fetchall()
    for system in systems:
        query = "SELECT * FROM gamedbprod.rdb WHERE systemId = " + str(system[0])
        cursor.execute(query)
        colnames = []
        db = []
        for d in cursor.description:
            colnames.append(d[0])
        for row in cursor:
            record = []
            for i in range(0,len(row)):
                field = rfield(colnames[i], row[i])
                record.append(field)
            db.append(record)
        write_rdb("rdb\\" + system[1] + " - " + system[2] + ".rdb",db)
        export_rdb_dat(db,system[1] + " - " + system[2])
        print system[1] + " - " + system[2] + " exported"
    cursor.close()
    cnx.close()
def export_rdb_xml(db,filename):
    outputxml = open(filename,'w')
    outputxml.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
    outputxml.write('<softwarelist>\n')
    for rcd in db:
        outputxml.write('\t<software>\n')
        for fld in rcd:
            outputxml.write("\t\t<" + fld.name + ">" + escape(str(fld.value)) + "</" + fld.name + ">\n")
        outputxml.write("\t</software>\n")
    outputxml.write('</softwarelist>\n')
    outputxml.close()

def export_rdb_dat(db,system):
    for flag in ['developer','franchise','genre','origin','publisher','releasemonth','releaseyear','theme','users']:
        if not os.path.exists("metadat\\" + flag):
            os.makedirs("metadat\\" + flag)
        filename = "metadat\\" + flag + "\\" + system + ".dat"
        outputdat = open(filename,'w')
        outputdat.write('clrmamepro (\n\tname \"' + system.encode("utf-8") + '\"\n\tdescription \"' + system.encode("utf-8") + '\"\n)\n\n')
        for rcd in db:
            name = [f for f in rcd if f.name == "name"]
            flagfield = [f for f in rcd if f.name == flag]
            crc  = [f for f in rcd if f.name == "crc"]
            if(len(name)>0 and flagfield[0].value !="" and len(crc)>0):
                outputdat.write("""game (\n\tname \""""
                                + name[0].value.encode("utf-8") + """\"\n\t"""
                                + flag.encode("utf-8") + """ \""""
                                + (str(flagfield[0].value) if isinstance(flagfield[0].value, (int, long)) else flagfield[0].value.encode("utf-8")) + """\"\n\t"""
                                + """rom ( crc """ + crc[0].value.encode("utf-8") + """ )\n)\n\n""")
        outputdat.close()
        print flag + " dat exported"
def main():
    import_rdb_mysql()
if __name__ == '__main__':
    main()

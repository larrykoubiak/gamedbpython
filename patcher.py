import xlrd
import codecs
from collections import OrderedDict

class Patcher:
    def __init__(self,path):
        self.sqls = []
        self.scripts = []
        self.LoadFile(path)
        
    def LoadFile(self,path):
        header = []
        rows = []
        self.sqls = []
        wb = xlrd.open_workbook(path)
        sheet = wb.sheet_by_index(0)
        for row in sheet.get_rows():
            rows.append(row)
        for col in rows[0]:
            header.append(col.value)
        for row in rows[1:]:
            sql = OrderedDict()
            for col in range(0,len(row)):
                sql[header[col]] = row[col].value
            self.sqls.append(sql)

    def GetColumnCount(self,sql):
        if len(sql["tofield1"])==0:
            count = 0
        if len(sql["tofield2"])==0:
            count = 1
        elif len(sql["tofield3"])==0:
            count = 2
        else:
            count = 3
        return count
    
    def GenerateScript(self,path,stage):
        output = ""
        for sql in [s for s in self.sqls if s['Stage'] == stage]:
            script = ""
            if sql["Action"] == "DELETE":
                strformat = "DELETE FROM {totable} WHERE {tokey} = {tovalue}"
                script = strformat.format(**sql)
            elif sql["Action"] == "UPDATE":
                strformat = "UPDATE {totable} SET {tofield1} = (SELECT {fromfield1} FROM {fromtable} WHERE {fromkey} = {fromvalue}) WHERE {tokey} = {tovalue}"
                script = strformat.format(**sql)
            elif sql["Action"] == "DELETELIST":
                strformat = "DELETE FROM {totable} WHERE {tokey} IN (SELECT {fromfield1} FROM {fromtable} WHERE {fromkey} = {fromvalue})"
                script = strformat.format(**sql)
            elif sql["Action"] == "INSERT":
                count = self.GetColumnCount(sql)
                strformat = "INSERT INTO {totable} ("
                strformat += ",".join("{tofield" + str(i+1) + "}" for i in range(0,count)) + ")"
                strformat += " SELECT "
                strformat += ", ".join("{fromfield" + str(i+1) + "}" for i in range(0,count))
                strformat += " FROM {fromtable} WHERE {fromkey} = {fromvalue}"
                strformat += " AND NOT EXISTS (SELECT 1 FROM {totable} WHERE "
                strformat += " AND ".join("{tofield" + str(i+1) + "} = {fromfield" + str(i+1) + "}" for i in range(0,count))
                strformat += ")"
                script = strformat.format(**sql)
            else:
                pass
            if script != "":
                self.scripts.append(script)
                output += script + ';\n'
        f = codecs.open(path,"w","utf-8")
        f.write(unicode(output))
        f.close()

if __name__ == "__main__":
    patcher = Patcher()
    patcher.LoadFile("patches.xlsx")
    patcher.GenerateScript("patch_softwaremap.sql","SoftwareMap")
    patcher.GenerateScript("patch_softwareflagmap.sql","SoftwareFlagMap")

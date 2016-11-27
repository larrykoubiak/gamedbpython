import xlrd
import codecs
from collections import OrderedDict

class Patcher:
    def __init__(self):
        self.sqls = []
        self.scripts = []
        
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
            for col in range(0,len(row)-1):
                sql[header[col]] = row[col].value
            self.sqls.append(sql)

    def GenerateScript(self,path):
        output = ""
        for sql in self.sqls:
            script = ""
            if sql["Action"] == "DELETE":
                strformat = "DELETE FROM {0} WHERE {1} = {2}"
                script = strformat.format(sql["totable"],sql["tokey"],str(int(sql["tovalue"])))
            elif sql["Action"] == "UPDATE":
                strformat = "UPDATE {0} SET {1} = (SELECT {2} FROM {3} WHERE {4} = '{5}') WHERE {6} = {7}"
                script = strformat.format(sql["totable"],sql["tofield"],sql["fromfield"],sql["fromtable"],sql["fromkey"],sql["fromvalue"],sql["tokey"],str(int(sql["tovalue"])))
            elif sql["Action"] == "DELETELIST":
                strformat = "DELETE FROM {0} WHERE {1} IN (SELECT {2} FROM {3} WHERE {4} = '{5}')"
                script = strformat.format(sql["totable"],sql["tokey"],sql["fromfield"],sql["fromtable"],sql["fromkey"],sql["fromvalue"])
            elif sql["Action"] == "INSERT":
                strformat = "INSERT INTO {0} ({1},{2}) SELECT {3},{4} FROM {5} WHERE {6} = '{7}'"
                script = strformat.format(sql["totable"],sql["tokey"],sql["tofield"],sql["tovalue"],sql["fromfield"],sql["fromtable"],sql["fromkey"],sql["fromvalue"])
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
    patcher.GenerateScript("patches.sql")

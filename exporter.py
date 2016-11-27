import os
import io
import subprocess
import platform

class Exporter:

    def export_rdb_dat(self,flag):
        if not os.path.exists("libretro-database/metadat/" + flag['name']):
            os.makedirs("libretro-database/metadat/" + flag['name'])
        for system in flag['systems']:
            print "Exporting flag " + flag['name'] + " for system " + system['name']
            filename = os.path.join("libretro-database","metadat",flag['name'],system['name'] + ".dat")
            outputdat = io.open(filename,'wb')
            outputdat.write(u'clrmamepro (\n\tname \"' + system['name'].encode("utf-8") + u'\"\n\tdescription \"' + system['name'].encode("utf-8") + u'\"\n)\n\n')
            for rom in system['roms']:
                outputdat.write(u"game (\n")
                outputdat.write(u"\tname \"" + rom['name'].encode("utf-8") + u"\"\n")
                outputdat.write(u"\t" + flag['name'].encode("utf-8") + u" \"" + rom['flagvalue'].encode("utf-8") + u"\"\n")
                outputdat.write(u"\trom ( crc " + rom['crc'].encode("utf-8") + u" )\n")
                outputdat.write(u")\n\n")
            outputdat.close()

    def create_rdb(self,systemName):
        if not os.path.exists("rdb"):
            os.makedirs("rdb")
        commands = []
        metadats = ['analog','bbfc','developer','elspa','enhancement_hw','esrb','franchise','genre','goodtools','libretro-dats','maxusers','no-intro','origin','publisher','releasemonth','releaseyear','rumble','serial','tgdb']
        metadats.extend(['magazine/edge','magazine/edge_review','magazine/famitsu'])
        if (os.path.exists("libretro-database/metadat/no-intro/" + systemName + ".dat") or os.path.exists("libretro-database/dat/" + systemName + ".dat")):
            if platform.system()=="Windows":
                commands.append("c_converter_win.exe")
            else:
                commands.append("./c_converter")
            commands.append("libretro-database/rdb/" + systemName + ".rdb")
            commands.append("rom.crc")
            if os.path.exists("libretro-database/dat/" + systemName + ".dat"):
                commands.append("libretro-database/dat/" + systemName + ".dat")
            for metadat in metadats:
                if os.path.exists("libretro-database/metadat/" + metadat + "/" + systemName + ".dat"):
                    commands.append("libretro-database/metadat/" + metadat + "/" + systemName + ".dat")
            subprocess.check_call(commands)

if __name__ == '__main__':
    exporter = Exporter()
    exporter.create_rdb("Coleco - ColecoVision")

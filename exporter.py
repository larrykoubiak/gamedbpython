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
        if os.path.exists("libretro-database/metadat/no-intro/" + systemName + ".dat"):
            if platform.system()=="Windows":
                commands.append("c_converter_win.exe")
            else:
                commands.append("./c_converter")
            commands.append("rdb/" + systemName + ".rdb")
            commands.append("rom.crc")
            commands.append("libretro-database/metadat/no-intro/" + systemName + ".dat")
            if os.path.exists("libretro-database/metadat/developer/" + systemName + ".dat"):
                commands.append("libretro-database/metadat/developer/" + systemName + ".dat")
            if os.path.exists("libretro-database/metadat/franchise/" + systemName + ".dat"):
                commands.append("libretro-database/metadat/franchise/" + systemName + ".dat")
            if os.path.exists("libretro-database/metadat/genre/" + systemName + ".dat"):
                commands.append("libretro-database/metadat/genre/" + systemName + ".dat")
            if os.path.exists("libretro-database/metadat/origin/" + systemName + ".dat"):
                commands.append("libretro-database/metadat/origin/" + systemName + ".dat")
            if os.path.exists("libretro-database/metadat/publisher/" + systemName + ".dat"):
                commands.append("libretro-database/metadat/publisher/" + systemName + ".dat")
            if os.path.exists("libretro-database/metadat/serial/" + systemName + ".dat"):
                commands.append("libretro-database/metadat/serial/" + systemName + ".dat")
            if os.path.exists("libretro-database/metadat/releasemonth/" + systemName + ".dat"):
                commands.append("libretro-database/metadat/releasemonth/" + systemName + ".dat")
            if os.path.exists("libretro-database/metadat/releaseyear/" + systemName + ".dat"):
                commands.append("libretro-database/metadat/releaseyear/" + systemName + ".dat")
            print commands
            subprocess.check_call(commands)

if __name__ == '__main__':
    exporter = Exporter()
    exporter.create_rdb("Coleco - ColecoVision")

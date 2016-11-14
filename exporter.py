import os
import io
import subprocess

class Exporter:

    def export_rdb_dat(self,flag):
        if not os.path.exists("metadat\\" + flag['name']):
            os.makedirs("metadat\\" + flag['name'])
        for system in flag['systems']:
            print "Exporting flag " + flag['name'] + " for system " + system['name']
            filename = os.path.join("metadat",flag['name'],system['name'] + ".dat")
            outputdat = io.open(filename,'wb')
            outputdat.write(u'clrmamepro (\n\tname \"' + system['name'].encode("utf-8") + u'\"\n\tdescription \"' + system['name'].encode("utf-8") + u'\"\n)\n\n')
            for rom in system['roms']:
                outputdat.write(u"game (\n")
                outputdat.write(u"\tname \"" + rom['name'].encode("utf-8") + u"\"\n")
                outputdat.write(u"\t" + flag['name'] + u" \"" + rom['flagvalue'] + u"\"\n")
                outputdat.write(u"\trom ( crc " + rom['crc'] + u" )\n")
                outputdat.write(u")\n\n")
            outputdat.close()

    def create_rdb(self,systemName):
        if not os.path.exists("rdb"):
            os.makedirs("rdb")
        commands = []
        if os.path.exists("metadat/no-intro/" + systemName + ".dat"):
            commands.append("c_converter.exe")
            commands.append("rdb/" + systemName + ".rdb")
            commands.append("rom.crc")
            commands.append("metadat/no-intro/" + systemName + ".dat")
            if os.path.exists("metadat/developer/" + systemName + ".dat"):
                commands.append("metadat/developer/" + systemName + ".dat")
            if os.path.exists("metadat/franchise/" + systemName + ".dat"):
                commands.append("metadat/franchise/" + systemName + ".dat")
            if os.path.exists("metadat/genre/" + systemName + ".dat"):
                commands.append("metadat/genre/" + systemName + ".dat")
            if os.path.exists("metadat/origin/" + systemName + ".dat"):
                commands.append("metadat/origin/" + systemName + ".dat")
            print "Command: \"" + '" "'.join(commands) + "\""
            print subprocess.check_output(commands,shell=True)

if __name__ == '__main__':
    exporter = Exporter()
    exporter.create_rdb("Entex - Adventure Vision")

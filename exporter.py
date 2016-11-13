import os
import io

class Exporter:

    def export_rdb_dat(self,flag):
        if not os.path.exists("metadat\\" + flag['name']):
            os.makedirs("metadat\\" + flag['name'])
        for system in flag['systems']:
            print "Exporting flag " + flag['name'] + " for system " + system['name']
            filename = os.path.join("metadat",flag['name'],system['name'] + ".dat")
            print filename
            outputdat = io.open(filename,'w',encoding='utf-8')
            outputdat.write(u'clrmamepro (\n\tname \"' + system['name'].encode("utf-8") + u'\"\n\tdescription \"' + system['name'].encode("utf-8") + u'\"\n)\n\n')
            for rom in system['roms']:
                outputdat.write(u"game (\n")
                outputdat.write(u"\tname \"" + rom['name'].encode("utf-8") + u"\"\n")
                outputdat.write(u"\t" + flag['name'] + u" \"" + rom['flagvalue'] + u"\"\n")
                outputdat.write(u"\trom ( crc " + rom['crc'] + u" )\n")
                outputdat.write(u")\n\n")
            outputdat.close()

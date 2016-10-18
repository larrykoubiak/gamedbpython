import regex as re
import xml.etree.ElementTree as ET

class GameDBRegex:
    def __init__(self):
        self.regexes = {}

    def init_regexes(self,releaseGroup):
        self.regexes = {}
        tree = ET.parse("Regexes/"+releaseGroup + ".xml")
        groupNode = tree.find(".//ReleaseGroup[@name='" + releaseGroup+ "']")
        for regex in groupNode.findall("Regex"):
            namenode = regex.find("Name")
            patternnode = regex.find("Pattern")
            self.regexes[namenode.text] = re.compile(patternnode.text)

    def get_regex_result(self,regname,value):
        return self.regexes[regname].search(value)

    def get_regex_results(self,regname,value):
        return self.regexes[regname].finditer(value)

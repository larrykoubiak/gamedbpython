import regex as re
import xml.etree.ElementTree as ET
from datetime import datetime

class GameDBRegex:
    def __init__(self):
        self.regexes = {}
        self.dateFormats = {}
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
	
    def get_cleaned_date(self,datestring):
            resultDate = None
            self.dateFormats = {}
            self.dateFormats['mobyRegex'] = {'regex':re.compile("^(?P<Month>.+?) (?P<Day>\d+?), (?P<Year>\d+?)$"),'format':'%d %B %Y'}
            self.dateFormats['mobyMonthYearRegex'] = {'regex':re.compile("^(?P<Month>.+?),\s(?P<Year>\d+?)$"),'format':'%d %B %Y'}
            self.dateFormats['monthYearRegex'] = {'regex':re.compile("^(?P<Month>\D+?)\s(?P<Year>\d+?)$"),'format':'%d %B %Y'}
            self.dateFormats['yearRegex'] = {'regex':re.compile("^(?P<Year>\d+?)$"),'format':'%d %m %Y'}
            self.dateFormats['dayMonthYearRegex'] = {'regex':re.compile("^(?P<Month>\d+?)\/(?P<Day>\d+?)\/(?P<Year>\d{2}?)$"),'format':'%d %m %y'}
            for dateformat in self.dateFormats.itervalues():
                result = dateformat['regex'].search(datestring)
                if result is not None:
                    day = '01'
                    month = '01'
                    year = '01'
                    if 'Day' in dateformat['regex'].groupindex:
                        day = result.group('Day')
                    if 'Month' in dateformat['regex'].groupindex:
                        month = result.group('Month')
                    if 'Year' in dateformat['regex'].groupindex:
                        year = result.group('Year')
                    resultDate = datetime.strptime(' '.join([day,month,year]),dateformat['format'])
                    break;
            return resultDate

if __name__ == '__main__':
    regexes = GameDBRegex()
    print regexes.get_cleaned_date('November 2008')
    print regexes.get_cleaned_date('03/15/10')
    print regexes.get_cleaned_date('2016')
    print regexes.get_cleaned_date('03/15/2011')    

import regex as re
import xml.etree.ElementTree as ET
from datetime import datetime

class GameDBRegex:
    def __init__(self):
        self.regexes = {}
        self.dateFormats = {}

    def init_regexes(self,releaseGroup):
        self.regexes = {}
        tree = ET.parse("regexes.xml")
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
            self.dateFormats['datRegex'] = {'regex':re.compile("(?P<Year>\d{4})(?P<Month>\d{2})(?P<Day>\d{2})-(?P<Hour>\d{2})(?P<Minute>\d{2})(?P<Second>\d{2})"),'format':'%d/%m/%Y %H:%M:%S'}
            self.dateFormats['mobyRegex'] = {'regex':re.compile("^(?P<Month>.+?) (?P<Day>\d+?), (?P<Year>\d+?)$"),'format':'%d/%B/%Y %H:%M:%S'}
            self.dateFormats['mobyMonthYearRegex'] = {'regex':re.compile("^(?P<Month>.+?),\s(?P<Year>\d+?)$"),'format':'%d/%B/%Y %H:%M:%S'}
            self.dateFormats['monthYearRegex'] = {'regex':re.compile("^(?P<Month>\D+?)\s(?P<Year>\d+?)$"),'format':'%d/%B/%Y %H:%M:%S'}
            self.dateFormats['yearRegex'] = {'regex':re.compile("^(?P<Year>\d+?)$"),'format':'%d/%m/%Y %H:%M:%S'}
            self.dateFormats['dayMonthYearRegex'] = {'regex':re.compile("^(?P<Month>\d+?)\/(?P<Day>\d+?)\/(?P<Year>\d{2}?)$"),'format':'%d/%m/%y %H:%M:%S'}
            for dateformat in self.dateFormats.itervalues():
                result = dateformat['regex'].search(datestring)
                if result is not None:
                    day = '01'
                    month = '01'
                    year = '01'
                    hour = '00'
                    minute = '00'
                    second = '00'
                    if 'Day' in dateformat['regex'].groupindex:
                        day = result.group('Day')
                    if 'Month' in dateformat['regex'].groupindex:
                        month = result.group('Month')
                    if 'Year' in dateformat['regex'].groupindex:
                        year = result.group('Year')
                    if 'Hour' in dateformat['regex'].groupindex:
                        hour = result.group('Hour')
                    if 'Minute' in dateformat['regex'].groupindex:
                        minute = result.group('Minute')
                    if 'Second' in dateformat['regex'].groupindex:
                        second = result.group('Second')
                    resultDate = datetime.strptime('{0}/{1}/{2} {3}:{4}:{5}'.format(day,month,year,hour,minute,second),dateformat['format'])
                    break;
            return resultDate

    def get_cleaned_developer(self,publisherName):
        regDeveloper = re.compile("(?: (?:and co|corporation|corp|, the|SA|S.A.|co|ltd|incorporated|inc))\.?,?",re.I)
        result = regDeveloper.sub('',publisherName)
        return result
    
if __name__ == '__main__':
    regexes = GameDBRegex()
    print regexes.get_cleaned_date('20130303-222635')
    print regexes.get_cleaned_date('November 2008')
    print regexes.get_cleaned_date('03/15/10')
    print regexes.get_cleaned_date('2016')
    print regexes.get_cleaned_date('03/15/2011')
    print regexes.get_cleaned_developer("NATSUME ATARI Inc.")

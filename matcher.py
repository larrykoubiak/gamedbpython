from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import regex as re
import codecs

class Matcher:
    def __init__(self):
        self.synonyms = []
        self.getSynonyms()
        
    def getSynonyms(self):
        self.synonyms = []
        synonymsfile = codecs.open('Scrapers/synonyms.csv','r',encoding='utf8')
        for synonym in synonymsfile:
            synonymDic = {}
            synonymrow = synonym.split(",")
            synonymDic['key'] = synonymrow[0]
            synonymDic['value'] = synonymrow[1].replace('\r\n','')
            self.synonyms.append(synonymDic)
        synonymsfile.close()

    def match_fuzzy(self, Dic, Entry):
        for key,value in Dic.items():
            Dic[key] = self.normalize(value)
        match = process.extractOne(self.normalize(Entry),Dic,scorer=fuzz.QRatio,score_cutoff=80)
        return match[2] if match is not None else None

    def normalize(self, s):
        s = re.sub(":","",s) # subtitle :
        s = re.sub("-","",s) # subtitle -
        s = re.sub("  "," ",s) # remove double space
        s = re.sub("The ","",s) # remove prefix The      
        s = re.sub(", The","",s) # remove suffix ,The
        return s        

if __name__ == '__main__':
    matcher = Matcher()
    print "\nMatcher Job done."    

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re


class Matcher:
    def __init__(self):
        self.synonyms = []
        self.getSynonyms()

    def getSynonyms(self):
        self.synonyms = []
        synonymsfile = open('Scrapers/synonyms.csv', 'r')
        for synonym in synonymsfile:
            synonymDic = {}
            synonymrow = synonym.split(",")
            synonymDic['key'] = synonymrow[0]
            synonymDic['value'] = synonymrow[1]
            synonymDic['type'] = synonymrow[2].replace('\r\n', '')
            self.synonyms.append(synonymDic)
        synonymsfile.close()

    def match_fuzzy(self, Dic, Entry, matchtype="Full", ratio=80):
        for key, value in list(Dic.items()):
            Dic[key] = self.normalize(value)
        if matchtype == "Full":
            scorertype = fuzz.QRatio
        elif matchtype == "Partial":
            scorertype = fuzz.partial_ratio
        match = process.extractOne(
            self.normalize(Entry), Dic,
            scorer=scorertype, score_cutoff=ratio)
        return match[2] if match is not None else None

    def normalize(self, s):
        s = re.sub(":", "", s)  # subtitle :
        s = re.sub("-", "", s)  # subtitle -
        s = re.sub("  ", " ", s)  # remove double space
        s = re.sub("The ", "", s)  # remove prefix The
        s = re.sub(", The", "", s)  # remove suffix , The
        return s


if __name__ == '__main__':
    matcher = Matcher()
    print("\nMatcher Job done.")

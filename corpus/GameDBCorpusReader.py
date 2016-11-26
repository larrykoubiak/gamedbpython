import os
import sqlite3 as lite

from nltk.corpus.reader.api import CorpusReader
from nltk.data import PathPointer, FileSystemPathPointer, ZipFilePathPointer
from nltk import word_tokenize

class GameDBCorpusReader(CorpusReader):
    def __init__(self,root,fileids=None):
        self._con = lite.connect(os.path.join(root,'GameDB.db'))
        self._cur = None
        self._root = FileSystemPathPointer(root)
        self._fileids = ['softwares','scraperSoftware']
        
    def open(self,fileid):
        self._cur = self._con.cursor() 
        query = "SELECT " + fileid + "Id, " + fileid + "Name FROM tbl" + fileid + "s"
        self._cur.execute(query)
    def encoding(self,file):
        return 'utf-8'
    def sents(self,fileids=None):
        _sents = []
        if fileids == None:
            fileids = self._fileids        
        for file in fileids:
            self.open(file)
            for row in self._cur:
                _sents.append(word_tokenize(row[1]))
        return _sents
                
if __name__=="__main__":
    cr = GameDBCorpusReader("../sqlite")
    print cr.sents(["software"])

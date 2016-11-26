import os
import sqlite3 as lite

import bisect

from nltk.tree import Tree
from nltk.tag import map_tag

from nltk.corpus.reader.api import SyntaxCorpusReader


FILES = """SELECT systemId, systemName
        FROM tblSystems s"""

BLOCKS = """SELECT softwareId, softwareName
        FROM tblSoftwares s WHERE systemId = ?"""



class StreamSQLiteCorpusView(AbstractLazySequence):
    def __init__(self,fileid,connection):
        self._fileid = fileid
        self._len = None
        self._con = connection
        self._stream = None
        self._cache = (-1, -1, None)
    def read_block(self, stream):
        raise NotImplementedError('Abstract Method')
    def _open(self):
        self._stream = self._con.cursor() 
        query = "SELECT " + fileid + "Id, " + fileid + "Name FROM tbl" + fileId
        self._stream.execute(query)
    def _close(self):
        if self._stream is not None:
            self._stream.close()
        self._stream = None
    def __len__(self):
        if self._len is None:
            self. = self._stream.rowcount
        return self._len
    def __getitem__(self, i):

    
        

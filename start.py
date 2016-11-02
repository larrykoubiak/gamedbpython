import sys
from os.path import isfile
from PyQt4 import QtCore, QtGui
from edytor import Ui_notepad
import codecs

class StartQT4(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_notepad()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.btnOpenFile,QtCore.SIGNAL("clicked()"), self.file_open)
        QtCore.QObject.connect(self.ui.btnSaveFile,QtCore.SIGNAL("clicked()"), self.file_save)
        QtCore.QObject.connect(self.ui.txtEditor,QtCore.SIGNAL("textChanged()"),self.enable_save)

    def file_open(self):
        fd = QtGui.QFileDialog(self)
        self.filename = fd.getOpenFileName()
        if isfile(self.filename):
            s = codes.open(self.filename,'r','utf-8').read()
            self.ui.txtEditor.setPlainText(s)

    def file_save(self):
        fd = QtGui.QFileDialog(self)
        self.filename = fd.getSaveFileName()
        s = codecs.open(self.filename,'w','utf-8')
        s.write(unicode(self.ui.txtEditor.toPlainText()))
        s.close()

    def enable_save(self):
        self.ui.btnSaveFile.setEnabled(True)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())

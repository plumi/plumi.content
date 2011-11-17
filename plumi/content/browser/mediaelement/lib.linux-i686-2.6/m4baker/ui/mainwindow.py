# -*- coding: utf-8 -*-
#
# M4Baker
# Copyright (C) 2010 Kilian Lackhove
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""
Module implementing MainWindow.
"""


from PyQt4.QtGui import *
from PyQt4.QtCore import *

from Ui_mainwindow import Ui_MainWindow

#from baseclasses import *
from m4baker.baseclasses import *
from ModifyBookDlg import ModifyBookDlg



class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    
    def updateUI(self):
        
        
        self.listWidget.clear()
        
        for element in self.processors:
            self.listWidget.addItem(element.audiobook.author.decode('utf-8') + u' - ' + element.audiobook.title.decode('utf-8'))
            
        if len(self.processors) >= 1:
            self.processButton.setEnabled(True)
            self.upButton.setEnabled(True)
            self.downButton.setEnabled(True)
            self.editButton.setEnabled(True)
            self.deleteButton.setEnabled(True)
        else:
            self.processButton.setEnabled(False)
            self.upButton.setEnabled(False)
            self.downButton.setEnabled(False)
            self.editButton.setEnabled(False)
            self.deleteButton.setEnabled(False)    
    
    def __init__(self, parent = None):
        """
        Constructor
        """
        self.processors = list()

        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        
    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Slot documentation goes here.
        """
        formats = ["*%s" % unicode(format) for format in supportedInputFiles]
        fnames = QFileDialog.getOpenFileNames(self, "Choose audio files to create audiobook from",
                'audio files',  'audio files (%s)' % " ".join(formats))
        if fnames:
            fnames = [unicode(element).encode('utf-8') for element in fnames]

            dialog = ModifyBookDlg(processor(audiobook([chapter(element) for element in fnames])))
            if dialog.exec_():
                self.processors += dialog.processorList
                self.updateUI()
           
    
    @pyqtSignature("")
    def on_upButton_clicked(self):
        """
        Slot documentation goes here.
        """
        procnum = self.listWidget.currentRow()
        
        if procnum >=1:
            self.processors.insert(procnum-1,  self.processors.pop(procnum))
            self.updateUI()
            self.listWidget.setCurrentRow(procnum -1)
        
    @pyqtSignature("")
    def on_downButton_clicked(self):
        """
        Slot documentation goes here.
        """
        procnum = self.listWidget.currentRow()
        
        if procnum < len(self.processors) -1 and procnum >= 0:
            print procnum
            self.processors.insert(procnum+1,  self.processors.pop(procnum))
            self.updateUI()
            self.listWidget.setCurrentRow(procnum +1)

    @pyqtSignature("")
    def on_deleteButton_clicked(self):
        """
        Slot documentation goes here.
        """
        procnum = self.listWidget.currentRow()
        self.processors.pop(procnum)
        self.updateUI()
    
    @pyqtSignature("")
    def on_processButton_clicked(self):
        """
        Slot documentation goes here.
        """
        
        self.processButton.setDisabled(True)
        self.addButton.setDisabled(True)
        self.deleteButton.setDisabled(True)
        self.upButton.setDisabled(True)
        self.downButton.setDisabled(True)
        self.editButton.setDisabled(True)
        self.progressBar.setEnabled(True)
        self.progressLabel.setText('processing')
        
        self.launchProcessor()
        

    def launchProcessor(self):
        self.processors[0].encode(Qt=True)
        self.connect(self.processors[0].faacProc, SIGNAL("readyReadStandardError()"), self.readOutput)
        self.connect(self.processors[0].faacProc,  SIGNAL("finished(int)"),  self.encFinished)
        
    def readOutput(self):
        string = str(self.processors[0].faacProc.readAllStandardError())
        try:
            percent = int(re.search('\(.*?(\d*?)\%\)', string).group(1))
            self.progressBar.setValue(percent)
        except:
            pass
            
    def encFinished(self,  exitCode):
        self.processors[0].tagChapters()
        self.processors[0].tagMeta(Qt=True)
        self.disconnect(self.processors[0].faacProc, SIGNAL("readyReadStandardError()"), self.readOutput)
        self.disconnect(self.processors[0].faacProc,  SIGNAL("finished(int)"),  self.encFinished)
        self.processors[0].faacProc.deleteLater()
        self.processors[0].soxProc.deleteLater()
        self.processors.pop(0)
        
        if len(self.processors) != 0:
            self.launchProcessor()
        else:
            self.progressBar.setDisabled(True)
            self.progressBar.setValue(0)
            self.progressLabel.setText('idle')
            self.addButton.setEnabled(True)
            self.updateUI()
    
    
    @pyqtSignature("")
    def on_editButton_clicked(self):
        """
        Slot documentation goes here.
        """
        
        procnum = self.listWidget.currentRow()
        dialog = ModifyBookDlg(self.processors[procnum])
        if dialog.exec_():
            self.processors[procnum] = dialog.processor
            self.updateUI()

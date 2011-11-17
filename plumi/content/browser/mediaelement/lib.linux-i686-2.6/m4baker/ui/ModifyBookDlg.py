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
Module implementing ModifyBookDlg.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from Ui_ModifyBookDlg import Ui_ModifyBookDlg


#from baseclasses import *
from m4baker.baseclasses import *
from copy import copy

class ModifyBookDlg(QDialog, Ui_ModifyBookDlg):
    """
    The modify audiobook dialog
    """
    def __init__(self, processor,  parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        
        self.processor = copy(processor)
        
        #setup GUI
        if hasattr(self.processor.audiobook,  'coverfile'):
            pixmap = QPixmap(self.processor.audiobook.coverfile)
            pixmap = pixmap.scaled(self.coverLabel.size(),  Qt.KeepAspectRatio )
            self.coverLabel.setPixmap(pixmap)
            
        self.titleEdit.setText(self.processor.audiobook.title.decode('utf-8' ))
        self.yearEdit.setText(self.processor.audiobook.year.decode('utf-8' ))
        self.authorEdit.setText(self.processor.audiobook.author.decode('utf-8' ))
        self.outfileEdit.setText(self.processor.audiobook.outfile.decode('utf-8' ))
        self.faacEdit.setText(self.processor.encodeString.decode('utf-8'))
        
        #allow only numbers in lineEdit
        self.yearEdit.setValidator(QRegExpValidator(QRegExp(r'\d*'), self))
        
        #setup the table
        self.update()


    @pyqtSignature("")
    def on_addButton_clicked(self):
        """
        Slot documentation goes here.
        """
        #TODO: implement add without file
        formats = ["*%s" % unicode(format) for format in supportedInputFiles]
        fnames = QFileDialog.getOpenFileNames(self, "Choose audio files to append to audiobook",
                'audio files', "supported audio files (%s)" % " ".join(formats))
        if fnames:
            fnames = [unicode(element).encode('utf-8') for element in fnames]
            for element in fnames:
                self.processor.audiobook.addChap(chapter(element),  number = len(self.processor.audiobook.chapters))
            self.processor.audiobook.sort('keep')
            self.update()
    
    @pyqtSignature("")
    def on_upButton_clicked(self):
        """
        Slot documentation goes here.
        """
        activerow = self.tableWidget.currentRow()
        activecolumn = self.tableWidget.currentColumn()
        
        if activerow >= 1:
            self.processor.audiobook.chapters[activerow-1:activerow-1] = [self.processor.audiobook.chapters.pop(activerow),  ]
            self.processor.audiobook.update()        
            self.update()
            self.tableWidget.setCurrentCell(activerow-1,  activecolumn)
    
    @pyqtSignature("")
    def on_downButton_clicked(self):
        """
        Slot documentation goes here.
        """
        activerow = self.tableWidget.currentRow()
        activecolumn = self.tableWidget.currentColumn()
        
        if activerow <= len(self.processor.audiobook.chapters)-1 and activerow >=0:
            self.processor.audiobook.chapters[activerow+1:activerow+1] = [self.processor.audiobook.chapters.pop(activerow),  ]
            self.processor.audiobook.update()
            self.update()
            self.tableWidget.setCurrentCell(activerow + 1,  activecolumn)

    
    @pyqtSignature("")
    def on_removeButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.processor.audiobook.remChaps([self.tableWidget.currentRow(),  ])
        self.processor.audiobook.update()        
        self.update()
        
    
    @pyqtSignature("")
    def on_outfileButton_clicked(self):
        """
        Slot documentation goes here.
        """
        fname = QFileDialog.getSaveFileName(self, 'save audiobook',  self.outfileEdit.text(), "Audiobook files (*.m4b)")
        if not fname.isEmpty():
            if not fname.endsWith('.m4b'):
                fname += ".m4b"
            self.outfileEdit.setText(fname)
            
        
    def update(self):
        #TODO: improve update() and on_tableWidget_cellChanged()
        #the function on_tableWidget_cellChanged needs this to know if the table was updated by the user or by this routine - very dirty,
        self.updatingTable = True
        
        self.tableWidget.setRowCount(len(self.processor.audiobook.chapters))
        for i in range(0, len(self.processor.audiobook.chapters)):
            
            self.tableWidget.setItem(i, 0,  QTableWidgetItem(unicode(self.processor.audiobook.chapters[i].trackNumber)))
            
            self.tableWidget.setItem(i,  1, QTableWidgetItem(self.processor.audiobook.chapters[i].title.decode('utf-8')) )

            
            duration = '%.2d:%.2d:%#06.3f' % secConverter(self.processor.audiobook.chapters[i].duration)
            self.tableWidget.setItem(i,  2, QTableWidgetItem(unicode(duration)))
            self.tableWidget.item(i,  2).setFlags(Qt.ItemFlags(17))
            
            startTime = '%.2d:%.2d:%#06.3f' % secConverter(self.processor.audiobook.chapters[i].startTime)
            self.tableWidget.setItem(i,  3, QTableWidgetItem(unicode(startTime)))
            self.tableWidget.item(i,  3).setFlags(Qt.ItemFlags(17))
            
            #prepared for fileless chapters
            if self.processor.audiobook.chapters[i].filename is not None: 
                self.tableWidget.setItem(i,  4, QTableWidgetItem(self.processor.audiobook.chapters[i].filename.decode('utf-8')))
            else:
                self.tableWidget.setItem(i,  4, QTableWidgetItem('No file'))
            self.tableWidget.item(i,  4).setFlags(Qt.ItemFlags(17))
            
        #adjust the table size
        for i in range(0, 5):
            self.tableWidget.resizeColumnToContents(i)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        
        self.updatingTable = False
        
        #10 hours maximum duration is hardcoded, actually ipods can 13 plus change but 10 looks better ;)
        minSplitDuration = 10*60*60
        for chapter in self.processor.audiobook.chapters:
            if chapter.duration <= minSplitDuration:
                minSplitDuration = chapter.duration
        hours,  minutes,  seconds = secConverter(minSplitDuration)
        self.splitTimeEdit.setMinimumTime(QTime(hours,  minutes,  seconds+1))

        self.splitTimeEdit.setMaximumTime(QTime(10,  0, 0))
        
    
    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        """
        Slot documentation goes here.
        """
        #write everything from the lineEdits back to the audiobook
        self.processor.encodeString = unicode(self.faacEdit.text()).encode('utf-8')
        self.processor.audiobook.outfile = unicode(self.outfileEdit.text()).encode('utf-8')
        self.processor.audiobook.author = unicode(self.authorEdit.text()).encode('utf-8')
        self.processor.audiobook.title = unicode(self.titleEdit.text()).encode('utf-8')
        self.processor.audiobook.year = unicode(self.yearEdit.text()).encode('utf-8') 
        
        #split processor to pieces     
        if self.splitCheckBox.checkState() ==2:
            maxDuration = (self.splitTimeEdit.time().hour()*60 + self.splitTimeEdit.time().minute())*60+ self.splitTimeEdit.time().second()
            self.processorList = self.processor.split(maxDuration)
        else:
            self.processorList = [self.processor,  ]
    
        # close
        self.accept()
    
    @pyqtSignature("")
    def on_coverButton_clicked(self):
        """
        Slot documentation goes here.
        """
        #with Qts integrated image converting functions we can open all the files Qt can read, 
        #we will convert them to pngs in tagMeta(Qt=True) anyway
        fname = QFileDialog.getOpenFileName(self, "Choose a cover file",  "cover.png", 
                "image files (*.png *.jpg *.jpeg *.bmp *.gif *.pbm *.pgm *ppm *xpm *xpm)" )
        if  not fname.isEmpty():
            self.processor.audiobook.coverfile = unicode(fname).encode('utf-8')
            pixmap = QPixmap(fname)
            pixmap = pixmap.scaled(self.coverLabel.size(),  Qt.KeepAspectRatio )
            self.coverLabel.setPixmap(pixmap)

    @pyqtSignature("int, int")
    def on_tableWidget_cellChanged(self, row, column):
        """
        Slot documentation goes here.
        """
        #check if the change was not made by update()
        if not self.updatingTable:
            if column == 0:
                self.processor.audiobook.chapters[row].trackNumber= int(self.tableWidget.item(row,  0).text())
            if column ==1:
                self.processor.audiobook.chapters[row].title  = unicode(self.tableWidget.item(row,  1).text()).encode('utf-8')
            self.update()
    
    @pyqtSignature("")
    def on_sortFilenameButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.processor.audiobook.sort(sortBy='filename')
        self.update()
    
    @pyqtSignature("")
    def on_sortTrackNumberButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.processor.audiobook.sort(sortBy='trackNumber')
        self.update()

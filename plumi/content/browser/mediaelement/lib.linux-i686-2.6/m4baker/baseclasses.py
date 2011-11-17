#!/usr/bin/python
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

'''the classes shared by the CLI and the GUI interface'''

import os, re
from subprocess import Popen,  PIPE

version = '0.1.2'

def findSupportedInputFiles():
    '''gets the supported input files from sox help'''
    p= Popen(['sox',  '-h'],  stdout = PIPE)
    soxHelp = p.stdout.read()
    os.waitpid(p.pid, 0)[1]
    filetypes = re.search(r'AUDIO FILE FORMATS:(.*)',  soxHelp).groups(0)
    filetypes = filetypes[0].split()
    return ['.'+ element for element in filetypes]
    
supportedInputFiles = findSupportedInputFiles()

class chapter:
    '''This class represents one chapter of an audiobook    '''

    def __init__(self,  filename = None):
        '''init the chapter with standard minimum data'''

        if filename != None:
            self.setFile(filename)
        else:
             self.duration = 0
             self.title = 'unknown chapter title'
             self.trackNumber = 0
             self.startTime = 0

    def setFile(self, filename):
        '''associate chapter with a file'''
        self.filename = filename
        
        #get fileinfo using soxi
        p= Popen(['soxi',  self.filename],  stdout = PIPE)
        self.__soxioutput = p.stdout.read()
        os.waitpid(p.pid, 0)[1]
        
        #calculate duration in seconds
        (hours, minutes,  seconds) = re.search('(\d\d):(\d\d):(\d\d.\d\d)', 
                                                self.__soxioutput).groups()
        self.duration = float(seconds) + 60.0*float(minutes) + 60*60.0*float(hours)
        
        #get title from soxi, if none found use filename without extension
        try:
            self.title =  re.search('Title=(.*?)\\n',  self.__soxioutput).groups()[0]
        except:
            self.title = re.match(r'(\/.*\/)?(.*?).mp3$', filename).groups()[1]
            

        #get tracknumber from soxi, or from filename
        try:
            self.trackNumber =  int(re.search('Tracknumber=(.*?)\\n',  self.__soxioutput).groups()[0])
        except:
            try:
                filename = re.match(r'(\/.*\/)?(.*?).mp3$', filename).groups()[1]
                self.trackNumber = int(re.search(r'\d+',  filename).group())
            except:
                self.trackNumber = 0            
        

        #set peliminary value for the startTime
        self.startTime = self.duration

    def getBookdata(self):
        '''get books metadata from chapterfile'''
        try:
            bookTitle = re.search('Album=(.*?)\\n',  self.__soxioutput).groups()[0]
        except:
            bookTitle = self.title
            
        try:
            author = re.search('Artist=(.*?)\\n',  self.__soxioutput).groups()[0]
        except:
            author = 'Unknown Author'
            
        try:
            year = re.search('Year=(.*?)\\n',  self.__soxioutput).groups()[0]
        except:
            year = '0000'
            
        return [bookTitle,  author,  year]

class audiobook:
    
    def __init__(self,  chapters,  sortBy = 'filename'):
        '''init audiobook from given chapters, sort them and calculate chapters starting times'''
        self.chapters = chapters
        self.sort(sortBy)
        
        #get book metadata from first chapter file
        self.title = self.chapters[0].getBookdata()[0]
        self.author = self.chapters[0].getBookdata()[1]
        self.year = self.chapters[0].getBookdata()[2]
        
        #set preliminary value for outfie
        self.outfile = self.author + ' - ' + self.title + '.m4b'
        
    def sort(self,  sortBy = None):
        '''sort chapters of audiobook and calculate chapters starttime'''

        if sortBy == 'filename':
            self.chapters = sorted(self.chapters, key=lambda k: k.filename)

        if sortBy == 'trackNumber':
            self.chapters = sorted(self.chapters, key=lambda k: k.trackNumber)
        
        self.update()
    
    def update(self):
        '''update audiobook. things  total time calculation go here'''
        position = 0
        for i in range(0, len(self.chapters)):
            self.chapters[i].startTime = position
            position = position + self.chapters[i].duration
    
    def addChap(self,  chapter,  number=None):
        if number==None:
            self.chapters.append(chapter)
        else:
            self.chapters[number:number] = [chapter,  ]
        
        self.update()

    def remChaps(self, indexList):
        newChapters = list()
        for i in range(0,  len(self.chapters)):
            if i not in indexList:
                newChapters.append(self.chapters[i])
        self.chapters = newChapters
        
        self.update()

class processor:
    
    def __init__(self,  audiobook):
        '''initi processor with audiobook'''
        self.audiobook = audiobook

        self.encodeString ='faac -o <output_file>' 
        
    def encode(self, Qt = False):
        '''encode the book to one file'''
        soxcommand = ['sox',  ]
        for i in range(0, len(self.audiobook.chapters)):
            soxcommand.append(self.audiobook.chapters[i].filename)
        soxcommand[len(soxcommand):]= ['-t',  '.wav',  '-o',  '-']
        
        faaccommand = self.encodeString.split()
        faaccommand = [ re.sub(r'<output_file>',  self.audiobook.outfile,  element) for element in faaccommand]
        faaccommand.append('-')
        
        if Qt:   #workaround because Popen doesnt work properly in Qt apps
            from PyQt4.QtCore import QProcess
            self.soxProc = QProcess()
            self.faacProc = QProcess()
            self.soxProc.setStandardOutputProcess(self.faacProc)
            
            #when faac has output to read it will emit the signal "readyReadStandardError():
            #
            #self.connect(self.faacProc, SIGNAL("readyReadStandardError()"), self.readOutput)
            #and     def readOutput(self):  print self.faacProc.readAllStandardError()
            
            #QProcess wants unicode strings
            soxcommand = [element.decode('utf-8') for element in soxcommand]
            faaccommand= [element.decode('utf-8') for element in faaccommand]
             
            self.soxProc.start(soxcommand[0],  soxcommand[1:])
            self.faacProc.start(faaccommand[0],  faaccommand[1:])
        else:
            p1 = Popen(soxcommand,  stdout=PIPE)
            p2 = Popen(faaccommand,  stdin = p1.stdout,  stdout=PIPE)
            output = p2.communicate()[0]
        
        #tell the audiobook it was encoded
        self.audiobook.encoded = True
        
    def tagChapters(self):
        '''create a chapterfile for mp4chaps and make it write the chapters to the outfile , remove chapterfile'''
        chapterfileName = re.sub('\..*$',  '',  self.audiobook.outfile) + '.chapters.txt'
        chapfile = open(chapterfileName,  'w')
        for element in self.audiobook.chapters:
            hours,  minutes,  seconds = secConverter(element.startTime)
            chapfile.write('%.2d:%.2d:%#06.3f %s - %s\n' % (hours, minutes, 
                                                            seconds, self.audiobook.chapters.index(element)+1, element.title))
        chapfile.close()
        
        p = Popen(['mp4chaps',  '-z',  '-i',  self.audiobook.outfile]) 
        os.waitpid(p.pid, 0)[1]
        
        #os.remove(chapfile.name) #clean up
        
    def tagMeta(self,  Qt = False):
        '''add tags from audiobokk to final outfile'''
        p = Popen(['mp4tags',  '-A',  self.audiobook.title,  '-a',  self.audiobook.author,  '-g',  'Audiobook',  '-s', 
                    self.audiobook.title,  '-y',  self.audiobook.year,  self.audiobook.outfile])
        os.waitpid(p.pid, 0)[1]
        
        if Qt:   #use Qts integrated image processing magic
            from PyQt4.QtGui import QPixmap
            from PyQt4.QtCore import QString
            if hasattr(self.audiobook,  'coverfile'):
                pixmap = QPixmap(self.audiobook.coverfile.decode('utf-8'))
                pixmap = pixmap.scaledToHeight(480)
                pixmap.save(self.audiobook.outfile.decode('utf-8') + u'.png')
                p = Popen(['mp4tags',  '-P',  self.audiobook.outfile + '.png',  self.audiobook.outfile])
                os.waitpid(p.pid, 0)[1]
                #os.remove(self.audiobook.outfile + '.png')
        else:
            #if a coverfile was specified, set it
            if hasattr(self.audiobook,  'coverfile'):
                p = Popen(['mp4tags',  '-P',  self.audiobook.coverfile,  self.audiobook.outfile])
                os.waitpid(p.pid, 0)[1]
    
    
    def split(self,  maxDuration):
        
        from copy import deepcopy
        
        processorList = [deepcopy(self),  ]
        sumDuration = 0
        splitNumber = 2
        
        for i in range(0,  len(self.audiobook.chapters)):
            sumDuration += self.audiobook.chapters[i].duration
            if sumDuration >= maxDuration:
                processorList.append(deepcopy(self))
                processorList[-1].audiobook.title = processorList[-1].audiobook.title + str(splitNumber)
                processorList[-1].audiobook.outfile = processorList[-1].audiobook.outfile[0:-4]+ str(splitNumber) + '.m4b'
                
                #trim last chapters 
                processorList[-2].audiobook.remChaps(range(len(processorList[-2].audiobook.chapters) - 
                                    (len(self.audiobook.chapters) -i ),  len(processorList[-2].audiobook.chapters)))
                #trim first chapters 
                processorList[-1].audiobook.remChaps(range(0,  i))
                
                
                sumDuration = 0
                splitNumber += 1

        
        return processorList
            

def secConverter(seconds):
    '''converts 'seconds' from 'SS.ms' to 'HH:MM:SS.ms' format'''
    hours, remain = divmod(seconds, 3600)
    minutes, seconds = divmod(remain, 60)
    return (hours,  minutes,  seconds)

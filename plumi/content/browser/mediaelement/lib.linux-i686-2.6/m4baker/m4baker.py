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

import sys,  getopt
from optparse import OptionParser
from baseclasses import *


# The following  "which()" function was taken from Stack Overflow
#http://stackoverflow.com/questions/377017
#answer by "Jay"  http://stackoverflow.com/users/20840/jay
#Thanks, Jay!
def which(program):
    import os
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def gui():
    
    print 'starting in GUI mode'
    from PyQt4 import QtCore, QtGui
    from ui.mainwindow import MainWindow
    app = QtGui.QApplication(sys.argv)
    ui = MainWindow()
    #check for dependencies
    for dependency in ['faac',  'sox',  'soxi',  'mp4chaps',  'mp4tags']:
        if which(dependency) == None:
            msgBox = QtGui.QMessageBox()
            msgBox.setIcon(QtGui.QMessageBox.Critical)
            msgBox.setText('Missing dependency: '+dependency+
                ' is not properly installed. \nPlease read INSTALL.txt \nExiting.')
            msgBox.exec_()
            sys.exit(2)
    ui.show()
    sys.exit(app.exec_())
    

def cli(options,  args):
    
    #check for dependencies
    for dependency in ['faac',  'sox',  'soxi',  'mp4chaps',  'mp4tags']:
        if which(dependency) == None:
            print '%s is not installed. Read INSTALL.txt for instructions' %(dependency,  )
            sys.exit(2)
    
    #check if input files are of correct file type and if input files are specified at all. if true, create audiobook instance
    for element in args:
        correctFiletype = False
        for value in [element.endswith(type) for type in supportedInputFiles]: #produces a list of boolean values
            correctFiletype = correctFiletype| value #checks if there is at least one True value in the list
        if not correctFiletype:
            print 'only the filetypes supported by soxi are supported input files. According to your sox install these are:'
            print ' '.join(supportedInputFiles)
            sys.exit(2)

    book01 = audiobook([chapter(element) for element in args],  options.sortBy)
    
    #check if a coverfile of correct filetype was given and set it
    if options.coverfile != None and options.coverfile.endswith('.png'):
        book01.coverfile = options.coverfile
    elif options.coverfile != None:
        print 'only .png files are supported cover files.'
        sys.exit(2)    
    
    
    #eventually, set output file name
    if options.outfile != None:
        book01.outfile = options.outfile
        
    # check if  split length is correct
    if options.split != None:
        try:
            options.split = int(options.split)
        except:
            print 'Only integer values for split duration accepted'
            sys.exit(2)
        minSplitDuration = 10*60*60
        for element in book01.chapters:
            if element.duration <= minSplitDuration:
                minSplitDuration = element.duration
        if options.split <= minSplitDuration:
            print 'split duration smaller than shortest chapter duration'
            sys.exit(2)

    #print an overview of whats going to happen
    print 'The following audiobook will be created:'
    print 'author: {0}| title: {1}| year: {2}'.format(book01.author,  book01.title,  book01.year)
    if hasattr(book01,  'coverfile'):
        print 'cover file: {0}'.format(book01.coverfile)
    else:
        print 'No cover'
    if options.split != None:
        print 'split duration: {0} seconds'.format(options.split)
    print 'output file: {0}'.format(book01.outfile)
    print '{0:4}|{1:5}| {2:12}| {3:40}| {4:30}'.format('#', 'track',  'start (sec)',  'filename', 'title')
    for element in book01.chapters:
        print '{0:4}| {1:4}| {2:12.2f}| {3:40}| {4:40}'.format(book01.chapters.index(element)+1,  element.trackNumber,  element.startTime,  
                                                        element.filename, element.title)
    
    #ask user if hes ok with that or if -y was given as argument
    print 'Proceed? (y/n)'
    if not options.dontask:
        if raw_input() != 'y':
            print 'aborted by user'
            sys.exit(2)
            
    #create a processor an run it
    proc01 = processor(book01)
    processorList=[]
    if options.split != None:
        processorList +=proc01.split(options.split)
    else:
        processorList +=[proc01,  ]
    for element in processorList:
        element.encode()
        element.tagChapters()
        element.tagMeta()
    

def main():
    
    #create command line argument parser
    parser = OptionParser()
    parser = OptionParser(usage= 'usage: %prog [options] input_file1 [input_file2 ...] OR %prog [options] for GUI mode', 
                          version = version)
    parser.add_option('-o', '--outfile',  dest='outfile', 
                      help='Set output file OUTFILE. If not specified, \"author - Booktitle.m4b\" will be used. Only in CLI mode')
    parser.add_option('-c', '--coverfile', dest= 'coverfile',
                      help='Include cover into audiobook form file COVERFILE. Only .png files are supported so far. \
                      Use GUI mode for more supported filetypes. Only in CLI mode')
    parser.add_option('-y',  action='store_true',  dest='dontask',  default=False, 
                      help= 'Dont ask for confirmation. Only in CLI mode')
    parser.add_option('-g',  '--GUI', action= 'store_true',  dest = 'gui',  default= False, 
                      help = 'use Graphical User Interface instead. Standard option if no arguments are given'  )
    parser.add_option('-s',  '--sort',  default = 'filename',  dest= 'sortBy',  
                      help = 'specify how the files should be sorted: by \"filename\" or by \"trackNumber\", \"filename\" is standard. Only in CLI mode.')
    parser.add_option('--split',  default= None,  dest='split',  
                      help='split audiobook into pices of duration SPLIT in seconds')
    (options, args) = parser.parse_args()
    
    if options.gui or len(args) == 0: 
        gui()
    else:
        cli(options,  args)

    
if __name__ == "__main__":
    
    main()

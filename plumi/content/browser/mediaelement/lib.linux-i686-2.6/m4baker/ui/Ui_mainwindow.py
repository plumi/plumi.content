# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'M4Baker/ui/mainwindow.ui'
#
# Created: Mon Mar 15 20:37:07 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(462, 228)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtGui.QListWidget(self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.addButton = QtGui.QPushButton(self.groupBox)
        self.addButton.setEnabled(True)
        self.addButton.setObjectName("addButton")
        self.verticalLayout.addWidget(self.addButton)
        self.upButton = QtGui.QPushButton(self.groupBox)
        self.upButton.setEnabled(False)
        self.upButton.setObjectName("upButton")
        self.verticalLayout.addWidget(self.upButton)
        self.downButton = QtGui.QPushButton(self.groupBox)
        self.downButton.setEnabled(False)
        self.downButton.setObjectName("downButton")
        self.verticalLayout.addWidget(self.downButton)
        self.deleteButton = QtGui.QPushButton(self.groupBox)
        self.deleteButton.setEnabled(False)
        self.deleteButton.setObjectName("deleteButton")
        self.verticalLayout.addWidget(self.deleteButton)
        self.editButton = QtGui.QPushButton(self.groupBox)
        self.editButton.setEnabled(False)
        self.editButton.setObjectName("editButton")
        self.verticalLayout.addWidget(self.editButton)
        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 1)
        self.progressBar = QtGui.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(False)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 1)
        self.progressLabel = QtGui.QLabel(self.centralwidget)
        self.progressLabel.setMinimumSize(QtCore.QSize(0, 0))
        self.progressLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.progressLabel.setObjectName("progressLabel")
        self.gridLayout.addWidget(self.progressLabel, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.processButton = QtGui.QPushButton(self.centralwidget)
        self.processButton.setEnabled(False)
        self.processButton.setCheckable(False)
        self.processButton.setObjectName("processButton")
        self.horizontalLayout_2.addWidget(self.processButton)
        self.quitButton = QtGui.QPushButton(self.centralwidget)
        self.quitButton.setObjectName("quitButton")
        self.horizontalLayout_2.addWidget(self.quitButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionClose = QtGui.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.quitButton, QtCore.SIGNAL("clicked()"), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "M4Baker - Job Queue", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Audiobook actions", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("MainWindow", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.upButton.setText(QtGui.QApplication.translate("MainWindow", "up", None, QtGui.QApplication.UnicodeUTF8))
        self.downButton.setText(QtGui.QApplication.translate("MainWindow", "down", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteButton.setText(QtGui.QApplication.translate("MainWindow", "delete", None, QtGui.QApplication.UnicodeUTF8))
        self.editButton.setText(QtGui.QApplication.translate("MainWindow", "edit", None, QtGui.QApplication.UnicodeUTF8))
        self.progressLabel.setText(QtGui.QApplication.translate("MainWindow", "idle", None, QtGui.QApplication.UnicodeUTF8))
        self.processButton.setText(QtGui.QApplication.translate("MainWindow", "Process", None, QtGui.QApplication.UnicodeUTF8))
        self.quitButton.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClose.setText(QtGui.QApplication.translate("MainWindow", "Exit", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


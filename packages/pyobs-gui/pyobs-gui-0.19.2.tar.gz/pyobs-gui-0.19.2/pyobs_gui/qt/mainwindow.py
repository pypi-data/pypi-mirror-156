# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1374, 916)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelAutonomousWarning = QtWidgets.QLabel(self.centralwidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 38, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 38, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(110, 113, 117))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.labelAutonomousWarning.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.labelAutonomousWarning.setFont(font)
        self.labelAutonomousWarning.setAutoFillBackground(True)
        self.labelAutonomousWarning.setFrameShape(QtWidgets.QFrame.Box)
        self.labelAutonomousWarning.setFrameShadow(QtWidgets.QFrame.Plain)
        self.labelAutonomousWarning.setLineWidth(2)
        self.labelAutonomousWarning.setAlignment(QtCore.Qt.AlignCenter)
        self.labelAutonomousWarning.setObjectName("labelAutonomousWarning")
        self.verticalLayout.addWidget(self.labelAutonomousWarning)
        self.labelWeatherWarning = QtWidgets.QLabel(self.centralwidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 38, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(35, 38, 41))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(110, 113, 117))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.labelWeatherWarning.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.labelWeatherWarning.setFont(font)
        self.labelWeatherWarning.setAutoFillBackground(True)
        self.labelWeatherWarning.setFrameShape(QtWidgets.QFrame.Box)
        self.labelWeatherWarning.setFrameShadow(QtWidgets.QFrame.Plain)
        self.labelWeatherWarning.setLineWidth(2)
        self.labelWeatherWarning.setAlignment(QtCore.Qt.AlignCenter)
        self.labelWeatherWarning.setObjectName("labelWeatherWarning")
        self.verticalLayout.addWidget(self.labelWeatherWarning)
        self.splitterLog = QtWidgets.QSplitter(self.centralwidget)
        self.splitterLog.setOrientation(QtCore.Qt.Vertical)
        self.splitterLog.setObjectName("splitterLog")
        self.layoutWidget = QtWidgets.QWidget(self.splitterLog)
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.listPages = QtWidgets.QListWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listPages.sizePolicy().hasHeightForWidth())
        self.listPages.setSizePolicy(sizePolicy)
        self.listPages.setMinimumSize(QtCore.QSize(84, 84))
        self.listPages.setMaximumSize(QtCore.QSize(84, 16777215))
        self.listPages.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.listPages.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listPages.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listPages.setProperty("showDropIndicator", False)
        self.listPages.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.listPages.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.listPages.setIconSize(QtCore.QSize(32, 32))
        self.listPages.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.listPages.setMovement(QtWidgets.QListView.Static)
        self.listPages.setFlow(QtWidgets.QListView.LeftToRight)
        self.listPages.setViewMode(QtWidgets.QListView.IconMode)
        self.listPages.setSelectionRectVisible(False)
        self.listPages.setObjectName("listPages")
        self.horizontalLayout.addWidget(self.listPages)
        self.splitterToolBox = QtWidgets.QSplitter(self.layoutWidget)
        self.splitterToolBox.setOrientation(QtCore.Qt.Horizontal)
        self.splitterToolBox.setObjectName("splitterToolBox")
        self.stackedWidget = QtWidgets.QStackedWidget(self.splitterToolBox)
        self.stackedWidget.setObjectName("stackedWidget")
        self.horizontalLayout.addWidget(self.splitterToolBox)
        self.splitterClients = QtWidgets.QSplitter(self.splitterLog)
        self.splitterClients.setOrientation(QtCore.Qt.Horizontal)
        self.splitterClients.setObjectName("splitterClients")
        self.tableLog = QtWidgets.QTableView(self.splitterClients)
        self.tableLog.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.tableLog.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableLog.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableLog.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableLog.setGridStyle(QtCore.Qt.NoPen)
        self.tableLog.setSortingEnabled(False)
        self.tableLog.setObjectName("tableLog")
        self.tableLog.horizontalHeader().setVisible(False)
        self.tableLog.horizontalHeader().setStretchLastSection(True)
        self.tableLog.verticalHeader().setVisible(False)
        self.tableLog.verticalHeader().setDefaultSectionSize(20)
        self.tableLog.verticalHeader().setMinimumSectionSize(20)
        self.listClients = QtWidgets.QListWidget(self.splitterClients)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listClients.sizePolicy().hasHeightForWidth())
        self.listClients.setSizePolicy(sizePolicy)
        self.listClients.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listClients.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.listClients.setObjectName("listClients")
        self.verticalLayout.addWidget(self.splitterLog)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "pyobs GUI"))
        self.labelAutonomousWarning.setText(_translate("MainWindow", "!!! WARNING: autonomous module(s) active !!!"))
        self.labelWeatherWarning.setText(_translate("MainWindow", "!!! WARNING: weather module disabled !!!"))
from . import resources_rc

# Form implementation generated from reading ui file 'c:\Users\Trash\VT2\ui\packageman.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setObjectName("mainLayout")
        self.tabWidget = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        self.tabWidget.setElideMode(QtCore.Qt.TextElideMode.ElideNone)
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.setObjectName("tabWidget")
        self.pluginTab = QtWidgets.QWidget()
        self.pluginTab.setObjectName("pluginTab")
        self.pluginTabLayout = QtWidgets.QVBoxLayout(self.pluginTab)
        self.pluginTabLayout.setObjectName("pluginTabLayout")
        self.widget = QtWidgets.QWidget(parent=self.pluginTab)
        self.widget.setMaximumSize(QtCore.QSize(16777215, 100))
        self.widget.setObjectName("widget")
        self.cardLayout = QtWidgets.QHBoxLayout(self.widget)
        self.cardLayout.setObjectName("cardLayout")
        self.widget_3 = QtWidgets.QWidget(parent=self.widget)
        self.widget_3.setObjectName("widget_3")
        self.cardTextLayout = QtWidgets.QVBoxLayout(self.widget_3)
        self.cardTextLayout.setObjectName("cardTextLayout")
        self.nameLbl = QtWidgets.QLabel(parent=self.widget_3)
        self.nameLbl.setObjectName("nameLbl")
        self.cardTextLayout.addWidget(self.nameLbl)
        self.repoLbl = QtWidgets.QLabel(parent=self.widget_3)
        self.repoLbl.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.repoLbl.setObjectName("repoLbl")
        self.cardTextLayout.addWidget(self.repoLbl)
        self.descriptLbl = QtWidgets.QLabel(parent=self.widget_3)
        self.descriptLbl.setObjectName("descriptLbl")
        self.cardTextLayout.addWidget(self.descriptLbl)
        self.cardLayout.addWidget(self.widget_3)
        self.pushButton = QtWidgets.QPushButton(parent=self.widget)
        self.pushButton.setObjectName("pushButton")
        self.cardLayout.addWidget(self.pushButton)
        self.pluginTabLayout.addWidget(self.widget)
        self.tabWidget.addTab(self.pluginTab, "")




        self.themeTab = QtWidgets.QWidget()
        self.themeTab.setObjectName("themeTab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.themeTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_2 = QtWidgets.QWidget(parent=self.themeTab)
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 100))
        self.widget_2.setObjectName("widget_2")
        self.themeTabLayout = QtWidgets.QHBoxLayout(self.widget_2)
        self.themeTabLayout.setObjectName("themeTabLayout")
        self.widget_4 = QtWidgets.QWidget(parent=self.widget_2)
        self.widget_4.setObjectName("widget_4")
        self.cardTextLayout_2 = QtWidgets.QVBoxLayout(self.widget_4)
        self.cardTextLayout_2.setObjectName("cardTextLayout_2")
        self.nameLbl_2 = QtWidgets.QLabel(parent=self.widget_4)
        self.nameLbl_2.setObjectName("nameLbl_2")
        self.cardTextLayout_2.addWidget(self.nameLbl_2)
        self.repoLbl_2 = QtWidgets.QLabel(parent=self.widget_4)
        self.repoLbl_2.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.repoLbl_2.setObjectName("repoLbl_2")
        self.cardTextLayout_2.addWidget(self.repoLbl_2)
        self.descriptLbl_2 = QtWidgets.QLabel(parent=self.widget_4)
        self.descriptLbl_2.setObjectName("descriptLbl_2")
        self.cardTextLayout_2.addWidget(self.descriptLbl_2)
        self.themeTabLayout.addWidget(self.widget_4)
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.widget_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.themeTabLayout.addWidget(self.pushButton_2)
        self.verticalLayout.addWidget(self.widget_2)
        self.tabWidget.addTab(self.themeTab, "")



        
        self.mainLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.nameLbl.setText(_translate("MainWindow", "Plugin v.1.0"))
        self.repoLbl.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic; color:#383838;\">https://github.com/cherry220-v/Plugin</span></p></body></html>"))
        self.descriptLbl.setText(_translate("MainWindow", "This is description of Plugin"))
        self.pushButton.setText(_translate("MainWindow", "Download"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pluginTab), _translate("MainWindow", "Tab 1"))
        self.nameLbl_2.setText(_translate("MainWindow", "Plugin v.1.0"))
        self.repoLbl_2.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-weight:600; font-style:italic; color:#383838;\">https://github.com/cherry220-v/Plugin</span></p></body></html>"))
        self.descriptLbl_2.setText(_translate("MainWindow", "This is description of Plugin"))
        self.pushButton_2.setText(_translate("MainWindow", "Download"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.themeTab), _translate("MainWindow", "Tab 2"))
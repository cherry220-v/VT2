import sys, json, os

from PyQt6 import QtCore, QtWidgets
from datetime import datetime
import msgpack, io

from addit import *
from api2 import PluginManager, VtAPI
from test import MyAPI

class Logger:
    def __init__(self, window):
        self._log = ""
        self.__window = window
        
        self._stdout_backup = sys.stdout
        self._log_stream = io.StringIO()
        sys.stdout = self

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        self._log = value
        if self.__window.console:
            self.__window.console.textEdit.clear()
            self.__window.console.textEdit.append(value)

    def write(self, message):
        if message:
            self.__window.api.App.setLogMsg(f"stdout: {message}")
            self._stdout_backup.write(message)

    def flush(self):
        pass

    def close(self):
        sys.stdout = self._stdout_backup
        self._log_stream.close()

class Ui_MainWindow(object):
    sys.path.insert(0, ".")

    def setupUi(self, MainWindow, argv=[]):
        self.MainWindow = MainWindow
        self.appPath = os.path.basename(__file__)
        self.appPath = os.path.dirname(argv[0])
        self.themeFile = ""
        self.localeDirs = []

        self.settings()

        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.setWindowTitle(self.MainWindow.appName)
        self.MainWindow.resize(800, 600)

        self.console = None

        self.logger = Logger(self.MainWindow)
        self.translator = QtCore.QTranslator()

        self.centralwidget = QtWidgets.QWidget(parent=self.MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.treeView = QtWidgets.QTreeView(parent=self.centralwidget)
        self.treeView.setMinimumWidth(150)
        self.treeView.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)
        self.treeView.setMaximumWidth(300)
        self.treeView.setObjectName("treeWidget")

        self.treeSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.horizontalLayout.addWidget(self.treeSplitter)

        self.tabWidget = TabWidget(parent=self.centralwidget, MainWindow=self.MainWindow)
        self.treeSplitter.addWidget(self.treeView)
        self.treeSplitter.addWidget(self.tabWidget)

        self.MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(parent=self.MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menuBar")

        self.MainWindow.setMenuBar(self.menubar)

        self.encodingLabel = QtWidgets.QLabel("UTF-8")
        self.encodingLabel.setObjectName("encodingLabel")
        self.statusbar = QtWidgets.QStatusBar(parent=self.MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.addPermanentWidget(self.encodingLabel)
        self.MainWindow.setStatusBar(self.statusbar)

        self.api = VtAPI(self.MainWindow)
        self.testApi = MyAPI()
        self.logger.log = "VarTexter window loading..."

        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def addTab(self, name: str = "", text: str = "", i: int = -1, file=None, canSave=True, canEdit=True,
               encoding="UTF-8"):
        self.tab = QtWidgets.QWidget()
        self.tab.file = file
        self.tab.canSave = canSave
        self.tab.canEdit = canEdit
        self.tabWidget.tabBar().setTabSaved(self.tab, True)
        self.tab.encoding = encoding
        self.tab.setObjectName("tab")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName("verticalLayout")

        self.frame = QtWidgets.QFrame(parent=self.tab)
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame.setObjectName("tabFrame")
        self.verticalLayout.addWidget(self.frame)

        self.tab.textEdit = TextEdit(self.MainWindow)
        self.tab.textEdit.setReadOnly(False)

        self.tab.textEdit.safeSetText(text)
        self.tab.textEdit.setObjectName("textEdit")

        self.verticalLayout.addLayout(self.tab.textEdit.layout)

        self.tabWidget.addTab(self.tab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), name or "Untitled")
        self.api.Tab.setTab(-1)

        new_view = MyAPI.View(self.testApi, self, qwclass=self.tab)
        self.testApi.active_window.views.append(new_view)
        self.testApi.active_window.active_view = new_view

        self.api.SigSlots.tabCreated.emit()

    def closeTab(self, i: int = None):
        if not i:
            i = self.api.Tab.currentTabIndex()
        self.tabWidget.closeTab(i)

    def defineLocale(self):
        return QtCore.QLocale.system().name().split("_")[0]

    def translate(self, d):
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, f"{self.locale}.vt-locale")):
            if self.translator.load(os.path.join(d, f"{self.locale}.vt-locale")):
                QtCore.QCoreApplication.installTranslator(self.translator)

    def translateStr(self, s):
        return self.tr(s)

    def showPackages(self):
        self.pl.pm.updateRepos()
        self.pl.pm.exec()

    def logConsole(self, checked=None):
        if not self.console:
            self.console = ConsoleWidget(self.MainWindow)
            self.console.textEdit.append(self.logger.log)
            self.MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self.console)
        else:
            self.console.deleteLater()
            self.console = None

    def settings(self):
        self.settFile = open(os.path.join(self.appPath, 'ui/Main.settings'), 'r+', encoding='utf-8')
        self.settData = json.load(self.settFile)
        self.packageDirs = self.settData.get("packageDirs")
        if self.packageDirs:
            self.packageDirs = StaticInfo.replacePaths(self.packageDirs.get(StaticInfo.get_platform()))
            if not os.path.isdir(self.packageDirs): os.makedirs(self.packageDirs)
            self.themesDir = StaticInfo.replacePaths(os.path.join(self.packageDirs, "Themes"))
            if not os.path.isdir(self.themesDir): os.makedirs(self.themesDir)
            self.pluginsDir = StaticInfo.replacePaths(os.path.join(self.packageDirs, "Plugins"))
            if not os.path.isdir(self.pluginsDir): os.makedirs(self.pluginsDir)
            self.uiDir = StaticInfo.replacePaths(os.path.join(self.packageDirs, "Ui"))
            if not os.path.isdir(self.uiDir): os.makedirs(self.uiDir)
            self.cacheDir = StaticInfo.replacePaths(os.path.join(self.packageDirs, "cache"))
            if not os.path.isdir(self.cacheDir): os.makedirs(self.cacheDir)
        self.MainWindow.appName = self.settData.get("appName")
        self.MainWindow.__version__ = self.settData.get("apiVersion")
        self.MainWindow.remindOnClose = self.settData.get("remindOnClose")
        self.menuFile = StaticInfo.replacePaths(os.path.join(self.packageDirs, self.settData.get("menu")))
        self.hotKeysFile = StaticInfo.replacePaths(os.path.join(self.packageDirs, self.settData.get("hotkeys")))
        self.locale = self.settData.get("hotkeys")
        os.chdir(self.packageDirs)

    def settingsHotKeys(self):
        if os.path.isfile(self.hotKeysFile):
            openFile = self.api.getCommand("openFile")
            if openFile:
                openFile.get("command")([self.hotKeysFile])
            else:
                QtWidgets.QMessageBox.warning(self.MainWindow, self.MainWindow.appName + " - Warning", f"Open file function not found. You can find file at {self.hotKeysFile}")

    def hideShowMinimap(self):
        tab = self.tabWidget.currentWidget()
        if tab:
            minimap = tab.textEdit.minimapScrollArea
            if minimap.isHidden():
                minimap.show()
            else:
                minimap.hide()


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        openFile = self.api.getCommand("openFile")
        if openFile:
            openFile.get("command")(files)
        else:
            QtWidgets.QMessageBox.warning(self.MainWindow, self.MainWindow.appName + " - Warning", f"Open file function not found. Check your Open&Save plugin at {os.path.join(self.pluginsDir, 'Open&Save')}")

    def windowInitialize(self):
        [os.makedirs(dir) for dir in [self.themesDir, self.pluginsDir, self.uiDir] if not os.path.isdir(dir)]
        self.tabLog = {}
        stateFile = os.path.join(self.packageDirs, 'data.msgpack')
        try:
            if os.path.isfile(stateFile):
                with open(stateFile, 'rb') as f:
                    packed_data = f.read()
                    self.tabLog = msgpack.unpackb(packed_data, raw=False)
                    if self.tabLog.get("themeFile") and os.path.isfile(self.tabLog.get("themeFile")): self.themeFile = self.tabLog.get("themeFile")
                    if self.tabLog.get("locale"): self.locale = self.tabLog.get("locale")
                    else:
                        if self.locale == "auto":
                            self.locale = self.defineLocale()
                    self.api.App.setTheme(self.themeFile)  
        except ValueError:
            self.logger.log += f"\nFailed to restore window state. No file found at {stateFile}"  

    def restoreWState(self):
        for tab in self.tabLog.get("tabs") or []:
            tab = self.tabLog.get("tabs").get(tab)
            self.addTab(name=tab.get("name"), text=tab.get("text"), file=tab.get("file"), canSave=tab.get("canSave"))
            self.api.Tab.setTabSaved(self.api.Tab.currentTabIndex(), tab.get("saved"))
            self.MainWindow.setWindowTitle(f"{self.MainWindow.tabWidget.tabText(self.api.Tab.currentTabIndex())} - VarTexter2")
            self.api.Text.setTextSelection(self.api.Tab.currentTabIndex(), tab.get("selection")[0], tab.get("selection")[1])
        if self.tabLog.get("activeTab"):
            self.tabWidget.setCurrentIndex(int(self.tabLog.get("activeTab")))
        if self.tabLog.get("splitterState"): self.treeSplitter.restoreState(self.tabLog.get("splitterState"))

    def closeEvent(self, e: QtCore.QEvent):
        self.saveWState()
        self.api.SigSlots.windowClosed.emit()

        e.accept()

    def saveWState(self):
        tabsInfo = {}
        tabs = tabsInfo["tabs"] = {}
        i = self.api.Tab.currentTabIndex()
        tabsInfo["themeFile"] = self.themeFile
        tabsInfo["locale"] = self.locale
        tabsInfo["activeTab"] = str(i)
        tabsInfo["splitterState"] = self.treeSplitter.saveState().data()
        stateFile = os.path.join(self.packageDirs, 'data.msgpack')
        for idx in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(idx)
            if widget and isinstance(widget, QtWidgets.QWidget):
                cursor = self.api.Text.getTextCursor(i)
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                tabs[str(idx)] = {
                    "name": self.api.Tab.getTabTitle(idx),
                    "file": self.api.Tab.getTabFile(idx),
                    "canSave": self.api.Tab.getTabCanSave(idx),
                    "text": self.api.Tab.getTabText(idx),
                    "saved": self.api.Tab.getTabSaved(idx),
                    "selection": [start, end],
                    "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        tabs = {str(idx): tabs[str(idx)] for idx in range(len(tabs))}
        if os.path.isfile(stateFile):
            mode = 'wb'
        else:
            mode = 'ab'
        with open(stateFile, mode) as f:
            packed_data = msgpack.packb(tabsInfo, use_bin_type=True)
            f.write(packed_data)
        self.settFile.close()

    def undo(self, i=None):
        tab = self.tabWidget.widget(i or self.api.Tab.currentTabIndex())
        tab.textEdit.undo()

    def redo(self, i=None):
        tab = self.tabWidget.widget(i or self.api.Tab.currentTabIndex())
        tab.textEdit.redo()

    def cut(self, i=None):
        tab = self.tabWidget.widget(i or self.api.Tab.currentTabIndex())
        tab.textEdit.cut()

    def copy(self, i=None):
        tab = self.tabWidget.widget(i or self.api.Tab.currentTabIndex())
        tab.textEdit.copy()

    def paste(self, i=None):
        tab = self.tabWidget.widget(i or self.api.Tab.currentTabIndex())
        tab.textEdit.paste()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.constants = {
            "platform": StaticInfo.get_platform(),
            "basedir": StaticInfo.get_basedir(),
            "filedir": StaticInfo.get_filedir(__file__),
            "username": os.getlogin(),
        }

        self.textContextMenu = QtWidgets.QMenu(self)
        self.tabBarContextMenu = QtWidgets.QMenu(self)


        self.setupUi(self, self.argvParse())
        self.testApi.active_window = self.testApi.Window(self.testApi, qmwclass=self)
        self.windowInitialize()

        self.pl = PluginManager(self.pluginsDir, self)
        self.pl.registerCommand({"command": "setTheme"})
        self.pl.registerCommand({"command": "hideShowMinimap"})
        self.pl.registerCommand({"command": "settingsHotKeys"})
        self.pl.registerCommand({"command": "argvParse"})
        self.pl.registerCommand({"command": "closeTab"})
        self.pl.registerCommand({"command": "addTab"})
        self.pl.registerCommand({"command": "showPackages"})

        if self.menuFile and os.path.isfile(self.menuFile): self.pl.loadMenu(self.menuFile)
        if os.path.isdir(os.path.join(self.uiDir, "locale")): self.translate(os.path.join(self.uiDir, "locale"))

        self.pl.load_plugins()
        self.api.loadThemes(self.menuBar())
        self.pl.registerCommands()

        if self.hotKeysFile and os.path.isfile(self.hotKeysFile): self.pl.registerShortcuts(json.load(open(self.hotKeysFile, "r+")))

        self.pl.clearCache()

        self.restoreWState()

        self.api.App.setTreeWidgetDir("/")

        openFileCommand = self.api.getCommand("openFile")
        if openFileCommand:
            openFileCommand.get("command")([sys.argv[1]] if len(sys.argv) > 1 else [], used=False)

    def setTheme(self, theme):
        themePath = os.path.join(self.themesDir, theme)

        if os.path.isfile(themePath):
            self.setStyleSheet(open(themePath, "r+").read())
            self.themeFile = themePath

    def argvParse(self):
        return sys.argv

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    # print(w.testApi.active_window.active_view.insert(w.testApi.Point(0, 0), "djelkjl"))
    # print(w.testApi.active_window.active_view.replace(w.testApi.Region(0, 3), "djelkjl"))
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
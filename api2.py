from PyQt6 import QtWidgets, QtCore, QtGui
import os, sys, configparser, json, importlib, re, subprocess, platform
import importlib.util
import PyQt6
import os, json
import builtins

from addit import PackageManager

BLOCKED = [
    "PyQt6"
]

oldCoreApp = QtCore.QCoreApplication

class SafeImporter:
    def __init__(self, disallowed_imports):
        self.disallowed_imports = disallowed_imports

    def __enter__(self):
        self.original_import = builtins.__import__
        builtins.__import__ = self.import_hook

    def __exit__(self, exc_type, exc_value, traceback):
        builtins.__import__ = self.original_import

    def import_hook(self, name, *args, **kwargs):
        for disallowed in self.disallowed_imports:
            if name.startswith(disallowed):
                raise ImportError(f"Importing '{name}' is not allowed.")
        return self.original_import(name, *args, **kwargs)

class BlockedQApplication:
    def __init__(self, *args, **kwargs):
        raise ImportError("Access to QApplication is not allowed.")

def importModule(path, n):
    spec = importlib.util.spec_from_file_location(n, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[n] = module
    spec.loader.exec_module(module)
    return module

class PluginManager:
    def __init__(self, plugin_directory: str, w):
        self.plugin_directory = plugin_directory
        self.__window = w
        self.pm = PackageManager(w, self.plugin_directory)
        self.__menu_map = {}
        self.commands = []
        self.shortcuts = []
        self.regCommands = {}
        self.dPath = None

    def load_plugins(self):
        try:
            self.dPath = os.getcwd()
            sys.path.insert(0, self.plugin_directory)
            for plugDir in os.listdir(self.plugin_directory):
                fullPath = os.path.join(self.plugin_directory, plugDir)
                os.chdir(fullPath)
                if os.path.isdir(fullPath) and os.path.isfile(f"config.vt-conf"):
                    module = None
                    info = self.initPlugin(os.path.join(fullPath, "config.vt-conf"))
                    if self.mainFile:
                        pyFile = self.mainFile
                        try:
                            with SafeImporter(BLOCKED):
                                sys.modules['PyQt6.QtWidgets'].QApplication = BlockedQApplication
                                sys.modules['PyQt6.QtCore'].QCoreApplication = BlockedQApplication
                                sys.path.insert(0, fullPath)
                                module = importModule(pyFile, self.name + "Plugin")
                                if hasattr(module, "initAPI"):
                                    module.initAPI(self.__window.api)
                                sys.modules['PyQt6.QtCore'].QCoreApplication = oldCoreApp
                        except Exception as e:
                            self.__window.api.App.setLogMsg(f"Failed load plugin '{self.name}' commands: {e}")
                        finally:
                            sys.path.pop(0)
                    if self.menuFile:
                        self.loadMenu(self.menuFile, module)
                    if self.scFile:
                        try:
                            self.registerShortcuts(json.load(open(self.scFile, "r+")))
                        except Exception as e:
                            self.__window.api.App.setLogMsg(
                                f"Failed load shortcuts for '{self.name}' from '{self.scFile}': {e}")

        finally:
            os.chdir(self.dPath)

    def loadMenu(self, f, module=None):
        try:
            menuFile = json.load(open(f, "r+"))
            localeDir = os.path.join(os.path.dirname(f), "locale")
            if os.path.isdir(localeDir): self.__window.translate(localeDir)
            for menu in menuFile:
                if menu == "menuBar" or menu == "mainMenu":
                    self.parseMenu(menuFile.get(menu), self.__window.menuBar(), module, "MainMenu")
                elif menu == "textContextMenu":
                    self.parseMenu(menuFile.get(menu), self.__window.textContextMenu, module, "TextContextMenu")
                elif menu == "tabBarContextMenu":
                    self.parseMenu(menuFile.get(menu), self.__window.tabBarContextMenu, module, "TabBarContextMenu")
        except Exception as e:
            self.__window.api.App.setLogMsg(f"Failed load menu from '{f}': {e}")

    def initPlugin(self, path):
        config = json.load(open(path, "r+"))

        self.name = config.get('name', 'Unknown')
        self.version = config.get('version', '1.0')
        self.mainFile = config.get('main', '')
        self.menuFile = config.get('menu', '')
        self.scFile = config.get('sc', '')

    def parseMenu(self, data, parent, pl=None, localemenu="MainMenu"):
        if isinstance(data, dict):
            data = [data]

        for item in data:
            if item.get('caption') == "-":
                parent.addSeparator()
                continue
            menu_id = item.get('id')
            if menu_id:
                fmenu = self.findMenu(parent, menu_id)
                if fmenu:
                    if 'children' in item:
                        self.parseMenu(item['children'], fmenu, pl)
                else:
                    menu = self.__menu_map.setdefault(menu_id, QtWidgets.QMenu(QtCore.QCoreApplication.translate("MainMenu", item.get('caption', 'Unnamed')), self.__window))
                    menu.setObjectName(item.get('id'))
                    parent.addMenu(menu)
                    if 'children' in item:
                        self.parseMenu(item['children'], menu, pl)
            else:
                action = QtGui.QAction(QtCore.QCoreApplication.translate(localemenu, item.get('caption', 'Unnamed')), self.__window)
                if 'shortcut' in item:
                    if not item['shortcut'] in self.shortcuts:
                        action.setShortcut(QtGui.QKeySequence(item['shortcut']))
                        action.setStatusTip(item['shortcut'])
                        self.shortcuts.append(item['shortcut'])
                    else:
                        self.__window.api.App.setLogMsg(
                            f"Shortcut '{item['shortcut']}' for function '{item['command']}' is already used.")

                if 'command' in item:
                    args = item.get('command').get("args")
                    kwargs = item.get('command').get("kwargs")
                    self.commands.append(
                        {"action": action, "command": item['command'], "plugin": pl, "args": args, "kwargs": kwargs})
                    if 'checkable' in item:
                        action.setCheckable(item['checkable'])
                        if 'checked' in item:
                            action.setChecked(item['checked'])
                    action.triggered.connect(lambda checked, cmd=item['command']:
                                             self.executeCommand(
                                                 cmd,
                                                 checked=checked
                                             )
                                             )
                parent.addAction(action)

    def executeCommand(self, c, *args, **kwargs):
        ckwargs = kwargs
        command = c
        c = self.regCommands.get(command.get("command"))
        if c:
            try:
                args = command.get("args")
                kwargs = command.get("kwargs")
                checkable = command.get("checkable")
                action = c.get("action")
                if action and action.isCheckable():
                    checked_value = ckwargs.get("checked")

                    if checked_value is not None:
                        action.setChecked(checked_value)
                    else:
                        new_checked_state = not action.isChecked()
                        action.setChecked(new_checked_state)
                out = c.get("command")(*args or [], **kwargs or {})
                self.__window.api.App.setLogMsg(f"Executed command '{command}' with args '{args}', kwargs '{kwargs}'")
                if out:
                    self.__window.api.App.setLogMsg(f"Command '{command}' returned '{out}'")
            except Exception as e:
                self.__window.api.App.setLogMsg(f"Found error in '{command}' - '{e}'.\nInfo: {c}")
                print(e)
        else:
            self.__window.api.App.setLogMsg(f"Command '{command}' not found")

    def registerShortcuts(self, data):
        for sh in data:
            keys = sh.get("keys")
            command = sh.get("command")
            cmd_name = command.get("command")

            if keys not in self.shortcuts:
                action = QtGui.QAction(self.__window)
                for key in keys:
                    action.setShortcut(QtGui.QKeySequence(key))
                    action.setStatusTip(key)
                    self.shortcuts.append(key)

                action.triggered.connect(lambda checked, cmd=command:
                                         self.executeCommand(cmd)
                                         )
                self.__window.addAction(action)
                self.__window.api.App.setLogMsg(f"Shortcut '{keys}' for function '{cmd_name}' registered.")
            else:
                self.__window.api.App.setLogMsg(f"Shortcut '{keys}' for function '{cmd_name}' already used.")

    def registerCommand(self, commandInfo):
        command = commandInfo.get("command")
        if type(command) == str:
            commandN = command
        else:
            commandN = command.get("command")
        pl = commandInfo.get("plugin")
        action = commandInfo.get("action")

        args = commandInfo.get("args", [])
        kwargs = commandInfo.get("kwargs", {})

        if pl:
            try:
                command_func = getattr(pl, commandN)
                self.regCommands[commandN] = {
                    "action": action,
                    "command": command_func,
                    "args": args,
                    "kwargs": kwargs,
                    "plugin": pl,
                }
            except (ImportError, AttributeError, TypeError) as e:
                self.__window.api.App.setLogMsg(f"Error when registering '{commandN}' from '{pl}': {e}")
        else:
            command_func = getattr(self.__window, commandN, None)
            if command_func:
                self.regCommands[commandN] = {
                    "action": action,
                    "command": command_func,
                    "args": args,
                    "kwargs": kwargs,
                    "plugin": None,
                }
            else:
                self.__window.api.App.setLogMsg(f"Command '{commandN}' not found")

    def registerCommands(self):
        for commandInfo in self.commands:
            command = commandInfo.get("command")
            if type(command) == str:
                commandN = command
            else:
                commandN = command.get("command")
            pl = commandInfo.get("plugin")
            action = commandInfo.get("action")

            args = commandInfo.get("args", [])
            kwargs = commandInfo.get("kwargs", {})
            checkable = commandInfo.get("checkable", False)

            if pl:
                try:
                    command_func = getattr(pl, commandN)
                    self.regCommands[commandN] = {
                        "action": action,
                        "command": command_func,
                        "args": args,
                        "kwargs": kwargs,
                        "plugin": pl,
                    }
                except (ImportError, AttributeError, TypeError) as e:
                    self.__window.api.App.setLogMsg(f"Error when registering '{commandN}' from '{pl}': {e}")
            else:
                command_func = getattr(self.__window, commandN, None)
                if command_func:
                    self.regCommands[commandN] = {
                        "action": action,
                        "command": command_func,
                        "args": args,
                        "kwargs": kwargs,
                        "plugin": None,
                    }
                else:
                    self.__window.api.App.setLogMsg(f"Command '{commandN}' not found")

    def findAction(self, parent_menu, caption=None, command=None):
        for action in parent_menu.actions():
            if caption and action.text() == caption:
                return action
            if command and hasattr(action, 'command') and action.command == command:
                return action

        for action in parent_menu.actions():
            if action.menu():
                found_action = self.findAction(action.menu(), caption, command)
                if found_action:
                    return found_action

        return None

    def findMenu(self, menubar, menu_id):
        for action in menubar.actions():
            menu = action.menu()
            if menu:
                if menu.objectName() == menu_id:
                    return menu
                found_menu = self.findMenu2(menu, menu_id)
                if found_menu:
                    return found_menu
        return None

    def findMenu2(self, menu, menu_id):
        for action in menu.actions():
            submenu = action.menu()
            if submenu:
                if submenu.objectName() == menu_id:
                    return submenu
                found_menu = self.findMenu2(submenu, menu_id)
                if found_menu:
                    return found_menu
        return None

    def clearMenu(self, menu, menu_id):
        menu = self.findMenu(menu, menu_id)
        if menu:
            menu.clear()

    def clearCache(self):
        del self.dPath, self.commands, self.shortcuts

class Tab:
    def __init__(self, w):
        self.__window = w

    def currentTabIndex(self):
        return self.__window.tabWidget.indexOf(self.__window.tabWidget.currentWidget())

    def getTabTitle(self, i):
        return self.__window.tabWidget.tabText(i)

    def setTabTitle(self, i, text):
        tab = self.__window.tabWidget.widget(i)
        return self.__window.tabWidget.setTabText(self.__window.tabWidget.indexOf(tab), text)

    def getTabText(self, i):
        tab = self.__window.tabWidget.widget(i)
        text = tab.textEdit.toPlainText()
        return text

    def getTabHtml(self, i):
        tab = self.__window.tabWidget.widget(i)
        text = tab.textEdit.toHtml()
        return text

    def setTabText(self, i, text: str | None):
        tab = self.__window.tabWidget.widget(i)
        tab.textEdit.setText(text)
        return text

    def getTabFile(self, i):
        tab = self.__window.tabWidget.widget(i)
        return tab.file

    def setTabFile(self, i, file):
        tab = self.__window.tabWidget.widget(i)
        tab.file = file
        return tab.file

    def getTabCanSave(self, i):
        tab = self.__window.tabWidget.widget(i)
        return tab.canSave

    def setTabCanSave(self, i, b: bool):
        tab = self.__window.tabWidget.widget(i)
        tab.canSave = b
        return b

    def getTabCanEdit(self, i):
        tab = self.__window.tabWidget.widget(i)
        return tab.canEdit

    def setTabCanEdit(self, i, b: bool):
        tab = self.__window.tabWidget.widget(i)
        tab.canEdit = b
        tab.textEdit.setReadOnly(b)
        tab.textEdit.setDisabled(b)
        return b

    def getTabEncoding(self, i):
        tab = self.__window.tabWidget.widget(i)
        return tab.encoding

    def setTabEncoding(self, i, enc):
        tab = self.__window.tabWidget.widget(i)
        tab.encoding = enc
        return enc

    def setTab(self, i):
        if i <= -1:
            self.__window.tabWidget.setCurrentIndex(self.__window.tabWidget.count() - 1)
        else:
            self.__window.tabWidget.setCurrentIndex(i - 1)
        return i

    def getTabSaved(self, i):
        tab = self.__window.tabWidget.widget(i)
        return self.__window.tabWidget.isSaved(tab)

    def setTabSaved(self, i, b: bool):
        tab = self.__window.tabWidget.widget(i)
        self.__window.tabWidget.tabBar().setTabSaved(tab or self.__window.tabWidget.currentWidget(), b)
        return b

class Text:
    def __init__(self, w):
        self.__window = w

    def getTextSelection(self, i):
        tab = self.__window.tabWidget.widget(i)
        return tab.textEdit.textCursor().selectedText()

    def getTextCursor(self, i):
        tab = self.__window.tabWidget.widget(i)
        return tab.textEdit.textCursor()

    def setTextSelection(self, i, s, e):
        tab = self.__window.tabWidget.widget(i)
        cursor = tab.textEdit.textCursor()
        cursor.setPosition(s)
        cursor.setPosition(e, QtGui.QTextCursor.MoveMode.KeepAnchor)
        tab.textEdit.setTextCursor(cursor)

    def getCompletePos(self, i):
        tab = self.__window.tabWidget.widget(i)
        current_text = tab.textEdit.toPlainText()
        cursor_position = tab.textEdit.textCursor().position()

        line_number = tab.textEdit.textCursor().blockNumber()
        column = tab.textEdit.textCursor().columnNumber()

        lines = current_text.splitlines()
        if 0 <= line_number < len(lines):
            line = lines[line_number]
            return current_text, line_number + 1, column
        else:
            return current_text, 0, 0

    def setCompleteList(self, i, lst):
        tab = self.__window.tabWidget.widget(i)
        self.completer = tab.textEdit.completer.updateCompletions(lst)

    def setHighlighter(self, i, hl):
        tab = self.__window.tabWidget.widget(i)
        tab.textEdit.highLighter.highlightingRules = hl

    def rehighlite(self, i):
        tab = self.__window.tabWidget.widget(i)
        if tab:
            tab.textEdit.highLighter.rehighlight()

class Commands:
    def __init__(self, w):
        self.__window = w

    def registerCommand(self, data):
        self.__window.pl.registerCommand(data)

    def loadShortcuts(self, data):
        self.__window.pl.registerShortcuts(data)

class App:
    def __init__(self, w):
        self.__window = w
        self.packagesDirs = self.__window.packageDirs
        self.pluginsDir = self.__window.pluginsDir
        self.themesDir = self.__window.themesDir
        self.uiDir = self.__window.uiDir

    def openFileDialog(e=None):
        dlg = QtWidgets.QFileDialog.getOpenFileNames(None, "Open File", "", "All Files (*);;Text Files (*.txt)")
        return dlg

    def saveFileDialog(e=None):
        dlg = QtWidgets.QFileDialog.getSaveFileName()
        return dlg

    def openDirDialog(self, e=None):
        dlg = QtWidgets.QFileDialog.getExistingDirectory(
            self.__window.treeView,
            caption="VarTexter - Get directory",
        )
        return str(dlg)

    def getTheme(self):
        return self.__window.themeFile

    def setTheme(self, theme):
        themePath = os.path.join(self.__window.themesDir, theme)
        if os.path.isfile(themePath):
            self.__window.setStyleSheet(open(themePath, "r+").read())

    def getLog(self):
        return self.__window.logger.log

    def setLogMsg(self, msg):
        self.__window.logger.log += f"\n{msg}"

    def getTreeModel(self):
        return self.model

    def getModelElement(self, i):
        return self.model.filePath(i)

    def setTreeWidgetDir(self, dir):
        self.model = QtGui.QFileSystemModel()
        self.model.setRootPath(dir)
        self.__window.treeView.setModel(self.model)
        self.__window.treeView.setRootIndex(self.model.index(dir))
        return self.model

    def setTheme(self, theme):
        themePath = os.path.join(self.__window.themesDir, theme)
        if os.path.isfile(themePath):
            self.__window.setStyleSheet(open(themePath, "r+").read())

    def updateMenu(self, menu, data):
        menuClass = self.__window.pl.findMenu(self.__window.menuBar(), menu)
        if menu:
            self.__window.pl.clearMenu(self.__window.menuBar(), menu)
            self.__window.pl.parseMenu(data, menuClass)

class FSys:
    def __init__(self, w):
        self.__window = w

    def osModule(self):
        return os

    def sysModule(self):
        return sys

    def jsonModule(self):
        return json

    def importlibModule(self):
        return importlib

    def PyQt6Module(self):
        return PyQt6

    def reModule(self):
        return re

    def sprModule(self):
        return subprocess

    def platformModule(self):
        return platform
    
    def importModule(self, name):
        return importlib.import_module(name)

class SigSlots(QtCore.QObject):
    commandsLoaded = QtCore.pyqtSignal()
    tabClosed = QtCore.pyqtSignal(int, str)
    tabCreated = QtCore.pyqtSignal()
    tabChanged = QtCore.pyqtSignal()
    textChanged = QtCore.pyqtSignal()
    windowClosed = QtCore.pyqtSignal()

    treeWidgetClicked = QtCore.pyqtSignal(QtCore.QModelIndex)
    treeWidgetDoubleClicked = QtCore.pyqtSignal(QtCore.QModelIndex)
    treeWidgetActivated = QtCore.pyqtSignal()

    def __init__(self, w):
        super().__init__(w)
        self.__window = w

        self.__window.treeView.doubleClicked.connect(self.onDoubleClicked)

    def tabChngd(self, index):
        if index > -1:
            self.__window.setWindowTitle(
                f"{os.path.normpath(self.__window.api.Tab.getTabFile(index) or 'Untitled')} - {self.__window.appName}")
            if index >= 0: self.__window.encodingLabel.setText(self.__window.tabWidget.widget(index).encoding)
            self.updateEncoding()
        else:
            self.__window.setWindowTitle(self.__window.appName)
        self.tabChanged.emit()

    def updateEncoding(self):
        e = self.__window.api.Tab.getTabEncoding(self.__window.api.Tab.currentTabIndex())
        self.__window.encodingLabel.setText(e)

    def onDoubleClicked(self, index):
        self.treeWidgetDoubleClicked.emit(index)

    def onClicked(self, index):
        self.treeWidgetClicked.emit(index)

    def onActivated(self):
        self.treeWidgetActivated.emit()

class VtAPI:
    def __init__(self, parent):
        self.__window = parent
        self.__version__ = self.__window.__version__
        self.Tab = Tab(self.__window)
        self.Text = Text(self.__window)
        self.SigSlots = SigSlots(self.__window)
        self.App = App(self.__window)
        self.FSys = FSys(self.__window)

    def __str__(self):
        return f"""\n------------------------------VtAPI--version--{str(self.__version__)}------------------------------\nDocumentation:https://wtfidklol.com"""

    def loadThemes(self, menu):
        themeMenu = self.__window.pl.findMenu(menu, "themes")
        if themeMenu:
            themes = []
            for theme in os.listdir(self.__window.themesDir):
                if os.path.isfile(os.path.join(self.__window.themesDir, theme)):
                    themes.append({"caption": theme, "command": {"command": f"setTheme", "kwargs": {"theme": theme}}})
            self.App.updateMenu("themes", themes)

    def getCommand(self, name):
        return self.__window.pl.regCommands.get(name)
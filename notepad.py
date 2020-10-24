from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
import notepad_function
import cv2
import re
import pysyntax
import cppsyntax


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        global file_name_remove
        super(Window, self).__init__(parent)
        settings = QtCore.QSettings("MyCompany", "MyApp")
        # settings.clear()
        self.visible = 1
        self.currently_seleceted = ""
        self.bg = settings.value("background", "")
        self.color = settings.value("color", "")

        self.setMouseTracking(True)
        self.file_opened = settings.value('file_opened', [], str)
        self.colors_opened = settings.value('colors_opened', [], QtGui.QFont)
        print("before main")
        print(self.file_opened)
        print(self.colors_opened)
        i = 0
        while i != len(self.file_opened):
            print(i)
            if not os.path.exists(self.file_opened[i]):
                # self.file_opened.remove(self.file_opened[i])
                # self.colors_opened.remove(self.colors_opened[i])
                self.file_opened[i] = 0
                self.colors_opened[i] = 0
                i = i;
            else:
                i = i + 1

        try:
            file = open(str(settings.value('last_file', '')), 'r')
            file_name = settings.value('last_file', '')
            file_name_remove = file_name
        except FileNotFoundError:
            file_name = ""

        print("in main")
        print(self.file_opened)
        print(self.colors_opened)

        self.restoreGeometry(settings.value("geometry", self.saveGeometry()))
        self.titleName = "Notepad"
        self.currentPath = ""
        self.setWindowTitle(self.titleName)

        # self.tabs=QtWidgets.QTabWidget()
        # self.tab1=QtWidgets.QWidget()
        # # self.tab2=QtWidgets.QWidget()
        # self.push=QtWidgets.QPushButton("hello")
        # # self.push.move(10,10)
        # self.tabs.addTab(self.tab1,"tab1")
        # # self.tabs.addTab(self.tab2,"tab2")
        # self.tab1.layout=QtWidgets.QVBoxLayout(self)
        # self.tab1.layout.addWidget(self.push)

        # self.textEdit=QtWidgets.QTextEdit()
        # self.highlight = cppsyntax.PythonHighlighter(self.textEdit.document())
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.openMenu)
        self.listWidget.currentItemChanged.connect(self.print_info)
        # self.listWidget=myListWidget()
        self.listWidget.itemClicked.connect(self.Clicked)

        self.dict = {}
        self.item_in_list()
        self.layout = QtWidgets.QHBoxLayout(self)
        self.splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setStyleSheet("QWidget{color: " + str(self.color) + ";background-color:" + str(self.bg) + "}")
        # self.textEdit.setStyleSheet("QWidget{color: #ffffff}")
        # self.splitter1.addWidget(self.tabs)
        self.splitter1.addWidget(self.listWidget)
        self.splitter1.addWidget(self.textEdit)
        self.layout.addWidget(self.splitter1)
        # layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        fontWidth = QtGui.QFontMetrics(self.textEdit.currentCharFormat().font()).averageCharWidth();
        self.textEdit.setTabStopWidth(4 * fontWidth);
        self.textEdit.textChanged.connect(self.content_changed)
        self.setCentralWidget(self.splitter1)
        self.not_allowed_format = ['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG', 'gif', 'GIF']

        if file_name != "" and file_name != None:
            try:
                self.currentPath = file_name
                file_name = file_name.split('/')
                length = len(file_name)
                file_name, self.titleName = file_name[length - 1], file_name[length - 1]
                file = open(str(file_name), 'r')
                try:
                    text = file.read()
                    self.setWindowTitle(file_name)
                    if self.currentPath in self.file_opened:
                        index = self.file_opened.index(self.currentPath)
                        font = self.colors_opened[index]
                        self.textEdit.setFont(QtGui.QFont(font))
                        self.textEdit.setStyleSheet("QWidget{background-color: %s}" % font)
                        self.textEdit.setStyleSheet("QWidget{color: %s}" % font)
                        self.textEdit.setText(text)
                except UnicodeDecodeError:
                    pass
            except FileNotFoundError:
                index = self.file_opened.index(file_name_remove)
                self.file_opened.remove(file_name_remove)
                self.colors_opened.remove(self.colors_opened[index])

        # Create all the actions here

        # fileopen action
        openAction = QtWidgets.QAction("&Open File", self)
        openAction.setShortcut("Ctrl+O")
        openAction.setStatusTip('Open new File')
        openAction.triggered.connect(self.file_open)

        # savefile action
        saveAction = QtWidgets.QAction('&Save File', self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.setStatusTip('Save your file')
        saveAction.triggered.connect(self.file_save)

        # saveas action
        saveAsAction = QtWidgets.QAction('&Save As', self)
        saveAsAction.setShortcut('Ctrl+Shift+S')
        saveAsAction.setStatusTip('Save as')
        saveAsAction.triggered.connect(self.file_save_as)

        # newfile action
        newfileAction = QtWidgets.QAction('&New File', self)
        newfileAction.setShortcut('Ctrl+N')
        newfileAction.setStatusTip('Create new file')
        newfileAction.triggered.connect(self.file_new)

        # quit action
        quitAction = QtWidgets.QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit application')
        quitAction.triggered.connect(self.file_close)

        # backgroundcolor action
        backgroundColorAction = QtWidgets.QAction('&Background Theme', self)
        backgroundColorAction.setStatusTip('Change the background theme')
        backgroundColorAction.triggered.connect(self.color_picker)

        # fontcolor action
        fontColorAction = QtWidgets.QAction('&Font color', self)
        fontColorAction.setStatusTip('Change the font color')
        fontColorAction.triggered.connect(self.font_color)

        # fontstyle action
        fontStyleAction = QtWidgets.QAction('&Font style', self)
        fontStyleAction.setStatusTip('Change the font style')
        fontStyleAction.triggered.connect(self.font_style)

        # capitalize action
        capAction = QtWidgets.QAction('&Capitalize text', self)
        capAction.setStatusTip('Capitalize font')
        capAction.triggered.connect(self.font_cap)

        # uncapitalize action
        uncapAction = QtWidgets.QAction('&Unapitalize text', self)
        uncapAction.setStatusTip('Capitalize font')
        uncapAction.triggered.connect(self.font_uncap)

        # pythonsyntax action
        pythonSyntaxAction = QtWidgets.QAction('&Python', self)
        pythonSyntaxAction.setStatusTip('Select Python')
        pythonSyntaxAction.triggered.connect(self.select_python)

        # cppsyntax action
        cppSyntaxAction = QtWidgets.QAction('&C++', self)
        cppSyntaxAction.setStatusTip('Select C++')
        cppSyntaxAction.triggered.connect(self.select_cpp)

        # csyntax action
        cSyntaxAction = QtWidgets.QAction('&C', self)
        cSyntaxAction.setStatusTip('Select C')
        cSyntaxAction.triggered.connect(self.select_cpp)

        # history action
        historyAction = QtWidgets.QAction('&History', self)
        historyAction.setStatusTip('See list of opened files')
        historyAction.setShortcut('Ctrl+H')
        historyAction.triggered.connect(self.see_history)

        # run action
        runAction = QtWidgets.QAction('&Complie&run', self)
        runAction.triggered.connect(self.load)

        self.statusBar()
        # file=self.statusbar.addAction(openAction)
        # self.toolbar=self.addToolBar('Save')
        # self.tool.addAction(fontStyleAction)
        # self.toolbar.addAction(openAction)
        # self.toolbar.addAction(saveAction)
        # self.toolbar.addAction(saveAsAction)
        # self.toolbar.addAction(newfileAction)

        mainMenu = self.menuBar()

        # add all the actions related to file menu here
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.setToolTipsVisible(True)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addAction(newfileAction)
        fileMenu.addAction(quitAction)

        # add all the actiobs realted to edit menu here
        editMenu = mainMenu.addMenu('&Edit')
        editMenu.setToolTipsVisible(True)

        # all actions related to run program
        runMenu = mainMenu.addMenu('&Complie&run')
        runMenu.setToolTipsVisible(True)
        runMenu.addAction(runAction)

        # add all the actions realted to Menu menu here
        menuMenu = mainMenu.addMenu('&Menu')
        menuMenu.setToolTipsVisible(True)
        menuMenu.addAction(backgroundColorAction)
        menuMenu.addAction(fontColorAction)
        menuMenu.addAction(fontStyleAction)
        menuMenu.addAction(capAction)
        menuMenu.addAction(uncapAction)

        # add all the actions related to view menu here
        viewMenu = mainMenu.addMenu('&View')
        syntaxMenu = viewMenu.addMenu('&Syntax')
        syntaxMenu.addAction(pythonSyntaxAction)
        syntaxMenu.addAction(cppSyntaxAction)
        syntaxMenu.addAction(cSyntaxAction)
        viewMenu.addAction(historyAction)

        self.show()

    def print_info(self):
        self.currently_seleceted = self.listWidget.currentItem().text()

    def openMenu(self, position):
        menu = QtWidgets.QMenu('&Select', self)
        # p = mapFromGlobal(QCursor.pos());
        delete_file = QtWidgets.QAction(QtGui.QIcon('py.png'), '&Delete File', self)
        delete_file.setShortcut('Ctrl+D')
        delete_file.setStatusTip('Delete File')
        # print("current")
        print(self.currently_seleceted)
        name, format1 = self.currently_seleceted.split('.')
        if format1 == "txt":
            summarize = QtWidgets.QAction(QtGui.QIcon('py.png'), '&Delete File', self)
            # summarize.setShortcut('Ctrl+D')
            summarize.setStatusTip('Delete File')
            menu.addAction(
                '&Summarize',
                self.summarize
            )
        # print(list(self.dict.keys())[position])
        # menu.move(self.listWidget.currentRow())
        menu.move(position)
        delete_file.triggered.connect(self.file_delete)
        menu.addAction(
            '&Delete this file',
            self.file_delete
        )
        # menu.move(100,150)
        menu.show()

    def summarize(self):
        print("hello")

    def file_delete(self):
        # self.listWidget.ContentList.tekeItem(self.listWidget.currentRow())
        # self.listWidget.takeItem(list(self.dict.keys())[list(self.dict.values()).index(self.currently_seleceted)])
        choice = QtWidgets.QMessageBox.question(self, "Confirmation",
                                                "Are you sure you want to delete this file",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)

        if choice == QtWidgets.QMessageBox.Yes:

            # print(self.currently_seleceted)
            os.remove(list(self.dict.keys())[list(self.dict.values()).index(self.currently_seleceted)])
            item = self.listWidget.takeItem(self.listWidget.currentRow())
            item = None
            self.titleName = self.currently_seleceted
            self.setWindowTitle(self.titleName)
            self.currentPath = list(self.dict.keys())[list(self.dict.values()).index(self.currently_seleceted)]
        elif choice == QtWidgets.QMessageBox.Cancel:
            pass

    def Clicked(self, item):
        # print(list(self.dict.keys())[list(self.dict.values()).index(item.text())])
        file = open(list(self.dict.keys())[list(self.dict.values()).index(item.text())], 'r')
        with file:
            try:
                text = file.read()
                self.currentPath = list(self.dict.keys())[list(self.dict.values()).index(item.text())]
                if self.currentPath in self.file_opened:
                    index = self.file_opened.index(self.currentPath)
                    font = self.colors_opened[index]
                    print(index)
                    self.textEdit.setFont(QtGui.QFont(font))
                self.titleName = item.text()
                self.setWindowTitle(self.titleName)
                # print(type(text))
                self.textEdit.setText(text)
            except FileNotFoundError:
                pass

    def see_history(self):
        if self.visible == 0:
            self.visible = 1
            self.listWidget.show()
        else:
            self.visible = 0
            self.listWidget.hide()

    def item_in_list(self):
        for i in range(len(self.file_opened)):
            if self.file_opened[i] != 0:
                list_item = self.file_opened[i].split('/')
                length = len(list_item)
                list_item = list_item[length - 1]
                self.dict[self.file_opened[i]] = list_item
                self.listWidget.addItem(list_item)
        # self.listWidget.hide()

    def select_python(self):
        self.highlight = pysyntax.PythonHighlighter(self.textEdit.document())

    def select_cpp(self):
        self.highlight = cppsyntax.PythonHighlighter(self.textEdit.document())

    def content_changed(self):
        wordCount = self.textEdit.toPlainText()

        count = re.findall("[a-zA-Z,./<>?0-9!@#$%^&*()-+=''\"\"_]+", wordCount)
        wordCount = len(count)
        self.statusBar().showMessage(str(wordCount) + " words")

    def font_uncap(self):
        myFont = QtGui.QFont()
        myFont.setCapitalization(False)
        self.textEdit.setFont(myFont)

    def font_cap(self):
        myFont = QtGui.QFont()
        myFont.setCapitalization(True)
        self.textEdit.setFont(myFont)

    def font_style(self):
        font, ok = QtWidgets.QFontDialog.getFont()
        if ok:
            self.textEdit.setFont(font)

    def font_color(self):
        color = QtWidgets.QColorDialog.getColor()
        self.color = color.name()
        if self.bg != "":
            self.textEdit.setStyleSheet("QWidget{color: " + str(self.color) + ";background-color:" + str(self.bg) + "}")
        else:
            self.textEdit.setStyleSheet("QWidget{color: %s}" % self.color)

    def color_picker(self):
        color = QtWidgets.QColorDialog.getColor()
        self.bg = color.name()
        if self.color != "":
            self.textEdit.setStyleSheet("QWidget{color: " + str(self.color) + ";background-color:" + str(self.bg) + "}")
        else:
            self.textEdit.setStyleSheet("QWidget{background-color: %s}" % self.bg)

    def keyPressEvent(self, event):
        if event.key() == 66:
            myFont = QtGui.QFont()
            myFont.setBold(True)
            self.textEdit.setFont(myFont)
        if event.key() == 73:
            myFont = QtGui.QFont()
            myFont.setItalic(True)
            # myFont.setCapitalization(True)
            self.textEdit.setFont(myFont)

    def file_open(self):
        print("open")
        self.apply_settings()

        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        try:
            file = open(str(name[0]), 'r')
            with file:
                try:
                    text = file.read()
                    self.currentPath = name[0]
                    if self.currentPath in self.file_opened:
                        index = self.file_opened.index(self.currentPath)
                        font = self.colors_opened[index]
                        self.textEdit.setFont(QtGui.QFont(font))
                    file_name = str(name[0]).split('/')
                    length = len(file_name)
                    self.titleName = file_name[length - 1]
                    self.setWindowTitle(self.titleName)
                    # print(type(text))
                    self.textEdit.setText(text)
                    self.apply_settings()
                    if self.currentPath not in self.dict:
                        self.dict[self.currentPath] = self.titleName
                        self.listWidget.addItem(self.titleName)

                except UnicodeDecodeError:
                    o_name = name[0]
                    name = name[0].split('/')
                    length = len(name)
                    name = name[length - 1]
                    if name.split('.')[1] == 'pdf':
                        # w = PictureFlow()
                        # d = QtPoppler.Poppler.Document.load(o_name)
                        # d.setRenderHint(QtPoppler.Poppler.Document.Antialiasing and QtPoppler.Poppler.Document.TextAntialiasing)

                        # page = 0
                        # pages = d.numPages() - 1
                        # while page < pages:
                        #     page += 1
                        #     print (page)
                        #     w.addSlide(d.page(page).renderToImage())
                        # w.show()
                        pass
                    else:
                        img = cv2.imread(o_name)
                        cv2.imshow('image', img)

                    # label=QtWidgets.QLabel(self)
                    # pixmap=QtWidgets.QPixmap(name[0])
                    # label.setPixmap(pixmap)
                    # self.layout.addWidget(label)
                    # label.show()

                    # choice=QtWidgets.QMessageBox.question(self,"Oops!!",
                    #         "Could not support the file format",
                    #          QtWidgets.QMessageBox.Cancel)

                    # if choice==QtWidgets.QMessageBox.Cancel:
                    #     pass
        except FileNotFoundError:
            pass

    def file_save(self):
        if (os.path.exists(self.currentPath)):
            self.apply_settings()
            file = open(str(self.currentPath), 'w')
            text = self.textEdit.toPlainText()
            file.write(text)
            file.close()
        else:
            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
            path_split = str(name).split('/')
            length = len(path_split)
            file_name = path_split[length - 1]
            if notepad_function.allow_save(file_name) == False:
                choice = QtWidgets.QMessageBox.question(self, "Oops!!",
                                                        "Could not support the file format",
                                                        QtWidgets.QMessageBox.Cancel)

                if choice == QtWidgets.QMessageBox.Cancel:
                    pass
            else:
                try:
                    file = open(str(name[0]), 'w')
                    text = self.textEdit.toPlainText()
                    file.write(text)
                    file.close()
                    self.currentPath = name[0]

                    settings = QtCore.QSettings("MyCompany", "MyApp")
                    if self.currentPath != "" and self.currentPath != None:
                        if self.currentPath not in self.file_opened:
                            self.file_opened.append(self.currentPath)
                            settings.setValue('file_opened', self.file_opened)
                        index = self.file_opened.index(self.currentPath)
                        try:
                            self.colors_opened[index] = self.textEdit.font()
                            settings.setValue('colors_opened', self.colors_opened)
                        except IndexError:
                            self.colors_opened.append(self.textEdit.font())
                            settings.setValue('colo_property', self.colors_opened)
                    print("in save")
                    print(self.file_opened)
                    print(self.colors_opened)
                    file_name = str(name[0]).split('/')
                    length = len(file_name)
                    self.titleName = file_name[length - 1]
                    self.setWindowTitle(self.titleName)
                    if self.currentPath not in self.dict:
                        self.dict[self.currentPath] = self.titleName
                        self.listWidget.addItem(self.titleName)
                except FileNotFoundError:
                    pass

    def file_save_as(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self, '', '', '')
        path_split = str(name).split('/')
        length = len(path_split)
        file_name = path_split[length - 1]
        if not notepad_function.allow_save(file_name):
            choice = QtWidgets.QMessageBox.question(self, "Oops!!",
                                                    "Could not support the file format",
                                                    QtWidgets.QMessageBox.Cancel)

            if choice == QtWidgets.QMessageBox.Cancel:
                pass
        else:
            try:
                file = open(str(name[0]), 'w')
                text = self.textEdit.toPlainText()
                file.write(text)
                file.close()
                self.currentPath = name[0]
                file_name = str(name[0]).split('/')
                length = len(file_name)
                self.titleName = file_name[length - 1]
                self.setWindowTitle(self.titleName)
            except FileNotFoundError:
                pass

    def apply_settings(self):
        settings = QtCore.QSettings("MyCompany", "MyApp")
        if self.currentPath != "" and self.currentPath != None:
            if self.currentPath not in self.file_opened:
                self.file_opened.append(self.currentPath)
                settings.setValue('file_opened', self.file_opened)
            index = self.file_opened.index(self.currentPath)
            try:
                self.colors_opened[index] = self.textEdit.font()
                settings.setValue('colors_opened', self.colors_opened)
            except IndexError:
                self.colors_opened.append(self.textEdit.font())
                settings.setValue('colo_property', self.colors_opened)
        print("in applysettings")
        print(self.file_opened)
        print(self.colors_opened)
        return

    def file_new(self):
        settings = QtCore.QSettings("MyCompany", "MyApp")
        if self.currentPath != "":
            file = open(str(self.currentPath), 'r')
            text = self.textEdit.toPlainText()
            original_text = file.read()
            if original_text != text:
                choice = QtWidgets.QMessageBox.question(self, "Unsaved changes",
                                                        "Save changes to existing file beore opening new file",
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
                if choice == QtWidgets.QMessageBox.Yes:
                    # print("new")
                    self.apply_settings()
                    file = open(str(self.currentPath), 'w')
                    text = self.textEdit.toPlainText()
                    file.write(text)
                    file.close()
                    self.textEdit.setText("")
                    self.titleName = "Notepad"
                    self.setWindowTitle(self.titleName)
                    self.currentPath = ""
                elif choice == QtWidgets.QMessageBox.No:
                    print("new")
                    self.apply_settings()
                    self.textEdit.clear()
                    self.titleName = "Notepad"
                    self.setWindowTitle(self.titleName)
                    self.currentPath = ""
                else:
                    pass
            else:
                self.apply_settings()
                self.textEdit.clear()
                self.titleName = "Notepad"
                self.setWindowTitle(self.titleName)
                self.currentPath = ""
        else:
            self.file_save()

    def closeEvent(self, event):
        settings = QtCore.QSettings("MyCompany", "MyApp")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("background", self.bg)
        settings.setValue("color", self.color)
        print("close color")
        print(self.bg)
        print(self.color)
        print("close")
        if self.currentPath != "" and self.currentPath != None:
            if self.currentPath not in self.file_opened:
                self.file_opened.append(self.currentPath)
                settings.setValue('file_opened', self.file_opened)
            index = self.file_opened.index(self.currentPath)
            try:
                self.colors_opened[index] = self.textEdit.font()
                settings.setValue('colors_opened', self.colors_opened)
            except IndexError:
                self.colors_opened.append(self.textEdit.font())
                settings.setValue('colors_opened', self.colors_opened)
            settings.setValue('last_file', self.currentPath)
            print("in close")
            print(self.file_opened)
            print(self.colors_opened)
        try:
            file = open(str(self.currentPath), 'r')
            text = self.textEdit.toPlainText()
            original_text = file.read()
            if original_text != text and self.textEdit.toPlainText() != "":
                choice = QtWidgets.QMessageBox.question(self, "Unsaved changes",
                                                        "Save changes to new file beore closing",
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
                if choice == QtWidgets.QMessageBox.Yes:
                    file = open(str(self.currentPath), 'w')
                    text = self.textEdit.toPlainText()
                    file.write(text)
                    file.close()
                    event.accept()
                elif choice == QtWidgets.QMessageBox.No:
                    event.accept()
                else:
                    event.ignore()
        except FileNotFoundError:
            if self.textEdit.toPlainText() != "" and self.textEdit.toPlainText() != None:
                self.file_save()

    def file_close(self):
        choice = QtWidgets.QMessageBox.question(self, "Quit application",
                                                "Do you really want to exit?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def load(self):
        file = self.currentPath.split("/")
        titleName = file[len(file) - 1]
        # print(filename)
        a = titleName.split(".")
        # print(a[1])
        if a[1] == "c":
            os.system("gcc " + self.currentPath)
            os.system("a.exe")
        elif a[1] == "cpp":
            os.system("g++ " + self.currentPath)
            os.system("a.exe")
        elif a[1] == "java":
            os.system("javac " + self.currentPath)
            os.system("java " + a[0])
        else:
            os.system("python3 " + self.currentPath)


def run():
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())


run()

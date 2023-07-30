import sys
import configparser
import sqlite3
import shutil
from PySide6.QtGui import QPixmap, QDesktopServices
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QTableWidgetItem, QHBoxLayout, QWidget, QCheckBox, QFileSystemModel, QAbstractItemView, QMessageBox
from ui_filemove_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        #상단콤보박스 셋팅
        self.setDbpathCmb()

        # slot 연결
        self.ui.startCmb.currentIndexChanged.connect(self.setStartTableWidget)
        self.ui.destCmb.currentIndexChanged.connect(self.setDestTreeView)
        self.ui.moveFileBtn.clicked.connect(self.moveFileData)
        self.ui.startSearchEdit.textChanged.connect(self.filterStartTable)

        # 시작테이블 width 셋팅
        self.ui.startTable.setColumnWidth(0, 60)
        self.ui.startTable.setColumnWidth(1, 80)
        self.ui.startTable.setColumnWidth(2, 200)
        self.ui.startTable.horizontalHeader().setStretchLastSection(True)

  
    # 시작지, 목적지 콤보박스 셋팅(config.ini)
    def setDbpathCmb(self):
        config = configparser.ConfigParser()
        config.read('config.ini', encoding="UTF-8")
        dbpaths = config.get("PATH", "dbpath").split('\n')
        self.ui.startCmb.addItem("선택해주세요")
        self.ui.destCmb.addItem("선택해주세요")
        for path in dbpaths:
            self.ui.startCmb.addItem(path)
            self.ui.destCmb.addItem(path)

    # 시작테이블 검색(필터)
    def filterStartTable(self, filter_text):
        for i in range(self.ui.startTable.rowCount()):
            for j in range(self.ui.startTable.columnCount()):
                if(j > 1):
                    item = self.ui.startTable.item(i, j)
                    match = filter_text.lower() not in item.text().lower()
                    self.ui.startTable.setRowHidden(i, match)
                    if not match:
                        break

    # 시작테이블 데이터 셋팅(sqlite)
    def setStartTableWidget(self):#스레드로 돌면 좋을텐데..
        self.startDbpath = str(self.ui.startCmb.currentText()) + "deepdark.db"
        self.startCon = sqlite3.connect(self.startDbpath)
        result = self.startCon.cursor().execute("SELECT uid, thumb, hashTag, filepath FROM Files;")
        self.ui.startTable.setRowCount(0) #테이블 초기화
        for row_num, row_data in enumerate(result):
            self.ui.startTable.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                item = str(col_data)
                if(col_num == 0): #체크박스
                    item = QTableWidgetItem(item)
                    item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled )
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.ui.startTable.setItem(row_num, col_num, item)
                elif(col_num == 1): #썸네일
                    item = self.getImageLabel(col_data)
                    self.ui.startTable.setCellWidget(row_num, col_num, item)
                else:
                    if(item == "None"):
                        item = ""
                    self.ui.startTable.setItem(row_num, col_num, QTableWidgetItem(item))
        self.ui.startTable.verticalHeader().setDefaultSectionSize(80)

    # 시작테이블 Blob 셋팅
    def getImageLabel(self, image):
        imageLabel = QLabel()
        imageLabel.setText("")
        imageLabel.setScaledContents(True)
        pixmap = QPixmap()
        pixmap.loadFromData(image, 'jpg')
        imageLabel.setPixmap(pixmap)
        return imageLabel
        
    def setDestTreeView(self):
        rootPath = self.ui.destCmb.currentText()
        self.model_file_system = QFileSystemModel()
        self.model_file_system.setRootPath(rootPath)
        self.model_file_system.setReadOnly(True)

        self.ui.destTree.setModel(self.model_file_system)
        self.ui.destTree.setRootIndex(self.model_file_system.index(rootPath))
        self.ui.destTree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.destTree.doubleClicked.connect(lambda index : self.item_double_clicked(index))
        
        #self.ui.destTree.setDragEnabled(True)
        self.ui.destTree.setColumnWidth(0, 300)

    def item_double_clicked(self, index):
        if(self.model_file_system.fileInfo(index).isFile()):
            print(self.model_file_system.filePath(index))
            QDesktopServices.openUrl(QUrl("file:///"+str(self.model_file_system.filePath(index)))); #파일실행

    def moveFileData(self):
        startPath = self.ui.startCmb.currentText()
        destTreeIdx = self.ui.destTree.currentIndex()
        destPath = self.model_file_system.filePath(destTreeIdx)
        #destDbPath = str(self.ui.destCmb.currentText()) + "deepdark.db"
        #destCon = self.destCon = sqlite3.connect(destDbPath)

        if(self.model_file_system.fileInfo(destTreeIdx).isDir()):
            for row in range(self.ui.startTable.rowCount()):
                if self.ui.startTable.item(row, 0).checkState() == Qt.CheckState.Checked:
                    startFile = startPath + self.ui.startTable.item(row, 3).text()
                    print('start: {0}, dest: {1}', startFile, destPath) 
                    shutil.move(startFile, destPath)

                #성공시 DB 변경
                #destCon
                #쿼리
                #self.startCon 상위에서 이미 연결
                #쿼리

                #동작시 progress바 나오게
        else:
            QMessageBox.warning(self,'경고','폴더만 가능합니다.\n폴더를 선택 후 이동해주세요.')



if __name__ == "__main__":
    app = QApplication(sys.argv)


    window = MainWindow()
    window.show()

    sys.exit(app.exec())
import sys, os
import configparser
import subprocess

from PySide6.QtGui import QPixmap, QDesktopServices, QAction
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QTableWidgetItem, QFileSystemModel, QAbstractItemView, QMessageBox
from ui_filemove_ui import Ui_MainWindow
from FileMoveThread import FileMoveThread
from StartTableThread import StartTableThread


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
        self.ui.moveFileLogBtn.clicked.connect(self.moveFileLogShell)

        # 출발지테이블 width 셋팅
        self.ui.startTable.setColumnWidth(0, 15) #체크박스
        self.ui.startTable.setColumnWidth(1, 40) #번호
        self.ui.startTable.setColumnWidth(2, 80) #썸네일
        self.ui.startTable.setColumnWidth(3, 30) #평점
        self.ui.startTable.setColumnWidth(4, 150)#태그
        self.ui.startTable.horizontalHeader().setStretchLastSection(True)#경로
        self.ui.startTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.startTable.cellDoubleClicked.connect(self.startTableCelldoubleclicked)
        self.ui.startTable.cellClicked.connect(self.startTableCellclicked)
        if not self.ui.startTable.isSortingEnabled():
            self.ui.startTable.setSortingEnabled(True)
        self.ui.startTable.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        startTableMenu1 = QAction("전체체크" , self.ui.startTable)
        startTableMenu2 = QAction("전체체크해제" , self.ui.startTable)
        startTableMenu3 = QAction("새로고침" , self.ui.startTable)
        startTableMenu1.triggered.connect(self.startTableMenu1_act)
        startTableMenu2.triggered.connect(self.startTableMenu2_act)
        startTableMenu3.triggered.connect(self.setStartTableWidget)
        self.ui.startTable.addAction(startTableMenu1)
        self.ui.startTable.addAction(startTableMenu2)
        self.ui.startTable.addAction(startTableMenu3)

        # 파일이동 프로그레스바
        self.ui.moveFilePrgs.setMaximum(100)

        # 목적지 Treeview 셋팅
        self.ui.destTree.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        destTreeMenu1 = QAction("현재폴더열기" , self.ui.destTree)
        destTreeMenu1.triggered.connect(self.destTreeMenu1_act)
        self.ui.destTree.addAction(destTreeMenu1)

    def moveFileLogShell(self):
        current_script_path = os.path.abspath(__file__)
        current_folder = os.path.dirname(current_script_path)
        logPath = current_folder + "\log\logfile.log"
        subprocess.run(['start', '', logPath], shell=True)
        # command = "get-content '"+logPath+"' -wait -tail 10"  # 실행할 PowerShell 명령어
        # subprocess.run(["powershell", "-Command", command], creationflags=subprocess.CREATE_NEW_CONSOLE)
        #result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)

    def startTableMenu1_act(self):
        for row in range(self.ui.startTable.rowCount()):
            for col in range(self.ui.startTable.columnCount()):
                if(col == 0):
                    if(self.ui.startTable.isRowHidden(row) == False):
                        self.ui.startTable.item(row, col).setCheckState(Qt.CheckState.Checked)
                        self.ui.startTable.item(row, col).setBackground(Qt.GlobalColor.yellow)

    def startTableMenu2_act(self):
        for row in range(self.ui.startTable.rowCount()):
            for col in range(self.ui.startTable.columnCount()):
                if(col == 0):
                    self.ui.startTable.item(row, col).setCheckState(Qt.CheckState.Unchecked)
                    self.ui.startTable.item(row, col).setBackground(Qt.GlobalColor.white)

    def destTreeMenu1_act(self):#현재폴더열기
        destTreeIdx = self.ui.destTree.currentIndex()
        destPath = self.model_file_system.filePath(destTreeIdx)
        if(self.model_file_system.fileInfo(destTreeIdx).isDir()):
            os.startfile(destPath) #폴더열기
        else:
            subprocess.run(['start', '', destPath], shell=True)

    def startTableCellclicked(self, row, col):
        if(col == 0):
            if self.ui.startTable.item(row, col).checkState() == Qt.CheckState.Checked:
                self.ui.startTable.item(row, col).setCheckState(Qt.CheckState.Unchecked)
                self.ui.startTable.item(row, col).setBackground(Qt.GlobalColor.white)
            else:
                self.ui.startTable.item(row, col).setCheckState(Qt.CheckState.Checked)
                self.ui.startTable.item(row, col).setBackground(Qt.GlobalColor.yellow)

    def startTableCelldoubleclicked(self, row, col):
        fileName = self.ui.startTable.item(row, 5).text()
        if(col == 2):
            video_file_path = str(self.ui.startCmb.currentText())+fileName
            subprocess.run(['start', '', video_file_path], shell=True)
        elif(col == 5):
            fileNameIdx = fileName.rfind('\\')
            if(fileNameIdx != -1):
               fileName = fileName[:fileNameIdx]
            os.startfile(str(self.ui.startCmb.currentText())+ fileName) #폴더열기
        

    # 출발지, 목적지 콤보박스 셋팅(config.ini)
    def setDbpathCmb(self):
        config = configparser.ConfigParser()
        config.read('config.ini', encoding="UTF-8")
        dbpaths = config.get("PATH", "dbpath").split('\n')
        self.ui.startCmb.addItem("선택해주세요")
        self.ui.destCmb.addItem("선택해주세요")
        for path in dbpaths:
            self.ui.startCmb.addItem(path)
            self.ui.destCmb.addItem(path)

    # 출발지 테이블 검색(필터)
    def filterStartTable(self, filter_text):
        for i in range(self.ui.startTable.rowCount()):
            for j in range(self.ui.startTable.columnCount()):
                if(j > 2):
                    item = self.ui.startTable.item(i, j)
                    match = filter_text.lower() not in item.text().lower()
                    self.ui.startTable.setRowHidden(i, match)
                    if not match:
                        break

    # 출발지 테이블 데이터 셋팅(sqlite)
    def setStartTableWidget(self):
        self.startDbpath = str(self.ui.startCmb.currentText()) + "deepdark.db"
        self.ui.startTable.setRowCount(0) #테이블 초기화
        self.ui.startTable.verticalHeader().setDefaultSectionSize(80)

        self.ui.startTable.setSortingEnabled(False)

        self.startExt = StartTableThread(self.startDbpath)
        self.startExt.startable_ui_insert_row_signal.connect(self.setStartTableInsertRow)
        self.startExt.startable_ui_signal.connect(self.setStartTableUIDraw)
        self.startExt.start()
        self.startExt.quit()
    
    def setStartTableInsertRow(self, totRow, percent):
        if(percent != 999):
            self.ui.startTable.insertRow(totRow)
            self.ui.moveFilePrgs.setValue(percent)
        else:
            self.ui.moveFilePrgs.setValue(0)
            self.filterStartTable(self.ui.startSearchEdit.text())
            if not self.ui.startTable.isSortingEnabled():
                self.ui.startTable.setSortingEnabled(True)
        
    def setStartTableUIDraw(self, col_data, row_num, col_num):
        dbStr = str(col_data)
        if(col_num == 0): #체크박스
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.ui.startTable.setItem(row_num, col_num, item)
        elif(col_num == 1): #번호
            item = QTableWidgetItem()
            item.setData(Qt.ItemDataRole.DisplayRole, int(col_data))
            self.ui.startTable.setItem(row_num, col_num, item)
            self.ui.startTable.item(row_num, col_num).setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
        elif(col_num == 2): #썸네일
            item = self.getImageLabel(col_data)
            self.ui.startTable.setCellWidget(row_num, col_num, item)
        else:
            if(dbStr == "None"):
                dbStr = ""
            self.ui.startTable.setItem(row_num, col_num, QTableWidgetItem(dbStr))
            if(col_num == 3):
                self.ui.startTable.item(row_num, col_num).setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)

    # 출발지 테이블 Blob 셋팅
    def getImageLabel(self, image):
        imageLabel = QLabel()
        imageLabel.setText("")
        imageLabel.setScaledContents(True)
        pixmap = QPixmap()
        pixmap.loadFromData(image, 'jpg')
        imageLabel.setPixmap(pixmap)
        return imageLabel
    
    # 목적지 트리뷰 셋팅
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
            destPath = str(self.model_file_system.filePath(index))
            subprocess.run(['start', '', destPath], shell=True)

    def moveFileData(self):
        startPath = self.ui.startCmb.currentText()
        destTreeIdx = self.ui.destTree.currentIndex()
        destPath = self.model_file_system.filePath(destTreeIdx)
        dbPath = {
              "startDbPath":self.startDbpath
            , "destDbPath":str(self.ui.destCmb.currentText()) + "deepdark.db"
        }
        filePaths = []
        if(self.model_file_system.fileInfo(destTreeIdx).isDir()):
            for row in range(self.ui.startTable.rowCount()):
                if self.ui.startTable.item(row, 0).checkState() == Qt.CheckState.Checked:
                    destOnlyFileName = os.path.split(self.ui.startTable.item(row, 5).text())[1]
                    startDbFilePath = self.ui.startTable.item(row, 5).text() #start DB PK
                    destDbFilePath = destPath.replace("/", "\\").replace(self.ui.destCmb.currentText(), "") + "\\" + destOnlyFileName #dest DB PK
                    if(startDbFilePath == destDbFilePath and dbPath["startDbPath"] == dbPath["destDbPath"]):
                        QMessageBox.warning(self,'경고','동일한 폴더입니다.\n다른폴더를 선택해주세요.')
                        return False
                    filePaths.append({  "startDbFilePath":startDbFilePath
                                    , "destDbFilePath":destDbFilePath
                                    , "startFullFilePath":startPath + self.ui.startTable.item(row, 5).text() #파일이동용 FullPath
                                    , "destFullFilePath":destPath + "/" + destOnlyFileName}) #파일이동용 FullPath
            reply = QMessageBox.question(self, 'Message', '(준비완료) 파일이동을 동작하시겠습니까?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.ext = FileMoveThread(dbPath, filePaths)
                self.ext.filemove_percent_signal.connect(self.on_count_change)
                self.ext.filemove_status_signal.connect(self.on_status_change)
                self.ext.start()
                self.ext.quit()
        else:
            QMessageBox.warning(self,'경고','폴더만 가능합니다.\n폴더를 선택 후 이동해주세요.')

    def on_count_change(self, value):
        self.ui.moveFilePrgs.setValue(value)
    def on_status_change(self, value):
        if(value == "다른폴더완료" or value == "동일폴더완료"): #파일이동 완료 시 선택된 row 삭제
            del_row = []
            for row in range(self.ui.startTable.rowCount()):
                    if self.ui.startTable.item(row, 0).checkState() == Qt.CheckState.Checked:
                        if(value == "다른폴더완료"):
                            del_row.append(row)
                        else:
                            destTreeIdx = self.ui.destTree.currentIndex()
                            destPath = self.model_file_system.filePath(destTreeIdx)
                            oriText = self.ui.startTable.item(row, 5).text()
                            oriTextIdx = oriText.rfind('\\')
                            if(oriTextIdx != -1):
                                oriText = oriText[oriTextIdx+1:]
                            newText = destPath.replace("/", "\\").replace(self.ui.destCmb.currentText(), "") + "\\" + oriText
                            self.ui.startTable.item(row, 5).setText(newText)
                        self.ui.startTable.item(row, 0).setCheckState(Qt.CheckState.Unchecked)
                        self.ui.startTable.item(row, 0).setBackground(Qt.GlobalColor.white)
                        self.filterStartTable(self.ui.startSearchEdit.text())
            if(value == "다른폴더완료"):
                del_row.reverse()
                for row in del_row:
                    self.ui.startTable.removeRow(row)
        self.ui.moveStatusLabel.setText(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)


    window = MainWindow()
    window.show()

    sys.exit(app.exec())
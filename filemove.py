import sys, os
import configparser
import subprocess

from PySide6.QtGui import QPixmap, QDesktopServices, QAction
from PySide6.QtCore import Qt, QUrl, QDir, QModelIndex
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QTableWidgetItem, QFileSystemModel, QAbstractItemView, QMessageBox, QTreeView, QInputDialog
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
        self.model = QFileSystemModel()
        self.ui.destTree.setModel(self.model)
        self.ui.destTree.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        destTreeMenu1 = QAction("현재폴더열기" , self.ui.destTree)
        destTreeMenu2 = QAction("ROOT폴더생성" , self.ui.destTree)
        destTreeMenu3 = QAction("하위폴더생성" , self.ui.destTree)
        destTreeMenu4 = QAction("폴더삭제" , self.ui.destTree)
        destTreeMenu5 = QAction("폴더이름변경" , self.ui.destTree)
        destSeparator1 = QAction("----------------" , self.ui.destTree)
        destSeparator2 = QAction("----------------" , self.ui.destTree)
        destTreeMenu1.triggered.connect(self.destTreeMenu1_act)
        destTreeMenu2.triggered.connect(self.destTreeMenu2_act)
        destTreeMenu3.triggered.connect(self.destTreeMenu3_act)
        destTreeMenu4.triggered.connect(self.destTreeMenu4_act)
        destTreeMenu5.triggered.connect(self.destTreeMenu5_act)
        destTreeMenu2.setShortcut("Ctrl+R")   # ROOT폴더생성: Ctrl+R
        destTreeMenu3.setShortcut("Ctrl+N")   # 하위폴더생성: Ctrl+N
        destTreeMenu4.setShortcut("Del")      # 폴더삭제: Del
        destTreeMenu5.setShortcut("F2")       # 폴더이름변경: F2
        self.ui.destTree.addAction(destTreeMenu1)
        self.ui.destTree.addAction(destSeparator1)
        self.ui.destTree.addAction(destTreeMenu2)
        self.ui.destTree.addAction(destTreeMenu3)
        self.ui.destTree.addAction(destSeparator2)
        self.ui.destTree.addAction(destTreeMenu4)
        self.ui.destTree.addAction(destTreeMenu5)
    
    def moveFileLogShell(self):
        current_folder = os.getcwd()
        logPath = current_folder + "\log"
        #subprocess.run(['start', '', logPath], shell=True)
        os.startfile(logPath)

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
    def destTreeMenu2_act(self):
        #ROOT폴더 생성
        parent_path = self.ui.destCmb.currentText()
        folder_name, ok = QInputDialog.getText(self, "Rename Folder", "Enter new folder name:", text='')
        if folder_name:
            new_folder_path = os.path.join(parent_path, folder_name)
            try:
                os.mkdir(new_folder_path)  # Create folder
            except Exception as e:
               QMessageBox.warning(self,'경고',f"Error creating folder: {e}")
    
    def destTreeMenu3_act(self):
        #하위폴더 생성
        destTreeIdxs = self.ui.destTree.selectedIndexes()
        if not destTreeIdxs:
            QMessageBox.warning(self,'경고','폴더를 선택해주세요.')
            return
        destTreeIdx = destTreeIdxs[0]
        parent_path = self.model_file_system.filePath(destTreeIdx)
        folder_name, ok = QInputDialog.getText(self, "Rename Folder", "Enter new folder name:", text='')
        if folder_name:
            new_folder_path = os.path.join(parent_path, folder_name)
            try:
                os.mkdir(new_folder_path)  # Create folder
            except Exception as e:
                QMessageBox.warning(self,'경고',f"Error creating folder: {e}")
    def destTreeMenu4_act(self):
        #폴더삭제
        destTreeIdxs = self.ui.destTree.selectedIndexes()
        if not destTreeIdxs:
            QMessageBox.warning(self,'경고','폴더를 선택해주세요.')
            return
        
        destTreeIdx = destTreeIdxs[0]
        folder_path = self.model_file_system.filePath(destTreeIdx)

        if not os.path.isdir(folder_path):
            QMessageBox.warning(self,'경고','폴더가 아닙니다.')
            return
        try:
            os.rmdir(folder_path)  # Remove folder (only empty folders)
        except Exception as e:
                QMessageBox.warning(self,'경고','폴더에 파일들이 있습니다.')
    def destTreeMenu5_act(self):
        #폴더이름변경
        # """ Override to handle folder name change after F2 key or double click """
        destTreeIdxs = self.ui.destTree.selectedIndexes()
        if not destTreeIdxs:
            QMessageBox.warning(self,'경고','폴더를 선택해주세요.')
            return
        destTreeIdx = destTreeIdxs[0]
        old_path = self.model.filePath(destTreeIdx)
        if not os.path.isdir(old_path):
            QMessageBox.warning(self,'경고','폴더가 아닙니다.')
            return
        old_name = self.model.fileName(destTreeIdx)
        new_name, ok = QInputDialog.getText(self, "Rename Folder", "Enter new folder name:", text=old_name)
        if ok and new_name and new_name != old_name:
            #"""Rename folder logic"""
           
            parent_dir = os.path.dirname(old_path)
            new_folder_path = os.path.join(parent_dir, new_name)
            try:
                # Rename the folder using os.rename or QDir.rename
                os.rename(old_path, new_folder_path)
            except Exception as e:
                QMessageBox.warning(self,'경고',f"Error renaming folder: {e}") 

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
                    filePaths.append({ "row" : row
                                    , "startDbFilePath":startDbFilePath
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
    def on_status_change(self, value, paramRow, paramPath):
        if(value == "다른폴더완료"): #파일이동 완료 시 선택된 row 삭제
            del_row = []
            for row in range(self.ui.startTable.rowCount()):
                if self.ui.startTable.item(row, 0).checkState() == Qt.CheckState.Checked:
                    del_row.append(row)
                    self.ui.startTable.item(row, 0).setCheckState(Qt.CheckState.Unchecked)
                    self.ui.startTable.item(row, 0).setBackground(Qt.GlobalColor.white)
            del_row.reverse()
            for row in del_row:
                self.ui.startTable.removeRow(row)
        if(value == "다른폴더완료" or value == "동일폴더완료"):
            self.filterStartTable(self.ui.startSearchEdit.text())

        if(value == "동일폴더개별"):
            self.ui.startTable.item(paramRow, 5).setText(paramPath)
            self.ui.startTable.item(paramRow, 0).setCheckState(Qt.CheckState.Unchecked)
            self.ui.startTable.item(paramRow, 0).setBackground(Qt.GlobalColor.white)
        else:
            self.ui.moveStatusLabel.setText(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)


    window = MainWindow()
    window.show()

    sys.exit(app.exec())
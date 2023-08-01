import sys, os
import configparser
import sqlite3
import shutil
from PySide6.QtGui import QPixmap, QDesktopServices
from PySide6.QtCore import Qt, QUrl, QThread, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QTableWidgetItem, QHBoxLayout, QWidget, QCheckBox, QFileSystemModel, QAbstractItemView, QMessageBox, QProgressBar
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

        # 파일이동 프로그레스바
        self.ui.moveFilePrgs.setMaximum(100)

  
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

        dbPath = {
              "startDbPath":self.startDbpath
            , "destDbPath":str(self.ui.destCmb.currentText()) + "deepdark.db"
        }
        
        filePaths = []
        if(self.model_file_system.fileInfo(destTreeIdx).isDir()):
            for row in range(self.ui.startTable.rowCount()):
                if self.ui.startTable.item(row, 0).checkState() == Qt.CheckState.Checked:
                    destOnlyFileName = os.path.split(self.ui.startTable.item(row, 3).text())[1];
                    filePaths.append({  "startDbFilePath":self.ui.startTable.item(row, 3).text() #start DB PK
                                      , "destDbFilePath":destPath.replace("/", "\\").replace(self.ui.destCmb.currentText(), "") + "\\" + destOnlyFileName #dest DB PK
                                      , "startFullFilePath":startPath + self.ui.startTable.item(row, 3).text() #파일이동용 FullPath
                                      , "destFullFilePath":destPath + "/" + destOnlyFileName}) #파일이동용 FullPath

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
                            oriText = self.ui.startTable.item(row, 3).text()
                            newText = destPath.replace("/", "\\").replace(self.ui.destCmb.currentText(), "") + oriText[oriText.rindex('\\'):]
                            self.ui.startTable.item(row, 3).setText(newText)
                        self.ui.startTable.item(row, 0).setCheckState(Qt.CheckState.Unchecked)
            if(value == "다른폴더완료"):
                for row in del_row:
                    self.ui.startTable.removeRow(row)
        self.ui.moveStatusLabel.setText(value)

class FileMoveThread(QThread):
    filemove_percent_signal= Signal(int)
    filemove_status_signal= Signal(str)

    def __init__(self, dbPath, filePaths):
        super().__init__()
        self.dbPath = dbPath
        self.filePaths = filePaths
        self.file_tot_size = 0
        self.temp_file_size = 0

    def run(self):
        try:
            isSameDbPath = self.dbPath['startDbPath'] == self.dbPath['destDbPath']

            self.startDbCon = sqlite3.connect(self.dbPath['startDbPath'])
            if(isSameDbPath == False):
                self.destDbCon = sqlite3.connect(self.dbPath['destDbPath'])

            for filepath in self.filePaths:
                self.file_tot_size += os.stat(filepath['startFullFilePath']).st_size

            for filepath in self.filePaths:
                self.my_callback_status(filepath['startDbFilePath']) #현재이동중인 파일명 UI 표시
                self.copyfileobj(filepath['startFullFilePath'], filepath['destFullFilePath'], self.my_callback) #파일복사
                os.remove(filepath['startFullFilePath']) #기존파일삭제
                self.setDbModify(filepath['startDbFilePath'], filepath['destDbFilePath'], filepath['destFullFilePath'], isSameDbPath) #DB변경
            if(isSameDbPath == False):
                self.filemove_status_signal.emit("다른폴더완료")
            else:
                self.filemove_status_signal.emit("동일폴더완료")
        except Exception as e:
            self.filemove_status_signal.emit("실패")
            #print(e)
        finally:
            self.startDbCon.close()
            if(isSameDbPath == False):
                self.destDbCon.close()

    def my_callback(self, temp_file_size):
        percent = int(temp_file_size/self.file_tot_size*100)
        self.filemove_percent_signal.emit(percent)
    def my_callback_status(self, statusValue):
        self.filemove_status_signal.emit(statusValue)

    def copyfileobj(self, fsrc, fdst, callback, length=16*1024):
        with open(fsrc, "rb") as fr, open(fdst, "wb") as fw:
            while True:
                buff = fr.read(length)
                if not buff:
                    break
                fw.write(buff)
                self.temp_file_size += len(buff)
                callback(self.temp_file_size)
    
    def setDbModify(self, sFilePath, dFilePath, dFileFullPath, isSameDbPath):
        try:
            if(isSameDbPath == False):#dbpath가 다르면 insert 
                sCon = self.startDbCon.cursor()
                dCon = self.destDbCon.cursor()
                # DB 복사
                result = sCon.execute("SELECT '"+dFilePath+"' as filepath, dvdid, stars, dbDate, fileDate, playDate, hashTag, Thumb, count, trash, dvdIsNotExists FROM Files WHERE filepath='"+sFilePath+"';")
                dCon.execute("INSERT INTO Files (filepath, dvdid, stars, dbDate, fileDate, playDate, hashTag, Thumb, count, trash, dvdIsNotExists) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", result.fetchone())
                result = sCon.execute("SELECT '"+dFilePath+"' as filepath, start, length, thumb FROM Favorites WHERE filepath='"+sFilePath+"';")
                dCon.executemany("INSERT INTO Favorites (filepath, start, length, thumb) VALUES(?, ?, ?, ?)", result.fetchall())
                # 기존 DB삭제
                sCon.execute("DELETE FROM Files WHERE filepath='"+sFilePath+"';")
                sCon.execute("DELETE FROM Favorites WHERE filepath='"+sFilePath+"';")
            else:#dbpath가 같으면 update
                sCon = self.startDbCon.cursor()
                sCon.execute("UPDATE Files SET filepath = '"+dFilePath+"' WHERE filepath='"+sFilePath+"'")
                sCon.execute("UPDATE Favorites SET filepath = '"+dFilePath+"' WHERE filepath='"+sFilePath+"'")

            self.startDbCon.commit()
            if(isSameDbPath == False):
                self.destDbCon.commit()
            
        except sqlite3.Error as er:
            self.startDbCon.rollback()
            if(isSameDbPath == False):
                self.destDbCon.rollback()
            #os.remove(dFileFullPath) 삭제는 위험
            print(self,'에러','SQLite error : %s' % (' '.join(er.args)))
        

if __name__ == "__main__":
    app = QApplication(sys.argv)


    window = MainWindow()
    window.show()

    sys.exit(app.exec())
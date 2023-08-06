import os
import logging.handlers
import shutil
import sqlite3
from PySide6.QtCore import QThread, Signal

class FileMoveThread(QThread):
    filemove_percent_signal= Signal(int)
    filemove_status_signal= Signal(str, int, str)

    def __init__(self, dbPath, filePaths):
        super().__init__()
        self.dbPath = dbPath
        self.filePaths = filePaths
        self.file_tot_size = 0
        self.temp_file_size = 0

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        timedfilehandler = logging.handlers.TimedRotatingFileHandler(filename='./log/logfile.log', when='midnight', interval=1, encoding='utf-8')
        timedfilehandler.setFormatter(formatter)
        timedfilehandler.suffix = "%Y%m%d"
        self.logger.addHandler(timedfilehandler)

    def run(self):
        try:
            isSameDbPath = self.dbPath['startDbPath'] == self.dbPath['destDbPath']
            isSameDrive = self.dbPath['startDbPath'][:self.dbPath['startDbPath'].find("\\")] == self.dbPath['destDbPath'][:self.dbPath['destDbPath'].find("\\")]

            self.startDbCon = sqlite3.connect(self.dbPath['startDbPath'])
            if(isSameDbPath == False):
                self.destDbCon = sqlite3.connect(self.dbPath['destDbPath'])

            for filepath in self.filePaths:
                self.file_tot_size += os.stat(filepath['startFullFilePath']).st_size

            for filepath in self.filePaths:                
                #--------------------목적지 폴더에 중복파일이 있으면 (숫자)로 중복회피------------------------
                dest_folder = filepath['destFullFilePath'][:filepath['destFullFilePath'].rfind("/")]
                src_file = filepath['destDbFilePath']
                base_folder = os.path.dirname(src_file)
                base_name = os.path.basename(src_file)
                file_name, file_extension = os.path.splitext(base_name)
                dest_full_file = os.path.join(dest_folder, base_name)
                dest_db_file = os.path.join(base_folder, base_name)
                
                counter = 1
                while os.path.exists(dest_full_file):
                    new_file_name = f"{file_name} ({counter}){file_extension}"
                    dest_full_file = os.path.join(dest_folder, new_file_name)
                    dest_db_file = os.path.join(base_folder, new_file_name)
                    counter += 1
                    
                filepath['destDbFilePath'] = dest_db_file
                filepath['destFullFilePath'] = dest_full_file
                #--------------------목적지 폴더에 중복파일이 있으면 (숫자)로 중복회피 End------------------------

                self.my_callback_status(filepath['startDbFilePath'], 0, "") #현재이동중인 파일명 UI 표시
                if(isSameDrive == False):
                    self.copyfileobj(filepath['startFullFilePath'], filepath['destFullFilePath'], self.my_callback) #파일복사
                    os.remove(filepath['startFullFilePath']) #기존파일삭제
                else:
                    self.movefileobj(filepath['startFullFilePath'], filepath['destFullFilePath'], self.my_callback) #파일이동

                self.setDbModify(filepath['startDbFilePath'], filepath['destDbFilePath'], filepath['startFullFilePath'], filepath['destFullFilePath'], isSameDbPath) #DB변경
                
                if(isSameDbPath == True):
                    self.my_callback_status("동일폴더개별", int(filepath["row"]), filepath['destDbFilePath'])
                    
            if(isSameDbPath == False):
                self.my_callback_status("다른폴더완료", 0, "")
            else:
                self.my_callback_status("동일폴더완료", 0, "")
        except Exception as e:
            self.my_callback_status("실패", 0, "")
            print(str(e) + "\n출발지파일:" + filepath['startFullFilePath'] + "\n목적지파일:" + filepath['destFullFilePath'])
            self.logger.error(str(e) + "\n출발지파일:" + filepath['startFullFilePath'] + "\n목적지파일:" + filepath['destFullFilePath'])
        finally:
            self.startDbCon.close()
            if(isSameDbPath == False):
                self.destDbCon.close()

    def my_callback(self, temp_file_size):
        percent = int(temp_file_size/self.file_tot_size*100)
        self.filemove_percent_signal.emit(percent)
    def my_callback_status(self, statusValue, paramRow, paramPath):
        self.filemove_status_signal.emit(statusValue, paramRow, paramPath)

    def copyfileobj(self, fsrc, fdst, callback, length=16*1024):
        with open(fsrc, "rb") as fr, open(fdst, "wb") as fw:
            while True:
                buff = fr.read(length)
                if not buff:
                    break
                fw.write(buff)
                self.temp_file_size += len(buff)
                callback(self.temp_file_size)
    
    def movefileobj(self, fsrc, fdst, callback):
        shutil.move(fsrc, fdst)
        self.temp_file_size += os.stat(fdst).st_size
        callback(self.temp_file_size)
    
    def setDbModify(self, sFilePath, dFilePath, sFileFullPath, dFileFullPath, isSameDbPath):
        try:
            if(isSameDbPath == False):#dbpath가 다르면 insert 
                sCon = self.startDbCon.cursor()
                dCon = self.destDbCon.cursor()
                # DB 복사
                result = sCon.execute("""SELECT "%s" as filepath, dvdid, stars, dbDate, fileDate, playDate, hashTag, Thumb, count, trash, dvdIsNotExists FROM Files WHERE filepath = ?;""" % dFilePath, (sFilePath,))
                dCon.execute("""INSERT INTO Files (filepath, dvdid, stars, dbDate, fileDate, playDate, hashTag, Thumb, count, trash, dvdIsNotExists) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", result.fetchone())
                result = sCon.execute("""SELECT "%s" as filepath, start, length, thumb FROM Favorites WHERE filepath = ?;""" % dFilePath, (sFilePath,))
                dCon.executemany("""INSERT INTO Favorites (filepath, start, length, thumb) VALUES(?, ?, ?, ?)""", result.fetchall())
                # 기존 DB삭제
                sCon.execute("""DELETE FROM Files WHERE filepath = ?;""", (sFilePath,))
                sCon.execute("""DELETE FROM Favorites WHERE filepath = ?;""", (sFilePath,))
            else:#dbpath가 같으면 update
                sCon = self.startDbCon.cursor()
                sCon.execute("""UPDATE Files SET filepath = ? WHERE filepath = ?""", (dFilePath, sFilePath))
                sCon.execute("""UPDATE Favorites SET filepath = ? WHERE filepath = ?""", (dFilePath, sFilePath))

            self.startDbCon.commit()
            if(isSameDbPath == False):
                self.destDbCon.commit()
            
        except sqlite3.Error as er:
            self.startDbCon.rollback()
            if(isSameDbPath == False):
                self.destDbCon.rollback()
            #os.remove(dFileFullPath) 삭제는 위험
            self.logger.error('SQLite error : %s' % (' '.join(er.args)) + "\n출발지파일:" + sFileFullPath + "\n목적지파일:" + dFileFullPath)
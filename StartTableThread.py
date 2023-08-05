import sqlite3

from PySide6.QtCore import QThread, Signal

class StartTableThread(QThread):
    startable_ui_insert_row_signal= Signal(int, int)
    startable_ui_signal= Signal(object, int, int)


    def __init__(self, dbPath):
        super().__init__()
        self.dbPath = dbPath

    def run(self):
        print(self.dbPath)
        self.startCon = sqlite3.connect(self.dbPath)
        con = self.startCon.cursor()
        
        # 총갯수 구함
        result = con.execute("SELECT count(uid) FROM Files;")
        totRow = result.fetchone()[0]

        result = con.execute("SELECT '', uid, thumb, stars, hashTag, filepath FROM Files;")
        for row_num, row_data in enumerate(result):
            percent = int((row_num+1)/totRow*100)
            self.startable_ui_insert_row_signal.emit(row_num, percent)
            for col_num, col_data in enumerate(row_data):
                self.startable_ui_signal.emit(col_data, row_num, col_num)
        self.startCon.close()

        self.startable_ui_insert_row_signal.emit(0, 999)

    
        
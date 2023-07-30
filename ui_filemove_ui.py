# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_filemove.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHeaderView,
    QLayout, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTableWidget, QTableWidgetItem, QTreeView, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1090, 602)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetFixedSize)
        self.startTable = QTableWidget(self.centralwidget)
        if (self.startTable.columnCount() < 4):
            self.startTable.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.startTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.startTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.startTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.startTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.startTable.setObjectName(u"startTable")
        self.startTable.setColumnCount(4)

        self.gridLayout.addWidget(self.startTable, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 0, 1, 3, 1)

        self.startSearchEdit = QLineEdit(self.centralwidget)
        self.startSearchEdit.setObjectName(u"startSearchEdit")

        self.gridLayout.addWidget(self.startSearchEdit, 1, 0, 1, 1)

        self.startCmb = QComboBox(self.centralwidget)
        self.startCmb.setObjectName(u"startCmb")

        self.gridLayout.addWidget(self.startCmb, 0, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.destCmb = QComboBox(self.centralwidget)
        self.destCmb.setObjectName(u"destCmb")

        self.verticalLayout.addWidget(self.destCmb)

        self.destTree = QTreeView(self.centralwidget)
        self.destTree.setObjectName(u"destTree")

        self.verticalLayout.addWidget(self.destTree)

        self.moveFileBtn = QPushButton(self.centralwidget)
        self.moveFileBtn.setObjectName(u"moveFileBtn")

        self.verticalLayout.addWidget(self.moveFileBtn)


        self.gridLayout.addLayout(self.verticalLayout, 0, 2, 3, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1090, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c\uc815\ub9ac\uae30", None))
        ___qtablewidgetitem = self.startTable.horizontalHeaderItem(1)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"\uc378\ub124\uc77c", None));
        ___qtablewidgetitem1 = self.startTable.horizontalHeaderItem(2)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\uacbd\ub85c", None));
        ___qtablewidgetitem2 = self.startTable.horizontalHeaderItem(3)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"\ud0dc\uadf8", None));
        self.moveFileBtn.setText(QCoreApplication.translate("MainWindow", u"\ud30c\uc77c\uc774\ub3d9", None))
    # retranslateUi


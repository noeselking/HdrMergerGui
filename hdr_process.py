#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import \
    QApplication, QMainWindow, QFileDialog, QTreeWidgetItem

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QFileInfo

from hdr_merger_thread import HdrMergerThread
from get_exif_info import getExifInfo


class HdrDialog(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui/gui.ui", self)
        self.initUi()
        self.setWindowTitle("HdrMergerGui")

    def initUi(self):
        # connect all QT signals
        self.addFilesPushButton.clicked.connect(self.addFilesClicked)
        self.removeFilesPushButton.clicked.connect(self.removeFilesClicked)
        self.mergeToHdrPushButton.clicked.connect(self.mergeToHdrClicked)
        self.fileTreeWidget.itemSelectionChanged.connect(self.itemSelectionChanged)

        # initialize some variables
        self.mergerThread = None
        self.pauseUpdate = False


    def addFilesClicked(self):
        newFiles = QFileDialog.getOpenFileNames(self, "Please select the files to add to stack", "",
                                                "Images (*.png *.jpg *.bmp)")
        for file in newFiles[0]:
            entries = self.fileTreeWidget.findItems(file, Qt.MatchCaseSensitive)
            for entry in entries:
                self.fileTreeWidget.takeItem(self.fileTreeWidget.row(entry))
            item = QTreeWidgetItem()

            fileInfo = QFileInfo(file)
            fileInfo.fileName()

            exif = getExifInfo(file)

            item.setText(0, fileInfo.fileName())
            item.setText(1, exif.exposureTime)
            item.setText(2, exif.aperture)
            item.setText(3, exif.ISO)
            item.setText(4, fileInfo.absolutePath())
            self.fileTreeWidget.insertTopLevelItem(self.fileTreeWidget.topLevelItemCount(), item)

    def removeFilesClicked(self):
        self.pauseUpdate = True
        selected = self.fileTreeWidget.selectedItems()
        for entry in selected:
            self.fileTreeWidget.takeTopLevelItem(self.fileTreeWidget.indexOfTopLevelItem(entry))
        self.previewLabel.clear()
        self.pauseUpdate = False

    def itemSelectionChanged(self):
        if not self.pauseUpdate:
            selected = self.fileTreeWidget.selectedItems()
            if len(selected) < 1:
                self.previewLabel.clear()
            else:
                image = QPixmap()
                imagePath = selected[0].text(4) + "/" + selected[0].text(0)
                image.load(imagePath)
                widgetWidth = self.previewLabel.width()
                self.previewLabel.setPixmap(image.scaledToWidth(widgetWidth))

    def mergeToHdrClicked(self):
        if self.fileTreeWidget.topLevelItemCount() == 0:
            self.statusBar().showMessage("No files in stack.", 5000)
            return

        files = []

        for index in range(self.fileTreeWidget.topLevelItemCount()):
            item = self.fileTreeWidget.topLevelItem(index)
            imagePath = item.text(4) + "/" + item.text(0)
            files.append(imagePath)

        filename = QFileDialog.getSaveFileName(self, "Save OpenEXR File", "", "OpenEXR Images (*.exr)")
        if filename[1] == "":
            self.statusBar().showMessage("Save aborted.", 5000)
            return

        self.mergerThread = HdrMergerThread(files, filename[0])
        self.mergerThread.newOutputLine.connect(self.addOutputLine)

        self.clearOutput()
        self.addOutputLine("<b>Starting merge of images:</b>")
        self.mergerThread.start()

        def enableButton():
            self.mergeToHdrPushButton.setEnabled(True)
            self.addOutputLine("<b>Merge finished.</b>")

        self.mergerThread.finished.connect(enableButton)

        self.mergeToHdrPushButton.setEnabled(False)

    def addOutputLine(self, text):
        self.textEdit.insertHtml("{}<br>".format(text))

    def clearOutput(self):
        self.textEdit.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon("icon/icon.png"))

    dialog = HdrDialog()
    dialog.show()

    sys.exit(app.exec_())

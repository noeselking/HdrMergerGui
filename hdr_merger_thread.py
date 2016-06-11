#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess, shlex
from PyQt5.QtCore import QThread, pyqtSignal

class HdrMergerThread(QThread):
    """Class to merge a stack of LDR image files to HDR

    The merge of the LDR files will be done in this thread, so you are
    free to do other stuff in the meantime.

    This thread will emit the qt signal "finished" as soon as the merge
    operation is done.

    The thread also emits the qt signal "newOutputLine" each time there
    is a line of message available.
    """
    newOutputLine = pyqtSignal(str)

    def __init__(self, stack, outputFile):
        super().__init__()
        self.stack = stack
        assert len(self.stack) > 0
        self.outputFile = outputFile

    def run(self):
        filesString = ""
        for file in self.stack:
            filesString = filesString + " " + shlex.quote(file)

        createHdrCommandLine = "pfsinme {} | pfshdrcalibrate - v | pfsoutexr {}"

        process = subprocess.Popen(createHdrCommandLine.format(filesString, shlex.quote(self.outputFile)), shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while process.poll() is None:
            text = process.stderr.readline().decode("utf8")
            self.newOutputLine.emit(text)

        text = process.stdout.read().decode("utf8")
        self.newOutputLine.emit(text)
        text = process.stderr.read().decode("utf8")
        self.newOutputLine.emit(text)
"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# Python
import os
from time import localtime, strftime

# PyQt
from PySide6.QtCore import QMessageLogContext, QtMsgType

# PackY
from packy.views.main_window import MainWindow


# -----------------------------------------------------------------------------
def currTime() -> str:
    return strftime("%Y-%m-%d %H:%M:%S", localtime())


# -----------------------------------------------------------------------------
def msgTypeToStr(type: QtMsgType):
    match type:
        case QtMsgType.QtDebugMsg:
            return "DEBUG"
        case QtMsgType.QtInfoMsg:
            return "INFO"
        case QtMsgType.QtWarningMsg:
            return "WARNING"
        case QtMsgType.QtCriticalMsg:
            return "CRITICAL"
        case QtMsgType.QtFatalMsg:
            return "FATAL"
        case _:
            raise Exception("[msgTypeToStr] Message type not recognized.")


# -----------------------------------------------------------------------------
def htmlFontColor(type: QtMsgType) -> str:
    match type:
        case QtMsgType.QtInfoMsg:
            return '<font color="black">'
        case QtMsgType.QtWarningMsg:
            return '<font color="yellow">'
        case QtMsgType.QtCriticalMsg:
            return '<font color="red">'
        case _:
            raise Exception("[htmlFontColor] Message type not recognized.")


# -----------------------------------------------------------------------------
def fileLogFormat(type: QtMsgType, ctx: QMessageLogContext, msg: str):
    return f"[{currTime()}][{msgTypeToStr(type)}][{ctx.function}] {msg}"


# -----------------------------------------------------------------------------
def guiLogFormat(type: QtMsgType, ctx: QMessageLogContext, msg: str):
    return f"[{currTime()}] {msg}"


# -----------------------------------------------------------------------------
def writeLogInFile(type: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
    if hasattr(MainWindow, "log_file_path"):
        os.makedirs(os.path.dirname(MainWindow.log_file_path), exist_ok=True)
        with open(MainWindow.log_file_path, "a") as log_file:
            log_file.write(fileLogFormat(type, ctx, msg) + "\n")


# -----------------------------------------------------------------------------
def printLogInGUI(type: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
    if hasattr(MainWindow, "log_panel"):
        html_font_color: str = htmlFontColor(type)
        html: str = html_font_color + guiLogFormat(type, ctx, msg) + "</font>"
        MainWindow.log_panel.appendHtml(html)

def printLogInConsole(type: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
    print(guiLogFormat(type, ctx, msg))  # noqa: T201


# -----------------------------------------------------------------------------
def messageHandler(type: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
    writeLogInFile(type, ctx, msg)
    printLogInConsole(type, ctx, msg)

    if type in {QtMsgType.QtInfoMsg, QtMsgType.QtWarningMsg, QtMsgType.QtCriticalMsg}:
        printLogInGUI(type, ctx, msg)

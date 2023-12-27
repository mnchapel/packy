"""
author: Marie-Neige Chapel
"""

# Python
import os
from time import localtime, strftime
from typing import Self

# PyQt
from PyQt6.QtCore import QMessageLogContext, QtMsgType

# PackY
from view.main_window import MainWindow

# -------------------------------------------------------------------------
def currTime() -> str:
	return strftime("%Y-%m-%d %H:%M:%S", localtime())

# -------------------------------------------------------------------------
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

# -------------------------------------------------------------------------
def styleSheet(type: QtMsgType) -> str:
	match type:
		case QtMsgType.QtInfoMsg:
			return "QPlainTextEdit {color: black}"
		case QtMsgType.QtWarningMsg:
			return "QPlainTextEdit {color: yellow}"
		case QtMsgType.QtCriticalMsg:
			return "QPlainTextEdit {color: red}"
		case _:
			raise Exception("[styleSheet] Message type not recognized.")

# -------------------------------------------------------------------------
def fileLogFormat(type: QtMsgType, ctx: QMessageLogContext, msg: str):
	return f"[{currTime()}][{msgTypeToStr(type)}][{ctx.function}] {msg}"

# -------------------------------------------------------------------------
def guiLogFormat(type: QtMsgType, ctx: QMessageLogContext, msg: str):
	return f"[{currTime()}] {msg}"

# -------------------------------------------------------------------------
def writeLogInFile(type: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
	if hasattr(MainWindow, "log_file_path"):
		os.makedirs(os.path.dirname(MainWindow.log_file_path), exist_ok=True)
		with open(MainWindow.log_file_path, "a") as log_file:
			log_file.write(fileLogFormat(type, ctx, msg) + "\n")

# -------------------------------------------------------------------------
def printLogInGUI(type: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
	if hasattr(MainWindow, "log_panel"):
		MainWindow.log_panel.setStyleSheet(styleSheet(type))
		MainWindow.log_panel.appendPlainText(guiLogFormat(type, ctx, msg))

# -------------------------------------------------------------------------
def messageHandler(type: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
	writeLogInFile(type, ctx, msg)

	if type in {QtMsgType.QtInfoMsg, QtMsgType.QtWarningMsg, QtMsgType.QtCriticalMsg}:
		printLogInGUI(type, ctx, msg)

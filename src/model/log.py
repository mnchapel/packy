"""
author: Marie-Neige Chapel
"""

# Python
from os import write
import os
from time import localtime, strftime

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
def formatLog(type: QtMsgType, ctx: QMessageLogContext, msg: str):
	return f"[{currTime()}][{ctx.function}] {msgTypeToStr(type)}: {msg}"

# -------------------------------------------------------------------------
def writeLogInFile(type: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
	if hasattr(MainWindow, "log_file_path"):
		os.makedirs(os.path.dirname(MainWindow.log_file_path), exist_ok=True)
		with open(MainWindow.log_file_path, "a+") as log_file:
			log_file.write(formatLog(type, ctx, msg))

# -------------------------------------------------------------------------
def printLogInView(type: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
	if hasattr(MainWindow, "log_panel"):
		MainWindow.log_panel.appendPlainText(formatLog(type, ctx, msg))

# -------------------------------------------------------------------------
def messageHandler(type: QtMsgType, ctx: QMessageLogContext, msg: str) -> None:
	writeLogInFile(type, ctx, msg)
	printLogInView(type, ctx, msg)

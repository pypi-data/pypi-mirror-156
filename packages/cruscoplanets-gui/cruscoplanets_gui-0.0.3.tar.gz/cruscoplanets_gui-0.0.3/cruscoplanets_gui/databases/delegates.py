#    This file is part of Cruscoplanets GUI.
#
#   Cruscoplanets GUI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Cruscoplanets GUI is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Cruscoplanets GUI.  If not, see <http://www.gnu.org/licenses/>.
from PyQt5.QtWidgets import QLineEdit, QWidget, QMainWindow, QHBoxLayout, QDateTimeEdit, QComboBox, QCheckBox, QGridLayout, QTableView, QMessageBox, QStyledItemDelegate, QLabel, QStyle, QProxyStyle
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QDate, QTime, QDateTime
from PyQt5.QtGui import QColor, QPalette, QPen
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from ..main_window_widgets import location_searcher
import cruscoplanets.cmdline
import os.path
from .. import config


class Delegate:

	updated = pyqtSignal()

	def __init__(self):
		self._row = None
		self._column = None
		
	def setRow(self, index: int):
		self._row = index
		
	def setColumn(self, index: int):
		self._column = index
		

class LocationDatum(location_searcher.LocationSearcher, Delegate):
	
	def __init__(self):
		super().__init__()
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.locationChosen.connect(self.updated.emit)
		
	def value(self):
		return self.selectedId


class IdLabel(QWidget, Delegate):

	def __init__(self, text):
		super().__init__()
		self.label = QLabel(text)
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.label)
		self.setLayout(layout)
		
	def value(self):
		return int(self.label.text())
		


class LineEdit(QWidget, Delegate):

	def __init__(self):
		super().__init__()
		self.lineEdit = QLineEdit()
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.lineEdit)
		self.setLayout(layout)
		self.lineEdit.textChanged.connect(self.updated.emit)
	
	def text(self):
		return self.lineEdit.text()
	
	def value(self):
		return self.lineEdit.text()
	
	def setText(self, value):
		self.lineEdit.setText(value)


class SexComboBox(QWidget, Delegate):

	def __init__(self):
		super().__init__()
		self._combobox = QComboBox()
		self.addItem(self.tr("male"))
		self.addItem(self.tr("female"))
		self.addItem(self.tr("undefined"))
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self._combobox)
		self.setLayout(layout)
		self._combobox.currentIndexChanged.connect(self.updated.emit)
		
	def addItem(self, value):
		self._combobox.addItem(value)
		
	def value(self):
		index = self._combobox.currentIndex()
		if index == 2:
			index = - 1
		return index
		
	def setCurrentIndex(self, sex_int):
		index = sex_int
		if index == -1:
			index = 2
		self._combobox.setCurrentIndex(index)


class TimeTypeComboBox(QComboBox):

	def __init__(self):
		super().__init__()
		self.addItem(self.tr("local_time"))
		self.addItem(self.tr("utc_time"))

	def setValue(self, value):
		if type(value) == str:
			value = True if value == 'l' else False
		if value == True:
			self.setCurrentIndex(0)
		elif value == False:
			self.setCurrentIndex(1)
			
	def currentValue(self):
		if self.currentIndex() == 0:
			return 'l'
		else:
			return 'u'


class DatetimeSetterError(Exception):

	def __init__(self):
		super().__init__()
	
	def __str__(self):
		return "The value 'now' can not be stored in the database as datetimestring."
		
		
class DatetimeSetter(QWidget, Delegate):

	def __init__(self):
		super().__init__()

		self.timeType = TimeTypeComboBox()
		self.datetime = QDateTimeEdit()
		self.datetime.setCalendarPopup(True)
		self.datetime.setDisplayFormat("yyyy/MM/dd hh:mm:ss")
		self.timeUnknown = QCheckBox(self.tr("unknown_time"))
		
		layout = QHBoxLayout()
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.timeType)
		layout.addWidget(self.datetime)
		layout.addWidget(self.timeUnknown)
		self.setLayout(layout)
		self.timeType.currentIndexChanged.connect(self.updated.emit)
		self.datetime.dateTimeChanged.connect(self.updated.emit)
		self.timeUnknown.clicked.connect(self.updated.emit)

	def setDatetimestring(self, dtstring):
		if dtstring == 'now':
			raise DatetimeSetterError
		
		is_time_local, is_time_known, year, month, day, hour, minute, second = cruscoplanets.cmdline.parseDatetimeString(dtstring)
		if hour == None:
			hour = 12
		if minute == None:
			minute = 0
		if second == None:
			second = 0
		date = QDate(year, month, day)
		time = QTime(hour, minute, second)
		self.timeType.setValue(is_time_local)
		self.datetime.setDateTime(QDateTime(date, time))
		self.timeUnknown.setChecked(not is_time_known)

	def value(self):
		return self.datetimeString()
	
	def datetimeString(self):
		ret_str = self.timeType.currentValue()
		ret_str += "%04d-%02d-%02d"%(self.datetime.date().year(), self.datetime.date().month(), self.datetime.date().day())
		unknown_time_char = '!' if self.timeUnknown.isChecked() else '-'
		ret_str += unknown_time_char
		ret_str += "%02d-%02d-%02d"%(self.datetime.time().hour(), self.datetime.time().minute(), self.datetime.time().second())
		return ret_str


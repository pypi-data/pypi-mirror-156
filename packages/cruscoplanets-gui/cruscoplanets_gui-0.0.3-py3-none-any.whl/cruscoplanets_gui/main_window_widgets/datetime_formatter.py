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
from PyQt5.QtWidgets import QWidget, QDateEdit, QTimeEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QRadioButton, QCheckBox, QSpinBox
from PyQt5.QtCore import QDate, QTime, pyqtSignal, Qt


class TimeOptions(QWidget):

	optionsChanged = pyqtSignal()
	
	def __init__(self):
		super().__init__()
		
		buttonslayout = QGridLayout()
		self.localTimeButton = QRadioButton(self.tr('local time'), self)
		self.localTimeButton.setChecked(True)
		self.UTCTimeButton = QRadioButton(self.tr('UTC time'), self)
		buttonslayout.addWidget(self.localTimeButton, 0, 0)
		buttonslayout.addWidget(self.UTCTimeButton, 1, 0)
		self.unknownTimeButton = QCheckBox(self.tr('unknown time'), self)
		buttonslayout.addWidget(self.unknownTimeButton, 0, 1)
		
		self.localTimeButton.toggled.connect(self.optionsChanged.emit)
		self.UTCTimeButton.toggled.connect(self.optionsChanged.emit)
		self.unknownTimeButton.stateChanged.connect(self.optionsChanged.emit)
		self.setLayout(buttonslayout)
	
	@property
	def timeType(self):
		return 'l' if self.localTimeButton.isChecked() else 'u'
	
	@property
	def unknownTimeChar(self):
		return '!' if self.unknownTimeButton.isChecked() else '-'
		

class CarryingSpinBox(QSpinBox):

	ACCEPTED_KEYS = (Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9, Qt.Key_Backspace, Qt.Key_Delete)

	carry = pyqtSignal(int)
	
	def __init__(self, maxValue, minValue, suffix):
		super().__init__(maximum = maxValue, minimum = minValue)
		self.setSuffix(suffix)
		self.setWrapping(True)
		self._oldValue = self.value()
		self.valueChanged.connect(self._adjustValue)

	@property
	def maximumDigitsAllowed(self):
		return len(str(self.maximum()-1))

	def valueFromText(self, text):
		digits = filter(lambda char: char.isdigit(), text)
		value = ''.join(digits)
		return int(value)
	
	def textFromValue(self, value):
		return "%02d"%value

	def _adjustValue(self):
		if self._oldValue == self.maximum() and self.value() == self.minimum():
			self.carry.emit(1)
		elif self._oldValue == self.minimum() and self.value() == self.maximum():
			self.carry.emit(-1)
		self._oldValue = self.value()
		
			
	def keyPressEvent(self, event):
		self._oldValue = int((self.maximum()-self.minimum())/2)#so we avoid carrying
		super().keyPressEvent(event) #datetime doesn't change
		
		if len(self.cleanText()) > self.maximumDigitsAllowed:#this could happen if the user continuously inserts 0 chars
			self.setValue(0)
			
	def _acceptCarry(self, carry: int):
		self.setValue(self.value() + carry)
		
		
class TimeSpinBox(CarryingSpinBox):

	def __init__(self, maxvalue, suffix):
		super().__init__(maxvalue, 0, suffix)


class TimeFormatter(QWidget):

	dateCarry = pyqtSignal(int)
	timeChanged = pyqtSignal()

	def __init__(self, mytime: QTime = QTime.currentTime()):
		super().__init__()
		layout = QHBoxLayout()
		layout.setSpacing(0)
		self.hoursWidget = TimeSpinBox(23, 'h')
		self.hoursWidget.setValue(mytime.hour())
		self.minutesWidget = TimeSpinBox(59, 'm')
		self.minutesWidget.setValue(mytime.minute())
		self.secondsWidget = TimeSpinBox(59, 's')
		self.secondsWidget.setValue(mytime.second())

		self.secondsWidget.carry.connect(lambda unit: self.minutesWidget._acceptCarry(unit))
		self.minutesWidget.carry.connect(lambda unit: self.hoursWidget._acceptCarry(unit))
		self.hoursWidget.carry.connect(lambda unit: self.dateCarry.emit(unit))
		
		self.secondsWidget.valueChanged.connect(lambda: self.timeChanged.emit())
		self.minutesWidget.valueChanged.connect(lambda: self.timeChanged.emit())
		self.hoursWidget.valueChanged.connect(lambda: self.timeChanged.emit())
		
		layout.addWidget(self.hoursWidget)
		layout.addWidget(self.minutesWidget)
		layout.addWidget(self.secondsWidget)
		self.setLayout(layout)

	@property
	def values(self):
		return (self.hoursWidget.value(), self.minutesWidget.value(), self.secondsWidget.value())
		
	def setTime(self, hours, minutes, seconds):
		self.hoursWidget.setValue(hours)
		self.minutesWidget.setValue(minutes)
		self.secondsWidget.setValue(seconds)
		
		
class DaySpinBox(CarryingSpinBox):

	DAYS_FOR_MONTHS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

	def __init__(self):
		super().__init__(31, 1, 'd')
		
	def _adaptToYearAndMonth(self, isLeap: bool, month: int):
		month %= 12
		new_maximum = self.__class__.DAYS_FOR_MONTHS[month-1]
		if month == 2 and isLeap:
			new_maximum = self.__class__.DAYS_FOR_MONTHS[month-1]+1
		self._oldValue = int((new_maximum-self.minimum())/2)#in this way we avoid carrying
		if self.value() > new_maximum:
			self.setValue(new_maximum)
		self.setMaximum(new_maximum)

	def setToMaximum(self, month_value):
		"""sets the day to the maximum value allowed for the month. Useful where month has negative carry"""
		self.setValue(self.__class__.DAYS_FOR_MONTHS[month_value-1])
		
		
class MonthSpinBox(CarryingSpinBox):

	adaptDay = pyqtSignal(int)

	def __init__(self):
		super().__init__(12, 1, 'm')
		
	def _acceptCarry(self, unit):
		super()._acceptCarry(unit)
		if unit == -1:
			self.adaptDay.emit(self.value())
		
		
class YearSpinBox(CarryingSpinBox):

	def __init__(self):
		super().__init__(10000, 0, 'y')
	
	def isLeap(self):
		value = self.value()
		return (value % 4 == 0) and ((value % 100 != 0) or (value % 400) == 0)
		

class DateFormatter(QWidget):

	dateChanged = pyqtSignal()

	def __init__(self, mydate: QDate = QDate.currentDate()):
		super().__init__()
		layout = QHBoxLayout()
		layout.setSpacing(0)
		self.yearsWidget = YearSpinBox()
		self.yearsWidget.setValue(mydate.year())
		self.monthsWidget = MonthSpinBox()
		self.monthsWidget.setValue(mydate.month())
		self.daysWidget = DaySpinBox()
		self.daysWidget.setValue(mydate.day())
		self.daysWidget._adaptToYearAndMonth(self.yearsWidget.isLeap(), self.monthsWidget.value())

		self.daysWidget.carry.connect(lambda unit: self.monthsWidget._acceptCarry(unit))
		self.monthsWidget.carry.connect(lambda unit: self.yearsWidget._acceptCarry(unit))
		
		self.yearsWidget.valueChanged.connect(lambda year: self.daysWidget._adaptToYearAndMonth(self.yearsWidget.isLeap(), self.monthsWidget.value()))
		self.monthsWidget.valueChanged.connect(lambda month: self.daysWidget._adaptToYearAndMonth(self.yearsWidget.isLeap(), month))
		self.monthsWidget.adaptDay.connect(lambda value: self.daysWidget.setToMaximum(value))
		
		self.yearsWidget.valueChanged.connect(lambda: self.dateChanged.emit())
		self.monthsWidget.valueChanged.connect(lambda: self.dateChanged.emit())
		self.daysWidget.valueChanged.connect(lambda: self.dateChanged.emit())
		
		layout.addWidget(self.yearsWidget)
		layout.addWidget(self.monthsWidget)
		layout.addWidget(self.daysWidget)
		self.setLayout(layout)
	
	def _carryOnDate(self, carry):
		self.daysWidget.setValue(self.daysWidget.value() + carry)
		
	def values(self):
		return (self.yearsWidget.value(), self.monthsWidget.value(), self.daysWidget.value())
	
	def setDate(self, year, month, day):
		self.yearsWidget.setValue(year)
		self.monthsWidget.setValue(month)
		self.daysWidget.setValue(day)


class DateTimeFormatter(QWidget):

	datetimeChanged = pyqtSignal(str)

	def __init__(self, mydate: QDate = QDate.currentDate(), mytime: QTime = QTime.currentTime()):
		super().__init__()
		firstlayout = QVBoxLayout()

		datetimelayout = QHBoxLayout()
		self.dateWidget = DateFormatter(mydate)
		self.dateWidget.dateChanged.connect(self._onDateTimeChanged)
		datetimelayout.addWidget(self.dateWidget)
		self.timeWidget = TimeFormatter(mytime)
		datetimelayout.addWidget(self.timeWidget)
		firstlayout.addLayout(datetimelayout)
		self.timeWidget.dateCarry.connect(lambda unit: self.dateWidget._carryOnDate(unit))
		self.timeWidget.timeChanged.connect(self._onDateTimeChanged)
		
		self.timeOptionsWidget = TimeOptions()
		self.timeOptionsWidget.optionsChanged.connect(self._onDateTimeChanged)
		firstlayout.addWidget(self.timeOptionsWidget)
		self.setLayout(firstlayout)

	def _onDateTimeChanged(self):
		self.datetimeChanged.emit(self.dateTimeString())

	def dateTimeString(self):
		timetype = self.timeOptionsWidget.timeType
		ret_str = timetype + '%04d-%02d-%02d'%(self.dateWidget.values())
		unknown_hour_char = self.timeOptionsWidget.unknownTimeChar
		ret_str += unknown_hour_char
		ret_str += '%02d-%02d-%02d'%(self.timeWidget.values)
		return ret_str
	
	def setDateTime(self, event):
		if event.cruscoplanetsString[0] == 'u':
			self.dateWidget.setDate(event.utcdatetime.year, event.utcdatetime.month, event.utcdatetime.day)
			self.timeWidget.setTime(event.utcdatetime.hour, event.utcdatetime.minute, event.utcdatetime.second)
			self.timeOptionsWidget.UTCTimeButton.setChecked(True)
		else:
			self.dateWidget.setDate(event.localdatetime.year, event.localdatetime.month, event.localdatetime.day)
			self.timeWidget.setTime(event.localdatetime.hour, event.localdatetime.minute, event.localdatetime.second)
			self.timeOptionsWidget.localTimeButton.setChecked(True)
		if event.isTimeUnknown:
			self.timeOptionsWidget.unknownTimeButton.setChecked(True)
		else:
			self.timeOptionsWidget.unknownTimeButton.setChecked(False)

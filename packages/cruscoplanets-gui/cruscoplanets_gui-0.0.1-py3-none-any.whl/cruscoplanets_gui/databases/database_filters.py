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
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc

		
class FilterError(Exception):

	def __init__(self, message):
		super().__init__()
		
	def __str__(self):
		return self.message
		

class Filter:

	STARTS_BY = 0
	ENDS_BY = 1
	EQUALS = 2
	DIFFERENT_FROM = 3
	LESS_THAN = 4
	GREATER_THAN = 5
	LESS_OR_EQUAL = 6
	GREATER_OR_EQUAL = 7
	
	def __init__(self, column, relation: int, control_value):
		self.column = column#this can be a column index or name
		self.relation = relation
		self.controlValue = control_value
		
	def __repr__(self):
		ret_str = "%s: value "%self.column
		if self.relation == self.__class__.STARTS_BY:
			ret_str += 'starts by '
		elif self.relation == self.__class__.ENDS_BY:
			ret_str += 'ends by '
		elif self.relation == self.__class__.EQUALS:
			ret_str += '== '
		elif self.relation == self.__class__.DIFFERENT_FROM:
			ret_str += '!= '
		elif self.relation == self.__class__.LESS_THAN:
			ret_str += '< '
		elif self.relation == self.__class__.GREATER_THAN:
			ret_str += '> '
		elif self.relation == self.__class__.LESS_OR_EQUAL:
			ret_str += '<= '
		elif self.relation == self.__class__.GREATER_OR_EQUAL:
			ret_str += '>= '
		ret_str += "%r"%self.controlValue
		return ret_str
		
	def check(self, value, case_sensitive = False) -> bool:
		"""Takes a value as argument and controls if it respects the filter, returning True if it is an acceptable value, False if it isn't."""

		control_value = self.controlValue
		if not case_sensitive:
			if type(value) == str:
				value = value.lower()
			if type(control_value) == str:
				control_value = control_value.lower()
		if self.relation in {self.__class__.STARTS_BY, self.__class__.ENDS_BY}:
			if type(value) != str:
				raise FilterError("STARTS_BY and ENDS_BY relations can be applied only to strings")
			else:
				control_value_length = len(control_value)
				if self.relation == self.__class__.STARTS_BY:
					return control_value == value[0:control_value_length]
				else:
					if control_value == '':
						return True
					else:
						return control_value == value[-control_value_length:]
		else:
			if self.relation == self.__class__.EQUALS:
				return control_value == value
			elif self.relation == self.__class__.DIFFERENT_FROM:
				return control_value != value
			elif self.relation == self.__class__.LESS_THAN:
				return value < control_value
			elif self.relation == self.__class__.GREATER_THAN:
				return value > control_value
			elif self.relation == self.__class__.LESS_OR_EQUAL:
				return value <= control_value
			elif self.relation == self.__class__.GREATER_OR_EQUAL:
				return value >= control_value


class FilterWidget(qtw.QWidget):

	def __init__(self):
		super().__init__()


class DtStringFilterWidget(FilterWidget):

	filterChanged = qtc.pyqtSignal(int, int, int, int, int)#last int to say if the filter is enabled (1) or disabled (0)

	def __init__(self):
		super().__init__()
		self.applyStart = qtw.QCheckBox(self.tr("apply"))
		self.applyStart.setChecked(False)
		self.applyEnd = qtw.QCheckBox(self.tr("apply"))
		self.applyEnd.setChecked(False)
		self.startDate = qtw.QDateEdit(qtc.QDate(1900, 1, 1))
		self.startDate.setCalendarPopup(True)
		self.startDate.setDisplayFormat("dd/MM/yyyy")
		self.startDate.setDisabled(True)
		self.endDate = qtw.QDateEdit(qtc.QDate.currentDate())
		self.endDate.setCalendarPopup(True)
		self.endDate.setDisplayFormat("dd/MM/yyyy")
		self.endDate.setDisabled(True)
		layout = qtw.QGridLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(qtw.QLabel(self.tr("start_date")), 0, 0)
		layout.addWidget(self.startDate, 0, 1)
		layout.addWidget(self.applyStart, 0, 2)
		layout.addWidget(qtw.QLabel(self.tr("end_date")), 1, 0)
		layout.addWidget(self.endDate, 1, 1)
		layout.addWidget(self.applyEnd, 1, 2)
		self.setLayout(layout)
		self.applyStart.clicked.connect(self._onApplyStartClicked)
		self.applyEnd.clicked.connect(self._onApplyEndClicked)
		self.applyStart.clicked.connect(self._onDatesChanged)
		self.applyEnd.clicked.connect(self._onDatesChanged)
		self.startDate.dateChanged.connect(self._onDatesChanged)
		self.endDate.dateChanged.connect(self._onDatesChanged)
		
	def _onDatesChanged(self):
		start_enabled = 1 if self.startDate.isEnabled() else 0
		start_date = self.startDate.date()
		self.filterChanged.emit(start_date.year(), start_date.month(), start_date.day(), Filter.GREATER_THAN, start_enabled)
		end_enabled = 1 if self.endDate.isEnabled() else 0
		end_date = self.endDate.date()
		self.filterChanged.emit(end_date.year(), end_date.month(), end_date.day(), Filter.LESS_THAN, end_enabled)
	
	def _onApplyStartClicked(self):
		if self.applyStart.isChecked():
			self.startDate.setEnabled(True)
		else:
			self.startDate.setEnabled(False)
	
	def _onApplyEndClicked(self):
		if self.applyEnd.isChecked():
			self.endDate.setEnabled(True)
		else:
			self.endDate.setEnabled(False)


class SexFilterWidget(FilterWidget):

	filterChanged = qtc.pyqtSignal(int, int)

	def __init__(self):
		super().__init__()
		self.relationComboBox = qtw.QComboBox()
		self.sexComboBox = qtw.QComboBox()
		self.relationComboBox.addItem(self.tr("equals_to"))
		self.relationComboBox.addItem(self.tr("different_from"))
		self.relationComboBox.addItem(self.tr("don't_apply"))
		self.relationComboBox.setCurrentIndex(2)
		self.sexComboBox.addItem(self.tr("male"))
		self.sexComboBox.addItem(self.tr("female"))
		self.sexComboBox.addItem(self.tr("undefined"))
		layout = qtw.QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.relationComboBox)
		layout.addWidget(self.sexComboBox)
		self.setLayout(layout)
		self.sexComboBox.currentIndexChanged.connect(self._onChange)
		self.relationComboBox.currentIndexChanged.connect(self._onChange)
	
	def _onChange(self, thevalue):
		if self.relationComboBox.currentIndex() == 0:
			relation = Filter.EQUALS
		elif self.relationComboBox.currentIndex() == 1:
			relation = Filter.DIFFERENT_FROM
		else:
			relation = -1
		sex = self.sexComboBox.currentIndex() if self.sexComboBox.currentIndex() != 2 else -1
		self.filterChanged.emit(relation, sex)
	

class TextFilterWidget(FilterWidget):

	filterChanged = qtc.pyqtSignal(int, str)
		
	def __init__(self):
		super().__init__()
		self.lineEdit = qtw.QLineEdit()
		self.lineEdit.textChanged.connect(self._onTextChanged)
		self.comboBox = qtw.QComboBox()
		self.comboBox.addItem(self.tr("starts_by"))
		self.comboBox.addItem(self.tr("ends_by"))
		self.comboBox.addItem(self.tr("equals_to"))
		self.comboBox.addItem(self.tr("different_from"))
		self.comboBox.addItem(self.tr("don't_apply"))
		self.comboBox.currentIndexChanged.connect(self._onConditionChanged)
		layout = qtw.QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.comboBox)
		layout.addWidget(self.lineEdit)
		self.setLayout(layout)

	def emitChange(self):
		if self.comboBox.currentIndex() == 0:
			relation = Filter.STARTS_BY
		elif self.comboBox.currentIndex() == 1:
			relation = Filter.ENDS_BY
		elif self.comboBox.currentIndex() == 2:
			relation = Filter.EQUALS
		elif self.comboBox.currentIndex() == 3:
			relation = Filter.DIFFERENT_FROM
		else:
			relation = -1
		value = self.lineEdit.text()
		self.filterChanged.emit(relation, value)
		
	def _onTextChanged(self, value):
		self.emitChange()

	def _onConditionChanged(self, value):
		self.emitChange()


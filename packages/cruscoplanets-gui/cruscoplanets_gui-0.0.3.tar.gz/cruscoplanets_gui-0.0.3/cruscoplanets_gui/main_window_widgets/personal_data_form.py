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
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFormLayout, QLineEdit, QRadioButton


class PersonalDataForm(QWidget):

	def __init__(self, name: str = None, surname: str = None, sex: int = None):
		super().__init__()

		self.baseLayout = QFormLayout()
		
		self.nameField = QLineEdit(self)
		if name != None:
			self.nameField.setText(name)
		self.surnameField = QLineEdit(self)
		if surname != None:
			self.surnameField.setText(surname)
		sexWidget = QWidget(self)#parent for sex radio buttons
		self.maleRadio = QRadioButton(self.tr("male"), sexWidget)
		self.femaleRadio = QRadioButton(self.tr("female"), sexWidget)
		self.undefinedRadio = QRadioButton(self.tr("undefined"), sexWidget)
		if sex == 0:
			self.maleRadio.setChecked(True)
		if sex == 1:
			self.femaleRadio.setChecked(True)
		else:
			self.undefinedRadio.setChecked(True)
		
		sexLayout = QHBoxLayout()
		sexLayout.addWidget(self.maleRadio)
		sexLayout.addWidget(self.femaleRadio)
		sexLayout.addWidget(self.undefinedRadio)
		sexWidget.setLayout(sexLayout)
		
		self.baseLayout = QFormLayout()
		self.baseLayout.addRow(self.tr("name"), self.nameField)
		self.baseLayout.addRow(self.tr("surname"), self.surnameField)
		self.baseLayout.addRow(self.tr("sex"), sexWidget)
		self.setLayout(self.baseLayout)
	
	@property
	def sex(self):
		if self.maleRadio.isChecked():
			return 0
		elif self.femaleRadio.isChecked():
			return 1
		else:
			return -1
			
	def setSex(self, sex_int):
		if sex_int == 0:
			self.maleRadio.setChecked(True)
		elif sex_int == 1:
			self.femaleRadio.setChecked(True)
		else:
			self.undefinedRadio.setChecked(True)

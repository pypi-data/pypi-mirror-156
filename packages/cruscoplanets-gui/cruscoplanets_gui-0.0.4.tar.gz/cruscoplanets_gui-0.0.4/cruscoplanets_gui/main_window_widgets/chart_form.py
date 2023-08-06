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
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import pyqtSignal
from .event_form import EventForm
from .location_searcher import LocationSearcher
from .personal_data_form import PersonalDataForm
from ..config import Configuration


class ChartForm(QWidget):

	submitData = pyqtSignal(tuple)

	def __init__(self, name: str = None, surname: str = None, sex: int = None, birthtime: str = None, birthlocation_id: int = None):
		super().__init__()
		self.configuration = Configuration()
		
		self.baseLayout = QVBoxLayout()
		
		self.personalDataForm = PersonalDataForm(name, surname, sex)
		self.baseLayout.addWidget(self.personalDataForm)
		
		#place and time for birth event is required in any case, so we put them here in the base class:
		self.birthEventForm = EventForm(birthtime, birthlocation_id)
		self.birthEventForm.eventChanged.connect(lambda: self.submitData.emit(self.chartdata()))
		self.baseLayout.addWidget(self.birthEventForm)
		
		self.setLayout(self.baseLayout)
		self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
		
	def _closeLocationSelectors(self):
		self.birthEventForm.locationSearcher._closeLocationSelector()
		
	def setDataFromDb(self, data_dict):
		self.personalDataForm.nameField.setText(data_dict['name'])
		self.personalDataForm.surnameField.setText(data_dict['surname'])
		self.personalDataForm.setSex(data_dict['sex'])
		self.birthEventForm.setEvent(data_dict['birthdtstring'], data_dict['birthlocationid'])
		
		
class BirthChartForm(ChartForm):

	def __init__(self, name: str = None, surname: str = None, sex: int = None, birthtime: str = None, birthlocation_id: int = None):
		super().__init__(name, surname, sex, birthtime, birthlocation_id)
		
	def voidchartdata(self):#returns a chart of a not specified person, useful when opening the program
		return (
			self.birthEventForm.datetime, self.birthEventForm.location_id, 
			"here", "and now", self.personalDataForm.sex, 
			self.configuration.CHART_DEFAULT_LANGUAGE

		)
		
	def chartdata(self, as_dict = False):
		nameValue = self.personalDataForm.nameField.text() if self.personalDataForm.nameField.text() != '' else "--"
		surnameValue = self.personalDataForm.surnameField.text() if self.personalDataForm.surnameField.text() != '' else "--"
		if not as_dict:
			return (
				self.birthEventForm.datetime, self.birthEventForm.location_id, 
				nameValue, surnameValue, self.personalDataForm.sex, 
				self.configuration.CHART_DEFAULT_LANGUAGE
			)
		else:
			return {
				'birthdtstring': self.birthEventForm.datetime, 
				'birthlocationid': self.birthEventForm.location_id, 
				'name': nameValue, 
				'surname': surnameValue, 
				'sex': self.personalDataForm.sex, 
			}
		
		
class TransitChartForm(ChartForm):

	def __init__(
		self, name: str = None, surname: str = None, sex: int = None, 
		birthtime: str = None, birthlocation_id: int = None, 
		transittime: str = None, transitlocation_id: int = None, 
	):
		super().__init__(name, surname, sex, birthtime, birthlocation_id)
		self.transitEventForm = EventForm(transittime, transitlocation_id)
		self.transitEventForm.eventChanged.connect(lambda: self.submitData.emit(self.chartdata()))
		self.baseLayout.addWidget(self.transitEventForm)
		
	def voidchartdata(self):#returns a chart of a not specified person, useful when opening the program
		return (
			self.birthEventForm.datetime, self.birthEventForm.location_id, 
			self.transitEventForm.datetime, self.transitEventForm.location_id,
			"here", "and now", self.personalDataForm.sex, 
			self.configuration.CHART_DEFAULT_LANGUAGE
		)
		
	def chartdata(self, as_dict = False):
		nameValue = self.personalDataForm.nameField.text() if self.personalDataForm.nameField.text() != '' else "--"
		surnameValue = self.personalDataForm.surnameField.text() if self.personalDataForm.surnameField.text() != '' else "--"
		if not as_dict:
			return (
				self.birthEventForm.datetime, self.birthEventForm.location_id, 
				self.transitEventForm.datetime, self.transitEventForm.location_id,
				nameValue, surnameValue, self.personalDataForm.sex, 
				self.configuration.CHART_DEFAULT_LANGUAGE
			)
		else:
			return {
				'birthdtstring': self.birthEventForm.datetime, 
				'birthlocationid': self.birthEventForm.location_id, 
				'transitdtstring': self.transitEventForm.datetime, 
				'transitlocationid': self.transitEventForm.location_id, 
				'name': nameValue, 
				'surname': surnameValue, 
				'sex': self.personalDataForm.sex, 
			}
		
	def _closeLocationSelectors(self):
		self.birthEventForm.locationSearcher._closeLocationSelector()
		self.transitEventForm.locationSearcher._closeLocationSelector()

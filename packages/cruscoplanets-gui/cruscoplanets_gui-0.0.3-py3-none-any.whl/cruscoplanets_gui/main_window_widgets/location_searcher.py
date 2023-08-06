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
from PyQt5.QtWidgets import QLineEdit, QCompleter, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QLabel, QMainWindow
from PyQt5.QtCore import QStringListModel, pyqtSignal
import cruscoplanets.cmdline
import cruscoplanets.angles
import pycountry

class LocationEntry:

	def __init__(self, locfromdatabase):
		self.id = locfromdatabase['id']
		self.name = locfromdatabase['name']
		self.country = locfromdatabase['country']
		self.countryName = pycountry.countries.get(alpha_2=self.country).name
		self.timezone = locfromdatabase['timezone']
		self.latitude = cruscoplanets.angles.Angle(locfromdatabase['latitude'])
		self.longitude = cruscoplanets.angles.Angle(locfromdatabase['longitude'])
	
	@property	
	def labelString(self):
		return "%s - %s (%s - %s, %s)"%(self.name, self.countryName, self.timezone, self.latitude.reprAsLatitude(), self.longitude.reprAsLongitude())
	
	@property	
	def dataString(self):
		return "%s, %s - %s, %s)"%(self.countryName, self.timezone, self.latitude.reprAsLatitude(), self.longitude.reprAsLongitude())
		
	def __repr__(self):
		return "LocationEntry(%d, %s, %s)"%(self.id, self.name, self.country)


class LocationDict:

	def __init__(self, loclist):
		self.loclist = tuple(LocationEntry(loc) for loc in loclist)
	
	def __getitem__(self, idnumber):
		for loc in self.loclist:
			if loc.id == idnumber:
				return loc
		return None

	def getByName(self, name):
		return tuple(filter(lambda loc: loc.name == name, self.loclist))
	
	def listNames(self):
		return tuple(loc.name for loc in self.loclist)


class LocationOption(QWidget):

	locationChosen = pyqtSignal(int, str)

	def __init__(self, location):
		super().__init__()
		self.location = location
		layout = QHBoxLayout()
		self.label = QLabel()
		self.label.setText(self.location.labelString)
		layout.addWidget(self.label)
		self.submit = QPushButton(self.tr('select'))
		self.submit.clicked.connect(self._onbuttonclick)
		layout.addWidget(self.submit)
		self.setLayout(layout)

	def _onbuttonclick(self):
		self.locationChosen.emit(self.location.id, self.location.dataString)

class LocationSelector(QWidget):
	
	locationChosen = pyqtSignal(int, str)


	def __init__(self, locations, parent=None):
		super().__init__()
		
		layout = QGridLayout()
		self.options = tuple(LocationOption(location) for location in locations)
		for option in self.options:
			layout.addWidget(option)
			option.locationChosen.connect(lambda integer, datastring: self._onLocationChosen(integer, datastring))
		self.setLayout(layout)
		
	def _onLocationChosen(self, integer, datastring):
		self.locationChosen.emit(integer, datastring)
		self.close()


class LocationSearcher(QWidget):

	locationChosen = pyqtSignal(int)

	def __init__(self):
		super().__init__()

		layout = QVBoxLayout()
		self.searchbar = QLineEdit()
		self.searchbar.textEdited.connect(lambda text: self._searchInDatabase(text))
		self.completer = QCompleter([])
		self.completer.setCaseSensitivity(False)
		self.searchbar.setCompleter(self.completer)
		self.completer.activated[str].connect(self._submitSearch)
		self.dataLabel = QLabel()
		layout.addWidget(self.searchbar)
		layout.addWidget(self.dataLabel)
		self.setLayout(layout)
		self.selector = None #toplevel selector in case multiple locations correspond to the selected name
		self.locations = {}
		self.selectedId = None
		
	def _searchInDatabase(self, string):
		if len(string) == 3:
			locations = cruscoplanets.cmdline.searchLocation(string)
			self.locations = LocationDict(locations)
			self.completer.setModel(QStringListModel(self.locations.listNames(), self.completer))
	
	def _submitSearch(self, search):
		self.searchbar.setText(search)
		values = self.locations.getByName(search)
		if len(values) > 1:
			self.selector = LocationSelector(values)
			self.selector.show()
			self.selector.locationChosen.connect(lambda integer, datastring: self._onLocationChosen(integer, datastring))
		else:
			value = values[0]
			self.dataLabel.setText(value.dataString)
			self.selectedId = value.id
			loc_entry = LocationEntry(cruscoplanets.cmdline.searchLocationById(value.id, asDatabaseEntry = True))
			self.dataLabel.setText(loc_entry.dataString)
			self.locationChosen.emit(value.id)
	
	def _onLocationChosen(self, integer, datastring):
		self.selectedId = integer
		self.dataLabel.setText(datastring)
		self.locationChosen.emit(integer)
		
	def setLocation(self, location_id):
		self.selectedId = location_id
		location_object = LocationEntry(cruscoplanets.cmdline.searchLocationById(location_id, asDatabaseEntry = True))
		self.dataLabel.setText(location_object.dataString)
		self.searchbar.setText(location_object.name)
		
	def _closeLocationSelector(self):
		if self.selector != None:
			self.selector.close()

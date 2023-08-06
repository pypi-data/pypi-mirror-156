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
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from .location_searcher import LocationSearcher
from .datetime_formatter import DateTimeFormatter
from ..config import Configuration
import cruscoplanets.cmdline


class EventForm(QWidget):
	"""Widget for entering the data of a cruscoplanets event.
	
	Args:
		datetimestring: the string in cruscoplanet format representing the initial date and time that the EventForm widget will display. If None, the default date and time string will be used.
		location_id: the integer representing the initial location that the EventForm widget will display. If None, the default location id will be used.
	"""

	eventChanged = pyqtSignal(str, int)

	def __init__(self, datetimestring: str = None, location_id: int = None):
		super().__init__()
		self.configuration = Configuration()
		self.location_id = location_id if location_id != None else self.configuration.DEFAULT_LOCATION
		if datetimestring != None:
			self.datetime = datetimestring
		else:
			if self.configuration.DEFAULT_DATETIME_STRING != 'now':
				self.datetime = self.configuration.DEFAULT_DATETIME_STRING
			else:
				self.datetime = cruscoplanets.cmdline.buildCurrentEvent(self.location_id).cruscoplanetsString

		self.locationSearcher = LocationSearcher()
		self.locationSearcher.locationChosen.connect(lambda loc_id: self._updateLocation(loc_id))
		self.datetimeFormatter = DateTimeFormatter()
		self.datetimeFormatter.datetimeChanged.connect(lambda dtstring: self._updateDatetime(dtstring))
		self.setEvent(self.datetime, self.location_id)
		
		layout = QVBoxLayout()
		layout.addWidget(self.locationSearcher)
		layout.addWidget(self.datetimeFormatter)
		self.setLayout(layout)

	def setEvent(self, datetime, location_id):
		self.event = cruscoplanets.cmdline.buildEvent(datetime, location_id)
		
		self.locationSearcher.setLocation(location_id)
		self.location_id = location_id
		self.datetimeFormatter.setDateTime(self.event)
		self.eventChanged.emit(datetime, location_id)
	
	def _updateLocation(self, loc_id):
		self.location_id = loc_id
		self.eventChanged.emit(self.datetime, self.location_id)

	def _updateDatetime(self, dtstring):
		self.datetime = dtstring
		self.eventChanged.emit(self.datetime, self.location_id)

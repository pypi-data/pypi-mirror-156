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
import cruscoplanets.utils as cruscoutils
from PyQt5.QtCore import QDate, QTime
import os
from . import resources


class Configuration(metaclass=cruscoutils.Singleton):

	CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "base.txt")
	DB_DIR = os.path.join(os.path.dirname(__file__), "databases")
	PERSONAL_DB_FILENAME = "personal.db"

	def __init__(self):
		self.reset()
		for directory in (self.__class__.DB_DIR,):
			os.makedirs(directory, exist_ok = True)#argument exist_ok set to True makes the function not alter the directories if existent
	
	def reset(self):
		config = cruscoutils.parseBanalConfig(self.__class__.CONFIG_FILE)
		for line in config:
			if line[1].isnumeric():
				self.__dict__[line[0]] = float(line[1])
			else:
				self.__dict__[line[0]] = line[1]
	
	def aboutFilePath(self):
		return ':/about/about/%s.md'%self.GUI_DEFAULT_LANGUAGE
		
	def databaseFilePath(self):
		return os.path.join(self.__class__.DB_DIR, self.__class__.PERSONAL_DB_FILENAME)

	def minimumDate(self):
		year, month, day = tuple(int(n) for n in self.MINIMUM_DATE.split('-'))
		return QDate(year, month, day)
	
	def defaultTime(self):#should most conveniently be set to 12:00
		return QTime(12, 0, 0)
		
	def guiLanguages(self):
		return tuple(self.GUI_LANGUAGES.split())
		
	def chartLanguages(self):
		return tuple(self.CHART_LANGUAGES.split())
		
	def __repr__(self):
		return '\n'.join(["%s: %s"%(key, value) for key, value in self.__dict__.items()])
		
	def save(self):
		new_config = cruscoutils.buildBanalConfig(self.__dict__.items())
		with open(self.__class__.CONFIG_FILE, 'w') as config_file:
			config_file.write(new_config)
	
	def saveDefaultLanguage(self, language):
		self.GUI_DEFAULT_LANGUAGE = language
		new_config = dict(cruscoutils.parseBanalConfig(self.__class__.CONFIG_FILE))
		new_config["GUI_DEFAULT_LANGUAGE"] = language
		new_config = cruscoutils.buildBanalConfig(new_config.items())
		with open(self.__class__.CONFIG_FILE, 'w') as config_file:
			config_file.write(new_config)

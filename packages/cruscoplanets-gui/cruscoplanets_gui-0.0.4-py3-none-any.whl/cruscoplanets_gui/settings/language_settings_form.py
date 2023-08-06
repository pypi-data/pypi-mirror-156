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
from PyQt5.QtWidgets import QMainWindow, QWidget, QComboBox, QFormLayout, QStyle, QMessageBox, QLabel
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from .. import config
import langcodes


class LanguageComboBox(QComboBox):

	languageChanged = pyqtSignal(str, str)
	
	def __init__(self, languages, defaultLanguage):
		super().__init__()
		self.configuration = config.Configuration()
		self.defaultLanguage = (defaultLanguage, langcodes.Language.get(defaultLanguage).display_name(self.configuration.GUI_DEFAULT_LANGUAGE))
		self.codesAndNames = []
		for language in languages:
			lang = langcodes.Language.get(language)
			self.codesAndNames.append((language, lang.display_name(self.configuration.GUI_DEFAULT_LANGUAGE)))
		
		for language in self.codesAndNames:
			self.addItem(language[1])

		self.reset()
		self.currentIndexChanged.connect(lambda index: self.languageChanged.emit(*self.codesAndNames[index]))
	
	def reset(self):
		self.setCurrentIndex(self.codesAndNames.index(self.defaultLanguage))
			

class LanguageSettingsWindow(QMainWindow):

	chartLanguageUpdated = pyqtSignal()		

	def __init__(self):
		super().__init__()
		self.setWindowTitle(self.tr("language_settings_window"))
		self.resize(400, 400)
		self.configuration = config.Configuration()
		self.container = QWidget(self)
		layout = QFormLayout()
		self.chartComboBox = LanguageComboBox(self.configuration.chartLanguages(), self.configuration.CHART_DEFAULT_LANGUAGE)
		self.guiComboBox = LanguageComboBox(self.configuration.guiLanguages(), self.configuration.GUI_DEFAULT_LANGUAGE)
		self.chartComboBox.languageChanged.connect(self._updateChartLanguage)
		self.guiComboBox.languageChanged.connect(self._updateGuiLanguage)
		self.notifications = QLabel()
		layout.addRow(self.tr("chart_language"), self.chartComboBox)
		layout.addRow(self.tr("gui_language"), self.guiComboBox)
		layout.addRow(self.notifications)
		self.container.setLayout(layout)
		self.setCentralWidget(self.container)

		self.toolbar = self.addToolBar(self.tr("actions"))
		save_icon = self.style().standardIcon(QStyle.SP_DialogSaveButton)
		self.save = self.toolbar.addAction(self.tr("save"))
		self.save.setIcon(save_icon)
		self.save.triggered.connect(self.configuration.save)
		reset_icon = self.style().standardIcon(QStyle.SP_DialogResetButton)
		self.reset = self.toolbar.addAction(self.tr("reset"))
		self.reset.setIcon(reset_icon)
		self.reset.triggered.connect(self._onReset)


	def _updateChartLanguage(self, langcode, langname):
		self.configuration.CHART_DEFAULT_LANGUAGE = langcode
		self.chartLanguageUpdated.emit()

	def _updateGuiLanguage(self, langcode, langname):
		self.configuration.saveDefaultLanguage(langcode)
		self.notifications.setText(self.tr("language_will_be_changed_to_{0}_at_next_loading").format(langname))

	def _onReset(self):
		self.configuration.reset()
		self.chartComboBox.reset()
		self.guiComboBox.reset()
		self.chartLanguageUpdated.emit()

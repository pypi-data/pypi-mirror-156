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
from PyQt5.QtWidgets import QTabWidget, QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QTranslator, QFile, QTextStream, QIODevice
from PyQt5.QtGui import QIcon
import os, sys
from .main_window_widgets import chart
from .settings import settings_form
from .settings import language_settings_form
from . import config
from .databases import database_models
from .databases import database_views
from . import resources


class TabWidget(QTabWidget):

	def __init__(self):
		super().__init__()
		self.birthChart = chart.BirthChart()
		self.transitChart = chart.TransitChart()
		self.addTab(self.birthChart, self.tr("Birth Chart"))
		self.addTab(self.transitChart, self.tr("Transit Chart"))
		
	def _updateGraphics(self):
		"""updates the graphics where settings are changed"""
		self.birthChart.chartForm.submitData.emit(self.birthChart.chartForm.chartdata())
		self.transitChart.chartForm.submitData.emit(self.transitChart.chartForm.chartdata())
		
	def newBirthChart(self):
		self.removeTab(0)
		self.birthChart = chart.BirthChart()
		self.insertTab(0, self.birthChart, self.tr("Birth Chart"))
		self.setCurrentIndex(0)
		
	def newTransitChart(self):
		self.removeTab(1)
		self.transitChart = chart.TransitChart()
		self.addTab(self.transitChart, self.tr("Transit Chart"))
		self.setCurrentIndex(1)
		
	def drawBirthChart(self, data):
		self.birthChart.chartForm.setDataFromDb(data)
		
	def drawTransitChart(self, data):
		self.transitChart.chartForm.setDataFromDb(data)

	def export(self, fileName):
		self.currentWidget().export(fileName)
	
	def currentData(self):
		return self.currentWidget().chartForm.chartdata(as_dict=True)


class MainWindow(QMainWindow):

	PERSONAL_DB_PATH = os.path.join(os.path.dirname(__file__), "databases", "personal.db")

	def __init__(self):
		super().__init__()
		self.setWindowIcon(QIcon(':/icon/images/cruscoplanets.png'))

		#calling configuration here makes sure that some initialization procedures are done, as creating the resource directories if they don't exist
		configuration = config.Configuration()

		self.setWindowTitle("Cruscoplanets GUI")
		self.tabWidget = TabWidget()
		self.setCentralWidget(self.tabWidget)
		self.actions = self.menuBar().addMenu(self.tr("Actions"))
		new_action = self.actions.addAction(self.tr("New"))
		open_action = self.actions.addAction(self.tr("Open_database"))
		save_action = self.actions.addAction(self.tr("Save_in_database"))
		self.databaseModel = database_models.PersonalDatabaseModel()
		self.peopleTableView = database_views.TableView(self.databaseModel.peopleTable)
		self.peopleTableView.setWindowTitle(self.tr("people"))
		self.peopleTableView.showData.connect(self._onShow)
		new_action.triggered.connect(self._onNew)
		open_action.triggered.connect(self.peopleTableView.show)
		save_action.triggered.connect(self._onAddToDatabase)


		export_action = self.actions.addAction(self.tr("Export"))
		export_action.triggered.connect(self._onExport)

		self.settings = self.menuBar().addMenu(self.tr("Settings"))
		graphic_settings = self.settings.addAction(self.tr("Graphics"))
		language_settings = self.settings.addAction(self.tr("Language"))
		self.about = self.menuBar().addMenu(self.tr("About"))
		about = self.about.addAction(self.tr("About cruscoplanets GUI"))
		about.triggered.connect(self._onAbout)

		self.settingsWindow = settings_form.SettingsWindow()
		graphic_settings.triggered.connect(self.settingsWindow.show)
		self.settingsWindow.optionsChanged.connect(self.tabWidget._updateGraphics)
		self.languageSettingsWindow = language_settings_form.LanguageSettingsWindow()
		self.languageSettingsWindow.chartLanguageUpdated.connect(self.tabWidget._updateGraphics)
		language_settings.triggered.connect(self.languageSettingsWindow.show)
		
	def _onOpen(self):
		self.peopleTableView.show()

	def _onShow(self, data):
		if self.tabWidget.currentIndex() == 0:
			self.tabWidget.drawBirthChart(data)
		elif self.tabWidget.currentIndex() == 1:
			self.tabWidget.drawTransitChart(data)

	def _onNew(self):
		if self.tabWidget.currentIndex() == 0:
			self.tabWidget.newBirthChart()
		elif self.tabWidget.currentIndex() == 1:
			self.tabWidget.newTransitChart()

	def _onAddToDatabase(self):
		data = self.tabWidget.currentData()
		print(data)
		for key in ('transitdtstring', 'transitlocationid'):#if the transit tab is open we save only the information related to birth
			if key in data.keys():
				del data[key]
		success = self.peopleTableView.tableData.addRow(data)
		if success:
			message = QMessageBox.information(self, self.tr("adding_success"), self.tr("the_new_birth_chart_has_been_successfully_added_to_the_database"))
		else:
			message = QMessageBox.critical(self, self.tr("adding_failure"), self.tr("the_new_birth_chart_has_not_been_successfully_added_to_the_database"))
			

	def _onAbout(self):
		message = QMessageBox()
		message.setWindowTitle(self.tr("about_cruscoplanets_GUI"))
		message.setTextFormat(Qt.MarkdownText)
		message.setIcon(QMessageBox.Information)
		about_file_path = config.Configuration().aboutFilePath()
		thefile = QFile(about_file_path)
		thefile.open(QIODevice.ReadOnly)
		thetext = QTextStream(thefile).readAll()
		thefile.close()
		message.setText(thetext)
		message.exec_()
		

	def _onExport(self):
		dialog = QFileDialog(self)
		dialog.setFileMode(QFileDialog.AnyFile)
		dialog.setDirectory(os.path.expanduser('~'))
		dialog.setNameFilter(self.tr("Image Files (*.png *.jpg *.svg)"))
		fileName, ok = dialog.getSaveFileName(self, self.tr("export_file"))
		if ok:
			self.tabWidget.export(fileName)

	def showEvent(self, event):
		"""Overridden to make the window occupy the whole screen"""
		super().showEvent(event)
		geometry = self.windowHandle().screen().availableGeometry()
		self.setGeometry(geometry)

		
	def closeEvent(self, event):
		self.settingsWindow.close()
		self.languageSettingsWindow.close()
		self.peopleTableView.close()
		self.tabWidget.birthChart.chartForm._closeLocationSelectors()
		self.tabWidget.transitChart.chartForm._closeLocationSelectors()
		super().close()

def main():
	app = QApplication(sys.argv)

	gui_language = config.Configuration().GUI_DEFAULT_LANGUAGE
	translator = QTranslator()
#	translator.load(os.path.join("translations", "tr_%s"%gui_language))
	translator.load(os.path.join(":/translations/translations/tr_%s.qm"%gui_language))
	app.installTranslator(translator)

	window = MainWindow()
	window.show()
	sys.exit(app.exec())

if __name__ == '__main__':
	main()

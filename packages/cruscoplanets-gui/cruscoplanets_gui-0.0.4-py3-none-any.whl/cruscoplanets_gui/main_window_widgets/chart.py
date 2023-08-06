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
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QMessageBox, QStyle
from PyQt5 import QtSvg
from PyQt5.QtSql import QSqlDatabase
from . import chart_form
from . import svg_widget
import cruscoplanets.cmdline
from cruscoplanets.chart_printer import FormatError
from .. import config


class Chart(QWidget):
	
	def __init__(self, name: str = None, surname: str = None, sex: int = None, birthtime: str = None, birthlocation_id: int = None):
		super().__init__()
		self.configuration = config.Configuration()

	def export(self, fileName):
		self.svgWidget.export(fileName)
		
	def _handleExportError(self, fileFormat):
		message = QMessageBox(QMessageBox.Critical, self.tr("error"), self.tr(f"{fileFormat}_is_not_an_allowed_format".format(fileFormat)))
		message.exec_()


class BirthChart(Chart):

	def __init__(self, name: str = None, surname: str = None, sex: int = None, birthtime: str = None, birthlocation_id: int = None):
		super().__init__(name, surname, sex, birthtime, birthlocation_id)
		self.chartForm = chart_form.BirthChartForm(name, surname, sex, birthtime, birthlocation_id)
		self.chartForm.submitData.connect(lambda data: self._onDataSubmitted(data))
		
		fillWidget = QWidget()
		fillWidget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
		
		formLayout = QVBoxLayout()
		formLayout.addWidget(self.chartForm)
		formLayout.addWidget(fillWidget)
		
		self.svgWidget = svg_widget.SvgWidget()
		self._onDataSubmitted(self.chartForm.voidchartdata())
		self.layout = QHBoxLayout()
		self.layout.addLayout(formLayout)
		self.layout.addWidget(self.svgWidget)
		self.setLayout(self.layout)

	def _onDataSubmitted(self, data: tuple):
		svgBuffer = cruscoplanets.cmdline.doBirthBuffer(*data)
		self.svgWidget.load(svgBuffer)
		
	def export(self, fileName):
		birthtime, birthlocation, name, surname, sex, language = self.chartForm.chartdata()
		try:
			chartprinter = cruscoplanets.cmdline.doBirthChart(birthtime, birthlocation, name, surname, sex, fileName, self.configuration.CHART_DEFAULT_LANGUAGE)
			message = QMessageBox(QMessageBox.NoIcon, self.tr("success"), self.tr("export_successful"))
			message.exec_()
		except FormatError as fe:
			self._handleExportError(fe.format)


class TransitChart(Chart):

	def __init__(self, name: str = None, surname: str = None, sex: int = None, birthtime: str = None, birthlocation_id: int = None):
		super().__init__(name, surname, sex, birthtime, birthlocation_id)
		self.chartForm = chart_form.TransitChartForm(name, surname, sex, birthtime, birthlocation_id)
		self.chartForm.submitData.connect(lambda data: self._onDataSubmitted(data))
		
		fillWidget = QWidget()
		fillWidget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
		
		formLayout = QVBoxLayout()
		formLayout.addWidget(self.chartForm)
		formLayout.addWidget(fillWidget)
		
		self.svgWidget = svg_widget.SvgWidget()
		self._onDataSubmitted(self.chartForm.voidchartdata())
		self.layout = QHBoxLayout()
		self.layout.addLayout(formLayout)
		self.layout.addWidget(self.svgWidget)
		self.setLayout(self.layout)

	def _onDataSubmitted(self, data: tuple):
		svgBuffer = cruscoplanets.cmdline.doTransitBuffer(*data)
		self.svgWidget.load(svgBuffer)

	def export(self, fileName):
		birthtime, birthlocation, transittime, transitlocation, name, surname, sex, language = self.chartForm.chartdata()
		try:
			chartprinter = cruscoplanets.cmdline.doTransitChart(birthtime, birthlocation, transittime, transitlocation, name, surname, sex, fileName, self.configuration.CHART_DEFAULT_LANGUAGE)
			message = QMessageBox(QMessageBox.NoIcon, self.tr("success"), self.tr("export_successful"))
			message.exec_()
		except FormatError as fe:
			self._handleExportError(fe.format)

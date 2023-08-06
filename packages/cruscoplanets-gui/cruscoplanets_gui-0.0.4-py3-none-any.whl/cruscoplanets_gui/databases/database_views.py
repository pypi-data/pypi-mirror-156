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
import PyQt5.QtGui as qtg
from . import database_models
from . import delegates
from . import database_filters
from . import resizable_grid
from .. import resources

class Header(qtw.QWidget):

	sort = qtc.pyqtSignal(str, bool)

	def __init__(self, column):
		super().__init__()
		self.column = column
		layout = qtw.QHBoxLayout()
		layout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		self.label = qtw.QLabel(self.column.header())
		layout.addWidget(self.label, qtc.Qt.AlignLeft)
		self.sortRight = qtw.QPushButton()
		self.sortRight.setIcon(self.style().standardIcon(qtw.QStyle.SP_ArrowDown))
		self.sortRight.setFixedWidth(self.sortRight.height())
		layout.addWidget(self.sortRight, qtc.Qt.AlignRight)
		self.sortReverse = qtw.QPushButton()
		self.sortReverse.setIcon(self.style().standardIcon(qtw.QStyle.SP_ArrowUp))
		self.sortReverse.setGeometry(qtc.QRect(0, 0, 20, 20))
		layout.addWidget(self.sortReverse, qtc.Qt.AlignRight)
		self.sortReverse.hide()
		self.setLayout(layout)
		
		self.sortRight.clicked.connect(self._onsortRightClicked)
		self.sortReverse.clicked.connect(self._onsortReverseClicked)

		self.sortRight.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
		self.sortReverse.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
		palette = qtg.QPalette()
		palette.setColor(qtg.QPalette.Window, qtg.QColor("white"))
		self.setAutoFillBackground(True)
		self.setPalette(palette)
		
	def _onsortRightClicked(self):
		self.sortRight.hide()
		self.sortReverse.show()
		self.sort.emit(self.column.name(), False)
		
	def _onsortReverseClicked(self):
		self.sortReverse.hide()
		self.sortRight.show()
		self.sort.emit(self.column.name(), True)
	
	def showEvent(self, event):
		super().showEvent(event)
		self.sortRight.setFixedWidth(self.sortRight.height())
		self.sortReverse.setFixedWidth(self.sortRight.height())
		

class Row(qtc.QObject):

	updated = qtc.pyqtSignal(dict)
	showData = qtc.pyqtSignal(dict)

	def __init__(self, record):
		super().__init__()
		self.record = record
		self.selectCheckBox = qtw.QCheckBox()
		self.showButton = qtw.QPushButton(qtg.QIcon(':/icon/images/show.png'), '')
		self.dataWidgets = tuple(self.buildWidget(field) for field in record.fields)
		self.widgets = (self.selectCheckBox,) + self.dataWidgets + (self.showButton,)
		self.showButton.clicked.connect(self._onShow)
	
	def buildWidget(self, field):
		if field.__class__ == database_models.SexField:
			ret_widget = delegates.SexComboBox()
			ret_widget.setCurrentIndex(field.value())
		elif field.__class__ == database_models.DtStringField:
			ret_widget = delegates.DatetimeSetter()
			ret_widget.setDatetimestring(field.value())
		elif field.__class__ == database_models.LocationField:
			ret_widget = delegates.LocationDatum()
			ret_widget.setLocation(field.value())
		elif field.__class__ == database_models.IdField:
			ret_widget = delegates.IdLabel(str(field.value()))
		else:
			ret_widget = delegates.LineEdit()
			ret_widget.setText(field.value())
			
		palette = qtg.QPalette()
		ret_widget.updated.connect(self.emitUpdate)
		return ret_widget
		
	def _onShow(self):
		data = {}
		for i in range(len(self.record.fields)):
			data.update({self.record.fields[i].name(): self.dataWidgets[i].value()})
		self.showData.emit(data)
		
	def emitUpdate(self):
		data = {}
		for i in range(len(self.record.fields)):
			data.update({self.record.fields[i].name(): self.dataWidgets[i].value()})
		self.updated.emit(data)
		
	def isSelected(self):
		return self.selectCheckBox.isChecked()
		
	def setSelected(self, value: bool):
		return self.selectCheckBox.setChecked(value)
		

class RowsSequence:

	def __init__(self, rows: tuple, columns: tuple):
		self.rows = rows
		self.columns = columns
		
	def __iter__(self):
		return iter(self.rows)
		
	def __getitem__(self, index):
		return self.rows[index]
		
	def iterateOnIndex(self, index):
		index = self.columns[index].index()
		for row in self.rows:
			yield row.widgets[index]
	
	def maxSizesByIndex(self, index):
		widths = [widget.width() for widget in self.iterateOnIndex(index)]
		heights = [widget.height() for widget in self.iterateOnIndex(index)]
		return (max(widths), max(heights))
	
	def maxSizes(self):
		return tuple(self.maxSizesByIndex(index) for index in self.columns.indexes())


class TableData(qtw.QWidget):

	showData = qtc.pyqtSignal(dict)

	def __init__(self, model: database_models.TableModel):
		super().__init__()
		self.model = model
		self.selectAll = qtw.QCheckBox()
		self.headers = (self.selectAll,) + tuple(Header(column) for column in self.model.columns)
		self.filters = tuple(self.buildFilter(column) for column in self.model.columns)
		self.main_layout = qtw.QVBoxLayout()
		self.main_layout.setSpacing(0)
		self.setLayout(self.main_layout)
		self.headers_row = qtw.QWidget()
		self.headers_layout = resizable_grid.GridLayout()
		self.headers_layout.setSpacing(2)
		self.headers_layout.setContentsMargins(2, 2, 2, 2)
		self.filterObjects = []
		for i in range(len(self.headers)):
			if i == 0:#selectAll checkbox
				self.headers_layout.addWidget(self.headers[i], 0, i)#, 1, 2)#spans on the headers' and filters' columns
			else:
				self.headers_layout.addWidget(self.headers[i], 0, i)
				self.headers[i].sort.connect(self._onSort)
		for i, filter_widget in enumerate(self.filters):
			self.headers_layout.addWidget(filter_widget, 1, i+1)
			self.connectFilter(filter_widget, i)
		self.headers_row.setLayout(self.headers_layout)
		self.main_layout.addWidget(self.headers_row)
		#now we hide the primary key header and filter:
		self.headers[self.model.columns.primaryKey().index() + 1].hide()#+1because of the selectAllBox
		self.filters[self.model.columns.primaryKey().index()].hide()
		self.dataContainer = qtw.QScrollArea()
		self.dataContainer.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
		self._rows = None
		self.fillTable()
		self.selectAll.clicked.connect(self._onSelectAll)
		self.main_layout.addWidget(self.dataContainer)
		
	def _onSelectAll(self):
		selected = self.selectAll.isChecked()
		for row in self._rows:
			row.setSelected(selected)
		
	def connectFilter(self, filter_widget, column_index):
		if filter_widget.__class__ == database_filters.TextFilterWidget:
			filter_widget.filterChanged.connect(lambda relation, string: self.applyTextFilter(column_index, relation, string))
		elif filter_widget.__class__ == database_filters.SexFilterWidget:
			filter_widget.filterChanged.connect(lambda relation, sex: self.applySexFilter(column_index, relation, sex))
		elif filter_widget.__class__ == database_filters.DtStringFilterWidget:
			filter_widget.filterChanged.connect(lambda year, month, day, relation, enabled: self.applyDtStringFilter(column_index, year, month, day, relation, enabled))

	def removePreviousFilters(self, column_index):
		if type(column_index) == str:
			column_index = self.columns[column_index].index()
		self.filterObjects = list(filter(lambda filt: filt.column != column_index, self.filterObjects))

	def removePreviousDtStringFilters(self, column_index, relation):
		if type(column_index) == str:
			column_index = self.columns[column_index].index()
		self.filterObjects = list(filter(lambda filt: not (filt.column == column_index and filt.relation == relation), self.filterObjects))
			
	def applyTextFilter(self, column_index, relation, string):
		self.removePreviousFilters(column_index)
		if relation != -1:	
			new_filter = database_filters.Filter(column_index, relation, string)
			self.filterObjects.append(new_filter)
		self.fillTable()
			
	def applySexFilter(self, column_index, relation, sex):
		self.removePreviousFilters(column_index)
		if relation != -1:
			new_filter = database_filters.Filter(column_index, relation, sex)
			self.filterObjects.append(new_filter)
		self.fillTable()

	def applyDtStringFilter(self, column_index, year, month, day, relation, enabled):
		self.removePreviousDtStringFilters(column_index, relation)
		if enabled == 1:
			datetime = qtc.QDateTime(qtc.QDate(year, month, day), qtc.QTime(0, 0, 0))
			new_filter = database_filters.Filter(column_index, relation, datetime)
			self.filterObjects.append(new_filter)
		self.fillTable()
		
	def updateTable(self, values):
		self.model.updateRecord(**values)
		
	def showRecord(self, values_dict):
		self.showData.emit(values_dict)
	
	def	rows(self):
		rows = RowsSequence(tuple(Row(record) for record in self.model.select()), self.model.columns)
		for row in rows:
			row.updated.connect(self.updateTable)
			row.showData.connect(self.showRecord)
		return rows

	def buildFilter(self, column):
		if column.fieldClass() == database_models.Field:
			ret_widget = database_filters.TextFilterWidget()
		elif column.fieldClass() == database_models.SexField:
			ret_widget = database_filters.SexFilterWidget()
		elif column.fieldClass() == database_models.DtStringField:
			ret_widget = database_filters.DtStringFilterWidget()
		else:
			ret_widget = database_filters.FilterWidget()
		return ret_widget

	def _onSort(self, column_name, is_reverse):
		self.model.sortByField(column_name, reverse = is_reverse)
		self.fillTable()

	def fillTable(self):
		self.model.filters = []
		self.model.filters.extend(self.filterObjects)
		if self.dataContainer.widget() != None:
			self.dataContainer.takeWidget()
		
		data_table = qtw.QWidget()
		data_layout = resizable_grid.GridLayout()
		data_layout.setSpacing(2)
		data_layout.setContentsMargins(2, 2, 2, 2)
		
		self._rows = self.rows()
		for row_index, row in enumerate(self._rows):
			for field_index, widget in enumerate(row.widgets):
				data_layout.addWidget(widget, row_index, field_index)
				#now we hide the primary key header:
				if widget.__class__ == delegates.IdLabel:
					widget.hide()
		data_table.setLayout(data_layout)
		
		self.dataContainer.setWidget(data_table)
		
	def adaptSizes(self):
		grid_layout = self.dataContainer.widget().layout()
		grid_layout.fillSpaces()
		self.headers_layout.fillSpaces(self.headers_layout.rowCount(), grid_layout.columnCount())
		for column_index in range(grid_layout.columnCount()):
			max_width = grid_layout.getMaxWidth(column_index)
			grid_layout.setWidth(column_index, max_width)
			self.headers_layout.setWidth(column_index, max_width)
	
	def showEvent(self, event):
		super().showEvent(event)
		
	def addRow(self, data):
		ret = self.model.addRecord(**data)
		self.fillTable()
		return ret
		
	def addVoidRow(self):
		ret = self.model.addVoidRecord()
		self.fillTable()
		return ret
	
	def removeSelectedRows(self):
		selected_rows_id = tuple(row.record.primaryKey() for row in self._rows if row.isSelected())
		ret = True
		for row_id in selected_rows_id:
			ret = self.model.deleteRecord(row_id)
		self.fillTable()
		return ret
		

class TableView(qtw.QMainWindow):

	showData = qtc.pyqtSignal(dict)

	def __init__(self, model: database_models.TableModel):
		super().__init__()
		self.toolbar = self.addToolBar(self.tr("actions"))
		add_action = self.toolbar.addAction(qtg.QIcon(':/icon/images/plus.png'), self.tr("add"))
		remove_action = self.toolbar.addAction(qtg.QIcon(':/icon/images/minus.png'), self.tr("remove"))
		self.tableData = TableData(model)
		self.tableData.showData.connect(self._onShowData)
		self.setCentralWidget(self.tableData)
		add_action.triggered.connect(self.tableData.addVoidRow)
		remove_action.triggered.connect(self.tableData.removeSelectedRows)

	def _onShowData(self, data_dict):
		self.showData.emit(data_dict)


	def showEvent(self, event):
		super().showEvent(event)
		self.tableData.adaptSizes()
		self.setMaximumWidth(self.tableData.dataContainer.widget().width())

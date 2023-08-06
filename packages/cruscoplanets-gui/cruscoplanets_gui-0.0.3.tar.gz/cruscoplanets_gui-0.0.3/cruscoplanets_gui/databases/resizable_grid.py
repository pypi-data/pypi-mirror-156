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


class VoidWidget(qtw.QWidget):
	
	def __init__(self):
		super().__init__()
		palette = qtg.QPalette()
		palette.setColor(qtg.QPalette.Window, qtg.QColor("white"))
		self.setAutoFillBackground(True)
		self.setPalette(palette)


class LayoutItem(qtw.QLayoutItem):
	
	def __init__(self, alignment):
		super().__init__(alignment)
		
	def expandingDirections(self):
		return 0


class GridLayout(qtw.QGridLayout):

	def __init__(self):
		super().__init__()
		self.setHorizontalSpacing(2)
	
	def	addItem(self, item, row, column, rowSpan = 1, columnSpan = 1, alignment = qtc.Qt.AlignLeft):
		item = LayoutItem(item.alignment())
		super().addItem(item, row, column, rowSpan, columnSpan, alignment)
	
	def fillSpaces(self, rows = None, columns = None):
		rows = rows if rows != None else self.rowCount()
		columns = columns if columns != None else self.columnCount()
		for i in range(rows):
			for j in range(columns):
				if self.itemAtPosition(i, j) == None:
					void_widget = VoidWidget()
					self.addWidget(void_widget, i, j)
					void_widget.show()
					
	def width(self):
		ret = 0
		if self.rowCount() > 0:
			for i in range(self.columnCount()):
				item = self.itemAtPosition(0, i)
				ret += item.widget().width()
			hspacings = self.columnCount() -1
			ret += hspacings*self.horizontalSpacing()
			left, top, right, bottom = self.getContentsMargins()
		return ret + left + right
					
	def height(self):
		ret = 0
		if self.columnCount() > 0:
			for i in range(self.rowCount()):
				item = self.itemAtPosition(1, 0)
				ret += item.widget().height()
			vspacings = self.rowCount() -1
			ret += vspacings*self.verticalSpacing()
			left, top, right, bottom = self.getContentsMargins()
		return ret + top + bottom
	
	def getMaxWidth(self, column_index):
		widths = []
		for i in range(self.rowCount()):
			item = self.itemAtPosition(i, column_index)
			if not item.widget().isVisible():
				widths.append(0)
			else:
				georect = item.geometry()
				widths.append(georect.width())
		return max(widths)

	def setWidth(self, column_index, width):
		for i in range(self.rowCount()):
			item = self.itemAtPosition(i, column_index)
			georect = item.geometry()
			georect.setWidth(width)
			item.setGeometry(georect)
			item.widget().setFixedWidth(georect.width())
			item.widget().setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)
	
	def getMaxHeight(self, row_index):
		heights = []
		for i in range(self.columnCount()):
			item = self.itemAtPosition(row_index, i)
			if not item.widget().isVisible():
				heights.append(0)
			else:
				georect = item.geometry()
				heights.append(georect.height())
		return max(heights)

	def setHeight(self, row_index, height):
		for i in range(self.columnCount()):
			item = self.itemAtPosition(row_index, i)
			georect = item.geometry()
			georect.setHeight(height)
			item.setGeometry(georect)
			item.widget().setFixedHeight(georect.height())
			item.widget().setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed)


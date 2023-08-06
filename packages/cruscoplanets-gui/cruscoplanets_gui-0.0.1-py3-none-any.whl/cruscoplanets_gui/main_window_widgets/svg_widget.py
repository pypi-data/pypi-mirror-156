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
from PyQt5 import QtSvg
from PyQt5.QtWidgets import QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QSize
from cruscoplanets.cmdline import getImagesSize


class SvgWidget(QtSvg.QSvgWidget):

	def __init__(self):
		super().__init__()
		width, height = getImagesSize()
		self.ratio = width/height

	def resizeEvent(self, event):
		super().resizeEvent(event)
		new_width = self.width()
		new_height = self.height() 
		if new_width/new_height > self.ratio:
			new_width = new_height * self.ratio
		elif new_width/new_height < self.ratio:
			new_height = new_width/self.ratio
		self.resize(new_width, new_height)

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
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QCoreApplication
import cruscoplanets.cmdline


class FontLineEdit(QWidget):

	fontChanged = pyqtSignal(str)

	def __init__(self, value):
		super().__init__()
		self.lineEdit = QLineEdit(value)
		self.lineEdit.textChanged.connect(self._handleTextChanged)
		self.button = QPushButton("...")
		self.button.clicked.connect(self._openFontDialogue)
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.lineEdit)
		layout.addWidget(self.button)
		self.setLayout(layout)
	
	def _openFontDialogue(self):
		start_font = self.lineEdit.text()
		new_font, ok = QFontDialog().getFont(QFont(start_font, 10), self)
		if ok:
			new_font = new_font.toString().split(',')[0]#font family name
		else:
			new_font = start_font
		self.lineEdit.setText(new_font)
		
	def _handleTextChanged(self, text):
		self.fontChanged.emit(text)


class ColorLineEdit(QWidget):

	colorChanged = pyqtSignal(str)

	def __init__(self, value):
		super().__init__()
		self.lineEdit = QLineEdit(value)
		self._changeLineEditColor(QColor(value))
		self.__currentColor = value
		self.lineEdit.textChanged.connect(self._handleTextChanged)
		self.button = QPushButton("...")
		self.button.clicked.connect(self._openColorDialogue)
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.lineEdit)
		layout.addWidget(self.button)
		self.setLayout(layout)

	def _changeLineEditColor(self, color):
		linePalette = QPalette()
		linePalette.setColor(QPalette.Base, color)
		if color == Qt.black:
			linePalette.setColor(QPalette.Text, QColor("white"))
		else:
			linePalette.setColor(QPalette.Text, QColor("black"))
		self.lineEdit.setPalette(linePalette)

	
	def _openColorDialogue(self):
		start_color = QColor(self.lineEdit.text()) if QColor(self.lineEdit.text()).isValid() else "#000000"
		new_color = QColorDialog().getColor(initial=start_color)
		if new_color.isValid():
			new_color = new_color.name()
		else:
			new_color = self.__currentColor
		self.lineEdit.setText(new_color)
		
	def _handleTextChanged(self, text):
		if QColor(text).isValid():
			self.__currentColor = text
			self._changeLineEditColor(QColor(text))
			self.colorChanged.emit(text)


class ScaleSlider(QSlider):

	valueSet = pyqtSignal(float)

	def __init__(self, value):
		super().__init__(Qt.Horizontal)
		self.setMinimum(0)
		self.setMaximum(100)
		self.setSingleStep(1)
		self.setValue(value*10)
		self.valueChanged.connect(lambda: self.valueSet.emit(self.value()/10))


class PercentageSlider(QSlider):

	valueSet = pyqtSignal(float)

	def __init__(self, value):
		super().__init__(Qt.Horizontal)
		self.setMinimum(0)
		self.setMaximum(100)
		self.setSingleStep(1)
		self.setValue(value*100)
		self.valueChanged.connect(lambda: self.valueSet.emit(self.value()/100))


class FontWeightComboBox(QComboBox):

	valueSet = pyqtSignal(str)

	VALUES = ("lighter", "normal", "bolder", "bold")	
	
	def __init__(self, myvalue):
		super().__init__()
		self.addItem(self.tr("lighter"))
		self.addItem(self.tr("normal"))
		self.addItem(self.tr("bolder"))
		self.addItem(self.tr("bold"))
		myindex = self.__class__.VALUES.index(myvalue)
		self.setCurrentIndex(myindex)
		self.activated.connect(self._onActivated)
		
	def _onActivated(self, index):
		self.valueSet.emit(self.__class__.VALUES[index])


class FontStyleComboBox(QComboBox):

	valueSet = pyqtSignal(str)

	VALUES = ("normal", "italic", "oblique")	
	
	def __init__(self, myvalue):
		super().__init__()
		self.addItem(self.tr("normal"))
		self.addItem(self.tr("italic"))
		self.addItem(self.tr("oblique"))
		myindex = self.__class__.VALUES.index(myvalue)
		self.setCurrentIndex(myindex)
		self.activated.connect(self._onActivated)
		
	def _onActivated(self, index):
		self.valueSet.emit(self.__class__.VALUES[index])


class ViewBoxSpin(QDoubleSpinBox):

	SINGLE_STEP = 10

	def __init__(self, minimum, maximum):
		super().__init__()
		self.setRange(minimum, maximum)
		self.setSingleStep(self.__class__.SINGLE_STEP)
		
	def keyPressEvent(self, event):
		event.ignore()
		
		
class ViewBoxSetter(QWidget):

	valueSet = pyqtSignal(str)

	def __init__(self, value):
		super().__init__()
		self._ratio = None#if set to None, width and height can change independently. If set to a float value, they will scale according to that ratio
		values = tuple(float(x) for x in value.split())
		center_x, center_y, self.width, self.height = values
		self.center_x, self.center_y = -center_x, -center_y

		self.center_x_spin = ViewBoxSpin(minimum = -self.width, maximum = self.width)
		self.center_x_spin.setValue(self.center_x)
		self.center_y_spin = ViewBoxSpin(minimum = -self.height, maximum = self.height)
		self.center_y_spin.setValue(self.center_y)
		self.width_spin = ViewBoxSpin(minimum = 0, maximum = 10*self.width)
		self.width_spin.setValue(self.width)
		self.width_spin.valueChanged.connect(self._controlHeight)
		self.width_spin.valueChanged.connect(lambda value: self._adjustCenter(self.center_x_spin, value))
		self.height_spin = ViewBoxSpin(minimum = 0, maximum = 10*self.height)
		self.height_spin.setValue(self.height)
		self.height_spin.valueChanged.connect(self._controlWidth)
		self.height_spin.valueChanged.connect(lambda value: self._adjustCenter(self.center_y_spin, value))

		self.keepRatio = QCheckBox(self.tr("keep_image_ratio"))
		self.keepRatio.stateChanged.connect(self._onKeepRatioChecked)

		self.width_spin.valueChanged.connect(lambda: self.valueSet.emit(self.valuesString()))
		self.height_spin.valueChanged.connect(lambda: self.valueSet.emit(self.valuesString()))
		self.center_x_spin.valueChanged.connect(lambda: self.valueSet.emit(self.valuesString()))
		self.center_y_spin.valueChanged.connect(lambda: self.valueSet.emit(self.valuesString()))
		
	def _controlHeight(self, width):
		if self._ratio != None:
			height = width/self._ratio
			self.height_spin.setValue(height)
		
	def _controlWidth(self, height):
		if self._ratio != None:
			width = height*self._ratio
			self.width_spin.setValue(width)

	def _onKeepRatioChecked(self):
		if self.keepRatio.isChecked():
			self._ratio = self.width/self.height
		else:
			self._ratio = None
		
	def _adjustCenter(self, widget, value):
		widget.setMaximum(value)
		widget.setMinimum(-value)

	def rowsSequence(self):
		return (
			(self.tr("CENTRE_X"), self.center_x_spin),
			(self.tr("CENTRE_Y"), self.center_y_spin),
			(self.tr("WIDTH"), self.width_spin),
			(self.tr("HEIGHT"), self.height_spin),
			("", self.keepRatio,)
		)
		
	def valuesString(self):
		return "%.1f %.1f %.1f %.1f"%(-self.center_x_spin.value(), -self.center_y_spin.value(), self.width_spin.value(), self.height_spin.value())

		
class SettingsOption(QObject):

	optionChanged = pyqtSignal([str, str], [str, float])
	COLOR = 0
	SIZE = 1
	PERCENTAGE = 2
	FONT_WEIGHT = 3
	FONT_STYLE = 4
	IMAGE_VIEWBOX = 5
	FONT_FAMILY = 6
	SCALE = 7
	
	def __init__(self, key, value, translation, opt_type):
		super().__init__()
		self.key = key
		self.translation = translation
		self.type = opt_type
		self.widget = self._buildWidget(value)
		
	def _buildWidget(self, myvalue):
		if self.type == self.__class__.SIZE:
			widget = QDoubleSpinBox(singleStep=1.0, maximum=10*myvalue, minimum=0)
			widget.setValue(myvalue)
			widget.valueChanged.connect(lambda value: self.optionChanged[str, float].emit(self.key, value))
		elif self.type == self.__class__.COLOR:
			widget = ColorLineEdit(myvalue)
			widget.colorChanged.connect(lambda value: self.optionChanged[str, str].emit(self.key, value))
		elif self.type == self.__class__.PERCENTAGE:
			widget = PercentageSlider(myvalue)
			widget.valueSet.connect(lambda value: self.optionChanged[str, float].emit(self.key, value))
		elif self.type == self.__class__.FONT_WEIGHT:
			widget = FontWeightComboBox(myvalue)
			widget.valueSet.connect(lambda value: self.optionChanged[str, str].emit(self.key, value))
		elif self.type == self.__class__.FONT_STYLE:
			widget = FontStyleComboBox(myvalue)
			widget.valueSet.connect(lambda value: self.optionChanged[str, str].emit(self.key, value))
		elif self.type == self.__class__.IMAGE_VIEWBOX:
			widget = ViewBoxSetter(myvalue)
			widget.valueSet.connect(lambda value: self.optionChanged[str, str].emit(self.key, value))
		elif self.type == self.__class__.FONT_FAMILY:
			widget = FontLineEdit(myvalue)
			widget.fontChanged.connect(lambda value: self.optionChanged[str, str].emit(self.key, value))
		elif self.type == self.__class__.SCALE:
			widget = ScaleSlider(myvalue)
			widget.valueSet.connect(lambda value: self.optionChanged[str, float].emit(self.key, value))
			
		return widget


class SettingsFormTab(QScrollArea):

	optionsChanged = pyqtSignal([str, str], [str, float])

	def __init__(self, options_tuple):
		super().__init__()
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.settingsClass = cruscoplanets.cmdline.svgSettings()
		self.settingsOptions = tuple(SettingsOption(option[0], self.settingsClass[option[0]], option[1], option[2]) for option in options_tuple)
		self.container = QWidget()
		layout = QFormLayout()
		for settings_option in self.settingsOptions:
			if settings_option.type != SettingsOption.IMAGE_VIEWBOX:
				layout.addRow(settings_option.translation, settings_option.widget)
			else:
				for row in settings_option.widget.rowsSequence():
					layout.addRow(*row)
			settings_option.optionChanged[str, str].connect(self._updateSettings)
			settings_option.optionChanged[str, float].connect(self._updateSettings)
		self.container.setLayout(layout)
		self.setWidget(self.container)

	def _updateSettings(self, key, value):
		self.settingsClass[key] = value
		self.optionsChanged[str, type(value)].emit(key, value)


class OptionsList(QObject):#unfortunately it can not be set as singleton, but anyway I will istantiate it just once

	def __init__(self):
		super().__init__()
		self.FONT_OPTIONS = (
			("FONT_FAMILY", self.tr("FONT_FAMILY"), SettingsOption.FONT_FAMILY),
			("PERSONAL_DATA_FONT_COLOR", self.tr("PERSONAL_DATA_FONT_COLOR"), SettingsOption.COLOR),
			("PERSONAL_DATA_FONT_WEIGHT", self.tr("PERSONAL_DATA_FONT_WEIGHT"), SettingsOption.FONT_WEIGHT),
			("PERSONAL_DATA_FONT_STYLE", self.tr("PERSONAL_DATA_FONT_STYLE"), SettingsOption.FONT_STYLE),
			("PERSONAL_DATA_FONT_SIZE", self.tr("PERSONAL_DATA_FONT_SIZE"), SettingsOption.SIZE),
			("PLANETS_TABLE_FONT_COLOR", self.tr("PLANETS_TABLE_FONT_COLOR"), SettingsOption.COLOR),
			("PLANETS_TABLE_FONT_WEIGHT", self.tr("PLANETS_TABLE_FONT_WEIGHT"), SettingsOption.FONT_WEIGHT),
			("PLANETS_TABLE_FONT_STYLE", self.tr("PLANETS_TABLE_FONT_STYLE"), SettingsOption.FONT_STYLE),
			("PLANETS_TABLE_FONT_SIZE", self.tr("PLANETS_TABLE_FONT_SIZE"), SettingsOption.SIZE),
			("HOUSES_TABLE_FONT_COLOR", self.tr("HOUSES_TABLE_FONT_COLOR"), SettingsOption.COLOR),
			("HOUSES_TABLE_FONT_WEIGHT", self.tr("HOUSES_TABLE_FONT_WEIGHT"), SettingsOption.FONT_WEIGHT),
			("HOUSES_TABLE_FONT_STYLE", self.tr("HOUSES_TABLE_FONT_STYLE"), SettingsOption.FONT_STYLE),
			("HOUSES_TABLE_FONT_SIZE", self.tr("HOUSES_TABLE_FONT_SIZE"), SettingsOption.SIZE),
			("TRANSITS_TABLE_FONT_COLOR", self.tr("TRANSITS_TABLE_FONT_COLOR"), SettingsOption.COLOR),
			("TRANSITS_TABLE_FONT_WEIGHT", self.tr("TRANSITS_TABLE_FONT_WEIGHT"), SettingsOption.FONT_WEIGHT),
			("TRANSITS_TABLE_FONT_STYLE", self.tr("TRANSITS_TABLE_FONT_STYLE"), SettingsOption.FONT_STYLE),
			("TRANSITS_TABLE_FONT_SIZE", self.tr("TRANSITS_TABLE_FONT_SIZE"), SettingsOption.SIZE),
			("ASPECTS_GRID_TITLE_FONT_WEIGHT", self.tr("ASPECTS_GRID_TITLE_FONT_WEIGHT"), SettingsOption.FONT_WEIGHT),
			("ASPECTS_GRID_TITLE_FONT_STYLE", self.tr("ASPECTS_GRID_TITLE_FONT_STYLE"), SettingsOption.FONT_STYLE),
			("ASPECTS_GRID_TITLE_FONT_SIZE", self.tr("ASPECTS_GRID_TITLE_FONT_SIZE"), SettingsOption.SIZE)
		)

		self.LAYOUT_OPTIONS = (
			("IMAGE_VIEWBOX", self.tr("IMAGE_VIEWBOX"), SettingsOption.IMAGE_VIEWBOX),
			("IMAGE_STROKE", self.tr("IMAGE_STROKE"), SettingsOption.COLOR),
			("BACKGROUND_COLOR", self.tr("BACKGROUND_COLOR"), SettingsOption.COLOR),
			("ASPECTS_GRID_STROKE_OPACITY", self.tr("ASPECTS_GRID_STROKE_OPACITY"), SettingsOption.PERCENTAGE),
			("ASPECTS_GRID_FILL_OPACITY", self.tr("ASPECTS_GRID_FILL_OPACITY"), SettingsOption.PERCENTAGE),
			("PERSONAL_DATA_X_OFFSET", self.tr("PERSONAL_DATA_X_OFFSET"), SettingsOption.SIZE),
			("PERSONAL_DATA_Y_OFFSET", self.tr("PERSONAL_DATA_Y_OFFSET"), SettingsOption.SIZE),
			("ASPECTS_GRID_STROKE_COLOR", self.tr("ASPECTS_GRID_STROKE_COLOR"), SettingsOption.COLOR),
			("ASPECTS_GRID_FILL_COLOR", self.tr("ASPECTS_GRID_FILL_COLOR"), SettingsOption.COLOR),
			("PLANETS_TABLE_X_OFFSET", self.tr("PLANETS_TABLE_X_OFFSET"), SettingsOption.SIZE),
			("PLANETS_TABLE_Y_OFFSET", self.tr("PLANETS_TABLE_Y_OFFSET"), SettingsOption.SIZE),
			("PLANETS_TABLE_CELL_LENGTH", self.tr("PLANETS_TABLE_CELL_LENGTH"), SettingsOption.SIZE),
			("HOUSES_TABLE_X_OFFSET", self.tr("HOUSES_TABLE_X_OFFSET"), SettingsOption.SIZE),
			("HOUSES_TABLE_Y_OFFSET", self.tr("HOUSES_TABLE_Y_OFFSET"), SettingsOption.SIZE),
			("HOUSES_TABLE_CELL_LENGTH", self.tr("HOUSES_TABLE_CELL_LENGTH"), SettingsOption.SIZE),
			("TRANSITS_TABLE_X_OFFSET", self.tr("TRANSITS_TABLE_X_OFFSET"), SettingsOption.SIZE),
			("TRANSITS_TABLE_Y_OFFSET", self.tr("TRANSITS_TABLE_Y_OFFSET"), SettingsOption.SIZE),
			("TRANSITS_TABLE_CELL_LENGTH", self.tr("TRANSITS_TABLE_CELL_LENGTH"), SettingsOption.SIZE),
			("ASPECTS_GRID_X_OFFSET", self.tr("ASPECTS_GRID_X_OFFSET"), SettingsOption.SIZE),
			("ASPECTS_GRID_Y_OFFSET", self.tr("ASPECTS_GRID_Y_OFFSET"), SettingsOption.SIZE),
			("ASPECTS_GRID_CELL_LENGTH", self.tr("ASPECTS_GRID_CELL_LENGTH"), SettingsOption.SIZE),
			("ASPECTS_GRID_STROKE_WIDTH", self.tr("ASPECTS_GRID_STROKE_WIDTH"), SettingsOption.SIZE),
		)

		self.SYMBOLS_COLORS = (
			("CHAR-ARIES_SIGN_COLOR", self.tr("CHAR-ARIES_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-TAURUS_SIGN_COLOR", self.tr("CHAR-TAURUS_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-GEMINI_SIGN_COLOR", self.tr("CHAR-GEMINI_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-CANCER_SIGN_COLOR", self.tr("CHAR-CANCER_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-LEO_SIGN_COLOR", self.tr("CHAR-LEO_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-VIRGO_SIGN_COLOR", self.tr("CHAR-VIRGO_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-LIBRA_SIGN_COLOR", self.tr("CHAR-LIBRA_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-SCORPIO_SIGN_COLOR", self.tr("CHAR-SCORPIO_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-SAGITTARIUS_SIGN_COLOR", self.tr("CHAR-SAGITTARIUS_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-CAPRICORN_SIGN_COLOR", self.tr("CHAR-CAPRICORN_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-AQUARIUS_SIGN_COLOR", self.tr("CHAR-AQUARIUS_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-PISCES_SIGN_COLOR", self.tr("CHAR-PISCES_SIGN_COLOR"), SettingsOption.COLOR),
			("CHAR-SUN_COLOR", self.tr("CHAR-SUN_COLOR"), SettingsOption.COLOR),
			("CHAR-MOON_COLOR", self.tr("CHAR-MOON_COLOR"), SettingsOption.COLOR),
			("CHAR-MERCURY_COLOR", self.tr("CHAR-MERCURY_COLOR"), SettingsOption.COLOR),
			("CHAR-VENUS_COLOR", self.tr("CHAR-VENUS_COLOR"), SettingsOption.COLOR),
			("CHAR-MARS_COLOR", self.tr("CHAR-MARS_COLOR"), SettingsOption.COLOR),
			("CHAR-JUPITER_COLOR", self.tr("CHAR-JUPITER_COLOR"), SettingsOption.COLOR),
			("CHAR-SATURN_COLOR", self.tr("CHAR-SATURN_COLOR"), SettingsOption.COLOR),
			("CHAR-URANUS_COLOR", self.tr("CHAR-URANUS_COLOR"), SettingsOption.COLOR),
			("CHAR-NEPTUNE_COLOR", self.tr("CHAR-NEPTUNE_COLOR"), SettingsOption.COLOR),
			("CHAR-PLUTO_COLOR", self.tr("CHAR-PLUTO_COLOR"), SettingsOption.COLOR),
			("CHAR-ERIS_COLOR", self.tr("CHAR-ERIS_COLOR"), SettingsOption.COLOR),
			("ARIES_COLOR", self.tr("ARIES_COLOR"), SettingsOption.COLOR),
			("TAURUS_COLOR", self.tr("TAURUS_COLOR"), SettingsOption.COLOR),
			("GEMINI_COLOR", self.tr("GEMINI_COLOR"), SettingsOption.COLOR),
			("CANCER_COLOR", self.tr("CANCER_COLOR"), SettingsOption.COLOR),
			("LEO_COLOR", self.tr("LEO_COLOR"), SettingsOption.COLOR),
			("VIRGO_COLOR", self.tr("VIRGO_COLOR"), SettingsOption.COLOR),
			("LIBRA_COLOR", self.tr("LIBRA_COLOR"), SettingsOption.COLOR),
			("SCORPIO_COLOR", self.tr("SCORPIO_COLOR"), SettingsOption.COLOR),
			("SAGITTARIUS_COLOR", self.tr("SAGITTARIUS_COLOR"), SettingsOption.COLOR),
			("CAPRICORN_COLOR", self.tr("CAPRICORN_COLOR"), SettingsOption.COLOR),
			("AQUARIUS_COLOR", self.tr("AQUARIUS_COLOR"), SettingsOption.COLOR),
			("PISCES_COLOR", self.tr("PISCES_COLOR"), SettingsOption.COLOR),
			("ARIES_SIGN_COLOR", self.tr("ARIES_SIGN_COLOR"), SettingsOption.COLOR),
			("TAURUS_SIGN_COLOR", self.tr("TAURUS_SIGN_COLOR"), SettingsOption.COLOR),
			("GEMINI_SIGN_COLOR", self.tr("GEMINI_SIGN_COLOR"), SettingsOption.COLOR),
			("CANCER_SIGN_COLOR", self.tr("CANCER_SIGN_COLOR"), SettingsOption.COLOR),
			("LEO_SIGN_COLOR", self.tr("LEO_SIGN_COLOR"), SettingsOption.COLOR),
			("VIRGO_SIGN_COLOR", self.tr("VIRGO_SIGN_COLOR"), SettingsOption.COLOR),
			("LIBRA_SIGN_COLOR", self.tr("LIBRA_SIGN_COLOR"), SettingsOption.COLOR),
			("SCORPIO_SIGN_COLOR", self.tr("SCORPIO_SIGN_COLOR"), SettingsOption.COLOR),
			("SAGITTARIUS_SIGN_COLOR", self.tr("SAGITTARIUS_SIGN_COLOR"), SettingsOption.COLOR),
			("CAPRICORN_SIGN_COLOR", self.tr("CAPRICORN_SIGN_COLOR"), SettingsOption.COLOR),
			("AQUARIUS_SIGN_COLOR", self.tr("AQUARIUS_SIGN_COLOR"), SettingsOption.COLOR),
			("PISCES_SIGN_COLOR", self.tr("PISCES_SIGN_COLOR"), SettingsOption.COLOR),
			("SUN_COLOR", self.tr("SUN_COLOR"), SettingsOption.COLOR),
			("MOON_COLOR", self.tr("MOON_COLOR"), SettingsOption.COLOR),
			("MERCURY_COLOR", self.tr("MERCURY_COLOR"), SettingsOption.COLOR),
			("VENUS_COLOR", self.tr("VENUS_COLOR"), SettingsOption.COLOR),
			("MARS_COLOR", self.tr("MARS_COLOR"), SettingsOption.COLOR),
			("JUPITER_COLOR", self.tr("JUPITER_COLOR"), SettingsOption.COLOR),
			("SATURN_COLOR", self.tr("SATURN_COLOR"), SettingsOption.COLOR),
			("URANUS_COLOR", self.tr("URANUS_COLOR"), SettingsOption.COLOR),
			("NEPTUNE_COLOR", self.tr("NEPTUNE_COLOR"), SettingsOption.COLOR),
			("PLUTO_COLOR", self.tr("PLUTO_COLOR"), SettingsOption.COLOR),
			("ERIS_COLOR", self.tr("ERIS_COLOR"), SettingsOption.COLOR),
			("TRANSIT-SUN_COLOR", self.tr("TRANSIT-SUN_COLOR"), SettingsOption.COLOR),
			("TRANSIT-MOON_COLOR", self.tr("TRANSIT-MOON_COLOR"), SettingsOption.COLOR),
			("TRANSIT-MERCURY_COLOR", self.tr("TRANSIT-MERCURY_COLOR"), SettingsOption.COLOR),
			("TRANSIT-VENUS_COLOR", self.tr("TRANSIT-VENUS_COLOR"), SettingsOption.COLOR),
			("TRANSIT-MARS_COLOR", self.tr("TRANSIT-MARS_COLOR"), SettingsOption.COLOR),
			("TRANSIT-JUPITER_COLOR", self.tr("TRANSIT-JUPITER_COLOR"), SettingsOption.COLOR),
			("TRANSIT-SATURN_COLOR", self.tr("TRANSIT-SATURN_COLOR"), SettingsOption.COLOR),
			("TRANSIT-URANUS_COLOR", self.tr("TRANSIT-URANUS_COLOR"), SettingsOption.COLOR),
			("TRANSIT-NEPTUNE_COLOR", self.tr("TRANSIT-NEPTUNE_COLOR"), SettingsOption.COLOR),
			("TRANSIT-PLUTO_COLOR", self.tr("TRANSIT-PLUTO_COLOR"), SettingsOption.COLOR),
			("TRANSIT-ERIS_COLOR", self.tr("TRANSIT-ERIS_COLOR"), SettingsOption.COLOR),
			("CONJUNCTION_COLOR", self.tr("CONJUNCTION_COLOR"), SettingsOption.COLOR),
			("OPPOSITION_COLOR", self.tr("OPPOSITION_COLOR"), SettingsOption.COLOR),
			("TRINE_COLOR", self.tr("TRINE_COLOR"), SettingsOption.COLOR),
			("SQUARE_COLOR", self.tr("SQUARE_COLOR"), SettingsOption.COLOR),
			("SEXTILE_COLOR", self.tr("SEXTILE_COLOR"), SettingsOption.COLOR),
			("SEMISEXTILE_COLOR", self.tr("SEMISEXTILE_COLOR"), SettingsOption.COLOR),
		)
		
		self.ZODIAC_OPTIONS = (
			("OUTER_BORDER_COLOR", self.tr("OUTER_BORDER_COLOR"), SettingsOption.COLOR),
			("OUTER_BORDER_WIDTH", self.tr("OUTER_BORDER_WIDTH"), SettingsOption.SIZE),
			("SIGN_BORDERS_COLOR", self.tr("SIGN_BORDERS_COLOR"), SettingsOption.COLOR),
			("SIGN_BORDERS_WIDTH", self.tr("SIGN_BORDERS_WIDTH"), SettingsOption.SIZE),
			("ZODIAC_CIRCLE_RADIUS", self.tr("ZODIAC_CIRCLE_RADIUS"), SettingsOption.SIZE),
			("HOUSES_CIRCLE_RADIUS", self.tr("HOUSES_CIRCLE_RADIUS"), SettingsOption.SIZE),
			("ASPECTS_CIRCLE_RADIUS", self.tr("ASPECTS_CIRCLE_RADIUS"), SettingsOption.SIZE),
			("ZODIAC_OPACITY", self.tr("ZODIAC_OPACITY"), SettingsOption.PERCENTAGE),
			("SIGN_SCALE", self.tr("SIGN_SCALE"), SettingsOption.SCALE),
			("PLANET_SCALE", self.tr("PLANET_SCALE"), SettingsOption.SCALE),
			("DEGREES_CIRCLE_STROKE_OPACITY", self.tr("DEGREES_CIRCLE_STROKE_OPACITY"), SettingsOption.PERCENTAGE),
			("DEGREES_CIRCLE_FILL_OPACITY", self.tr("DEGREES_CIRCLE_FILL_OPACITY"), SettingsOption.PERCENTAGE),
			("ASPECTS_CIRCLE_STROKE_OPACITY", self.tr("ASPECTS_CIRCLE_STROKE_OPACITY"), SettingsOption.PERCENTAGE),
			("ASPECTS_CIRCLE_FILL_OPACITY", self.tr("ASPECTS_CIRCLE_FILL_OPACITY"), SettingsOption.PERCENTAGE),
			("HOUSE_SYMBOLS_COLOR", self.tr("HOUSE_SYMBOLS_COLOR"), SettingsOption.COLOR),
			("HOUSE_SYMBOLS_SIZE", self.tr("HOUSE_SYMBOLS_SIZE"), SettingsOption.SIZE),
			("HOUSE_SYMBOLS_OFFSET", self.tr("HOUSE_SYMBOLS_OFFSET"), SettingsOption.SIZE),
			("DEGREES_CIRCLE_COLOR", self.tr("DEGREES_CIRCLE_COLOR"), SettingsOption.COLOR),
			("TENTH_DEGREE_LINE", self.tr("TENTH_DEGREE_LINE"), SettingsOption.SIZE),
			("FIFTH_DEGREE_LINE", self.tr("FIFTH_DEGREE_LINE"), SettingsOption.SIZE),
			("DEGREE_LINE", self.tr("DEGREE_LINE"), SettingsOption.SIZE),
			("ASPECTS_CIRCLE_COLOR", self.tr("ASPECTS_CIRCLE_COLOR"), SettingsOption.COLOR),
			("DEGREES_CIRCLE_FILL_COLOR", self.tr("DEGREES_CIRCLE_FILL_COLOR"), SettingsOption.COLOR),
			("ASPECTS_CIRCLE_FILL_COLOR", self.tr("ASPECTS_CIRCLE_FILL_COLOR"), SettingsOption.COLOR),
			("HOUSE_LINE_COLOR", self.tr("HOUSE_LINE_COLOR"), SettingsOption.COLOR),
			("HOUSE_LINE_WIDTH", self.tr("HOUSE_LINE_WIDTH"), SettingsOption.SIZE),
			("ASCENDANT_LINE_COLOR", self.tr("ASCENDANT_LINE_COLOR"), SettingsOption.COLOR),
			("ASCENDANT_LINE_WIDTH", self.tr("ASCENDANT_LINE_WIDTH"), SettingsOption.SIZE),
			("MOEDIUM_COELI_LINE_COLOR", self.tr("MOEDIUM_COELI_LINE_COLOR"), SettingsOption.COLOR),
			("MOEDIUM_COELI_LINE_WIDTH", self.tr("MOEDIUM_COELI_LINE_WIDTH"), SettingsOption.SIZE),
			("INNER_POINTERS_LENGTH", self.tr("INNER_POINTERS_LENGTH"), SettingsOption.SIZE),
			("OUTER_POINTERS_LENGTH", self.tr("OUTER_POINTERS_LENGTH"), SettingsOption.SIZE),
			("ANGLE_POINTERS_WIDTH", self.tr("ANGLE_POINTERS_WIDTH"), SettingsOption.SIZE),
			("ZODIAC_SIGNS_OFFSET", self.tr("ZODIAC_SIGNS_OFFSET"), SettingsOption.SIZE),
			("PLANETS_OFFSET", self.tr("PLANETS_OFFSET"), SettingsOption.SIZE),
			("TRANSIT_PLANETS_OFFSET", self.tr("TRANSIT_PLANETS_OFFSET"), SettingsOption.SIZE),
			("CONJUNCTION_WIDTH", self.tr("CONJUNCTION_WIDTH"), SettingsOption.SIZE),
			("OPPOSITION_WIDTH", self.tr("OPPOSITION_WIDTH"), SettingsOption.SIZE),
			("TRINE_WIDTH", self.tr("TRINE_WIDTH"), SettingsOption.SIZE),
			("SQUARE_WIDTH", self.tr("SQUARE_WIDTH"), SettingsOption.SIZE),
			("SEXTILE_WIDTH", self.tr("SEXTILE_WIDTH"), SettingsOption.SIZE),
			("SEMISEXTILE_WIDTH", self.tr("SEMISEXTILE_WIDTH"), SettingsOption.SIZE)
		)


class SettingsForm(QTabWidget):

	optionsChanged = pyqtSignal()

	def __init__(self):
		super().__init__(parent = None)
		self.setWindowTitle(self.tr("Settings"))
		self.layoutOptionsScroll = 0
		self.symbolsColorsScroll = 0
		self.zodiacOptionsScroll = 0
		self.fontOptionsScroll = 0
		self.setTabs()

	def setTabs(self):
		self.optionsList = OptionsList()
		self.layoutOptions = SettingsFormTab(self.optionsList.LAYOUT_OPTIONS)
		self.layoutOptions.verticalScrollBar().setValue(self.layoutOptionsScroll)
		self.symbolsColors = SettingsFormTab(self.optionsList.SYMBOLS_COLORS)
		self.symbolsColors.verticalScrollBar().setValue(self.symbolsColorsScroll)
		self.zodiacOptions = SettingsFormTab(self.optionsList.ZODIAC_OPTIONS)
		self.zodiacOptions.verticalScrollBar().setValue(self.zodiacOptionsScroll)
		self.fontOptions = SettingsFormTab(self.optionsList.FONT_OPTIONS)
		self.fontOptions.verticalScrollBar().setValue(self.fontOptionsScroll)
		self.addTab(self.layoutOptions, self.tr("layout_options"))
		self.addTab(self.symbolsColors, self.tr("symbols_colors"))
		self.addTab(self.zodiacOptions, self.tr("zodiac_options"))
		self.addTab(self.fontOptions, self.tr("font_options"))

		for i in range(self.count()):
			self.widget(i).optionsChanged[str, str].connect(self.optionsChanged.emit)
			self.widget(i).optionsChanged[str, float].connect(self.optionsChanged.emit)

	def reset(self):
		self.layoutOptionsScroll = self.layoutOptions.verticalScrollBar().value()
		self.symbolsColorsScroll = self.symbolsColors.verticalScrollBar().value()
		self.zodiacOptionsScroll = self.zodiacOptions.verticalScrollBar().value()
		self.fontOptionsScroll = self.fontOptions.verticalScrollBar().value()

		while self.count() >= 1:
			first_widget = self.widget(0)
			self.removeTab(0)
			del first_widget#in this way we actually destroy the widgets instead of merely removing them
		self.setTabs()
			

class SettingsWindow(QMainWindow):

	optionsChanged = pyqtSignal()		

	def __init__(self):
		super().__init__()
		self.setWindowTitle(self.tr("settings_window"))
		self.settingsClass = cruscoplanets.cmdline.svgSettings()
		self.settingsForm = SettingsForm()
		self.settingsForm.optionsChanged.connect(self.optionsChanged.emit)
		self.setCentralWidget(self.settingsForm)
		
		self.toolbar = self.addToolBar(self.tr("actions"))
		save_icon = self.style().standardIcon(QStyle.SP_DialogSaveButton)
		self.save = self.toolbar.addAction(self.tr("save"))
		self.save.setIcon(save_icon)
		self.save.triggered.connect(self.settingsClass.save)
		reset_icon = self.style().standardIcon(QStyle.SP_DialogResetButton)
		self.reset = self.toolbar.addAction(self.tr("reset"))
		self.reset.setIcon(reset_icon)
		self.reset.triggered.connect(self._onReset)
		
	def _onReset(self):
		self.settingsClass.reset()
		self.settingsForm.reset()
		self.optionsChanged.emit()

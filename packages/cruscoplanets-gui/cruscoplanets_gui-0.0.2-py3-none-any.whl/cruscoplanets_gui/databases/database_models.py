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
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QDate, QTime, QDateTime
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import cruscoplanets.cmdline
from .. import config
from . import database_filters


class IdFieldError(Exception):

	def __init__(self):
		super().__init__()
		
	def __str__(self):
		return "ID value can not be edited"


class FieldError(Exception):

	def __init__(self):
		super().__init__()
		
	def __str__(self):
		return "Fields can be set only with the setValue() function"


class Field:

	def __init__(self, name, value):
		self._name = name
		self._value = value
		
	def name(self):
		return self._name
		
	def value(self):
		return self._value
		
	def setValue(self, new_value):
		self._value = new_value
		
	def __repr__(self):
		return "(%s, %s)"%(self._name, self._value)
		
	def __lt__(self, other):
		return self._value < other._value
		
	def __eq__(self, other):
		return self._value == other._value
		
	def valueForFilters(self):
		return self.value()
		

class IdField(Field):

	def __init__(self, name, value):
		super().__init__(name, value)
		
	def setValue(self, new_value):
		return IdFieldError()
		

class SexField(Field):

	def __init__(self, name, value):
		super().__init__(name, value)
		

class LocationField(Field):

	def __init__(self, name, value):
		super().__init__(name, value)
		

class DtStringField(Field):

	def __init__(self, name, value):
		super().__init__(name, value)
		self.is_time_local, self.is_time_known, year, month, day, hour, minute, second = cruscoplanets.cmdline.parseDatetimeString(value)
		self._qdatetime = QDateTime(QDate(year, month, day,), QTime(hour, minute, second))
		
	def valueForFilters(self):
		return self._qdatetime
		
	def __lt__(self, other):
		return self._qdatetime < other._qdatetime
		
	def __eq__(self, other):
		return self._qdatetime == other._qdatetime


class FieldsDict:

	def __init__(self, fields, values):
		self.fieldNames = fields.names()
		_fields = []
		for i in range(len(fields)):
			fieldClass = fields[i].fieldClass()
			_fields.append(fieldClass(fields[i].name(), values[i]))
		self._fields = tuple(_fields)
		
	def __getitem__(self, index):
		if type(index) == int:
			return self._fields[index]
		elif type(index) == str:
			the_index = self.fieldNames.index(index)
			return self._fields[the_index]

	def __setitem__(self, index, value):
		return FieldError("Can not set a new value to a field")
		
	def __iter__(self):
		return iter(self._fields)
		
	def __len__(self):
		return len(self._fields)


class Record(QObject):

	def __init__(self, values, columns):
		self._columns = columns
		self._values = values
		self.fields = FieldsDict(self._columns, values)
		
	def __repr__(self):
		retstr = '(' + ', '.join([field.__repr__() for field in self.fields]) + ')'
		return retstr
		
	def valuesString(self):
		retstr = '(' + ', '.join(["%r"%field.value() for field in self.fields]) + ')'
		return retstr
		
	def _applyFilter(self, thefilter: database_filters.Filter):
		value = self.fields[thefilter.column].valueForFilters()
		return thefilter.check(value)
	
	def primaryKey(self):
		return self.fields[self._columns.primaryKey().index()].value()
		
		
class Column:

	def __init__(self, index, name, type_val, not_null, default, primary_key):
		self._index = index
		self._name = name
		self._header = name
		self._type = type_val
		self._isNotNull = not_null == 1
		self._defaultValue = default
		self._isPrimaryKey = primary_key == 1
		self._fieldClass = IdField if self._isPrimaryKey else Field
		
	def fieldClass(self):
		return self._fieldClass
		
	def setFieldClass(self, the_class):
		self._fieldClass = the_class
	
	def index(self):
		return self._index
	
	def name(self):
		return self._name
	
	def type(self):
		return self._type
	
	def isNotNull(self):
		return self._isNotNull
	
	def defaultValue(self):
		return self._defaultValue
	
	def isPrimaryKey(self):
		return self._isPrimaryKey
		
	def header(self):
		return self._header
	
	def setHeader(self, value):
		self._header = value
		
	def __repr__(self):
		return "%s, %s, not null: %r, default: %r, primary key: %r"%(self.name(), self.type(), self.isNotNull(), self.defaultValue(), self.isPrimaryKey())
		
		
class Columns:

	def __init__(self, col_list):
		self._columns = tuple(col_list)
		
	def indexes(self):
		return tuple(column.index() for column in self._columns)
		
	def names(self):
		return tuple(column.name() for column in self._columns)
		
	def types(self):
		return tuple(column.type() for column in self._columns)
		
	def defaultValues(self):
		return tuple(column.defaultValue() for column in self._columns)
		
	def primaryKey(self):
		ret = None
		for column in self._columns:
			if column.isPrimaryKey() == True:
				ret = column
		return ret
		
	def __repr__(self):
		return '(' + ', '.join(self.names()) + ')'
		
	def __getitem__(self, index_or_name):
		if type(index_or_name) == str:
			index = self.names().index(index_or_name)
		elif type(index_or_name) == int:
			index = index_or_name
		return self._columns[index]
		
	def __iter__(self):
		return iter(self._columns)
		
	def __len__(self):
		return len(self._columns)


class TableModelError(Exception):

	def __init__(self, message):
		super().__init__()
		self.message = message
	
	def __str__(self):
		return self.message
		
		
class TableModel(QObject):

	deleted = pyqtSignal(int)
	updated = pyqtSignal(dict)
	added = pyqtSignal(dict)

	def __init__(self, db, table_name):
		super().__init__()
		self.db = db
		self.tableName = table_name
		self.setColumns()
		self.refresh()
		self.filters = []

	def setColumns(self):
		columns_query = "PRAGMA table_info(%s)"%self.tableName
		columns_result = self.db.exec(columns_query)
		columns = []
		while columns_result.next():
			columns.append(Column(columns_result.value(0), columns_result.value(1), columns_result.value(2), columns_result.value(3), columns_result.value(4), columns_result.value(5)))
		self.columns = Columns(columns)

	def addFilter(self, thefilter: database_filters.Filter):
		self.filters.append(thefilter)
		
	def _applyFilter(self, thefilter: database_filters.Filter, data):
		return filter(lambda record: record._applyFilter(thefilter), data)
		
	def select(self):
		data = self.records
		for thefilter in self.filters:
			data = self._applyFilter(thefilter, data)
		return tuple(data)
		
	def sortByField(self, index_or_name, reverse: bool = False):
		self.records = sorted(self.records, key = lambda record: record.fields[index_or_name], reverse = reverse)
		
	def refresh(self):
		query = ("SELECT * FROM %s"%self.tableName)
		result = self.db.exec(query)
		values_number = result.record().count()
		records = []
		while result.next():
			record = []
			for i in range(values_number):
				record.append(result.value(i))
			records.append(record)
		self.records = tuple(Record(record, self.columns) for record in records)
		#now we cast the primary key field in each record to the IdField class
		
	def updateRecord(self, **kwargs):
		primary_key = self.columns.primaryKey().name()
		if primary_key not in kwargs.keys():
			raise TableModelError("A value for '%s' must be set where updating"%primary_key)
			
		set_values = {key: value for key, value in kwargs.items() if key != primary_key}
		if len(set_values.keys()) == 0:
			print("No field to update has been specified")
			return

		set_values = self._sortByColumnsOrder(set_values.items())
		keys = tuple(value[0] for value in set_values)
		bindParams = tuple(":%s"%key for key in keys)
		expressions = tuple("%s = %s"%(keys[i], bindParams[i]) for i in range(len(keys)))
		values = tuple(value[1] for value in set_values)
		query_str = "UPDATE %s SET "%self.tableName
		query_str += ', '.join(expressions)
		query_str += " WHERE "
		query_str += "%s = :%s"%(primary_key, primary_key)
		query = QSqlQuery(self.db)
		query.prepare(query_str)
		for i in range(len(values)):
			query.bindValue(bindParams[i], values[i])
		query.bindValue(":%s"%primary_key, kwargs[primary_key])
		success = query.exec()
		if success:
			self.updated.emit(kwargs)
			self.refresh()
		else:
			print(query.lastError().text())
		return success

	def deleteRecord(self, id_value):
		query_str = "DELETE FROM " + self.tableName + " WHERE " + self.columns.primaryKey().name() + " = :" + self.columns.primaryKey().name()
		query = QSqlQuery(self.db)
		query.prepare(query_str)
		query.bindValue(":" + self.columns.primaryKey().name(), id_value)
		success = query.exec()
		if success:
			self.deleted.emit(id_value)
			self.refresh()
		else:
			print(query.lastError().text())
		return success
		
	def _deleteByFieldAndValue(self, field, value):
		select_str = "SELECT " + self.columns.primaryKey().name() + " FROM " + self.tableName + " WHERE " + field + " = :" + field
		select = QSqlQuery(self.db)
		select.prepare(select_str)
		select.bindValue(":%s"%field, value)
		select.exec()
		id_values = []
		while select.next():
			id_values.append(select.value(0))
		success = True
		for value in id_values:
			success = self.deleteRecord(value)
		return success
			
	def _sortByColumnsOrder(self, pairs):
		"""Sorts a sequence of key-value pairs, where the keys are the column names, based on the order of the columns in the table"""
		return sorted(pairs, key = lambda couple: self.columns.names().index(couple[0]))
		
	def addRecord(self, **kwargs):
		pairs = self._sortByColumnsOrder(kwargs.items())
		keys = tuple(pair[0] for pair in pairs)
		bindParams = tuple(":%s"%key for key in keys)
		values = tuple(pair[1] for pair in pairs)
		query_str = "INSERT INTO " + self.tableName 
		query_str += "(" + ', '.join(keys) + ')'
		query_str += " VALUES (" + ', '.join(bindParams) + ')'
		query = QSqlQuery(self.db)
		query.prepare(query_str)
		for i in range(len(values)):
			query.bindValue(bindParams[i], values[i])
		success = query.exec()
		if success:
			self.added.emit(kwargs)
			self.refresh()
		else:
			print(query.lastError().text())
		return success
			
	def __repr__(self):
		ret_str = self.columns.__repr__()
		ret_str += '\n' +'-'*len(ret_str) + '\n'
		ret_str += '\n'.join([record.valuesString() for record in self.select()])
		return ret_str			


class PeopleTableModel(TableModel):

	def __init__(self, db):
		super().__init__(db, 'people')

	def setColumns(self):
		super().setColumns()
		self.columns['name'].setHeader(self.tr('name'))
		self.columns['surname'].setHeader(self.tr('surname'))
		self.columns['sex'].setHeader(self.tr('sex'))
		self.columns['sex'].setFieldClass(SexField)
		self.columns['birthdtstring'].setHeader(self.tr('birthdtstring'))
		self.columns['birthdtstring'].setFieldClass(DtStringField)
		self.columns['birthlocationid'].setHeader(self.tr('birthlocationid'))
		self.columns['birthlocationid'].setFieldClass(LocationField)
		
	def addRecord(self, name, surname, sex, birthdtstring, birthlocationid):
		kwargs = {
			'id': None,#id None will set automatically the value as autoincrement in the SQL database
			'name': name,
			'surname': surname,
			'sex': self.columns['sex'].defaultValue() if sex == None else sex,
			'birthdtstring': birthdtstring if birthdtstring != None else config.Configuration().DEFAULT_DTSTRING,
			'birthlocationid': birthlocationid if birthlocationid != None else config.Configuration().DEFAULT_LOCATION
		}
		return super().addRecord(**kwargs)
	
	def addVoidRecord(self):
		return self.addRecord(name = None, surname = None, sex = None, birthdtstring = None, birthlocationid = None)
		

class PersonalDatabaseModel(QObject):

	def __init__(self):
		super().__init__()
		self.personaldb = QSqlDatabase.addDatabase("QSQLITE")
		self.personaldb.setDatabaseName(config.Configuration().databaseFilePath())
		self._initDatabase()
		self.peopleTable = PeopleTableModel(self.personaldb)

	def _initDatabase(self):
		if not self.personaldb.open():
			print(self.personaldb.lastError().text())
			sys.exit(1)
		self.personaldb.exec("""
		CREATE TABLE IF NOT EXISTS people (
			id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
			name TEXT,
			surname TEXT,
			sex INTEGER CHECK( sex IN (-1, 0, 1)) NOT NULL DEFAULT -1,
			birthdtstring TEXT NOT NULL,
			birthlocationid INT NOT NULL
		);
		""")

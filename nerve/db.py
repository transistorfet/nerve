#!/usr/bin/python
# -*- coding: utf-8 -*-

import nerve

import apsw
import os.path


class Database (object):
    def __init__(self, filename):
	self.filename = filename
	self.dbcon = apsw.Connection(os.path.join(nerve.configdir(), filename))


class DatabaseCursor (object):
    def __init__(self, db):
	self.db = db
	self.dbcursor = self.db.dbcon.cursor()
	self.reset_cache()

    def reset_cache(self):
	self.cache_where = u""
	self.cache_group = u""
	self.cache_order = u""
	self.cache_limit = u""
	self.cache_select = u"*"
	self.cache_distinct = u""

    def query(self, q):
	self.dbcursor.execute(text)

    def table_exists(self, name):
        for row in self.dbcursor.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name = '" + name + "' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table','view') AND name = '" + name + "'"):
            return True
        return False

    def create_table(self, table, columns):
	self.dbcursor.execute(u"CREATE TABLE IF NOT EXISTS %s (%s)" % (table, columns))

    def escape(self, text):
	if text is None:
	    return u""
	if isinstance(text, str):
	    text = unicode(text, 'utf-8')
	elif not isinstance(text, unicode):
	    text = str(text)
	return text.replace(u"'", u"''")

    def inline_expr(self, name, val, compare='='):
	return u"%s%s'%s' " % (name, compare, self.escape(val))

    def where(self, where, val, compare='='):
	where_sql = self.inline_expr(where, val, compare)
	if not self.cache_where:
	    self.cache_where = where_sql
	else:
	    self.cache_where += u" AND " + where_sql

    def where_not(self, where, val):
	self.where(where, val, "<>")

    def where_gt(self, where, val):
	self.where(where, val, ">")

    def where_lt(self, where, val):
	self.where(where, val, "<")

    def where_like(self, where, val):
	self.where(where, val, " LIKE ")

    def set_where(self, where):
	self.cache_where = where

    def group_by(self, group):
	self.cache_group = group

    def order_by(self, order):
	self.cache_order = order

    def limit(self, limit):
	self.cache_limit = limit

    def select(self, fields):
	self.cache_select = fields

    def distinct(self, enabled):
	if enabled is True:
	    self.cache_distinct = u'DISTINCT'
	else:
	    self.cache_distinct = u""

    def compile_clauses(self):
	query = u""
	if self.cache_where:
	    query += u"WHERE %s " % (self.cache_where,)
	if self.cache_group:
	    query += u"GROUP BY %s " % (self.cache_group,)
	if self.cache_order:
	    query += u"ORDER BY %s " % (self.cache_order,)
	if self.cache_limit:
	    query += u"LIMIT %s " % (self.cache_limit,)
	return query

    def compile_select(self, table, select=None, where=None):
	if select is not None:
	    self.cache_select = select
	if where is not None:
	    self.cache_where = where

	query = u"SELECT %s %s FROM %s " % (self.cache_distinct, self.cache_select, table)
	query += self.compile_clauses()
	return query

    def get(self, table, select=None, where=None):
	query = self.compile_select(table, select, where)
	#print query
	result = self.dbcursor.execute(query)
	#result = self.dbcursor.execute(query.decode('utf-8'))
	self.reset_cache()
	return result

    def get_assoc(self, table, select=None, where=None):
	query = self.compile_select(table, select, where)
	#print query.encode('utf-8', 'replace')
	result = self.dbcursor.execute(query)
	#result = self.dbcursor.execute(query.decode('utf-8'))

	# TODO this doesn't work with SELECT *
	keys = [ key.strip() for key in self.cache_select.split(',') ]
	rows = [ ]
	for row in result:
	    assoc = { }
	    for i in range(len(keys)):
		if isinstance(row[i], unicode):
		    assoc[keys[i]] = row[i].encode('utf-8')
		else:
		    assoc[keys[i]] = row[i]
	    rows.append(assoc)

	self.reset_cache()
	return rows

    def get_single(self, table, select=None, where=None):
	result = list(self.get(table, select, where))
	if len(result) > 0:
	    return result[0]
	else:
	    return None

    def insert(self, table, data, replace=False):
	columns = data.keys()
	values = [ ]
	for key in columns:
	    values.append(u"\'%s\'" % (self.escape(data[key]),))

	insert = 'INSERT' if replace is False else 'INSERT OR REPLACE'
	query = u"%s INTO %s (%s) VALUES (%s)" % (insert, table, ','.join(columns), ','.join(values))
	#print query
	self.dbcursor.execute(query)
	#self.dbcursor.execute(query.decode('utf-8'))
	self.reset_cache()

    def update(self, table, data, where=None):
	if where is not None:
	    self.cache_where = where

	values = [ ]
	for key in data.keys():
	    values.append(u"%s=\'%s\'" % (key, self.escape(data[key])))

	query = u"UPDATE %s SET %s " % (table, ','.join(values))
	query += self.compile_clauses()
	#print query
	result = self.dbcursor.execute(query)
	#result = self.dbcursor.execute(query.decode('utf-8'))
	self.reset_cache()
	return result

    """
    def select(self, table, values=None, where=None, whereval=None, order_by=None):
	if values is None:
	    values = '*'
	query = "SELECT %s FROM %s " % (values, table)
	if where is not None:
	    query += "WHERE %s='%s' " % (where, self.escape(whereval))
	if order_by is not None:
	    query += "ORDER BY %s " % (order_by,)
	return self.dbcursor.execute(query.decode('utf-8'))
    """

 

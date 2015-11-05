#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nerve

import apsw
import os.path


class Database (object):
    databases = { }

    def __init__(self, filename):
        if filename not in Database.databases:
            Database.databases[filename] = apsw.Connection(os.path.join(nerve.configdir(), filename))
        self.dbcon = Database.databases[filename]
        self.reset_cache()

    def reset_cache(self):
        self.cache_where = ""
        self.cache_group = ""
        self.cache_order = ""
        self.cache_offset = ""
        self.cache_limit = ""
        self.cache_select = "*"
        self.cache_distinct = ""

    def query(self, query, bindings=None):
        dbcursor = self.dbcon.cursor()
        result = dbcursor.execute(query, bindings)
        try:
            self.columns = dbcursor.getdescription()
        except apsw.ExecutionCompleteError:
            self.columns = [ ]
        return result

    def table_exists(self, name):
        for row in self.query("SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name = '" + name + "' UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table','view') AND name = '" + name + "'"):
            return True
        return False

    def create_table(self, table, columns):
        self.query("CREATE TABLE IF NOT EXISTS %s (%s)" % (table, columns))

    def get_column_info(self, table):
        dbcursor = self.dbcon.cursor()
        result = dbcursor.execute("PRAGMA table_info(" + table + ")")
        return list(result)

    def add_column(self, table, column, datatype, default=None):
        self.query("ALTER TABLE %s ADD COLUMN %s %s" % (table, column, datatype))

    def escape(self, text):
        if text is None:
            return ""
        text = str(text)
        return text.replace("'", "''")

    def inline_expr(self, name, val, compare='='):
        return "%s %s '%s' " % (name, compare, self.escape(val))

    def where(self, where, val, compare='=', cond='AND'):
        where_sql = self.inline_expr(where, val, compare)
        if not self.cache_where:
            self.cache_where = where_sql
        else:
            self.cache_where += " %s %s" % (cond, where_sql)

    def where_not(self, where, val):
        self.where(where, val, "<>")

    def where_gt(self, where, val):
        self.where(where, val, ">")

    def where_lt(self, where, val):
        self.where(where, val, "<")

    def where_like(self, where, val):
        self.where(where, val, "LIKE")

    def where_not_like(self, where, val):
        self.where(where, val, "NOT LIKE")

    def or_where(self, where, val):
        self.where(where, val, "=", "OR")

    def or_where_not(self, where, val):
        self.where(where, val, "<>", "OR")

    def or_where_gt(self, where, val):
        self.where(where, val, ">", "OR")

    def or_where_lt(self, where, val):
        self.where(where, val, "<", "OR")

    def or_where_like(self, where, val):
        self.where(where, val, "LIKE", "OR")

    def or_where_not_like(self, where, val):
        self.where(where, val, "NOT LIKE", "OR")

    def set_where(self, where):
        self.cache_where = where

    def group_by(self, group):
        self.cache_group = group

    def order_by(self, order):
        self.cache_order = order

    def limit(self, limit):
        self.cache_limit = limit

    def offset(self, offset):
        self.cache_offset = offset

    def select(self, fields):
        self.cache_select = fields

    def distinct(self, enabled):
        if enabled is True:
            self.cache_distinct = 'DISTINCT'
        else:
            self.cache_distinct = ""

    def compile_clauses(self):
        query = ""
        if self.cache_where:
            query += "WHERE %s " % (self.cache_where,)
        if self.cache_group:
            query += "GROUP BY %s " % (self.cache_group,)
        if self.cache_order:
            query += "ORDER BY %s " % (self.cache_order,)
        if self.cache_limit:
            query += "LIMIT %s " % (self.cache_limit,)
        if self.cache_offset:
            query += "OFFSET %s " % (self.cache_offset,)
        return query

    def compile_select(self, table, select=None, where=None):
        if select is not None:
            self.cache_select = select
        if where is not None:
            self.cache_where = where

        query = "SELECT %s %s FROM %s " % (self.cache_distinct, self.cache_select, table)
        query += self.compile_clauses()
        return query

    def get(self, table, select=None, where=None):
        query = self.compile_select(table, select, where)
        #print (query)
        result = self.query(query)
        self.reset_cache()
        return result

    def get_assoc(self, table, select=None, where=None):
        query = self.compile_select(table, select, where)
        #print (query)
        result = self.query(query)

        keys = self.columns
        rows = [ ]
        for row in result:
            assoc = { }
            for i, key in enumerate(keys):
                (column, datatype) = key
                assoc[column] = row[i]
            rows.append(assoc)

        self.reset_cache()
        return rows

    def get_single(self, table, select=None, where=None):
        result = list(self.get(table, select, where))
        if len(result) > 0:
            return result[0]
        else:
            return None

    def get_columns(self):
        #return self.dbcursor.getdescription()
        return self.columns

    def insert(self, table, data, replace=False):
        columns = data.keys()
        values = [ ]
        for key in columns:
            values.append(u"\'%s\'" % (self.escape(data[key]),))

        insert = 'INSERT' if replace is False else 'INSERT OR REPLACE'
        query = "%s INTO %s (%s) VALUES (%s)" % (insert, table, ','.join(columns), ','.join(values))
        #print (query)
        result = self.query(query)
        self.reset_cache()
        return result

    def update(self, table, data, where=None):
        if where is not None:
            self.cache_where = where

        values = [ ]
        for key in data.keys():
            values.append("%s=\'%s\'" % (key, self.escape(data[key])))

        query = "UPDATE %s SET %s " % (table, ','.join(values))
        query += self.compile_clauses()
        #print (query)
        result = self.query(query)
        self.reset_cache()
        return result

    def delete(self, table, where=None):
        if where is None:
            where = self.cache_where

        query = "DELETE FROM %s WHERE %s" % (table, where)

        result = self.query(query)
        self.reset_cache()
        return result

 

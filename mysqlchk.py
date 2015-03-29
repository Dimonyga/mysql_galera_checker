#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from mysql.connector import MySQLConnection, Error
from iniparse import ConfigParser

PORT_NUMBER = 8080
MYSQL_CONFIG = '/etc/my.cnf.d/mysql-clients.cnf'

def read_db_config(filename='/etc/my.cnf', section='mysql'):
	parser = ConfigParser()
	parser.read(filename)
	db = {}
	if parser.has_section(section):
		items = parser.items(section)
		for item in items:
			db[item[0]] = item[1]
	else:
		raise Exception('{0} not found in the {1} file'.format(section, filename))
	return db

def connect():
	db_config = read_db_config(MYSQL_CONFIG)
	try:
		conn = MySQLConnection(**db_config)
	except Error as error:
		print(error)
	return conn

class mysqlchk(BaseHTTPRequestHandler):

	db = connect()
	mysql = db.cursor()

	def do_GET(self):
		sql= "SHOW STATUS LIKE 'wsrep_local_state';"
		if self.db.is_connected() == 0:
			self.db = connect()
			self.mysql = self.db.cursor()
			print ('reconnect to mysql')
		self.mysql.execute (sql)
		row = self.mysql.fetchone()
		if row[1] == '4':
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write("OK")
		else:
			self.send_response(503)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write("ERR")
		return
try:
	server = HTTPServer(('', PORT_NUMBER), mysqlchk)
	print 'Started httpserver on port ' , PORT_NUMBER
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()


#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from mysql.connector import MySQLConnection, Error
from iniparse import ConfigParser
import sys, time, os.path
from inc.daemon import Daemon


PORT_NUMBER = 8080
MYSQL_CONFIG = '/etc/my.cnf.d/mysql-clients.cnf'

class mysqlchk(Daemon):

	def read_db_config(self,filename='/etc/my.cnf', section='mysql'):
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

	def connect(self):
		db_config = self.read_db_config(MYSQL_CONFIG)
		try:
			conn = MySQLConnection(**db_config)
		except Error as error:
			print(error)
		return conn


	def do_GET(self):
		sql= "SHOW STATUS LIKE 'wsrep_local_state';"
		if self.db.is_connected() == 0:
			self.db = connect()
			self.mysql = self.db.cursor()
			print('reconnect to mysql')
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
	def run(self):
		try:
			db = self.connect()
			mysql = db.cursor()
			server = HTTPServer(('', PORT_NUMBER), mysqlchk)
			server.serve_forever()
		finally:
			print('shutting down the web server')

if __name__ == "__main__":
        daemon = mysqlchk('/tmp/daemon-example.pid', '/dev/null', '/dev/null', '/dev/stderr')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
        else:
                print "usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)

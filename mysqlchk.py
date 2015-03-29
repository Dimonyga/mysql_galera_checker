#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import MySQLdb

PORT_NUMBER = 8080
MYSQL_USER = "root"
MYSQL_PASSWORD = ""

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		sql= "SHOW STATUS LIKE 'wsrep_local_state';"
		mysql.execute (sql)
		#state = mysql.fetchone()
		#self.wfile.write(state)
		#print state
		row = mysql.fetchone()
		#print row[0], "-->", row[1]
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
	#Create a web server and define the handler to manage the
	#incoming request
	db = MySQLdb.connect(host="localhost", user=MYSQL_USER, passwd=MYSQL_PASSWORD, db="mysql", charset='utf8')
	mysql = db.cursor()
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()


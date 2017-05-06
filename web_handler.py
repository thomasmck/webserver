import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer

import os
import glob
import time
import calendar
import time
import wiringpi
from time import sleep

"""Simple HTTP server in python.
Usage::
    ./dummy-web-server.py [<port>]
Send a GET request::
    curl http://localhost
Send a HEAD request::
    curl -I http://localhost
Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost
"""

wiringpi.wiringPiSetup()
os.system('modprobe w1-gpio')
base_dir = ('/sys/bus/w1/devices/')
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

class S(BaseHTTPRequestHandler):
    commands = {"on": 1, "off": 0}
    pins = {"fan": 0, "light": 1}    

    def set_power(self, pin_number, state):
        wiringpi.pinMode(pin_number, 1)
        wiringpi.digitalWrite(pin_number, state)
        print "You set pin %s to %d" %(pin_number, state)

    def get_details(self, appliance, state):
        pin_number = self.pins[appliance]
        state = self.commands[state.lower()] 
        return pin_number, state

    def run_commands(self, postvars):
        print "Run commands"
        for key, value in postvars.iteritems():
            pin_number, state = self.get_details(key, value[0])
            self.set_power(pin_number, state)
            
    def handle_POST_data(self, data):
        print data 
        ctype, pdict = data
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        self._set_headers()
        postvars = self.handle_POST_data(cgi.parse_header(self.headers.getheader('content-type')))
        self.wfile.write(postvars)
        self.run_commands(postvars)

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
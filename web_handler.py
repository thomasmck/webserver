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

import argparse

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
    #first number is the pin number, second is the state
    pins = {"fan": [0, 0], "light": [1, 0]}    

    def set_power(self, pin_number, state, appliance):
        wiringpi.pinMode(pin_number, 1)
        wiringpi.digitalWrite(pin_number, state)
        self.pins[appliance] = [pin_number, state]
        print "You set pin %s to %d" %(pin_number, state)

    def get_details(self, appliance, state):
        pin_number = self.pins[appliance][0]
        state = self.commands[state.lower()] 
        return pin_number, state

    def run_commands(self, postvars):
        print "Run commands"
        for key, value in postvars.iteritems():
            self.wfile.write("You set the %s to %s \n" %(key, value[0]))
            pin_number, state = self.get_details(key, value[0])
            self.set_power(pin_number, state, key)
            
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
        for key, value in self.pins.iteritems():
            self.wfile.write("<html><body><h1>%s: %d</h1></body></html>" %(key,value[1]))

    def do_POST(self):
        self._set_headers()
        postvars = self.handle_POST_data(cgi.parse_header(self.headers.getheader('content-type')))
        self.run_commands(postvars)

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description='Handle address port')
    parser.add_argument('port', metavar='p', type=int, default="80", nargs='?')
    args = parser.parse_args()
    run(port=args.port) 

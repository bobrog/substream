#! /usr/bin/env python

import os
import sys
import libsonic
import time
import re
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from pprint import pprint

class SubStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if re.match('^/song/*', self.path):
            sid = re.match('^/song/(\d+)', self.path)
            if not sid:
                self.send_response(400, 'Bad Request - Missing Song ID')
                return
            try:
                song = subsonic.getSong(sid.group(1))
            except libsonic.errors.SonicError:
                self.send_response(404, 'Song ID not found')
                return
            self.send_response(200)
            self.send_header("Content-type", "audio/mpeg")
            self.end_headers()
            self.wfile.write(subsonic.stream(sid = song['song']['id'], tformat = 'raw').read())
        elif re.match('^/pl/*', self.path):
            plid = re.match('^/pl/(\d+)', self.path)
            if not plid:
                self.send_response(400, 'Bad Request - Missing Playlist ID')
                return
            try:
                pl = subsonic.getPlaylist(plid.group(1))
            except libsonic.errors.SonicError:
                self.send_response(404, 'Playlist ID not found')
                return
            self.send_response(200)
            self.send_header("Content-type", "audio/mpeg")
            self.end_headers()
            for song in pl['playlist']['entry']:
                self.wfile.write(subsonic.stream(sid = song['id'], tformat = 'raw').read())    
        elif re.match('^/+$', self.path):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write('%-3s - %s\n\n' % ('ID', 'Name'))
            playlists = subsonic.getPlaylists()
            for p in playlists['playlists']['playlist']:
                 self.wfile.write('%-3d - %s\n' % (p['id'], p['name'])) 
        else:
            self.send_response(404, 'Not Found')

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ == '__main__':
    # Load config
    from ConfigParser import RawConfigParser
    config = RawConfigParser()
    config.read('config')
    host_name = config.get('substream', 'INTERFACE')
    port_number = int(config.get('substream', 'PORT'))
    ss_base = config.get('subsonic', 'BASEURL')
    ss_path = config.get('subsonic', 'SERVERPATH')
    ss_port = config.get('subsonic', 'PORT')
    ss_user = config.get('subsonic', 'USERNAME')
    ss_pass = config.get('subsonic', 'PASSWORD')
    
    # Create the py-sonic connection object
    subsonic = libsonic.Connection(ss_base, ss_user, ss_pass, 
            port = ss_port, serverPath = ss_path, appName = 'substream')

    server_class = ThreadedHTTPServer
    httpd = server_class((host_name, port_number), SubStreamHandler)
    print time.asctime(), "Server Starts - %s:%s" % (host_name, port_number)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (host_name, port_number)



from si_b_http import BaseHTTPRequestHandler, HTTPServer

#import asyncio
import json
import logging
from sys import argv

from si_serve_routing import route_fs_get, route_get, route_post
from serve_config import *
from serve_util import *
"""

 ##Test with Curl

OPTIONS
curl -v -X OPTIONS  http://localhost:1110/

HEAD
curl -I  http://localhost:1110/si_serve_home.js
curl -I  http://localhost:1110/si_serve_home.css

GET
curl -X GET http://localhost:1110/

POST
 curl -X POST  -H "Accept: Application/json" -H "Content-Type: application/json" http://localhost:1110/post_test_data -d '{"id":"si post key","name":"si post val"}'


 ##Start python with permissions and pipe output to null ~

exec sudo -u www-data /usr/bin/python /data/examples/python_minimal_http/server.py 8009 >> /dev/null 2>> /dev/null
"""

'''
Other routing options ~ 
Local Static File Server ( use to avoid writing urls for everything )

By default, server binds itself to all interfaces. The option -b/--bind specifies a specific address to which it should bind. Both IPv4 and IPv6 addresses are supported.
For example, the following command causes the server to bind to localhost only:
python -m http.server 8000 --bind 127.0.0.1
New in version 3.4: --bind argument was introduced.
New in version 3.8: --bind argument enhanced to support IPv6

By default, server uses the current directory. The option -d/--directory specifies a directory to which
 it should serve the files. For example, the following command uses a specific directory:
python -m http.server --directory /tmp/

import http.server
import socketserver

PORT = 7777
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()

'''



class SC_Root_Server(BaseHTTPRequestHandler):
   
    def __init__(self, *args, **kwargs):
        print("SI Server Init ~ ")
        print(" Server Methods ~~ " + str( dir(BaseHTTPRequestHandler) ))
        super().__init__(*args, **kwargs)

    def si_HEAD(self):
        print("SI serve HEAD headers")
        
        req_found = True
        g_resp, get_stat = self.handle_get(self.path)
        
        if get_stat == 404 or get_stat == 555:
            self._headers_buffer = []
            p_resp, post_stat = self.handle_post(self.path, "head")
        
        


    def si_OPTIONS(self):
        #self.send_response(HTTPStatus.NO_CONTENT.value)
        print("SI serve OPTIONS headers")    
        self.send_response(200)
        
        self.send_header("Allow", "GET, POST, HEAD, OPTIONS")
        
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,HEAD,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Origin', '*') 
        
        self.send_header('Cache-Control', 'no-store')
        
        self.end_headers()

    def handle_get(self, qpath):
        get_stat = 555
        get_encresp = ""
        get_ctx_resp = ""

        # look for /static/path routes
        pgs = qpath.split("/")[1]


        if pgs == "static":
            print("use static file resp")
            get_encresp, resp_type, get_stat = route_fs_get( qpath)
            print("check ctypes with content type gc_resp ~ " + str(resp_type))
            need_encode_resp = check_ctypes_for_enc(resp_type)

            if need_encode_resp == True:
                get_encresp = get_encresp.encode("utf-8")
            
            print("send resp")
            self.send_response(get_stat)
            self.send_header('Content-type', resp_type )
            self.send_header('Content-length', len(get_encresp))
            print("wfile encode resp")

        else:
            print("route get with url")
            get_encresp, resp_type, get_stat = route_get(qpath)
            self.send_response(get_stat)
            self.send_header('Content-type', resp_type)
            
            c, need_encode_resp = check_ctypes_for_enc( resp_type )
            
            if need_encode_resp == True:
                get_encresp = get_encresp.encode("utf-8")
            
            #self.send_header('Content-length', len(get_encresp))
    
        self.end_headers()
        
        return get_encresp, get_stat

    def si_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        gheaders = self.headers
        print("GET headers ~")
        print( str(gheaders ))

        # could add ctx type check here later but not neccessary, force cli to adhere
        accept_type = ""
        for h,v in gheaders.items():
            print(" headers ~ "+str(h)+" ::: " + str(v))
            if h =="Accept":
                print("cd accept ctx ~ " + str(v))
                accept_type = v

        qpath = str(self.path)
      
        get_resp, get_stat = self.handle_get( qpath )
        
        self.wfile.write( get_resp )

    def handle_post(self, ppath, post_data):
        post_encresp = route_post( ppath, post_data )
        post_stat = 555
        if post_encresp["success"] == True:
            post_stat = 200
            self.send_response(200)
            self.send_header('Content-type', defcon_type )
        if post_encresp["success"] == False:
            post_stat = 404 
            self.send_response(404)

        print("POST resp pre encode ", post_encresp )
        
        encode_resp=json.dumps( post_encresp)
        print("encoded resp ~ " + encode_resp)
        self.send_header('Content-length', len(encode_resp))

        self.end_headers()

        return encode_resp, post_stat
        
    # POST echoes the message adding a JSON field
    def si_POST(self):
        #contype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        ppath = str( self.path )
        print("post  PATH ~ " + ppath )
        pheaders = self.headers 
        print( "POST req  Headers  ~ " + str( pheaders ))

        post_data = {"null post": "no data"}
        print("cont length header ~ " + str( pheaders["content-length"]))
        if pheaders['content-length'] != None:
            length = int(self.headers['content-length'])
            post_data = self.rfile.read(length)
        
        print("POST data ")
        print( str(post_data))
        # return json to encode, or 404 if route not found
        print("args for handle ppapth " + ppath )
        print("Args for handle pdata " + str(post_data))
        raw_resp, post_stat = self.handle_post(ppath, post_data)

        print("end headers write resp")
        self.wfile.write(raw_resp.encode("utf-8"))

       

# mark async to use asyncio
def run_sc_root(server_class=HTTPServer, handler_class=SC_Root_Server, port=g_port ):
    server_address = ('localhost', g_port)
    httpd = server_class(server_address, handler_class)
    print('Starting root sc bttp daemon on port %d...' % g_port)
    httpd.serve_forever()

    
def scm_start():
    logging.basicConfig(level=logging.DEBUG)
    logging.info(" si base http server INIT ")
        
    run_sc_root()
    
    ## with async
    # sst = asyncio.create_task(run_sc_static())
    # rst = asyncio.create_task(run_sc_root())
    # await sst


scm_start()

# Can run with asyncio
# asyncio.run_until_complete(scm_astart())

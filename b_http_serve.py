
from si_b_http import BaseHTTPRequestHandler, HTTPServer

#import asyncio
import json
import logging
from sys import argv

from si_serve_routing import route_fs_get, route_get, route_post
from serve_config import *


# Test Curl
# curl -X POST  -H "Accept: Application/json" -H "Content-Type: application/json" http://localhost:8888/test_post_data -d '{"id":"si post key","name":"si post val"}'

## Start python with permissions and pipe output to null ~
#exec sudo -u www-data /usr/bin/python /data/examples/python_minimal_http/server.py 8009 >> /dev/null 2>> /dev/null


'''
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

g_port = 1110
defcon_type = 'application/json'


def check_ctypes_for_enc(c_resp):
    print("check for ctext type in c_resp ~ " + str(c_resp))
    encode_resp = False
    if "text/html,application/xhtml+xml," in c_resp or "application/xml;q=0.9" in c_resp or c_resp == "text/html;" or c_resp == "text/html; charset=utf-8":
        print("found text/ html and no multiline python or statements ...")
        encode_resp = True
    if c_resp == "text/javascript;" or c_resp == "text/javascript; charset=utf-8":
        print("found js ctext")
        encode_resp = True

    if  "text/css;" in c_resp or  "text/css; charset=utf-8" or "text/css,*/*;q=0.1" in c_resp:
        print("check_ctypes_for_enc css")
        encode_resp = True

    
    if "image/*" in c_resp or  "image/jpeg;" in c_resp or "image/jpg;" in c_resp or "image/png;" in c_resp:
        print("check_ctypes_for_enc image jpg")
        encode_resp = False
    
    print("check ctypes return ~ " + str(encode_resp))
    return encode_resp

class SC_Root_Server(BaseHTTPRequestHandler):
   
    def __init__(self, *args, **kwargs):
        print("SI Server Init ~ ")
        print(" Server Methods ~~ " + str( dir(BaseHTTPRequestHandler) ))
        super().__init__(*args, **kwargs)

    def si_HEAD(self):
        print("Root HEAD")
        print("set head headers")
        self.send_header("Accept", "*/*") 
        self.send_header("Accept-Encoding", "*/*" )
        self.send_header("Allow", "GET, POST, HEAD, OPTIONS")
        
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,HEAD,OPTIONS') 
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Origin', '*')
      
        self.send_header('Cache-Control', 'no-store')
        
        self.send_header('Sec-Fetch-Site', '')
        self.send_header('Sec-Fetch-Mode', '')

        self.send_response(200)



    def si_OPTIONS(self):
        # Send allow-origin header for preflight POST XHRs.
        #self.send_response(HTTPStatus.NO_CONTENT.value)
        print("Root OPTIONS set headers")
        
        #self.send_header("Accept", "text/html;q=.9, application/json;q=.8, application/xml;q=0.7,") 
        self.send_response(200)
        self.end_headers()

    
    def si_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        gheaders = self.headers
        print("GET headers ~")
        print( str(gheaders ))

        accept_type = ""
        for h,v in gheaders.items():
            print(" headers ~ "+str(h)+" ::: " + str(v))
            if h =="Accept":
                print("cd accept ctx ~ " + str(v))
                accept_type = v

        qpath = str(self.path)
        # look for /static/path routes
        print("route get with ctype ~ " + str(accept_type) )
        pgs = qpath.split("/")[1]

        get_stat = 555
        get_encresp = ""
        get_ctx_resp = ""

        if pgs == "static":
            print("use static file resp")
            get_encresp, resp_type, get_stat = route_fs_get( qpath, accept_type )
            print("check ctypes with content type gc_resp ~ " + str(resp_type))
            need_encode_resp = check_ctypes_for_enc(resp_type)

            if need_encode_resp == True:
                get_encresp = get_encresp.encode("utf-8")
            
            print("send resp")
            self.send_response(get_stat)
            self.send_header('Content-type', )
            print("wfile encode resp")
            self.end_headers()

        else:
            print("route get with url")
            get_encresp, resp_type, get_stat = route_get(qpath)
            self.send_response(get_stat)
            self.send_header('Content-type', resp_type)
            self.end_headers()
            
            need_encode_resp = check_ctypes_for_enc( resp_type )
            if need_encode_resp == True:
                get_encresp = get_encresp.encode("utf-8")
        
        self.wfile.write( get_encresp )


#header options ~ 'Cache-Control', 'no-store') 'Accept-Ranges', 'bytes') 'Content-Encoding', 'br')
    def set_post_headers(self, contype, conlen):
        print("call set_headers")    
        
        self.send_header('Access-Control-Allow-Credentials', 'true')
        
        self.send_header('Access-Control-Allow-Origin', '*')
        if len(contype) < 1:
            print("set_header contype not set ~ set def con type" )
            self.send_header('Content-type', defcon_type )
        else:
            print("setting contype ~ " + str( contype ))
            self.send_header('Content-type', contype )
        print("set content-length ") 
        self.send_header('Content-Length', str(conlen) )

    # POST echoes the message adding a JSON field
    def si_POST(self):
        #contype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        ppath = str( self.path )
        print("post  PATH ~ " + ppath )
        # print("call get headers ")
        pheaders = self.headers 
        print( "Root POST REQ HEADERS ~ " + str( pheaders ))

        post_data = {"null post": "no data"}
        print("cont length header ~ " + str( self.headers["content-length"]))
        if self.headers['content-length'] != None:
            length = int(self.headers['content-length'])
            post_data = self.rfile.read(length)
        
        print("POST data ")
        print( str(post_data))
        # return json to encode, or 404 if route not found
        resp = None
        resp = route_post( ppath, post_data )
        
        print("POST resp pre encode ", resp )
        
        encode_resp=json.dumps(resp)
        print("encoded resp ~ " + encode_resp)
        # send the message back if route_post returns not 404
        self.send_response(200)
        print("send post resp 2")
        ler = len(encode_resp)
        print("get len encode resp ~ " + str(ler))
        print("set post resp default content type ~" + defcon_type)

        self.set_post_headers(defcon_type, ler)
        print("set ph")
        self.end_headers()
        print("end headers write resp")
        self.wfile.write(encode_resp.encode("utf-8"))

       

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

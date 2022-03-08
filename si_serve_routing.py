
import pprint
import json

from serve_config import *

def route_fs_get(get_path, get_cd_ctx):
    print("route_fs_get call ROUTE ~ " + str( get_path ))
    b_resp = ""
    c_resp = ""
    stat = 404

    # get file name
    q_path_fn = get_path.split("static/")[1]

    # Cut last slash for dir str lookup
    if sf_spath[ len(sf_spath) - 1] == "/":
        sf_spath = sf_spath[0:len(sf_spath) - 1]

    print("open sf path ~ " + str(sf_spath))
    
    #context type check
    if "html" in q_path_fn:
        c_resp = "text/html"
        if "text/html" not in get_cd_ctx:
            stat = 500
            req_resp = "Ctx type error" 
            c_resp = "text/html"
            return req_resp, c_resp, stat
        # etc if api cares
    
    try:
        with open( q_path ) as sresp:
            b_resp = sresp.read()
    except:
        print("couldnt open sc static dir ... err out")
        stat = 404
        with open('SI_src/si_notfound.html', 'r') as nff:
            b_resp = nff.read()
    
        c_resp = "text/html; charset=utf-8"
        return b_resp, c_resp, stat   
    stat = 200

    return b_resp, c_resp, stat

def route_get(q_path):
    print("route_get call ROUTE ~ " + q_path )
    get_resp = ""
    c_resp = ""
    stat = 404

    print("len qpath ~ " + str( len(q_path)))
    sq_path = q_path
    # Cut last slash for dir str lookup
    if len(q_path) > 1 and q_path[ len(q_path) - 1] == "/":
        sq_path = q_path[0:len(q_path) - 1]

    print("sanitized query path ~ " + sq_path )
    #HTML
    if sq_path == "/":
        with open('routes/si_serve_home.html', 'r') as jhct:
            get_resp = jhct.read()
        stat = 200
        c_resp = "text/html; charset=utf-8"


    # JS
    elif sq_path == "/si_serve_home.js":
        with open('routes/si_serve_home.js', 'r') as jhct:
            get_resp = jhct.read()
        stat = 200
        c_resp = "text/javascript; charset=utf-8"

    # CSS
    elif sq_path== "/si_serve_home.css":
        with open('routes/si_serve_home.css', 'r') as jhct:
            get_resp = jhct.read()
        stat = 200
        c_resp = "text/css; charset=utf-8"

    #MEDIA
    elif sq_path == "/si_media/si_drip_logo_png":
        with open('media_routes/si_fav_drip.png', 'rb') as jhct:
            get_resp = jhct.read()
        stat = 200
        c_resp = "image/png;"
    
    
    elif sq_path == "/favicon.ico":
        with open('media_routes/si_fav_drip.png', 'rb') as jhct:
            get_resp = jhct.read()
        stat = 200
        c_resp = "image/png;"

    # Config
    elif sq_path == "/manifest.webmanifest":
        with open('routes/manifest.webmanifest', 'r') as jhct:
            get_resp = jhct.read()
        stat = 200
        c_resp = "application/manifest+json"
    

    else:
        print("get NOT FOUND call 404 resp")     
        with open('routes/si_notfound.html', 'r') as jhct:
            get_resp = jhct.read()
        
        stat = 404
        c_resp = "text/html; charset=utf-8"
    
    return get_resp, c_resp, stat


def route_post(q_path, post_data):
    print("route_post called with path ~ " + str( q_path ))
    
    # Cut last slash for route str lookup
    sq_path = ""
    if len(q_path) > 1 and q_path[ len(q_path) - 1] == "/":
        sq_path = q_path[0:len(q_path) - 1]

    pd_load = "unable to load post data"

    print("post data type ~ " + str(type( post_data )))
    if type(post_data) == str:
        print("found type pd string")
        try:
            pd_load = json.loads(post_data)
        except:
            print("unable to load post data string")
            pd_load = post_data
    
    if type(post_data) == bytes:
        print("found type pd bytes")
        try:
            pd_load = json.loads(json.dumps(post_data))
        except:
            print("unable to load post data bytes")
            pd_load = str(post_data)


    if sq_path  == "/post_test":
        print( "route post path called w path ~ ")
        return "post_test response success" 
    
    if sq_path  == "/post_test_data":
        print("post test data data ~" + pd_load)
        post_data_resp = {"success":True, "posted_data": pd_load}
        return json.dumps(post_data_resp)
    
    else:
        return {"success":False, "si route_post error": "error, path not found"}

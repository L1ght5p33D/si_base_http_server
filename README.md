
A minimal http server that supports get, post, head and options requests

Can be customized to comply with opinionated API header requirements 


Start with python3 ./b_http_serve.py

Set a different port in serve_config.py


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


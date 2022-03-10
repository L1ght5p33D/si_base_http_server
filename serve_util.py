

# context types set loosely by file name and definitively in routing response
def check_ctypes_for_enc(ct_ft):
    print("check for ctext type in c_resp ~ " + str(ct_ft))
    ctx_type = "context-type not found"
    encode_resp = False
    if "html" in ct_ft or "text/html" in ct_ft:
        ctx_type = "text/html"
        encode_resp = True
    if "js" in ct_ft or "text/javascript" in ct_ft:
        ctx_type = "text/javascript"
        encode_resp = True
    if "css" in ct_ft or "text/css" in ct_ft:
        ctx_type = "text/css"
        encode_resp = True
    if "png" in ct_ft:
        ctx_type = "image/png"
        encode_resp = False
    if "jpg" in ct_ft or "jpeg" in ct_ft:
        ctx_type = "image/jpeg"
        encode_resp = False
    #if  "image" in ct_ft:
    #    ctx_type = "image/*"
    #    encode_resp = False
    print("check ret ctype ~ " + ctx_type)
    print("check ret enc ~ " + str(encode_resp))
    return ctx_type, encode_resp


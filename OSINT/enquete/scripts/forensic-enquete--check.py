import json,urllib.request
BASE="http://172.28.31.2:8080"
answers={1:"EXPURGE",2:"EXPURGE",3:"EXPURGE",4:"10:35",5:"EXPURGE",6:"EXPURGE",7:"EXPURGE",8:"EXPURGE",9:"EXPURGE",10:"EXPURGE",11:"EXPURGE",12:"EXPURGE",13:"EXPURGE",14:"4",15:"EXPURGE",16:"EXPURGE",17:"EXPURGE",18:"EXPURGE",19:"Sarpi",20:"EXPURGE",21:"EXPURGE",22:"EXPURGE",23:"EXPURGE",24:"EXPURGE",25:"EXPURGE",26:"EXPURGE",27:"EXPURGE",28:"EXPURGE"}
for i in sorted(answers):
    body=json.dumps({"id":i,"answer":answers[i]}).encode()
    r=urllib.request.Request(BASE+"/api/check",data=body,headers={"Content-Type":"application/json"})
    try:
        out=json.loads(urllib.request.urlopen(r).read())
    except Exception as e:
        out={"err":str(e)}
    print(i, out, "|", answers[i])

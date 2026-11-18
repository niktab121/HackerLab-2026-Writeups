#!/usr/bin/env python3
# Relay cote Mac : le conteneur se connecte sur RELAY_PORT, notre outil local sur LOCAL_PORT.
import socket, select, sys

RELAY_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9002
LOCAL_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 1445

def forward(a, b):
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

def main():
    relay = socket.socket()
    relay.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    relay.bind(("0.0.0.0", RELAY_PORT))
    relay.listen(16)

    local = socket.socket()
    local.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    local.bind(("127.0.0.1", LOCAL_PORT))
    local.listen(16)

    print(f"[*] relay sur 0.0.0.0:{RELAY_PORT} (pivot conteneur)", flush=True)
    print(f"[*] local sur 127.0.0.1:{LOCAL_PORT} (smbclient/impacket)", flush=True)

    while True:
        pivot, pa = relay.accept()
        print(f"[+] pivot connecte : {pa}", flush=True)
        client, ca = local.accept()
        print(f"[+] client connecte : {ca}", flush=True)
        forward(client, pivot)

if __name__ == "__main__":
    main()

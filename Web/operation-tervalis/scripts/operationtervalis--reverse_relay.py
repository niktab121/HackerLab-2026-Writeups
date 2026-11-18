#!/usr/bin/env python3
import socket
import select
import threading

HOST = "0.0.0.0"
RELAY_PORT = 9001
LOCAL_PORT = 1389

def forward(a, b):
    sockets = [a, b]
    try:
        while True:
            readable, _, _ = select.select(sockets, [], [], 120)
            if not readable:
                print("[!] Tunnel inactif", flush=True)
                break

            for source in readable:
                data = source.recv(65536)
                if not data:
                    return

                destination = b if source is a else a
                destination.sendall(data)

    except (OSError, ConnectionError) as e:
        print(f"[!] Connexion fermée : {e}", flush=True)
    finally:
        a.close()
        b.close()

def main():
    pivot_listener = socket.socket()
    pivot_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    pivot_listener.bind((HOST, RELAY_PORT))
    pivot_listener.listen(5)

    local_listener = socket.socket()
    local_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    local_listener.bind(("127.0.0.1", LOCAL_PORT))
    local_listener.listen(5)

    print(f"[*] Pivot attendu sur {RELAY_PORT}", flush=True)
    print(f"[*] LDAP local sur 127.0.0.1:{LOCAL_PORT}", flush=True)

    while True:
        pivot, address = pivot_listener.accept()
        print(f"[+] Pivot connecté : {address}", flush=True)

        client, address = local_listener.accept()
        print(f"[+] Client LDAP connecté : {address}", flush=True)

        forward(client, pivot)

if __name__ == "__main__":
    main()
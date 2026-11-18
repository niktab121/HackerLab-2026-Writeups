#!/usr/bin/env python3
"""Client STOMP minimal pour interroger ActiveMQ (challenge 11 - Sealed Order)."""
import socket, sys, time

HOST = "172.28.5.2"
PORT = 61613

def stomp_send(sock, frame):
    sock.sendall(frame.encode() + b"\x00")

def stomp_recv(sock, timeout=3):
    sock.settimeout(timeout)
    buf = b""
    while b"\x00" not in buf:
        try:
            d = sock.recv(65536)
        except socket.timeout:
            break
        if not d:
            break
        buf += d
    return buf.decode(errors="replace")

s = socket.create_connection((HOST, PORT), timeout=10)
# CONNECT
stomp_send(s, "CONNECT\naccept-version:1.2\nhost:localhost\n\n")
print("=== CONNECT ===")
print(stomp_recv(s))

# SUBSCRIBE to the transmissions queue
stomp_send(s, "SUBSCRIBE\nid:sub-0\ndestination:/queue/valdoria.transmissions\nack:auto\n\n")
print("=== SUBSCRIBE (waiting messages) ===")
for i in range(5):
    msg = stomp_recv(s, timeout=2)
    if msg.strip():
        print(f"--- message {i} ---")
        print(msg)

# Also try to discover queues by attempting to subscribe to a few likely names
for q in ["/queue/valdoria.transmissions", "/queue/sealed.order", "/queue/sealed", "/queue/orders",
          "/queue/valdoria.sealed", "/queue/kappa", "/queue/VF-FISC", "/queue/valdoria.recon"]:
    stomp_send(s, f"SUBSCRIBE\nid:sub-{q}\ndestination:{q}\nack:auto\n\n")
    time.sleep(0.3)

print("=== DISCONNECT ===")
stomp_send(s, "DISCONNECT\n\n")
s.close()

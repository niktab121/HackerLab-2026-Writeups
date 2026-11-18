#!/usr/bin/env python3
"""Listen MQTT topics for N seconds, pretty-print."""
import socket, struct, sys, time

HOST = "172.28.9.3"
PORT = 1883
TOPICS = ["ActiveMQ.Advisory.>", "ActiveMQ.Advisory.Queue", "ActiveMQ.Advisory.Topic/#", "#"]
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 20


def enc_str(s):
    b = s.encode(); return struct.pack(">H", len(b)) + b


def rem_len(n):
    out = b""
    while True:
        d = n % 128; n //= 128
        if n: d |= 0x80
        out += bytes([d])
        if not n: return out


def pkt(t, f, p):
    return bytes([(t << 4) | f]) + rem_len(len(p)) + p


def read_pkt(s):
    h = s.recv(1)
    if not h: return None
    mult, length, i = 1, 0, 0
    while True:
        b = s.recv(1)
        if not b: return None
        d = b[0]; length += (d & 127) * mult; mult *= 128; i += 1
        if not (d & 128): break
        if i > 3: return None
    data = b""
    while len(data) < length:
        c = s.recv(length - len(data))
        if not c: break
        data += c
    return h[0] >> 4, h[0] & 0xF, data


s = socket.create_connection((HOST, PORT), timeout=10)
s.sendall(pkt(1, 0, enc_str("MQTT") + bytes([4, 0x02]) + struct.pack(">H", 60) + enc_str("l%d" % (time.time() % 99999))))
print("CONNACK", read_pkt(s))
sub = struct.pack(">H", 1)
for t in TOPICS:
    sub += enc_str(t) + bytes([0])
s.sendall(pkt(8, 2, sub))
print("SUBACK", read_pkt(s))
s.settimeout(1.0)
end = time.time() + DUR
while time.time() < end:
    try:
        p = read_pkt(s)
    except socket.timeout:
        continue
    except Exception:
        break
    if p is None:
        break
    t, f, d = p
    if t == 3:
        tl = struct.unpack(">H", d[:2])[0]
        print("MSG topic=%s body=%r" % (d[2:2 + tl].decode(errors="replace"), d[2 + tl:]))
    else:
        print("PKT", t, f, d[:80])

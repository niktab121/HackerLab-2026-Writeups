#!/usr/bin/env python3
"""Minimal MQTT 3.1.1 probe: connect anon, subscribe to topics, listen."""
import socket, struct, sys, time

HOST = sys.argv[1] if len(sys.argv) > 1 else "172.28.9.3"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 1883
TOPICS = sys.argv[3].split(",") if len(sys.argv) > 3 else ["#"]
LISTEN = float(sys.argv[4]) if len(sys.argv) > 4 else 8.0


def enc_str(s):
    b = s.encode()
    return struct.pack(">H", len(b)) + b


def rem_len(n):
    out = b""
    while True:
        d = n % 128
        n //= 128
        if n:
            d |= 0x80
        out += bytes([d])
        if not n:
            return out


def pkt(ptype, flags, payload):
    return bytes([(ptype << 4) | flags]) + rem_len(len(payload)) + payload


def read_pkt(s):
    h = s.recv(1)
    if not h:
        return None
    mult, length, i = 1, 0, 0
    while True:
        b = s.recv(1)
        if not b:
            return None
        d = b[0]
        length += (d & 127) * mult
        mult *= 128
        i += 1
        if not (d & 128):
            break
        if i > 3:
            return None
    data = b""
    while len(data) < length:
        chunk = s.recv(length - len(data))
        if not chunk:
            break
        data += chunk
    return h[0] >> 4, h[0] & 0xF, data


def main():
    s = socket.create_connection((HOST, PORT), timeout=10)
    cid = "probe%d" % (int(time.time()) % 100000)
    vh = enc_str("MQTT") + bytes([4, 0x02]) + struct.pack(">H", 60)
    payload = vh + enc_str(cid)
    s.sendall(pkt(1, 0, payload))
    r = read_pkt(s)
    print("CONNACK:", r)
    if not r or r[0] != 2:
        print("connect failed")
        return
    sub = struct.pack(">H", 1)
    for i, t in enumerate(TOPICS):
        sub += enc_str(t) + bytes([0])
    s.sendall(pkt(8, 2, sub))
    r = read_pkt(s)
    print("SUBACK:", r)
    end = time.time() + LISTEN
    s.settimeout(1.0)
    while time.time() < end:
        try:
            p = read_pkt(s)
        except socket.timeout:
            continue
        except Exception as e:
            print("err", e)
            break
        if p is None:
            print("closed")
            break
        print("PKT type=%d flags=%d len=%d" % (p[0], p[1], len(p[2])))
        if p[0] == 3:
            tlen = struct.unpack(">H", p[2][:2])[0]
            topic = p[2][2:2 + tlen].decode(errors="replace")
            body = p[2][2 + tlen:]
            print("  topic=%s body=%r" % (topic, body))


if __name__ == "__main__":
    main()

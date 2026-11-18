#!/usr/bin/env python3
"""Operation Tervalis / Dead Drop (NorvethSecure v3) - solver.

Vulnerability: the priority channel (key_id 0x00000003) counter state is NOT
persisted across reconnections of session 461f78d8...  session_03 (a
reconnection that reuses the master secret) therefore re-uses nonces 0..6 that
session_01 already used on the same key.  AES-GCM is CTR mode, so equal nonce +
equal key => equal keystream.  One known plaintext heartbeat in session_01
reveals the keystream and lets us decrypt the session_03 priority traffic.

No key material is required: only XOR of ciphertexts with a recovered keystream.

Plaintext model
---------------
session_01's priority channel is a heartbeat stream:
    {"type":"HEARTBEAT","seq":20+c,"ts":<base + c*interval>,"pad":"A"*100}
counter 0 is given verbatim in known_messages.json, which pins `base`.

The heartbeat interval is *unknown*, so instead of trusting the first candidate
that parses we require one single interval to make **all seven** session_03
frames valid JSON at once.  Only interval=120s satisfies that; incorrect
intervals corrupt individual bytes (e.g. "ABJ"/"CBI"/"DBJ Valdoria" instead of
"FBI Valdoria") and generally break the JSON structure outright.
"""
import json
import pickle
import sys
from datetime import datetime, timedelta, timezone

PKL = "/tmp/msgs.pkl"
PAD = "A" * 100
BASE = datetime(2024, 11, 2, 8, 30, 0, tzinfo=timezone.utc)
# counter 0 plaintext, verbatim from known_messages.json
KNOWN0 = ('{"type":"HEARTBEAT","seq":20,"ts":"2024-11-02T08:30:00Z",'
          '"pad":"' + PAD + '"}').encode()


def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def heartbeat(seq, ts):
    return json.dumps({"type": "HEARTBEAT", "seq": seq, "ts": ts, "pad": PAD},
                      separators=(",", ":")).encode()


def decrypt_all(paired, s1, interval):
    """Return {counter: object}; raise ValueError on the first frame that fails."""
    out = {}
    for counter, m3 in paired:
        guess = (KNOWN0 if counter == 0 else
                 heartbeat(20 + counter,
                           (BASE + timedelta(seconds=interval * counter))
                           .strftime("%Y-%m-%dT%H:%M:%SZ")))
        keystream = xor(s1[counter]["ct"], guess)
        obj = json.loads(xor(m3["ct"], keystream).decode("utf-8"))
        if "type" not in obj:
            raise ValueError("no type field")
        out[counter] = obj
    return out


def main():
    S = pickle.load(open(PKL, "rb"))
    s1 = [m for m in S["session_01.pcapng"] if m["kid"] == "00000003"]
    s3 = [m for m in S["session_03.pcapng"] if m["kid"] == "00000003"]

    idx = {m["nonce"]: i for i, m in enumerate(s1)}
    paired = [(idx[m["nonce"]], m) for m in s3 if m["nonce"] in idx]
    print("[*] re-used priority nonces: %d / %d" % (len(paired), len(s3)))

    hits = []
    for interval in range(30, 601, 30):
        try:
            hits.append((interval, decrypt_all(paired, s1, interval)))
        except Exception:
            continue

    print("[*] intervals with 7/7 well-formed frames: %s"
          % [i for i, _ in hits])
    if len(hits) != 1:
        print("[-] expected exactly one consistent interval, got %d" % len(hits))
        return 1

    interval, msgs = hits[0]
    print("[+] heartbeat interval = %d s" % interval)
    print()
    for c in sorted(msgs):
        print("  c%-2d %s" % (c, json.dumps(msgs[c])))
    return 0


if __name__ == "__main__":
    sys.exit(main())

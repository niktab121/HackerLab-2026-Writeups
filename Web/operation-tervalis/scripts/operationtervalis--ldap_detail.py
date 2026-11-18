#!/usr/bin/env python3
"""Details LDAP des comptes de service et recherche 'recon' exhaustive."""
from ldap3 import Server, Connection, ALL, SUBTREE

HOST, PORT = "127.0.0.1", 1389
USER, PASSWORD = "contact@example.invalid", "EXPURGE"
BASE = "DC=valdoria,DC=fbi,DC=lab"

server = Server(HOST, port=PORT, get_info=ALL)
conn = Connection(server, user=USER, password=PASSWORD, auto_bind=False)
if not conn.bind():
    print("[-] bind fail:", conn.result)
    raise SystemExit(1)
print("[+] Bind OK")

def get(dn, attrs):
    conn.search(dn, "(objectClass=*)", SUBTREE, attributes=attrs)
    return conn.entries

ALL_ATTRS = ["sAMAccountName","userAccountControl","userPrincipalName","description",
             "servicePrincipalName","msDS-AllowedToDelegateTo","msDS-AllowedToActOnBehalfOfOtherIdentity",
             "memberOf","objectClass","distinguishedName","adminCount","cn"]

print("\n=== DETAILS svc_backup / svc_mssql / svc_gmsa_backup ===")
for sam in ["svc_backup","svc_mssql","svc_gmsa_backup","svc_certsvc","svc_web"]:
    conn.search(BASE, f"(sAMAccountName={sam})", SUBTREE, attributes=ALL_ATTRS)
    for e in conn.entries:
        for a in ALL_ATTRS:
            try:
                v = e[a].value
                if v:
                    print(f"  {sam}.{a} = {v}")
            except Exception:
                pass
        print("  ---")

print("\n=== RECHERCHE 'recon' (case-insensitive) dans TOUS les attributs ===")
# search across common attributes that might contain the hint
conn.search(BASE, "(|(cn=*recon*)(description=*recon*)(info=*recon*)(name=*recon*)(displayName=*recon*))",
            SUBTREE, attributes=["cn","name","description","distinguishedName","objectClass","info"])
for e in conn.entries:
    print(" ", e.entry_dn)

print("\n=== RECHERCHE SUBJ-7742 / AVALD / KAPPA dans description/info ===")
conn.search(BASE, "(|(description=*7742*)(description=*AVALD*)(description=*KAPPA*)(info=*7742*)(info=*AVALD*)(info=*KAPPA*)(description=*SUBJ*))",
            SUBTREE, attributes=["cn","description","distinguishedName","info"])
for e in conn.entries:
    print(" ", e.entry_dn)
    for a in ["description","info","cn"]:
        try:
            print("     ", a, "=", e[a].value)
        except Exception:
            pass

print("\n=== TOUS les groupes ===")
conn.search(BASE, "(objectClass=group)", SUBTREE, attributes=["cn","description","member","distinguishedName"])
for e in conn.entries:
    desc = ""
    try: desc = e["description"].value or ""
    except: pass
    print(f"  {e['cn'].value}  ({desc})")

print("\n=== FIN ===")

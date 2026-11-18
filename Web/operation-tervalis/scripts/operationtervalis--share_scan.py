#!/usr/bin/env python3
"""Scan de noms de partages FS01 (standalone Samba) avec détection précise d'erreur."""
from impacket.smbconnection import SMBConnection

conn = SMBConnection('FS01', '172.28.5.5', sess_port=445)
conn.login('svc_mssql', '', 'FS01', lmhash='', nthash='HEX_EXPURGE')
print("[+] auth OK (svc_mssql local)")

# large list of candidate share names (with and without $, case variants)
base = ["vault","filevault","file-vault","file_vault","backup","data","files","docs","documents",
        "ops","operational","operations","intel","reports","records","storage","archive","archives",
        "share","public","home","homes","tmp","temp","transfer","uploads","downloads","dossiers",
        "coffre","sauvegarde","depot","gmsa","gmsa_backup","svc_gmsa","sealed","order","orders",
        "casefiles","evidence","surveillance","detention","kappa","valdoria","fbi","config","cfg",
        "sysvol","netlogon","it-share","recon-data","applications","apps","database","db","web",
        "www","html","logs","audit","monitoring","alerts"]
names = set()
for b in base:
    for n in (b, b.capitalize(), b.upper(), b+"$", b.capitalize()+"$"):
        names.add(n)

found = 0
for n in sorted(names):
    try:
        tid = conn.connectTree(n)
        print(f"[OPEN] {n}")
        conn.disconnectTree(tid)
        found += 1
    except Exception as e:
        code = getattr(e, 'get_error_code', lambda: None)()
        if code == 0xc0000022:  # STATUS_ACCESS_DENIED
            print(f"[DENIED] {n}")
        elif code == 0xc00000cc:  # STATUS_BAD_NETWORK_NAME
            pass
        else:
            # only print unusual codes
            if code not in (None, 0xc00000cc, 0xc0000022):
                print(f"[{n}] code=0x{code:x}")
print("=== scan done ===")

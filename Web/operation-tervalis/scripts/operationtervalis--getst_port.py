#!/usr/bin/env python3
"""getST wrapper avec port KDC personnalise (par defaut 8899) pour passer le tunnel."""
import sys
import impacket.krb5.kerberosv5 as kv5

KDC_PORT = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 8899

_orig = kv5.sendReceive
def _patched(data, host, kdcHost, port=KDC_PORT):
    return _orig(data, host, kdcHost, port=port)
kv5.sendReceive = _patched

# retirer le port des argv si present
if sys.argv[-1].isdigit():
    sys.argv = sys.argv[:-1]

from impacket.examples import getST
getST.main()

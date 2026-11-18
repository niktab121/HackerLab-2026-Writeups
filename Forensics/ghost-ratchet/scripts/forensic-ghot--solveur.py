#!/usr/bin/env python3
"""Ghost Ratchet / NordLink — validation MAC et déchiffrement des messages.
Usage: python3 solveur.py [chemin_vers_nordlink_device]
Dépendance: python3 -m pip install cryptography
"""
import sys, json, sqlite3, hmac, hashlib
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

DEFAULT = Path(__file__).resolve().parents[2] / 'ghost' / 'nordlink_device'
BASE = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DEFAULT
APP = BASE / 'data/data/nrv.nordlink'

def hkdf(ikm, salt, info, length):
    return HKDF(algorithm=hashes.SHA256(), length=length,
                salt=salt if salt else bytes(32), info=info).derive(ikm)

def mac(key, data):
    return hmac.new(key, data, hashlib.sha256).digest()

def kdf_root(root, dh):
    out = hkdf(dh, root, b'NORDLINK-root-kdf', 64)
    return out[:32], out[32:]

def kdf_chain(chain_key):
    return mac(chain_key, b'\x01'), mac(chain_key, b'\x02')

def message_keys(message_key):
    out = hkdf(message_key, b'', b'NORDLINK-msg-keys', 80)
    return out[:32], out[32:64], out[64:80]

def x25519_shared(private_raw, public_raw):
    sk = x25519.X25519PrivateKey.from_private_bytes(private_raw)
    pk = x25519.X25519PublicKey.from_public_bytes(public_raw)
    return sk.exchange(pk)

def decrypt_from_anchor(root, local_private, remote_public, row):
    """Construit la chaîne d’un DH distant depuis l’ancre et authentifie un message."""
    _, chain_key = kdf_root(root, x25519_shared(local_private, remote_public))
    for _ in range(row['msg_num'] + 1):
        next_chain, message_key = kdf_chain(chain_key)
        enc_key, mac_key, iv = message_keys(message_key)
        ad = (row['msg_type'].to_bytes(4, 'big') + row['msg_num'].to_bytes(4, 'big') +
              row['prev_chain_len'].to_bytes(4, 'big') + remote_public)
        ciphertext = bytes.fromhex(row['ciphertext'])
        expected = mac(mac_key, ad + ciphertext)
        if hmac.compare_digest(expected, bytes.fromhex(row['mac'])):
            dec = Cipher(algorithms.AES(enc_key), modes.CBC(iv)).decryptor()
            padded = dec.update(ciphertext) + dec.finalize()
            pad = padded[-1]
            if not 1 <= pad <= 16 or padded[-pad:] != bytes([pad]) * pad:
                raise ValueError('Padding PKCS#7 invalide malgré MAC valide')
            return padded[:-pad]
        chain_key = next_chain
    return None

def main():
    if not (APP / 'files/session_init.bak').is_file():
        raise SystemExit(f'Extraction introuvable: {APP}\nPassez le chemin nordlink_device en argument.')
    state = json.loads((APP / 'files/session_init.bak').read_text())
    anchor_priv = bytes.fromhex(state['dh_private_key'])
    anchor_root = bytes.fromhex(state['root_key'])
    db = sqlite3.connect(f'file:{APP / "databases/nordlink.db"}?mode=ro', uri=True)
    query = ('SELECT id,direction,msg_num,msg_type,dh_public,ciphertext,mac,'
             'prev_chain_len,timestamp FROM messages ORDER BY id')
    fields = ('id direction msg_num msg_type dh_public ciphertext mac '
              'prev_chain_len timestamp').split()
    count = 0
    for values in db.execute(query):
        row = dict(zip(fields, values))
        if row['direction'] != 'recv':
            continue
        public = bytes.fromhex(row['dh_public'])
        plaintext = decrypt_from_anchor(anchor_root, anchor_priv, public, row)
        if plaintext is not None:
            count += 1
            print(f"[{row['id']}] {row['timestamp']} — MAC valide")
            print(plaintext.decode('utf-8', 'replace'))
            print()
    print(f'{count} message(s) reçu(s) déchiffré(s) et authentifié(s).')
    print('La sauvegarde permet de retrouver les chaînes dont le ratchet DH est dérivable depuis cette ancre;')
    print('les messages des générations précédentes/suivantes peuvent nécessiter le rejeu complet du ratchet.')

if __name__ == '__main__':
    main()

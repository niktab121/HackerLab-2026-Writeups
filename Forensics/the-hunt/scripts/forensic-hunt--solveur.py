#!/usr/bin/env python3
"""The Hunt / RELAY: evidence-first Docker/SQLite decryptor."""
import argparse, hashlib, json, re, sqlite3, subprocess, tarfile, tempfile
from pathlib import Path
from collections import defaultdict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CODES = {1:'EXPURGE',2:'EXPURGE',3:'EXPURGE'}
KDF = dict(n=2**15,r=8,p=1,maxmem=64*1024*1024,dklen=32)
EMAIL = re.compile(r'(?i)\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b')

def extract_db(archive, root):
    """Read docker-save outer tar, then inspect layer tars in manifest order."""
    with tarfile.open(archive, 'r:*') as outer:
        members = {m.name.lstrip('./'):m for m in outer.getmembers() if m.isfile()}
        manifest = json.load(outer.extractfile(members['manifest.json']))
        layers = manifest[0]['Layers']
        found = None
        for layer in layers:
            member = members.get(layer.lstrip('./'))
            if member is None: continue
            stream = outer.extractfile(member)
            with tarfile.open(fileobj=stream, mode='r|') as inner:
                for item in inner:
                    name = item.name.lstrip('./')
                    if item.isfile() and name == 'data/relay.db':
                        found = inner.extractfile(item).read()
                        print(f'[+] SQLite dans couche {layer}: {len(found)} octets')
        if found is None: raise RuntimeError('data/relay.db introuvable dans les couches')
        path = root/'relay.db'
        path.write_bytes(found)
        return path

def key_for(code, salt):
    return hashlib.scrypt(code.encode(), salt=bytes(salt), **KDF)

def decrypt_outer(key, blob, cid, author):
    blob = bytes(blob)
    if len(blob)<29: raise ValueError('blob AES-GCM trop court')
    aad = f'relay:message:{cid}:{author}'.encode()
    return AESGCM(key).decrypt(blob[:12],blob[12:],aad).decode('utf-8')

def decrypt_inner(payload, exe, mode):
    if not exe: return None, 'cipher.exe non fourni'
    if mode == 'wine': cmd=['wine',str(exe),'-d',payload]
    elif mode == 'native': cmd=[str(exe),'-d',payload]
    else: return None, 'mode de lancement inconnu'
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=12)
    except (OSError,subprocess.TimeoutExpired) as exc:
        return None, f'execution impossible: {exc}'
    if result.returncode or not result.stdout.strip():
        return None, f'code={result.returncode}, stderr={result.stderr[:200]!r}'
    return result.stdout.strip(), None

def main():
    ap=argparse.ArgumentParser(description='RELAY forensics, déchiffrement et collecte de preuves')
    ap.add_argument('--archive',type=Path,help='Archive docker save relay.tar.gz')
    ap.add_argument('--db',type=Path,help='Base SQLite relay.db déjà extraite')
    ap.add_argument('--cipher',type=Path,help='Chemin vers cipher.exe (optionnel)')
    ap.add_argument('--mode',choices=['wine','native'],default='wine')
    ap.add_argument('--output',type=Path,default=Path('the_hunt_report.json'))
    args=ap.parse_args()
    if not args.archive and not args.db: ap.error('fournir --archive ou --db')
    if args.cipher and not args.cipher.exists(): ap.error('cipher.exe introuvable')
    with tempfile.TemporaryDirectory() as td:
        db=args.db if args.db else extract_db(args.archive,Path(td))
        con=sqlite3.connect(f'file:{db.resolve()}?mode=ro',uri=True)
        con.row_factory=sqlite3.Row
        print('[+] Tables:',', '.join(r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")))
        channels=list(con.execute('SELECT id,name,key_salt,key_check FROM channels'))
        keys={}
        for c in channels:
            cid=c['id']
            if cid not in CODES:
                print(f'[!] Canal {cid} sans code connu');continue
            keys[cid]=key_for(CODES[cid],c['key_salt'])
            print(f'[+] Canal {cid} ({c["name"]}): clé dérivée; authentification au premier message')
        results=[]
        for row in con.execute('SELECT id,channel_id,author,body FROM messages ORDER BY id'):
            mid,cid,author=row['id'],row['channel_id'],row['author']
            rec={'id':mid,'channel':cid,'author':author}
            try:
                outer=decrypt_outer(keys[cid],row['body'],cid,author)
                rec['outer']=outer
                clear,error=decrypt_inner(outer,args.cipher,args.mode)
                rec['plaintext']=clear
                if error:rec['inner_error']=error
                print(f'[{mid:02d}] [{cid}] {author}: {clear if clear is not None else "[interne non déchiffré]"}')
            except Exception as exc:
                rec['outer_error']=str(exc)
                print(f'[!] Message {mid}: AES-GCM invalide ({type(exc).__name__})')
            results.append(rec)
        con.close()
    emails=defaultdict(list)
    for rec in results:
        for field in ('outer','plaintext'):
            for email in EMAIL.findall(rec.get(field) or ''):
                emails[email.lower()].append({'message_id':rec['id'],'author':rec['author'],'layer':field})
    print('\n=== EMAILS OBSERVÉS ===')
    if emails:
        for email,evidence in emails.items():print(email, evidence)
    else:print('Aucun e-mail explicite dans les messages déchiffrés.')
    print('\n[!] Une adresse déduite d’un annuaire externe n’est PAS une preuve extraite du binaire.')
    report={'messages':results,'emails':dict(emails),'hypothesis':'EXPURGE (non vérifié)'}
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'[+] Rapport: {args.output}')

if __name__=='__main__':main()

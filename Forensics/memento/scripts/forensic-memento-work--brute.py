import hashlib, itertools, string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

data = open('assets_scelle-P7.enc','rb').read()
assert data[:8] == b'Salted__'
salt = data[8:16]
ct = data[16:]

def evp_bytes_to_key(pw, salt, klen, md=hashlib.md5):
    d = b''; prev = b''
    while len(d) < klen:
        prev = md(prev + pw + salt).digest()
        d += prev
    return d[:klen]

def pbkdf2(pw, salt, klen, it=10000):
    return hashlib.pbkdf2_hmac('sha256', pw, salt, it, klen)

def dec(key, iv, cipher):
    c = Cipher(cipher(key), modes.CBC(iv)).decryptor()
    return c.update(ct) + c.finalize()

def score(pt):
    try:
        s = pt.rstrip(b'\x00')
        # valid pkcs7 already ensured by manual check
        txt = s.decode('utf-8')
    except Exception:
        return 0
    if all(32 <= ord(ch) < 127 or ch in '\n\r\t' for ch in txt):
        return sum(1 for ch in txt if ch.isprintable())
    return 0

def check(pw):
    if isinstance(pw, str): pw = pw.encode()
    for name, alg, klen in [('aes256', algorithms.AES, 32), ('aes192', algorithms.AES, 24), ('aes128', algorithms.AES, 16)]:
        for kdf_name, kdf in [('md5', lambda k: evp_bytes_to_key(pw, salt, k, hashlib.md5)),
                              ('sha256', lambda k: evp_bytes_to_key(pw, salt, k, hashlib.sha256)),
                              ('pbkdf2', lambda k: pbkdf2(pw, salt, k))]:
            kd = kdf(klen + 16)
            key, iv = kd[:klen], kd[klen:klen+16]
            pt = dec(key, iv, alg)
            pad = pt[-1]
            if 1 <= pad <= 16 and pt[-pad:] == bytes([pad])*pad:
                body = pt[:-pad]
                sc = score(body)
                if sc > 0:
                    print('HIT', name, kdf_name, repr(pw), '->', repr(body))
                    return True
    return False

tokens = ['0452','045872','204','137','QR4T9Z','MV-2026-0518','HDL-2026-04873','SC-0518-G','SC-0518',
'BV-2026-0518','0518','MERTENS','Mertens','mertens','HENRI','Henri','henri','03714290','03 71 42 90',
'unite 7','unité 7','KAO','KA088','KAO88','KA088137','KA088-137','137KA088','Laurent','LAURENT',
'M. Laurent','M Laurent','NORNVANE','NORNVANE HOLDINGS LTD','BIBZBZBZ','Vexholm','VEXHOLM','Valdoria',
'VALDORIA','Kaltyr','KALTYR','KDR','KTY','VLD','KVX','Residence du Phare','Résidence du Phare','Phare',
'2026-05-17','17/05/2026','17.05.2026','17052026','20260517','20260517071244','17052026071244',
'071244','07:12:44','2026:05:17 07:12:44','VA0117','VA0231','003A','011C','CLASSE J','classe j',
'MV20260518','HDL202604873','SC0518G','P-7','P7','scelle-P7','scelle-P7.enc','laisser filer',
'pas la ligne','laisserfiler','paslaligne','Vexholm laisser filer','memento','Memento','MEMENTO',
'Henri Mertens','henri.mertens','hmertens','Cabinet Mertens & Vale','Mertens & Vale','MertensVale',
'ValExchange','VALEXCHANGE','USD','1200000','1 200 000,00 USD','1200','1 200,00 USD','120000',
'16/05/2026','16052026','20260516','15:40','17:05','17:25','18:00','19:20']

cands = set()
for t in tokens:
    cands.add(t); cands.add(t.lower()); cands.add(t.upper())
    cands.add(t.replace(' ','').replace('-','').replace('.','').replace('/',''))
# combos of two short tokens
short = ['0452','045872','204','137','0518','QR4T9Z','KA088','KAO88','KDR','KVX','VLD','KTY','Mertens','Henri','Laurent','Vexholm','Phare','P7','P-7','07:12:44','071244']
for a,b in itertools.product(short, repeat=2):
    for sep in ['','-','_','.',' ','/',':']:
        cands.add(a+sep+b)
# numeric ranges small
for n in range(0,10000):
    cands.add(str(n))
    cands.add('%04d'%n)
for d in ['170526','17052026','20260517','2026-05-17','17-05-2026','17.05.26']:
    cands.add(d)
print('candidates', len(cands))
for c in cands:
    if check(c):
        print('FOUND', c); break

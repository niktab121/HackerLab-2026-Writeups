import base64, codecs
b64_str = "DONNEE_ENCODEE_EXPURGEE"

# Sens 1 : Base64 -> ROT13
try:
    d1 = base64.b64decode(b64_str).decode('utf-8', errors='ignore')
    print('1. B64 puis ROT13:', codecs.encode(d1, 'rot_13'))
except Exception as e:
    print('1. Erreur:', e)

# Sens 2 : ROT13 -> Base64
try:
    r1 = codecs.encode(b64_str, 'rot_13')
    print('2. ROT13 puis B64:', base64.b64decode(r1).decode('utf-8', errors='ignore'))
except Exception as e:
    print('2. Erreur:', e)
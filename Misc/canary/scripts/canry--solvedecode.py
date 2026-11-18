import base64
import codecs

cipher = "DONNEE_ENCODEE_EXPURGEE"
rot13_decoded = codecs.encode(cipher, "rot_13")
flag = base64.b64decode(rot13_decoded).decode("utf-8", errors="ignore")

print(flag)
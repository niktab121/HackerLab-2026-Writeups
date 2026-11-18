import hashlib

TARGET = "HEX_EXPURGE"

with open("transactions.txt") as f:
    for line in f:
        tx = line.strip().lower()
        if not tx:
            continue

        variants = [tx, tx.removeprefix("0x")]

        for candidate in variants:
            digest = hashlib.sha256(candidate.encode()).hexdigest()

            if digest == TARGET:
                print(f"[+] FLAG : EXPURGE}}")
                raise SystemExit

print("[-] Aucune correspondance trouvée")

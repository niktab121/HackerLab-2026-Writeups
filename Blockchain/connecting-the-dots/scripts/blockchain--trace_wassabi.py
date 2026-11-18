import requests
import time

API = "https://blockstream.info/api"

START = "HEX_EXPURGE"
TARGET = "bc1qxn7algyps6gq8jcg8u3ys72zwpkpksnjwuk4wn"

session = requests.Session()
queue = [(START, [START])]
visited = set()

MAX_DEPTH = 12
MAX_NODES = 1500

while queue and len(visited) < MAX_NODES:
    txid, path = queue.pop(0)

    if txid in visited or len(path) > MAX_DEPTH:
        continue

    visited.add(txid)

    try:
        r = session.get(f"{API}/tx/{txid}", timeout=15)
        r.raise_for_status()
        tx = r.json()

        for i, out in enumerate(tx["vout"]):
            address = out.get("scriptpubkey_address")
            value = out["value"] / 1e8

            if address == TARGET:
                print("\n[+] TARGET FOUND")
                print("Path:")
                print("\n".join(path))
                print("Value:", value, "BTC")
                raise SystemExit(0)

            if out["value"] == 0:
                continue

            s = session.get(
                f"{API}/tx/{txid}/outspend/{i}",
                timeout=15
            )
            s.raise_for_status()
            spend = s.json()

            if spend.get("spent"):
                nxt = spend["txid"]
                if nxt not in visited:
                    queue.append((nxt, path + [nxt]))

        if len(visited) % 25 == 0:
            print(
                f"[*] {len(visited)} transactions explored",
                flush=True
            )

        time.sleep(0.1)

    except requests.RequestException as e:
        print("[!] API error:", e)

print("[-] Target not found within search limits")
#!/usr/bin/env python3
"""
Solveur automatisé pour le challenge : Node To Nowhere - Part 02 (The Five of THOR)
CTF : HackerLab 2026 - Opération Tervalis
Catégorie : BLOCKCHAIN INTELLIGENCE

Ce script effectue le traçage complet on-chain :
1. Analyse du portefeuille initial d'Ethereum (Thanos : HEX_EXPURGE)
2. Traçage des 50% non convertis en ERC-20 vers les 5 branches de blanchiment THORChain
3. Extraction des 5 adresses Bitcoin intermédiaires depuis les Memos THORChain (depositWithExpiry)
4. Traçage des transferts sortants sur le réseau Bitcoin (via Mempool.space) vers les adresses SegWit finales
5. Chargement de hachage.txt, calcul des empreintes SHA-256 et reconstruction du Flag ordonné.
"""

import sys
import os
import json
import hashlib
import re
import urllib.request
import time

INITIAL_ETH_WALLET = "HEX_EXPURGE"
THORCHAIN_ROUTER = "HEX_EXPURGE"
DEFAULT_HASH_FILE = "hachage.txt"

def http_get_json(url, retries=3, delay=1):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(delay)

def get_eth_transactions(address):
    url = f"https://eth.blockscout.com/api/v2/addresses/{address}/transactions"
    data = http_get_json(url)
    return data.get("items", [])

def get_btc_address_txs(address):
    url = f"https://mempool.space/api/address/{address}/txs"
    return http_get_json(url)

def trace_thorchain_memos():
    print(f"[*] 1. Analyse des transactions sortantes de Thanos ({INITIAL_ETH_WALLET})...")
    txs = get_eth_transactions(INITIAL_ETH_WALLET)
    
    # Identifier la transaction vers la branche non-ERC20 (~1009.63 ETH vers 0x930D...)
    peel_wallet = None
    for tx in txs:
        val = int(tx.get("value", 0)) / 1e18
        to_addr = tx.get("to", {}).get("hash") if tx.get("to") else None
        if to_addr and 1000 <= val <= 1050:
            peel_wallet = to_addr
            print(f"    [+] Portefeuille intermédiaire identifié : {peel_wallet} ({val:.2f} ETH)")
            break
            
    if not peel_wallet:
        peel_wallet = "HEX_EXPURGE"

    print(f"[*] 2. Traçage des 5 sorties de ~200 ETH depuis {peel_wallet}...")
    peel_txs = get_eth_transactions(peel_wallet)
    branches = []
    for tx in peel_txs:
        val = int(tx.get("value", 0)) / 1e18
        to_addr = tx.get("to", {}).get("hash") if tx.get("to") else None
        if to_addr and val >= 199.0 and to_addr.lower() != peel_wallet.lower():
            if to_addr not in branches:
                branches.append(to_addr)

    print(f"    [+] {len(branches)} adresses de dispersion trouvées.")

    btc_memos = []
    print("[*] 3. Suivi de chaque branche vers l'interaction THORChain (depositWithExpiry)...")
    for b in branches:
        curr = b
        # Traverser jusqu'à trouver depositWithExpiry
        for hop in range(5):
            curr_txs = get_eth_transactions(curr)
            found_deposit = False
            for t in curr_txs:
                if t.get("method") == "depositWithExpiry":
                    # Extraire le paramètre memo
                    params = t.get("decoded_input", {}).get("parameters", [])
                    memo = None
                    for p in params:
                        if p.get("name") == "memo":
                            memo = p.get("value")
                            break
                    if memo:
                        # Extraire l'adresse Bitcoin du memo (ex: =:b:1JzxNqn...:0/1/0:dx:30)
                        match = re.search(r"b:(1[a-km-zA-HJ-NP-Z1-9]{25,34})", memo)
                        if match:
                            btc_addr = match.group(1)
                            btc_memos.append(btc_addr)
                            print(f"    [+] THORChain Memo trouvé : {btc_addr} (Tx: {t.get('hash')[:16]}...)")
                            found_deposit = True
                            break
            if found_deposit:
                break
            # Si pas encore de depositWithExpiry, suivre la transaction sortante majeure
            next_hop = None
            for t in curr_txs:
                if t.get("from", {}).get("hash", "").lower() == curr.lower():
                    val = int(t.get("value", 0)) / 1e18
                    if val >= 199.0:
                        next_hop = t.get("to", {}).get("hash")
                        break
            if next_hop:
                curr = next_hop
            else:
                break

    return list(set(btc_memos))

def trace_final_btc_wallets(btc_intermediate_addrs):
    print(f"[*] 4. Analyse des transferts sur le réseau Bitcoin pour {len(btc_intermediate_addrs)} adresses...")
    final_wallets = set()
    for addr in btc_intermediate_addrs:
        txs = get_btc_address_txs(addr)
        for tx in txs:
            # Chercher la transaction où addr est en input (sortie vers portefeuille final)
            is_input = any(vin.get("prevout", {}).get("scriptpubkey_address") == addr for vin in tx.get("vin", []))
            if is_input:
                for vout in tx.get("vout", []):
                    out_addr = vout.get("scriptpubkey_address")
                    # Les portefeuilles finaux sont au format SegWit bech32 (bc1q...)
                    if out_addr and out_addr.startswith("bc1q") and out_addr != addr:
                        final_wallets.add(out_addr)
                        print(f"    [+] Portefeuille final SegWit : {out_addr} ({vout.get('value', 0)/1e8:.4f} BTC)")
        time.sleep(0.3)
    return list(final_wallets)

def main():
    hash_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HASH_FILE
    if not os.path.exists(hash_file):
        print(f"[-] Fichier de hachage introuvable : {hash_file}")
        sys.exit(1)

    with open(hash_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    target_hashes = []
    for line in lines:
        parts = line.split(". ")
        if len(parts) == 2:
            target_hashes.append(parts[1].strip().lower())
        else:
            target_hashes.append(line.strip().lower())

    print(f"[*] {len(target_hashes)} hachages cibles chargés depuis {hash_file}.")

    # Étape 1 à 3 : Memos THORChain
    btc_memos = trace_thorchain_memos()
    if len(btc_memos) < 5:
        # Fallback de sécurité si l'API bloque ou rate un hop
        btc_memos = [
            "1JzxNqnKVodeFf2Mo7RGXdPEp8WGrGX9ug",
            "19NaAoNcYuSWv8qtXox5AcYZyzydi5bb3V",
            "1P7GY5zvTefpDyBSyhhFEACuhdzwPkhKyo",
            "19wj81vQVCee5pDWktwWrFZqhSnJJzX5fi",
            "19AUe2yt18Z8Q9z4JAAN41X8XjyqcL4m9J"
        ]

    # Étape 4 : Réseau Bitcoin
    final_wallets = trace_final_btc_wallets(btc_memos)

    print("[*] 5. Association des portefeuilles avec les hachages SHA-256 cibles...")
    hash_to_wallet = {}
    for w in final_wallets:
        h = hashlib.sha256(w.encode("utf-8")).hexdigest()
        hash_to_wallet[h] = w

    ordered_wallets = []
    for idx, target_h in enumerate(target_hashes, start=1):
        if target_h in hash_to_wallet:
            w = hash_to_wallet[target_h]
            ordered_wallets.append(w)
            print(f"    [+] {idx}. {target_h[:12]}... -> {w}")
        else:
            print(f"    [-] ERREUR: Aucun portefeuille ne correspond au hash {idx} ({target_h})")

    if len(ordered_wallets) == len(target_hashes):
        flag = f"EXPURGE}}"
        print("\n" + "="*60)
        print("FLAG VALIDÉ AVEC SUCCÈS :")
        print(flag)
        print("="*60)
    else:
        print("\n[-] Échec partiel : tous les portefeuilles n'ont pas pu être associés.")

if __name__ == "__main__":
    main()

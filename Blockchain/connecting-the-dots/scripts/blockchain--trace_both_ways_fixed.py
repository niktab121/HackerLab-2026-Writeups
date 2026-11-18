#!/usr/bin/env python3
"""CTF Bitcoin UTXO path finder. Requires: pip install requests"""
import argparse
import collections
import json
import sys
import time
import requests

START = 'HEX_EXPURGE'
END = 'HEX_EXPURGE'
ADDRESS = 'bc1qxn7algyps6gq8jcg8u3ys72zwpkpksnjwuk4wn'

class Explorer:
    def __init__(self, api, delay):
        self.api = api.rstrip('/')
        self.delay = delay
        self.session = requests.Session()
        self.cache = {}

    def get(self, path):
        if path in self.cache:
            return self.cache[path]
        for attempt in range(5):
            try:
                r = self.session.get(self.api + path, timeout=20)
                if r.status_code == 404:
                    raise ValueError('Not found: ' + path)
                if r.status_code in (429, 500, 502, 503, 504):
                    time.sleep(min(2 ** attempt, 20))
                    continue
                r.raise_for_status()
                data = r.json()
                self.cache[path] = data
                time.sleep(self.delay)
                return data
            except requests.RequestException as exc:
                if attempt == 4:
                    raise RuntimeError(f'API failed for {path}: {exc}') from exc
                time.sleep(min(2 ** attempt, 20))
        raise RuntimeError('API retries exhausted: ' + path)

    def tx(self, tid):
        return self.get('/tx/' + tid)

    def spent(self, tid):
        return self.get('/tx/' + tid + '/outspends')


def backward(exp, end, start, depth, limit):
    # parent tx -> (next tx toward end, input index in next tx)
    next_step = {}
    seen = {end}
    queue = collections.deque([(end, 0)])
    while queue:
        tid, level = queue.popleft()
        if tid == start or level >= depth:
            continue
        tx = exp.tx(tid)
        for vin_idx, vin in enumerate(tx.get('vin', [])):
            parent = vin.get('txid')
            if not parent or parent in seen:
                continue
            seen.add(parent)
            next_step[parent] = (tid, vin_idx)
            if len(seen) >= limit:
                print(f'[!] Backward node limit reached: {limit}', flush=True)
                return next_step, seen
            queue.append((parent, level + 1))
        if len(seen) % 100 == 0:
            print(f'[*] Backward visited {len(seen)}', flush=True)
    return next_step, seen


def reconstruct(meet, fprev, bnext, end):
    prefix = [meet]
    while prefix[-1] in fprev:
        prefix.append(fprev[prefix[-1]][0])
    prefix.reverse()
    suffix = []
    cur = meet
    while cur != end:
        if cur not in bnext:
            raise RuntimeError('Broken backward chain')
        cur = bnext[cur][0]
        suffix.append(cur)
    return prefix + suffix


def verify(exp, path, target):
    print('\n[*] Checking each UTXO edge:', flush=True)
    for a, b in zip(path, path[1:]):
        tx = exp.tx(b)
        matches = [(i, vin.get('vout')) for i, vin in enumerate(tx.get('vin', [])) if vin.get('txid') == a]
        if not matches:
            raise RuntimeError(f'Invalid edge {a} -> {b}')
        print(f'  {a} -> {b}  inputs={matches}', flush=True)
    last = exp.tx(path[-1])
    found = [(i, v.get('value')) for i, v in enumerate(last.get('vout', [])) if v.get('scriptpubkey_address') == target]
    print(f'[*] Last tx pays target address: {bool(found)}; outputs={found}', flush=True)
    if not found:
        print('[!] The hardcoded end transaction is NOT a payment to the target address. Check whether it spends an output owned by the target instead.', flush=True)
    return bool(found)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--api', default='https://blockstream.info/api')
    p.add_argument('--start', default=START)
    p.add_argument('--end', default=END)
    p.add_argument('--address', default=ADDRESS)
    p.add_argument('--back-depth', type=int, default=7)
    p.add_argument('--forward-depth', type=int, default=8)
    p.add_argument('--max-nodes', type=int, default=10000)
    p.add_argument('--delay', type=float, default=0.12)
    args = p.parse_args()
    exp = Explorer(args.api, args.delay)
    endtx = exp.tx(args.end)
    outputs = [i for i, v in enumerate(endtx.get('vout', [])) if v.get('scriptpubkey_address') == args.address]
    print(f'[*] End transaction output indices paying target: {outputs}', flush=True)
    bnext, bseen = backward(exp, args.end, args.start, args.back_depth, args.max_nodes)
    print(f'[+] Backward transactions: {len(bseen)}', flush=True)
    queue = collections.deque([(args.start, 0)])
    fseen = {args.start}
    fprev = {}
    meet = None
    while queue:
        tid, depth = queue.popleft()
        if tid in bseen:
            meet = tid
            break
        if depth >= args.forward_depth:
            continue
        tx = exp.tx(tid)
        outspends = exp.spent(tid)
        for idx, out in enumerate(outspends):
            if idx >= len(tx.get('vout', [])) or tx['vout'][idx].get('value', 0) <= 0:
                continue
            if not out.get('spent') or not out.get('txid'):
                continue
            child = out['txid']
            if child not in fseen:
                fseen.add(child)
                fprev[child] = (tid, idx)
                if len(fseen) >= args.max_nodes:
                    print('[!] Forward node limit reached', flush=True)
                    queue.clear()
                    break
                queue.append((child, depth + 1))
        if len(fseen) % 100 == 0:
            print(f'[*] Forward visited {len(fseen)}', flush=True)
    if meet is None:
        print(f'[-] No path found (forward={len(fseen)}, backward={len(bseen)}). Increase depths or check end tx.', flush=True)
        return 2
    path = reconstruct(meet, fprev, bnext, args.end)
    verify(exp, path, args.address)
    print('\n[+] Transaction path (' + str(len(path)) + ' transactions):')
    print('\n'.join(path))
    print('\nCANDIDATE FLAG: EXPURGE')
    print('[!] Graph connectivity does not by itself establish illicit-fund provenance.')
    with open('trace_result.json', 'w') as f:
        json.dump({'path': path, 'target_address': args.address}, f, indent=2)
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, RuntimeError) as e:
        print('[ERROR]', e, file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""Crack the Android lock pattern from /data/system/gesture.key (SHA-1)."""
import hashlib
from itertools import permutations

TARGET = "HEX_EXPURGE"

# Cells numbered 0-8 row-major:
#   0 1 2
#   3 4 5
#   6 7 8
# Skip rules: (A, B) -> intermediate C that must already be visited.
SKIP = {
    (0, 2): 1, (2, 0): 1,
    (0, 6): 3, (6, 0): 3,
    (0, 8): 4, (8, 0): 4,
    (1, 7): 4, (7, 1): 4,
    (2, 6): 4, (6, 2): 4,
    (2, 8): 5, (8, 2): 5,
    (3, 5): 4, (5, 3): 4,
    (6, 8): 7, (8, 6): 7,
}


def valid(seq):
    """Return True if seq is a valid Android unlock pattern (with skip rules)."""
    seen = set()
    for i, c in enumerate(seq):
        if c in seen:
            return False
        if i > 0:
            prev = seq[i - 1]
            mid = SKIP.get((prev, c))
            if mid is not None and mid not in seen:
                return False
        seen.add(c)
    return True


def gen_patterns():
    for length in range(4, 10):
        for p in permutations(range(9), length):
            if valid(p):
                yield p


def sha1_of_bytes(seq):
    return hashlib.sha1(bytes(seq)).hexdigest()


def sha1_of_digits_1based(seq):
    s = "".join(str(c + 1) for c in seq)
    return hashlib.sha1(s.encode()).hexdigest()


def sha1_of_digits_0based(seq):
    s = "".join(str(c) for c in seq)
    return hashlib.sha1(s.encode()).hexdigest()


def main():
    found = []
    count = 0
    for p in gen_patterns():
        count += 1
        candidates = {
            "bytes_0based": sha1_of_bytes(p),
            "digits_1based": sha1_of_digits_1based(p),
            "digits_0based": sha1_of_digits_0based(p),
        }
        for kind, h in candidates.items():
            if h == TARGET:
                found.append((kind, p))
    print(f"total valid patterns checked: {count}")
    for kind, p in found:
        print(f"MATCH [{kind}]: pattern={p}  (1-based: {[c+1 for c in p]})")
    if not found:
        print("no match found")


if __name__ == "__main__":
    main()

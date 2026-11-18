#!/bin/bash
set -u
H=herald-discuss-simpson-gonna.trycloudflare.com
R="$H:443:104.18.32.7"
U="https://$H"
T=$(curl -s -m 20 --resolve "$R" -X POST "$U/api/unlock" -H 'Content-Type: application/json' -d '{"pattern":[1,6,5,0,7,2,3,8]}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
echo "token acquired"
for i in $(seq 1 30); do
  OUT=$(curl -s -m 20 --resolve "$R" -X POST "$U/api/real" -H 'Content-Type: application/json' -d "{\"token\":\"$T\",\"bearing\":118}")
  if echo "$OUT" | grep -q '"ok": *true'; then echo "real mode reached"; break; fi
  sleep 0.35
done
for a in 1 2 3 4 5; do
  curl -s --retry 5 --retry-all-errors --retry-delay 2 -C - -m 600 --resolve "$R" "$U/api/file?token=$T&name=beth.png" -o beth.png
  SZ=$(stat -f %z beth.png)
  echo "attempt $a size=$SZ"
  if [ "$SZ" = "13775536" ]; then break; fi
  sleep 2
done
file beth.png

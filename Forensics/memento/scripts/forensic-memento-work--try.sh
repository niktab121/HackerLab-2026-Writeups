#!/bin/bash
try() {
  local pass="$1" cipher="$2" kdf="$3"
  out=$(openssl enc -d -$cipher $kdf -in assets_scelle-P7.enc -pass pass:"$pass" 2>/dev/null)
  if [ $? -eq 0 ]; then
    echo "SUCCESS cipher=$cipher kdf=$kdf pass=[$pass]"
    printf '%s' "$out" | xxd | head -5
  fi
}
while IFS= read -r p; do
  [ -z "$p" ] && continue
  for c in aes-256-cbc aes-128-cbc aes-192-cbc; do
    try "$p" "$c" "-pbkdf2"
    try "$p" "$c" ""
  done
done

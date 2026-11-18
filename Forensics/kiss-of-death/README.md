# Kiss of Death

[Accueil](../../README.md) · [Forensics](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Kiss of Death |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Forensics |
| Difficulté | Non documentée |
| Points | 100 |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | JavaScript, API HTTP, schéma Android, SHA-1 |
| Validation | Signalement local uniquement (reported) |

## 1. Introduction

Perquisitionner une simulation, puis exploiter les scellés et le téléphone pour poursuivre l’enquête.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** La validation de la perquisition est affirmée dans la note, sans export du système de notation. Les questions intermédiaires ne sont pas reconstituées artificiellement. Le script Android essaie trois représentations du schéma ; seul le SHA-1 des octets des cellules correspond au format Android historique. Le fichier gesture.key original est absent.

## 2. Énoncé du challenge

- Q1 — Recueillir les 18 scellés et clôturer la perquisition.
- Q2 à Q4 — Énoncés originaux absents ; déverrouillage Android mentionné comme prérequis.
- Q5 — Identifier l’application qui cache le vrai téléphone et son mécanisme d’accès.
- Q6 — Énoncé absent ; document numérisé conservé.
- Q7 — Dreamer, documenté séparément sous son nom propre.

### Objectif

Source : [writeup-kiss-of-death.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-md.txt)

Diriger la perquisition de l'appartement 3B après l'arrestation de Mikkel
STRANDHJELM (alias `mstrand`), identifié dans le challenge précédent. Le
challenge est une **simulation de perquisition en 3D** (application web) où il
faut explorer les pièces, découvrir les objets, et placer sous scellé
exactement les **éléments d'intérêt** de l'enquête. La clôture de la
perquisition n'est acceptée par le serveur que si l'ensemble des scellés
correspond exactement aux éléments d'intérêt, et renvoie alors le flag.

### Objectif

Source : [writeup-kiss-of-death-q5.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-q5-md.txt)

La question 5 de *Kiss of Death* (Forensics, HackerLab 2026) demande :

> Derrière quelle application se trouvait le véritable téléphone, et quel était
> le code permettant d'y accéder ?

Format attendu : `Application:Code`. Ce document décrit la démarche complète,
les commandes exactes et la validation reproductible, sans publier la valeur
soumise.

## 3. Analyse initiale

61 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### État initial

Source : [writeup-kiss-of-death.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-md.txt)

- Cible annoncée : `172.28.8.2:8080` (simulation de perquisition, navigateur).
- Accès via un VPN WireGuard fourni par la plateforme (HackerLab).
- Le VPN de l'instance a été téléchargé dans `~/Downloads` :
  `dvpn-464da960.conf` (AllowedIPs `172.28.8.0/24`).
- L'instance ayant expiré en cours de route, le joueur l'a relancée : la
  nouvelle instance utilise le sous-réseau `172.28.2.0/24` (config
  `dvpn-4ad7e8df.conf`), cible `172.28.2.2:8080`.

### État initial

Source : [writeup-kiss-of-death-q5.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-q5-md.txt)

Les questions précédentes ont fourni :

- le code de déverrouillage du téléphone simulé (schéma Android à 9 points),
  retrouvé hors ligne à partir du condensat de `gesture.key` ;
- la page « Pièce à conviction — Téléphone », servie par un tunnel
  `trycloudflare` ;
- un premier profil du téléphone, contenant les applications Téléphone,
  Messages, Galerie, Horloge, Boussole et Paramètres ;
- la liste des objets placés sous scellés lors de la perquisition, dont une
  **montre à aiguilles** portée au poignet gauche du suspect.

Le profil accessible après le schéma ne contient que des conversations banales
(maman, pizzeria, garage). Le contenu intéressant est ailleurs : la page parle
d'un « profil principal » et le JavaScript mentionne un mode `real`.

L'indice officiel de la question oriente vers les scellés :

> L'un des objets que vous avez placés sous scellés, retrouvé sur le suspect,
> ressemble à une boussole. Il lui sert d'aide-mémoire pour retenir le code.

## 4. Reconnaissance et investigation

### Reconnaissance

Source : [writeup-kiss-of-death.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-md.txt)

### 1. Connexion VPN

Le VPN est un tunnel WireGuard géré par l'application macOS « Gabcloud VPN »
(`com.gabcloudtech.myvpn`). Les tunnels sont pilotables sans `sudo` via
`scutil` :

```bash
scutil --nc list          # lister les services VPN
scutil --nc start <nom>   # activer un tunnel
scutil --nc status <nom>  # vérifier l'état
```

Après activation du tunnel `dvpn-4ad7e8df`, la route `172.28.2/24` apparaît
via `utun6`, et la cible répond :

```bash
curl -sS http://172.28.2.2:8080/   # HTTP 200 — HTML de l'app
```

### 2. Analyse de l'application web

La page HTML charge un bundle JavaScript (SPA Three.js) :
`./assets/index-OeMI0vsb.js` (~1 Mo). Le titre interne est
« Opération RESSAC — Simulation de perquisition ».

L'analyse du JS révèle l'architecture :

- L'état est maintenu côté **serveur** via une API JSON (cookie de session
  `rs_sid`), pas seulement côté client.
- Endpoints identifiés (fonction `hi(r, e)` → `POST api/<r>` avec corps JSON) :

| Endpoint | Corps | Rôle |
|----------|-------|------|
| `api/new`    | `{}`                 | démarre une session |
| `api/action` | `{id}`               | action sur un objet (fouiller, décrocher…) révèle des objets cachés |
| `api/open`   | `{id, open}`         | ouvre un meuble (tiroir, armoire, valise) |
| `api/seal`   | `{id}`               | place un objet sous scellé |
| `api/unseal` | `{id}`               | lève un scellé |
| `api/finish` | `{}`                 | clôture : vérifie les scellés et renvoie le flag |

Le JS contient la table `N2` des **37 objets** de la scène. Chaque objet a un
`id`, `name`, `cat` (catégorie), `room`, `location`, `description`,
`findings[]` (indices), et pour 25 d'entre eux un champ `seal` (libellé du
scellé). Les 12 autres (suspect + meubles) n'ont pas de `seal`.

### 3. Mécanique de découverte

Certains objets ne sont accessibles qu'après une action ou l'ouverture d'un
meuble :

- **Actions** (`api/action`) qui révèlent un objet `<EXPURGE>` :
  - `trash` → révèle `receipt`
  - `parcel` → révèle `simbox`
  - `cigs` → révèle `microsd`
  - `book` → révèle `usb`
  - `frame` → révèle `envelope`
- **Ouvertures** (`api/open`) qui exposent un objet `inside` :
  - `desk_drawer` → `postit`
  - `cab_d2` → `cards`
  - `cab_d3` → `sims`
  - `ns_drawer` → `pistol`
  - `ward_r` → `suitcase`
  - `suitcase` → `cash`, `burner`

Sceller un objet non encore découvert renvoie :
`{"ok":false,"error":"Élément non accessible : il n'a pas encore été découvert."}`.

### Reconnaissance

Source : [writeup-kiss-of-death-q5.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-q5-md.txt)

### 1. Accès à la page

Le tunnel `trycloudflare` ne résout pas correctement en local ; on force l'IP
d'un nœud Cloudflare qui répond :

```bash
curl -s --resolve herald-discuss-simpson-gonna.trycloudflare.com:443:104.18.32.7 \
  https://herald-discuss-simpson-gonna.trycloudflare.com/ -o /tmp/herald.html
```

Autres IP testées : `188.114.96.1`, `104.17.0.1` et `104.21.0.1` fonctionnent
aussi ; `104.16.230.132`, `104.16.231.132` expirent et `104.16.132.229`
renvoie une erreur 403.

### 2. Lecture du JavaScript de la page

Le script embarqué (sauvegardé dans `/tmp/herald.js`) contient trois points
d'entrée :

```js
// déverrouillage du premier profil
const r = await fetch("api/unlock", {method:"POST", ... body: JSON.stringify({pattern: cells})});

// envoi d'un cap de boussole
async function postBearing(bearing){
  const r = await fetch("api/real", {method:"POST", ... body: JSON.stringify({token: TOKEN, bearing: Number(bearing)})});
}

// commentaire révélateur au-dessus de openCompass()
// --- boussole (coffre déguisé : viser le bon AZIMUT fait basculer dans le vrai tél) ---
```

La fonction `boot(data, mode)` positionne `REALMODE = (mode === "real")` et
affiche un message différent selon le mode. Autrement dit :

- `api/unlock` ouvre toujours le profil affiché par défaut ;
- `api/real` ne bascule sur le profil **réel** que si le cap envoyé est le bon
  et s'il est maintenu assez longtemps.

La table des applications nomme explicitement l'application concernée :

```js
{key:"compass", label:"Boussole", ...}
```

### 3. La montre-scellé : un aide-mémoire en forme de boussole

Dans le JavaScript de la scène 3D, la montre portée par le suspect est un
objet externe `compass_watch` (« Montre à aiguilles », scellé `MONTRE`,
description : *« Elle ne fonctionne pas : la trotteuse est immobile sur le
12 »*). Elle est construite par la fonction `R7`, qui reçoit un cap par défaut
et le transmet au modèle :

```js
async function R7(r,{pos:e,heading:t=…,facing:n=[-1,0,0]}){ … }
…
xt = await R7(ve.scene,{pos:ks.seat, facing:ks.facing, heading:ks.heading})
```

Le cap est converti en **heure affichée** par `L7` :

```js
function L7(r){
  const e = Math.round((r % 360 + 360) % 360 * 2);
  return { h: Math.floor(e / 60) % 12, m: e % 60 };
}
```

Puis `D7` place les aiguilles aux angles correspondants :

```js
function D7(r){
  const {h:e, m:t} = L7(r),
        n = e*30 + t*0.5,   // angle de l'aiguille des heures
        i = t*6;            // angle de l'aiguille des minutes
  …
}
```

La montre se lit donc comme un rapporteur : l'aiguille des heures matérialise
un cap. Vérification hors ligne, sans toucher au serveur :

```bash
python3 - <<'EOF'
import re
src = open("app.js").read()
h = int(re.search(r"heading:t=(\d+)", src).group(1))
e = round((h % 360) * 2)
hh, mm = (e // 60) % 12, e % 60
print("heure affichée : %02d:%02d" % (hh, mm))
print("azimut approché :", hh * 30 + mm * 0.5, "degrés")
EOF
```

Sortie observée :

```text
heure affichée : 03:48
azimut approché : …
```

La montre affiche **03:48**. L'angle de son aiguille des heures
(`30°×h + 0,5°×m`) donne un azimut de quelques degrés inférieur à celui de la
cible : une montre analogique arrêtée est un aide-mémoire approximatif, pas un
instrument de visée. C'est exactement le rôle décrit par l'indice.

### 4. L'azimut exact dans la galerie

Le profil accessible contient une photo dont la légende donne l'azimut
précis :

```text
IMG_1004 — Rando dimanche — viser le pylône, azimut 118°
```

Cette légende est un artefact de scénario rattaché au suspect (photo de
randonnée, repère du pylône). Elle donne la valeur exacte, là où la montre
n'en donne qu'une lecture approchée.

## 5. Identification du mécanisme

Le serveur suit la découverte, l’ouverture et le placement sous scellés. Pour le téléphone, un cap doit être maintenu plusieurs secondes : une réponse holding n’équivaut pas à un déverrouillage.

### Raisonnement

Source : [writeup-kiss-of-death.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-md.txt)

Le flag est renvoyé uniquement par `api/finish` lorsque l'ensemble scellé
correspond aux « éléments d'intérêt ». Les tests initiaux montrent que :

- Sceller **tous** les 25 objets scellables → refus (le serveur exige une
  correspondance exacte, pas un sur-ensemble).
- Le message d'erreur est générique et ne donne aucune indication d'objet.

Il faut donc déterminer l'ensemble exact des « éléments d'intérêt ». L'histoire
de l'enquête (espionnage, désinformation, atteinte à la sûreté nationale)
permet de classer les 25 objets scellables en deux groupes :

**Contenants / leurres** (7 — pas des éléments d'intérêt) :
- `trash` (sac poubelle), `parcel` (carton), `cigs` (paquet), `book` (livre),
  `frame` (cadre), `suitcase` (valise) → simples cachettes.
- `watch` (montre de la table de chevet, « rien de notable »).

**Éléments d'intérêt** (18 — la preuve elle-même) :
- Désinformation : `simbox`, `sims`
- Outillage espionnage : `phone`, `laptop`, `usb`, `microsd`
- Financier : `receipt`, `cash`, `envelope`, `cards`
- Arme : `pistol`
- Communications : `burner`
- Documents/identité : `notebook`, `mail`, `wallet`, `postit`
- Divers suspects : `compass_watch` (montre morte), `cam` (caméra IP)

La soumission de cet ensemble de 18 objets fait accepter la clôture et renvoie
le flag, selon la note d’origine ; aucune capture de ce retour n’est conservée.

### Raisonnement

Source : [writeup-kiss-of-death-q5.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-q5-md.txt)

1. `api/unlock` ne renvoie que le profil par défaut : le schéma ouvre le
   téléphone mais ne donne pas le vrai contenu.
2. Le commentaire du script dit littéralement que la boussole est un « coffre
   déguisé » et que viser le bon azimut fait basculer dans le vrai téléphone.
3. L'application qui cache le vrai téléphone est donc la **Boussole**.
4. Le code n'est pas un PIN : c'est un **azimut**. La montre scellée (03:48)
   sert d'aide-mémoire approximatif ; la valeur exacte est l'azimut inscrit
   dans la galerie.
5. Le serveur ne valide pas un cap isolé : il répond d'abord
   `{"ok": false, "holding": true, "held_ms": 0, "hold_ms": 2000}`, puis
   `{"ok": true, "mode": "real", ...}` si le même cap est renvoyé pendant au
   moins deux secondes. Il faut donc boucler.

## 6. Exploitation ou résolution

### Script de résolution (API directe)

Source : [writeup-kiss-of-death.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-md.txt)

On court-circuite l'interface 3D en parlant directement à l'API JSON avec un
cookie de session :

```python
import requests

B = "http://172.28.2.2:8080/api"
s = requests.Session()

def post(ep, data={}):
    return s.post(f"{B}/{ep}", json=data, timeout=15).json()

post("new", {})
# révéler les objets cachés
for a in ["trash", "parcel", "cigs", "book", "frame"]:
    post("action", {"id": a})
# ouvrir les meubles
for o in ["desk_drawer", "cab_d2", "cab_d3", "ns_drawer", "ward_r", "suitcase"]:
    post("open", {"id": o, "open": True})

interest = ["compass_watch", "cam", "receipt", "simbox", "wallet", "phone",
            "microsd", "usb", "laptop", "notebook", "mail", "postit", "cards",
            "sims", "pistol", "envelope", "cash", "burner"]
for oid in interest:
    post("seal", {"id": oid})

r = post("finish", {})          # {"ok": true, "flag": "..."}
print(r)
```

### Validation reproductible (sans le flag)

Source : [writeup-kiss-of-death.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-md.txt)

1. Activer le VPN de l'instance (`scutil --nc start <tunnel>`), vérifier
   `netstat -rn | grep 172.28` puis `curl -sS http://172.28.X.2:8080/` → HTTP 200.
2. Exécuter le script ci-dessus (en remplaçant l'IP de base par celle de
   l'instance courante).
3. Le dernier appel `api/finish` renvoie `{"ok": true, "flag": ...}`.
4. Le flag soumis est validé par la plateforme selon la note d’origine ; aucune
   capture de ce retour n’est conservée.

### Commandes exactes

Source : [writeup-kiss-of-death-q5.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-q5-md.txt)

### Obtention d'un jeton

Le schéma Android a été retrouvé à partir du condensat SHA-1 du fichier
`/data/system/gesture.key` (comparaison des empreintes des séquences
possibles). Le déverrouillage renvoie un jeton de session :

```bash
H=herald-discuss-simpson-gonna.trycloudflare.com
curl -s -m 25 --resolve $H:443:104.18.32.7 \
  -X POST -H 'Content-Type: application/json' \
  -d '{"pattern":[1,6,5,0,7,2,3,8]}' \
  https://$H/api/unlock -o /tmp/unlock.json
```

Réponse (extrait) :

```json
{"ok": true, "token": "…", "mode": "decoy",
 "content": {"apps": {"phone": …, "messages": …, "gallery": …, "clock": …, "compass": …, "settings": …}}}
```

### Récupération de l'azimut

```bash
A=$(python3 -c "
import json, re
d = json.load(open('/tmp/unlock.json'))
caps = [p.get('caption','') for p in d['content']['apps']['gallery']['photos']]
print(int(re.search(r'azimut\s+(\d+)', ' '.join(caps)).group(1)))")
echo "azimut = $A"
```

### Envoi d'un cap unique

```bash
H=herald-discuss-simpson-gonna.trycloudflare.com
T=$(python3 -c "import json;print(json.load(open('/tmp/unlock.json'))['token'])")
curl -s -m 20 --resolve $H:443:104.18.32.7 \
  -X POST -H 'Content-Type: application/json' \
  -d "{\"token\":\"$T\",\"bearing\":$A}" https://$H/api/real
```

```json
{"ok": false, "holding": true, "held_ms": 0, "hold_ms": 2000}
```

### Boucle de maintien

Une requête toutes les ~350 ms jusqu'au basculement :

```bash
H=herald-discuss-simpson-gonna.trycloudflare.com
T=$(python3 -c "import json;print(json.load(open('/tmp/unlock.json'))['token'])")
for i in $(seq 1 8); do
  curl -s -m 15 --resolve $H:443:104.18.32.7 \
    -X POST -H 'Content-Type: application/json' \
    -d "{\"token\":\"$T\",\"bearing\":$A}" https://$H/api/real -o "/tmp/r$i.json"
  python3 -c "
import json
d=json.load(open('/tmp/r$i.json'))
print('$i','ok=',d.get('ok'),'mode=',d.get('mode'),'held_ms=',d.get('held_ms'),'apps=',len(d.get('content',{}).get('apps',{})))"
  sleep 0.35
done
```

Sortie observée lors de la dernière exécution :

```text
1 ok= False mode= None held_ms= 0 apps= 0
2 ok= False mode= None held_ms= 877 apps= 0
3 ok= False mode= None held_ms= 1814 apps= 0
4 ok= True  mode= real held_ms= None apps= 17
5 ok= False mode= None held_ms= 0 apps= 0
```

Les réponses courtes sont des refus avec progression du maintien ; les
réponses `mode: real` contiennent les 17 applications du profil réel
(messages, chat, contacts, email, navigateur, notes, galerie, calendrier,
cartes, banque, fichiers, réglages, musique, horloge, météo, coffre, …). On y
trouve notamment une discussion avec « Le Relais » et un dossier « Masque »
dans le coffre — matière des questions suivantes, hors sujet ici.

### Tolérance du serveur (important pour l'interprétation)

Le serveur n'exige pas la valeur au degré près : le contrôle est un écart
angulaire maximal, de l'ordre de ±4°, autour de la cible. Mesures réalisées
avec un jeton neuf à chaque essai (un seul POST, donc pas de maintien) :

| Cap relatif à l'azimut de la galerie | Réponse |
| --- | --- |
| −5° | `{"ok": false}` (rejeté, pas de maintien) |
| −4° | `holding: true` |
| valeur exacte | `holding: true` |
| +4° | `holding: true` |
| +5° | `{"ok": false}` (rejeté) |

La plage acceptée est donc centrée sur l'azimut de la galerie. La lecture
approchée de la montre tombe dans cette plage, ce qui explique qu'elle
fonctionne aussi : c'est un aide-mémoire, pas la valeur de référence. La
valeur centrale, celle qui est encodée côté serveur, est l'azimut de la légende.

### Validation reproductible (sans publier la réponse)

Source : [writeup-kiss-of-death-q5.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-q5-md.txt)

Le script ci-dessous rejoue toute la chaîne. Il lit l'azimut dans la légende
de la galerie, déverrouille le téléphone, maintient le cap et vérifie
l'ouverture du profil réel. Aucune valeur de réponse n'est écrite en clair.

```python
import json, re, subprocess, time

HOST = "herald-discuss-simpson-gonna.trycloudflare.com"
IP   = "104.18.32.7"
BASE = f"https://{HOST}"

def post(path, payload):
    out = subprocess.run(
        ["curl", "-s", "-m", "20", "--resolve", f"{HOST}:443:{IP}",
         "-X", "POST", "-H", "Content-Type: application/json",
         "-d", json.dumps(payload), BASE + path],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)

# 1. déverrouillage (schéma retrouvé hors ligne)
decoy = post("/api/unlock", {"pattern": [1, 6, 5, 0, 7, 2, 3, 8]})
token = decoy["token"]

# 2. azimut lu dans la légende de la galerie
captions = [p.get("caption", "") for p in decoy["content"]["apps"]["gallery"]["photos"]]
azimut = int(re.search(r"azimut\s+(\d+)", " ".join(captions)).group(1))
print("azimut lu dans la galerie")

# 3. maintien du cap jusqu'à la bascule
real = None
for _ in range(12):
    r = post("/api/real", {"token": token, "bearing": azimut})
    if r.get("ok") and r.get("mode") == "real":
        real = r
        break
    time.sleep(0.35)

assert real is not None, "le maintien n'a pas abouti"
apps = set(real["content"]["apps"])
assert {"vault", "bank", "chat", "files"} <= apps
print("OK — profil réel ouvert via la Boussole ;", len(apps), "applications")
```

Exécution attendue :

```text
azimut lu dans la galerie
OK — profil réel ouvert via la Boussole ; 17 applications
```

### Réponse

Source : [writeup-kiss-of-death-q5.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-q5-md.txt)

- Application : **Boussole** (`compass`), le « coffre déguisé ».
- Code : l'**azimut** indiqué dans la galerie du téléphone. La montre scellée
  (03:48) n'en donne qu'une lecture approchée, cohérente avec la cible à
  quelques degrés près et acceptée grâce à la tolérance du serveur.

La valeur exacte a été transmise au hub CTFHUB et n'est pas recopiée ici.

## 7. Scripts et automatisation

Les copies sont expurgées et peuvent nécessiter la remise en place de paramètres ou d’artefacts. **Analyse syntaxique uniquement, sans exécution des solveurs ni de leurs opérations réseau.** Les imports listés ne constituent pas un environnement de dépendances testé. Les chemins relatifs historiques peuvent nécessiter une adaptation.

| Script | Source | Imports / dépendances | Contrôle | Nature |
|---|---|---|---|---|
| [adb--crack_pattern.py](scripts/adb--crack_pattern.py) | `adb/crack_pattern.py` | hashlib, itertools | syntaxe Python valide | traitement local apparent |
| [forensic-kissofdeath--dl.sh](scripts/forensic-kissofdeath--dl.sh) | `forensic/kissofdeath/dl.sh` | voir imports/commandes | non applicable | réseau ou interaction de service |
| [forensic-kissofdeath--dl2.sh](scripts/forensic-kissofdeath--dl2.sh) | `forensic/kissofdeath/dl2.sh` | voir imports/commandes | non applicable | réseau ou interaction de service |

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Q1 — Recueillir les 18 scellés et clôturer la perquisition. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |
| Q2 à Q4 — Énoncés originaux absents ; déverrouillage Android mentionné comme prérequis. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |
| Q5 — Identifier l’application qui cache le vrai téléphone et son mécanisme d’accès. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |
| Q6 — Énoncé absent ; document numérisé conservé. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |
| Q7 — Dreamer, documenté séparément sous son nom propre. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |

## 9. Difficultés rencontrées

### Pistes qui ont échoué

Source : [writeup-kiss-of-death.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-md.txt)

- **Connexion VPN de la première instance** : le tunnel `dvpn-464da960.conf`
  (172.28.8.0/24) ne réalisait pas de handshake (0 paquet entrant sur `utun6`),
  très probablement parce que l'instance avait expiré et/ou que le réseau
  invité bloquait l'UDP WireGuard. La relance de l'instance (nouvelle config
  `dvpn-4ad7e8df.conf`) a résolu le problème.
- **Sceller les 25 objets** : refus — le serveur exige l'ensemble exact, pas un
  sur-ensemble.
- **Réduction « un à la fois »** : tenter de désactiver un seul scellé puis
  `finish` ne suffit pas, car il reste plusieurs leurres à retirer d'un coup ;
  la classification par le scénario a été nécessaire.
- **Chercher un marqueur « interest » dans le JS** : absent, la liste des
  éléments d'intérêt est uniquement côté serveur.

### Pistes qui ont échoué

Source : [writeup-kiss-of-death-q5.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-q5-md.txt)

- **Utiliser le schéma comme « code »** : `api/unlock` ne renvoie que le profil
  par défaut, et le code attendu par la question est un code d'accès au vrai
  téléphone.
- **Chercher un code PIN dans le coffre** : la liste des documents du coffre
  (`beth.png`, `vault.enc`, `ticket_parking.pdf`, `plan_km7.jpg`,
  `signalx.apk`) est affichée, mais la page ne propose aucune saisie de PIN et
  le JavaScript n'appelle aucune API de coffre.
- **Prendre l'angle de la montre pour la valeur exacte** : il ne donne qu'une
  lecture approchée, à quelques degrés de la cible, et ne tombe juste que
  parce que le serveur tolère un écart.
- **Un seul POST sur `api/real`** : la réponse est toujours
  `holding: true, held_ms: 0` ; sans maintien, le serveur ne valide jamais.
- **Compter sur la boussole du navigateur** : sur un poste de travail, aucun
  événement `deviceorientationabsolute` n'arrive ; la page affiche
  « Capteur indisponible ». Il faut simuler le cap via l'API.
- **Lire le profil `real` via `api/unlock` avec un autre schéma** : le mode
  reste celui du profil par défaut, la bascule est uniquement déclenchée par
  `api/real`.

## 10. Analyse technique approfondie

Le serveur suit la découverte, l’ouverture et le placement sous scellés. Pour le téléphone, un cap doit être maintenu plusieurs secondes : une réponse holding n’équivaut pas à un déverrouillage. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Aucune recommandation spécifique supplémentaire n’est établie au-delà des limites du mécanisme décrit. Pour les exercices purement documentaires, la priorité est la conservation des originaux, la provenance des pièces et la séparation des hypothèses et des constats.

## 12. Conclusion

Perquisitionner une simulation, puis exploiter les scellés et le téléphone pour poursuivre l’enquête. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Signalement local uniquement (reported).

### Leçons

Source : [writeup-kiss-of-death.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-md.txt)

- Une « simulation 3D » cache souvent une API JSON stateful derrière un client
  Three.js : lire le bundle JS et interroger l'API directement est plus rapide
  et plus fiable que l'exploration manuelle.
- Le flag est servi par le serveur au moment de la clôture ; le client ne fait
  que l'afficher. L'analyse du JS révèle les endpoints et la table d'objets,
  mais pas la logique de validation (côté serveur).
- La mécanique action/ouverture → découverte → scellé est le cœur du
  challenge : identifier les objets « cachés »/« intérieurs » et leurs
  déclencheurs était indispensable pour constituer l'ensemble complet.

### Leçons

Source : [writeup-kiss-of-death-q5.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-q5-md.txt)

- Lire le JavaScript d'une simulation : un simple commentaire (« coffre
  déguisé ») donne la mécanique exacte.
- Un objet de scène peut être un aide-mémoire : une horloge analogique est un
  rapporteur d'angle, mais sa lecture reste approximative.
- Toujours distinguer une valeur exacte écrite dans un artefact (légende de
  photo) d'une valeur dérivée approximative (angle d'aiguille).
- Une API à « dwell » (maintien) ne se valide pas en un seul appel : prévoir
  une boucle et interpréter `holding` / `held_ms`.
- Mesurer la tolérance serveur avant de conclure : une valeur acceptée n'est
  pas nécessairement la valeur cible. Le centre de la plage acceptée donne la
  cible réelle.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-kiss-of-death.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-md.txt) — origine : `forensic/kissofdeath/writeup-kiss-of-death.md`.

- [writeup-kiss-of-death-q5.md](evidence/forensic-kissofdeath-writeup-kiss-of-death-q5-md.txt) — origine : `forensic/kissofdeath/writeup-kiss-of-death-q5.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


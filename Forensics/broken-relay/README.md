# Broken relay

[Accueil](../../README.md) · [Forensics](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Broken relay |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Forensics |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | AD1, Firefox, SQLite |
| Validation | Signalement local uniquement (reported) |

## 1. Introduction

Retrouver l’URL de stockage utilisée par le suspect à partir de son poste.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

## 2. Énoncé du challenge

- Retrouver l’URL dans les traces de navigation du poste.

### Objectif

Source : [writeup-broken-relay.md](evidence/forensic-broken-writeup-broken-relay-md.txt)

- **Challenge** : Broken relay — FORENSICS (100 pts)
- **Auteur** : uchiwa
- **Énoncé** : un groupe de hackers (ayant initié les attaques contre Tervalis)
  utiliserait une « plateforme secrète » pour planifier ses opérations. Il faut
  identifier, sur la machine du suspect, **l'URL utilisée pour accéder à cette
  plateforme**.
- **Format attendu** : le préfixe de la compétition, suivi d'une URL
  `http://domain.tld:XXXX` entre accolades.

## 3. Analyse initiale

2 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### État initial

Source : [writeup-broken-relay.md](evidence/forensic-broken-writeup-broken-relay-md.txt)

Une seule ressource est fournie : un lien `mega.nz` pointant vers une archive
`thanos_desktop.zip` (~1,16 Gio). Le nom suggère l'image de la machine du
suspect « Thanos ».

## 4. Reconnaissance et investigation

### Reconnaissance

Source : [writeup-broken-relay.md](evidence/forensic-broken-writeup-broken-relay-md.txt)

### 1. Récupération du fichier

```
megadl "https://mega.nz/file/Qwc2SCaR#SEiGdkrYkH8bklsUCO1vlEHJNifKldEUz9Tf1ZzEYKc"
```

Contenu de l'archive :

```
thanos_desktop.zip  ->  thanos_desktop.ad1  (1 264 587 858 octets)
```

`file` identifie le fichier décompressé comme un conteneur forensique :

```
$ file thanos_desktop.ad1
thanos_desktop.ad1: data
```

L'en-tête hexadécimal (`xxd`) révèle la signature `ADSEGMENTEDFILE` suivie de
`ADLOGICALIMAGE` et du libellé `Custom Content Image([Multi])`. Il s'agit d'une
**image logique AccessData AD1** (format de FTK Imager), un conteneur arborescent
de fichiers avec métadonnées NTFS et données compressées zlib — et non une image
disque brute.

### 2. Choix du parseur AD1

- `mega.py` (pip) : échoue sur Python 3.14 (`asyncio.coroutine` supprimé).
- `strings` sur le `.ad1` brut : inefficace (données zlib + structurées, pas de
  séquences d'URL en clair).
- **`dissect.evidence`** (pip) : parseur AD1 fonctionnel, retenu.

```bash
.venv/bin/pip install dissect.evidence
```

Script de parcours de l'arborescence :

```python
from pathlib import Path
from dissect.evidence.ad1 import AD1

img = AD1([Path("thanos_desktop.ad1")])

def walk(entry, prefix=""):
    path = f"{prefix}/{entry.name}" if entry.name != "/" else prefix
    print(("[DIR ] " if entry.is_dir() else "[FILE] ") + path)
    if entry.is_dir():
        for child in entry.iterdir():
            walk(child, path)

walk(img.root, "")
```

L'image contient un poste Windows (NTFS), un utilisateur **`thanos`** (SID
`S-1-5-21-3267892857-469485820-920249857-1000`), et notamment un profil
**Firefox** actif :

```
Users/thanos/AppData/Roaming/Mozilla/Firefox/Profiles/hk1xy9bm.default-release/
├── places.sqlite        (5 242 880 octets)
├── cookies.sqlite       (98 304 octets)
├── logins.json          (845 octets)
├── key4.db              (294 912 octets)
├── formhistory.sqlite   (262 144 octets)
├── sessionstore.jsonlz4 (2 649 octets)
└── bookmarkbackups/bookmarks-2026-11-09_10_*.jsonlz4
```

On note aussi, dans `Users/thanos/Recent`, des raccourcis `hosts.lnk` et
`etc.lnk` (le suspect a ouvert/édité le fichier `hosts`), ainsi qu'un
`Desktop/channel.pdf` (protégé par mot de passe — piste secondaire, non
nécessaire).

### 3. Extraction ciblée

Un script `dissect.evidence` extrait les fichiers d'intérêt (profil Firefox,
Documents/Desktop/Downloads/Recent/Favorites) vers `./extract/` en préservant
un nom aplati de chemin.

### Découverte de l'URL

Source : [writeup-broken-relay.md](evidence/forensic-broken-writeup-broken-relay-md.txt)

La source la plus directe pour « l'URL d'accès à une plateforme » est l'historique
Firefox (`places.sqlite`).

```bash
sqlite3 "<extract>/...hk1xy9bm.default-release__places.sqlite" \
  "SELECT url, title, visit_count, last_visit_date
   FROM moz_places ORDER BY visit_count DESC;"
```

Résultat : un **seul et unique site réellement visité** (`visit_count = 1`),
dont le titre est `RELAY`. Les autres entrées sont les favoris par défaut de
Firefox (`mozilla.org`, `support.mozilla.org`) avec `visit_count = 0`.

Interrogations complémentaires confirmant le résultat :

```bash
# Historique de visites (table de jointure)
sqlite3 "$PL" "SELECT v.visit_date, p.url FROM moz_historyvisits v
               JOIN moz_places p ON v.place_id=p.id ORDER BY v.visit_date;"

# Favoris
sqlite3 "$PL" "SELECT b.title, p.url FROM moz_bookmarks b
               LEFT JOIN moz_places p ON b.fk=p.id WHERE p.url IS NOT NULL;"
```

Le champ `rev_host` (hôte inversé) confirme la cohérence de l'hôte de la
plateforme. L'URL correspond exactement au gabarit attendu
`http://domain.tld:XXXX` (schéma `http`, hôte interne non public, port
applicatif non standard).

## 5. Identification du mécanisme

L’image AD1 conserve les bases Firefox. La jointure des visites et des URL, puis la comparaison aux favoris, relie une adresse à l’activité du profil.

### Raisonnement

Source : [writeup-broken-relay.md](evidence/forensic-broken-writeup-broken-relay-md.txt)

1. Le titre du challenge **« Broken relay »** et le thème « plateforme secrète
   de planification » orientent vers un service de messagerie/relais.
2. L'image est un poste d'un utilisateur « thanos » avec un profil Firefox
   actif — l'historique est l'endroit attendu pour retrouver une URL visitée.
3. Une seule URL porte un titre explicite (`RELAY`) et un `visit_count > 0` :
   c'est la plateforme recherchée.

## 6. Exploitation ou résolution

### Validation reproductible (sans l'answer)

Source : [writeup-broken-relay.md](evidence/forensic-broken-writeup-broken-relay-md.txt)

1. Télécharger l'archive et extraire `thanos_desktop.ad1`.
2. `pip install dissect.evidence` puis ouvrir l'image avec `AD1([Path("thanos_desktop.ad1")])`.
3. Extraire
   `Users/thanos/AppData/Roaming/Mozilla/Firefox/Profiles/hk1xy9bm.default-release/places.sqlite`.
4. Exécuter :

   ```sql
   SELECT url, title, visit_count FROM moz_places ORDER BY visit_count DESC;
   ```

5. La ligne avec `title = 'RELAY'` et `visit_count = 1` donne l'URL attendue,
   qu'il suffit d'envelopper dans le format du flag décrit en tête de document.

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Retrouver l’URL dans les traces de navigation du poste. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |

## 9. Difficultés rencontrées

### Pistes échouées / écartées

Source : [writeup-broken-relay.md](evidence/forensic-broken-writeup-broken-relay-md.txt)

- **`mega.py`** : incompatibilité `asyncio` avec Python 3.14.
- **`strings` brut sur le `.ad1`** : aucune URL en clair (contenu zlib + offsets
  structurés).
- **`channel.pdf`** (Desktop) : protégé par mot de passe ; non nécessaire.
- **`hosts.lnk` / `etc.lnk`** : indices d'édition du fichier `hosts`, mais pas
  de plateforme distante dédiée à exploiter ici.
- Téléchargement `megadl` : blocage répété à ~62,93 % ; contourné par une boucle
  de reprise automatique (watchdog qui relance `megadl`, lequel reprend depuis le
  fichier temporaire `.megatmp`).

## 10. Analyse technique approfondie

L’image AD1 conserve les bases Firefox. La jointure des visites et des URL, puis la comparaison aux favoris, relie une adresse à l’activité du profil. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Aucune recommandation spécifique supplémentaire n’est établie au-delà des limites du mécanisme décrit. Pour les exercices purement documentaires, la priorité est la conservation des originaux, la provenance des pièces et la séparation des hypothèses et des constats.

## 12. Conclusion

Retrouver l’URL de stockage utilisée par le suspect à partir de son poste. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Signalement local uniquement (reported).

### Enseignements

Source : [writeup-broken-relay.md](evidence/forensic-broken-writeup-broken-relay-md.txt)

- L'AD1 est un conteneur **logique** (arborescence + zlib), pas une image disque ;
  `strings`/TSK ne suffisent pas, il faut un parseur dédié (`dissect.evidence`,
  `pyad1`, `ad1-viewer`…).
- Pour « retrouver une URL visitée », cibler en priorité l'historique navigateur
  (`places.sqlite`) plutôt que scanner tout le conteneur.
- Distinguer `visit_count` (pages réellement consultées) des favoris par défaut
  (`visit_count = 0`).

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-broken-relay.md](evidence/forensic-broken-writeup-broken-relay-md.txt) — origine : `forensic/broken/writeup-broken-relay.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


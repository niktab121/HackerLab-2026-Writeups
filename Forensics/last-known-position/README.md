# Last Known Position

[Accueil](../../README.md) · [Forensics](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Last Known Position |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Forensics |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | SQLite, historiques shell, GPS, SIGINT, EXIF |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Retrouver la destination réelle d’un transport dont le registre a été falsifié.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** La consigne anglaise est reproduite comme citation d’énoncé. Les historiques cachés .bash_history et .sqlite_history sont des pièces du challenge, pas l’historique personnel de la machine.

## 2. Énoncé du challenge

- Determine the exact facility where Agent AVALD is being held.

## 3. Analyse initiale

65 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### 1. Inventaire et consignes de format

Source : [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt)

Après extraction de `challenge.zip`, le fichier `BRIEFING.md` indique que l’agent a été transporté le 2024-11-03 par une unité tactique et qu’un opérateur a falsifié les registres. Les éléments importants sont notamment :

- `evidence_files.zip` : poste de travail de l’opérateur, avec base de transfert, historique shell, notes, manifeste et journal des accès aux portails ;
- `vehicle_tracking.db` : positions GPS des véhicules ;
- `signal_intel.csv`, `sigint_stations.json` et `station_diagnostics.json` : interceptions et stations de radiogoniométrie ;
- `checkpoint_logs.csv` et `dispatch_records.jsonl` : passages et événements opérationnels ;
- `facility_registry.csv`, `transport_routes.csv` et `gate_map.conf` : installations, itinéraires et correspondance des portails.

Le fichier `reporting_format.md` impose la structure suivante :

```text
<EXPURGE>
```

Les coordonnées doivent être arrondies au degré entier. Les longitudes ouest sont encodées en valeur positive, avec le suffixe `W`.

---

## 4. Reconnaissance et investigation

La reconnaissance conservée se limite aux fichiers décrits dans l’inventaire. Aucun journal de commandes permettant d’établir une chronologie plus fine n’a été retrouvé.

## 5. Identification du mécanisme

Le croisement du manifeste, des historiques de modification, des accès aux portails et des checkpoints permet de distinguer la route réelle des champs falsifiés. GPS et radiogoniométrie nécessitent de contrôler diagnostics, biais et calibration.

## 6. Exploitation ou résolution

### Résumé

Source : [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt)

Le challenge demande de retrouver la destination réelle du transport de l’agent AVALD, parti du Nordvelt Grand Hotel le 3 novembre 2024. Les registres informatiques de transfert ont été altérés : la ligne associée au sujet `SUBJ-7742` ne conserve ni la destination ni le véhicule. Il faut donc recouper les artefacts indépendants : manifeste, historique opérateur, journaux de portail, checkpoints, GPS, SIGINT et registre des installations.

La destination identifiée est **FACILITY-KAPPA**, dans la région **Nordvelt**. La position à encoder est arrondie à **64°N, 22°W**.

**Flag :**

```text
<EXPURGE>
```

> Le flag doit être saisi sans espaces. Les espaces ajoutés lors de la soumission expliquent vraisemblablement le rejet rencontré précédemment.

---

### 2. Repérer la ligne de transfert falsifiée

Source : [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt)

Dans la base extraite `transfer_log.db`, la ligne correspondant à `SUBJ-7742` est la ligne 15 :

```text
(15, SUBJ-7742, 2024-11-03T14:15:00Z, TSD-HQ,
 NULL, TSD-OPR-4451, NULL, priority, TSD-2024-1887, COMPLETED)
```

Deux champs essentiels ont été vidés : `destination` et `vehicle_id`. La suppression est cohérente avec l’historique shell de l’opérateur, qui montre une commande de mise à jour visant explicitement `SUBJ-7742` :

```sql
UPDATE transfers
SET destination=NULL, vehicle_id=NULL
WHERE subject_id='SUBJ-7742'
```

L’historique contient aussi une commande de suppression d’entrées d’audit pour le record 15, ainsi que des commandes visant à effacer des journaux et des documents temporaires. La ligne de base de données ne peut donc pas être considérée comme une preuve de destination.

Le manifeste opérationnel `transport_manifest_VLD-2024-1103-047.txt`, lui, rattache le transport à l’opération `TSD-2024-1887` et fournit plusieurs pivots fiables :

- sujet : `TIMS AVALD`, identifiant `SUBJ-7742` ;
- escorte : `TSD-OPR-4451`, unité `TSD-OPS-04` ;
- véhicule : `VLD-74-OPS` ;
- fréquence radio : `148.325 MHz` ;
- corridor : `Nord-7` ;
- départ indiqué : 14:10 UTC ;
- arrivée annoncée : 16:42 UTC.

Le nom de la destination a été remplacé par la mention « SEE GATE LOG » : le manifeste confirme donc qu’il faut exploiter les traces de portail plutôt que faire confiance au champ effacé.

---

### 3. Établir le parcours réel

Source : [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt)

Les journaux de dispatch associent bien l’opération au véhicule `VLD-74-OPS` et à l’escorte `TSD-OPR-4451` :

- 13:50 UTC : affectation de la directive `TSD-2024-1887` ;
- 14:10 UTC : départ du Nordvelt Grand Hotel ;
- 14:22 UTC : passage du checkpoint `CP-N7-02` ;
- 15:15 UTC : passage de `CP-N7-05` ;
- 16:05 UTC : passage de `CP-N7-08` ;
- 16:38 UTC : passage du checkpoint final `CP-N7-11` ;
- 16:42 UTC : arrivée au point désigné et transfert à l’agent récepteur `TSD-OPR-4460`.

`checkpoint_logs.csv` confirme les passages Nord-7 sous la même plaque et le même badge. Cela permet d’écarter les autres véhicules et transferts visibles dans le reste des fichiers.

La planche des caméras de circulation apporte une confirmation visuelle : les images `frame_tcam_n7_003_143022.jpg`, `frame_tcam_n7_005_145542.jpg`, `frame_tcam_n7_006_150815.jpg` et `frame_tcam_n7_008_171205.jpg` montrent la plaque `VLD-74-OPS` sur le corridor. Les autres images contiennent différents véhicules, qui ne doivent pas être confondus avec le convoi.

---

### 4. Identifier le portail d’arrivée

Source : [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt)

Le journal `evidence/var/log/gate_access.log` contient l’événement décisif :

```text
2024-11-03T16:42:00Z GATE-12E TSD-OPR-4451 ENTRY
```

L’heure est identique à celle de l’arrivée dans le dispatch et le manifeste, et le badge est celui de l’escorte du convoi. Le portail `GATE-12E` est donc lié au transfert de l’agent, et non à une visite sans rapport.

La carte `evidence/etc/gate_map.conf` indique :

```text
GATE-12E    SECTOR-NV-12    CLASSIFIED
```

Le portail est dans le secteur Nordvelt, mais son installation n’est pas nommée dans cette carte. C’est précisément pourquoi les autres sources et le registre des installations sont nécessaires. La correspondance temporelle — même minute, badge de l’escorte, arrivée opérationnelle — donne toutefois une association forte entre le portail classifié et le transfert.

---

### 5. Retrouver l’installation et contrôler la région

Source : [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt)

Le registre `facility_registry.csv` liste notamment :

```text
FACILITY-KAPPA,Nordvelt,MAXIMUM,High-Security Detention,75,,
```

Kappa est l’installation de détention à sécurité maximale du registre. Ses coordonnées sont masquées, mais son code et sa région sont connus. Parmi les installations enregistrées dans la région Nordvelt, c’est la destination cohérente avec un transfert prioritaire d’un sujet classé « HIGH-VALUE » et une arrivée à un portail classifié.

Les autres destinations Nordvelt enregistrées ont des fonctions différentes : `FACILITY-LAMBDA` est un soutien opérationnel, `FACILITY-XI` un poste SIGINT et `FACILITY-TAU` une station de patrouille frontalière. Elles ne correspondent pas à une installation de détention de haute sécurité.

Le choix de Kappa s’appuie donc sur le recoupement de plusieurs éléments : portail classifié dans le secteur Nordvelt, transfert prioritaire d’un détenu de haute valeur, arrivée confirmée au même instant, et registre qui identifie Kappa comme le centre de détention de niveau maximal.

---

### 6. Traiter le GPS et le SIGINT sans se laisser piéger

Source : [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt)

### GPS

La base nationale contient de nombreux pings pour `VLD-74-OPS`, mais les valeurs affichées durant le trajet sont manifestement aberrantes : certaines latitudes/longitudes sont autour de `134` et `106`, impossibles comme coordonnées géographiques ordinaires. À l’approche de la fin, les positions semblent artificielles et restent regroupées autour de ces valeurs. Elles ne doivent pas être interprétées littéralement comme la position du convoi.

Cette anomalie explique pourquoi il faut privilégier les événements de checkpoint, les heures et les identifiants recoupés, plutôt que de lire directement un point GPS brut comme destination.

### SIGINT

La fréquence `148.325 MHz` est explicitement indiquée dans le manifeste. Les interceptions de cette fréquence, en particulier celles proches de 16:39 UTC, apportent une vérification indépendante de la zone d’arrivée. Les relevés des stations sont cependant à interpréter avec `station_diagnostics.json` : les stations ALPHA et DELTA ont des anomalies signalées autour de la fenêtre de transfert (saturation AGC, multipath ou ambiguïté de relèvement). Il est donc prudent de ne pas s’appuyer sur un seul relèvement dégradé.

Les relevés des stations non signalées comme dégradées, associés aux coordonnées connues des stations, pointent vers le secteur autour de **64°N, 22°W**, compatible avec le site de Kappa et avec les traces d’arrivée. Les caméras fournissent aussi des coordonnées EXIF pour les emplacements des caméras ; ces coordonnées ne sont pas celles du véhicule ou de l’installation et ne doivent pas être prises pour la position finale.

---

### 7. Construire le flag

Source : [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt)

À ce stade, les champs sont :

- `DEST_CODE` : `KAPPA` — le format demande le code court utilisé dans le nom `FACILITY-KAPPA` ;
- `ADMIN_REGION` : `NORDVELT` ;
- latitude arrondie : `64N` ;
- longitude ouest arrondie, sans signe négatif : `22W`.

En respectant exactement le modèle du fichier `reporting_format.md`, on obtient :

```text
<EXPURGE>
```

Il faut soumettre cette chaîne sans espaces au début, à la fin ou entre ses composantes.

---

### 8. Indices décisifs, en bref

Source : [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt)

1. `SUBJ-7742` correspond à l’agent AVALD et le record 15 a été vidé intentionnellement ; l’historique shell confirme la manipulation.
2. Le manifeste fournit la plaque `VLD-74-OPS`, l’escorte `TSD-OPR-4451`, la fréquence `148.325 MHz` et le corridor Nord-7.
3. Dispatch et checkpoints confirment l’itinéraire et l’arrivée à 16:42 UTC.
4. Le journal de portail place `TSD-OPR-4451` à `GATE-12E` exactement à 16:42 UTC ; la carte situe ce portail dans le secteur Nordvelt, mais le marque classifié.
5. Le registre désigne `FACILITY-KAPPA` comme l’installation de détention de sécurité maximale de Nordvelt.
6. Les données SIGINT utilisables corroborent la zone géographique ; les mesures GPS brutes sont incohérentes et les anomalies de station imposent un recoupement.
7. Le code demandé est le code court `KAPPA`, avec région et coordonnées normalisées conformément au protocole.

### Réponse

Source : [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt)

```text
<EXPURGE>
```

## 7. Scripts et automatisation

Les copies sont expurgées et peuvent nécessiter la remise en place de paramètres ou d’artefacts. **Analyse syntaxique uniquement, sans exécution des solveurs ni de leurs opérations réseau.** Les imports listés ne constituent pas un environnement de dépendances testé. Les chemins relatifs historiques peuvent nécessiter une adaptation.

| Script | Source | Imports / dépendances | Contrôle | Nature |
|---|---|---|---|---|
| [misc-last--solveur.py](scripts/misc-last--solveur.py) | `misc/last/solveur.py` | argparse, datetime | syntaxe Python valide | traitement local apparent |

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Determine the exact facility where Agent AVALD is being held. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

Aucune tentative infructueuse n’est consignée dans les sources rattachées. Cela ne prouve pas qu’il n’y en a pas eu. Les limites matérielles sont indiquées dans l’introduction.

## 10. Analyse technique approfondie

Le croisement du manifeste, des historiques de modification, des accès aux portails et des checkpoints permet de distinguer la route réelle des champs falsifiés. GPS et radiogoniométrie nécessitent de contrôler diagnostics, biais et calibration. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Aucune recommandation spécifique supplémentaire n’est établie au-delà des limites du mécanisme décrit. Pour les exercices purement documentaires, la priorité est la conservation des originaux, la provenance des pièces et la séparation des hypothèses et des constats.

## 12. Conclusion

Retrouver la destination réelle d’un transport dont le registre a été falsifié. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Aucune validation plateforme exportée.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [Write-up_—_challenge06___Last_Known_Position.md](evidence/operationtervalis-write-up-challenge06-last-known-position-md.txt) — origine : `operationtervalis/Write-up_—_challenge06___Last_Known_Position.md`.

- [BRIEFING.md](evidence/misc-last-challenge-briefing-md.txt) — origine : `misc/last/challenge/BRIEFING.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


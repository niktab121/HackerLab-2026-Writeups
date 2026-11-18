# Connecting the Dots

[Accueil](../../README.md) · [Blockchain](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Connecting the Dots |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Blockchain |
| Difficulté | Non documentée |
| Points | 200 |
| Auteur | W1z4rd |
| Statut | **Partial** |
| Technologies | Bitcoin, UTXO, Blockstream, mempool.space |
| Validation | Signalement local uniquement (reported) |

## 1. Introduction

Reconstituer les chemins de transactions entre le départ THORChain et une adresse cible.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Le rectificatif du hub prime sur le récit local : le chemin de huit transactions a été refusé ; un chemin de onze transactions reste candidat. trace.py et check_paths.py cités par le hub sont absents. Les scripts locaux diffèrent et ne doivent pas être présentés comme ces outils. Aucune requête blockchain n’a été effectuée pour cette édition.

## 2. Énoncé du challenge

- Identifier le chemin des hachages entre la transaction de départ et le portefeuille cible.

### 1. Contexte & Objectif

Source : [anotherwu](evidence/blockchain-anotherwu.txt)

L'énoncé indique :
> *"Des fonds illicites provenant d'une autre transaction inter-chaînes Thorchain dont le hachage est : `<HEX_EXPURGE>` ont atteint le portefeuille `bc1qxn7algyps6gq8jcg8u3ys72zwpkpksnjwuk4wn` après plusieurs relais de fonds, puis ont été agrégés avec un portefeuille `bc1qermfghzn6u475vktnxusklxe60cthv98djfwwy` qui a reçu 0,00412369 BTC du portefeuille de retrait Wasabi du criminel. Identifiant le chemin des hachages de transaction entre la transaction Thorchain et le portefeuille `bc1qxn7algyps6gq8jcg8u3ys72zwpkpksnjwuk4wn`.*
> 
> **Format du drapeau** : `<EXPURGE>`

---

## 3. Analyse initiale

8 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### Objectif et périmètre

Source : [compte rendu du hub](evidence/hub-49647.txt)

Challenge de traçage blockchain, annoncé à 200 points. Retrouver le chemin de transactions entre la transaction Bitcoin associée à THORChain fournie dans l'énoncé et l'adresse cible fournie. L'indice complémentaire est une agrégation ultérieure avec une seconde adresse ayant reçu 412 369 satoshis.

Les recherches portent uniquement sur les données publiques Bitcoin et le hub local. Aucun transfert, aucune signature et aucune soumission au site de compétition ne sont effectués. L'attribution criminelle et l'étiquette Wasabi sont des éléments de l'énoncé : les relations entre transactions les corroborent structurellement, mais ne prouvent pas à elles seules l'identité d'un propriétaire.

Les hachages du chemin sont volontairement absents de ce document, car ils constituent la réponse soumise. Les arguments correspondants des commandes sont remplacés par des variables. Aucun résultat brut contenant ces hachages n'est conservé ici.

### État initial et reconnaissance

Source : [compte rendu du hub](evidence/hub-49647.txt)

Le point de départ est confirmé au bloc 884973. Il comporte une entrée et trois sorties : 80 965 529 satoshis vers une première adresse, 11 459 184 106 satoshis vers une seconde et une sortie de valeur nulle.

L'historique de l'adresse cible révèle une transaction qui la crédite de 373 660 satoshis, puis une transaction qui dépense ce montant avec deux autres entrées : 423 618 et 412 369 satoshis. Cette dernière entrée provient bien de la seconde adresse de l'énoncé. La transaction d'agrégation a une sortie de 1 208 368 satoshis et des frais de 1 279 satoshis. La conservation des montants est vérifiée :

```text
423618 + 373660 + 412369 = 1208368 + 1279
```

Cette agrégation est un contrôle contextuel ; elle se produit après l'arrivée des fonds à la cible et n'appartient donc pas au chemin demandé.

## 4. Reconnaissance et investigation

La reconnaissance conservée se limite aux fichiers décrits dans l’inventaire. Aucun journal de commandes permettant d’établir une chronologie plus fine n’a été retrouvé.

## 5. Identification du mécanisme

Une entrée Bitcoin désigne un outpoint précis. Une suite d’outpoints prouve une chaîne de dépenses, pas l’identité des propriétaires ni une allocation unique des satoshis dans une transaction à plusieurs entrées.

## 6. Exploitation ou résolution

### Challenge : Node To Nowhere — 03 : "Connecting the Dots"

Source : [anotherwu](evidence/blockchain-anotherwu.txt)

- **Catégorie** : Blockchain Intelligence / Forensics
- **Points** : 200 pts
- **Auteur** : W1z4rd

---

### 2. Analyse et Traçage Bidirectionnel

Source : [anotherwu](evidence/blockchain-anotherwu.txt)

### Étape 1 : Transaction Thorchain Initiale
- **TXID** : `<HEX_EXPURGE>`
  - Sortie 0 : `bc1q2ckjg8a997md83acvmc0pknzdwlgz9pgy0zc3a` (0.80965529 BTC)
  - Sortie 1 : `bc1qgc563ccy622345pk6pmuhnlmsru87v32gvwzzz` (114.59 BTC - Vault THORChain)

### Étape 2 : Traçage de la chaîne de blanchiment (Peeling Chain)

Chaque saut a été identifié par analyse des UTXO dépensées (*outspends*) :

1. **Hop 0 (Tx Thorchain)** : `<HEX_EXPURGE>`
   - Dépose vers `bc1q2ckjg8a997md83acvmc0pknzdwlgz9pgy0zc3a` (0.80965529 BTC)
2. **Hop 1** : `<HEX_EXPURGE>`
   - Dépense `bc1q2ck...` → envoie 0.803 BTC vers `bc1qtnu3zlyuxrfmug8k02germdkzwp0qccdwg0hlt`
3. **Hop 2** : `<HEX_EXPURGE>`
   - Dépense `bc1qtnu...` → envoie 0.524782 BTC vers `bc1q589qw53d5p8qnkk290mgqu4w6ljncjrn9qewee`
4. **Hop 3** : `<HEX_EXPURGE>`
   - Dépense `bc1q589...` → envoie 0.5168 BTC vers `bc1qvludfndj0av53gdp75xqwwfpn58ejaca7qh8qz`
5. **Hop 4** : `<HEX_EXPURGE>`
   - Dépense `bc1qvlu...` → envoie 0.511961 BTC vers `bc1q0pzywaljf28kkq0wggzuvs73xxlws3ufgqnj8x`
6. **Hop 5** : `<HEX_EXPURGE>`
   - Dépense `bc1q0pz...` → envoie 0.00098177 BTC vers `bc1qyxxf695clcv3c4w7yg8f6z2ydywpy9sp8p3qn2`
7. **Hop 6** : `<HEX_EXPURGE>`
   - Dépense `bc1qyxx...` → envoie 0.001 BTC vers `bc1q0vn7sfkhg456t3hrx2wr2xfszwkewzzpde0yl9`
8. **Hop 7 (Tx Finale vers le portefeuille cible)** : `<HEX_EXPURGE>`
   - Dépense `bc1q0vn...` → envoie 0.0037366 BTC vers **`bc1qxn7algyps6gq8jcg8u3ys72zwpkpksnjwuk4wn`** !

*(Ensuite, la transaction `<HEX_EXPURGE>` agrège les fonds de `bc1qxn7...` avec `bc1qerm...` comme décrit dans l'énoncé).*

---

### 3. Flag

Source : [anotherwu](evidence/blockchain-anotherwu.txt)

### Option 1 (Complète avec la Tx Thorchain initiale - 8 hachages) :
```text
<EXPURGE>
```

### Option 2 (Strictement les relais intermédiaires sans la Tx Thorchain - 7 hachages) :
```text
<EXPURGE>
```

### Connecting the Dots — analyse de transactions Bitcoin

Source : [compte rendu du hub](evidence/hub-49647.txt)

> **Correction après rejet par la plateforme.** La première réponse, construite à partir du chemin court de huit transactions, a été refusée. Les vérifications de liaisons étaient exactes, mais ne démontraient ni l’unicité du chemin ni le format attendu. Ne pas considérer la réception locale comme une résolution validée.

### Commandes et méthode reproductible

Source : [compte rendu du hub](evidence/hub-49647.txt)

Depuis le répertoire du challenge, saisir les valeurs publiques fournies dans l'énoncé sans les recopier dans les notes :

```bash
read -r SOURCE
read -r TARGET
```

Les requêtes de reconnaissance utilisées sont les suivantes, avec les arguments sensibles pour la réponse remplacés par ces variables :

```bash
curl -sS --max-time 25 "https://blockstream.info/api/address/$TARGET/txs"
curl -sS --max-time 25 "https://blockstream.info/api/tx/$SOURCE"
curl -sS --max-time 25 "https://blockstream.info/api/tx/$SOURCE/outspends"
```

Attention : ces commandes de reconnaissance affichent des hachages. Ne pas rediriger leurs résultats vers le compte rendu. Le script `trace.py` présent dans ce répertoire masque les identifiants dans ses sorties de diagnostic.

La commande de résolution exécutée, avec remplacement des deux arguments de l'énoncé, est :

```bash
python3 -u trace.py --source "$SOURCE" --target "$TARGET" --report
```

Pour reproduire uniquement l'analyse et la validation, sans nouvel envoi au hub :

```bash
python3 -u trace.py --source "$SOURCE" --target "$TARGET"
```

Le script charge les transactions qui créditent la cible et remonte leurs entrées. Chaque entrée désigne exactement une transaction antérieure et un indice de sortie. Il explore les entrées par valeur décroissante, mémorise les transactions déjà visitées et abandonne les branches antérieures au bloc de départ. Il impose également une profondeur maximale de 50 et un budget de 700 transactions. Ces limites sont des garde-fous pratiques ; elles ne constituent pas un algorithme exhaustif pour toute blockchain. Pour ce challenge, le chemin a été trouvé dans ces limites.

Quand le hachage de départ est rencontré, la remontée récursive construit la séquence chronologique jusqu'à la transaction qui crédite la cible. Le point de départ est inclus ; la dépense ultérieure d'agrégation est exclue.

### Observations validées

Source : [compte rendu du hub](evidence/hub-49647.txt)

Les diagnostics suivants ne contiennent aucun fragment de la réponse :

| Position chronologique | Hauteur de bloc | Entrées | Sorties |
| --- | ---: | ---: | ---: |
| Départ | 884973 | 1 | 3 |
| Relais 1 | 884973 | 1 | 2 |
| Relais 2 | 890514 | 1 | 2 |
| Relais 3 | 890515 | 1 | 2 |
| Relais 4 | 890773 | 1 | 2 |
| Relais 5 | 890852 | 1 | 2 |
| Relais 6 | 891305 | 2 | 2 |
| Arrivée à la cible | 891572 | 3 | 2 |

```text
Path found: 8 transactions including source; checking independent explorer.
All edges independently verified.
Flag reported to CTFHUB.
```

La transaction d'arrivée possède trois entrées de 100 000, 100 000 et 316 394 satoshis, deux sorties de 373 660 et 142 331 satoshis, et 403 satoshis de frais. Le chemin trouvé passe par l'entrée de 100 000 satoshis issue du bloc 891305.

### Validation indépendante

Source : [compte rendu du hub](evidence/hub-49647.txt)

Pour chaque transaction du chemin découvert avec Blockstream, le script demande la même transaction à l'API de mempool.space. Il confirme son identifiant et, pour chaque liaison, vérifie :

1. qu'une entrée de la transaction suivante référence la précédente ;
2. que l'indice de sortie référencé existe ;
3. que le montant et le script de cette sortie correspondent aux données de l'entrée ;
4. que la dernière transaction paie effectivement l'adresse cible.

Les huit transactions et les sept liaisons ont été vérifiées. Cette vérification démontre une chaîne de dépenses d'UTXO. Lorsqu'une transaction possède plusieurs entrées, elle ne démontre pas une affectation individuelle de chaque satoshi à chaque sortie.

La réponse soumise a été construite en mémoire puis transmise au hub local via son pont, sans être écrite dans ce compte rendu ni affichée. Le hub a confirmé la réception. Le succès auprès du système de notation reste distinct de cette réception locale.

## 7. Scripts et automatisation

Les copies sont expurgées et peuvent nécessiter la remise en place de paramètres ou d’artefacts. **Analyse syntaxique uniquement, sans exécution des solveurs ni de leurs opérations réseau.** Les imports listés ne constituent pas un environnement de dépendances testé. Les chemins relatifs historiques peuvent nécessiter une adaptation.

| Script | Source | Imports / dépendances | Contrôle | Nature |
|---|---|---|---|---|
| [blockchain--solveur.py](scripts/blockchain--solveur.py) | `blockchain/solveur.py` | hashlib, json, os, re, sys, time, urllib | syntaxe Python valide | réseau ou interaction de service |
| [blockchain--trace_both_ways_fixed.py](scripts/blockchain--trace_both_ways_fixed.py) | `blockchain/trace_both_ways_fixed.py` | argparse, collections, json, requests, sys, time | syntaxe Python valide | réseau ou interaction de service |
| [blockchain--trace_wassabi.py](scripts/blockchain--trace_wassabi.py) | `blockchain/trace_wassabi.py` | requests, time | syntaxe Python valide | réseau ou interaction de service |
| [blockchain--verifiy.py](scripts/blockchain--verifiy.py) | `blockchain/verifiy.py` | hashlib | syntaxe Python valide | traitement local apparent |

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Identifier le chemin des hachages entre la transaction de départ et le portefeuille cible. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |

## 9. Difficultés rencontrées

### Pistes non retenues et limites

Source : [compte rendu du hub](evidence/hub-49647.txt)

- La recherche web du hachage initial a seulement retrouvé une page du bloc Bitcoin correspondant ; elle n'a pas fourni le chemin.
- L'examen des dépenses des deux premières sorties du départ a révélé plusieurs branches possibles. Leur montant seul ne permet pas de choisir celle qui rejoint la cible.
- La plus grosse entrée de la transaction d'arrivée, de 316 394 satoshis, n'a pas conduit au départ dans la remontée effectuée. Privilégier uniquement le montant le plus élevé aurait donc écarté le bon chemin.
- La liste publique des 30 challenges du hub et la recherche du nom dans la base locale ne montraient pas ce challenge. L'appel réel au pont local a toutefois accepté le signalement sous le nom exact fourni par l'utilisateur. Aucune acceptation par le jury de la compétition n'est déduite de ce succès local.
- L'API d'historique est paginée en général. L'adresse cible ne présentait ici que les deux transactions pertinentes ; le script n'implémente pas une pagination générale pour les adresses très actives.

### Réexamen après le rejet

Source : [compte rendu du hub](evidence/hub-49647.txt)

Le script `check_paths.py` lit le premier résultat dans le hub, sans l’écrire dans un fichier, et explore en largeur les ancêtres de la transaction d’arrivée sur huit niveaux. Il récupère 43 transactions et reconstruit les chemins dans ce sous-graphe. Cette exploration couvre les chemins au moins aussi courts que le premier résultat, mais ne prétend pas épuiser tous les chemins plus longs. Le sous-graphe révèle aussi un deuxième chemin de onze transactions, car plusieurs transactions sont accessibles à différentes profondeurs.

Commande exécutée pour cette vérification :

```bash
python3 -u check_paths.py
```

Les deux chemins partagent leurs sept premières transactions. Au bloc 891305, une sortie de 100 000 satoshis rejoint directement la transaction d’arrivée. Une autre sortie de 63 989 satoshis poursuit sa route par trois transactions supplémentaires, aux blocs 891311, 891315 et 891318. Les liaisons de cette branche portent successivement sur 63 989, 60 953 et 58 793 satoshis ; elle fournit finalement une autre entrée de 100 000 satoshis à la transaction d’arrivée au bloc 891572.

Le chemin court est donc réel, mais il ne représente pas cette seconde branche. Le chemin long est un nouveau candidat, pas une réponse acceptée par le jury. Son format retire aussi les espaces après les virgules ; sans retour de la plateforme, il n’est pas possible de déterminer séparément l’effet du chemin choisi et celui des espaces.

La première recherche non bornée a été interrompue lorsque les branches collatérales se sont fortement multipliées ; la vérification a ensuite été bornée à huit niveaux. Aucun résultat exhaustif n’est revendiqué pour les chemins plus longs.

Le mode suivant vérifie indépendamment le candidat long auprès de mempool.space puis l’enregistre au hub avec une source signalant son statut de candidat. Il affiche la valeur : ne pas copier sa sortie dans les notes ou ce document.

```bash
python3 -u check_paths.py --report-candidate
```

La vérification indépendante des onze transactions a réussi. Le hub a enregistré le nouveau candidat. Son acceptation par la plateforme de compétition demeure inconnue.

## 10. Analyse technique approfondie

Une entrée Bitcoin désigne un outpoint précis. Une suite d’outpoints prouve une chaîne de dépenses, pas l’identité des propriétaires ni une allocation unique des satoshis dans une transaction à plusieurs entrées. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Aucune recommandation spécifique supplémentaire n’est établie au-delà des limites du mécanisme décrit. Pour les exercices purement documentaires, la priorité est la conservation des originaux, la provenance des pièces et la séparation des hypothèses et des constats.

## 12. Conclusion

Reconstituer les chemins de transactions entre le départ THORChain et une adresse cible. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Signalement local uniquement (reported).

### Enseignements et nettoyage

Source : [compte rendu du hub](evidence/hub-49647.txt)

Partir de l'adresse d'arrivée et remonter les références exactes d'UTXO réduit fortement l'espace de recherche. Un indice d'agrégation et un montant précis permettent de vérifier que l'on suit la bonne adresse. Une seconde source évite de dépendre d'un seul explorateur, et les vérifications de scripts et de montants sont plus solides qu'une simple proximité temporelle.

Le script est terminé. Aucun service, écouteur ou processus de fond n'a été lancé, et aucun secret d'accès n'a été enregistré dans ce répertoire. Les seuls livrables sont le script reproductible et ce compte rendu expurgé.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [anotherwu](evidence/blockchain-anotherwu.txt) — origine : `blockchain/anotherwu`.

- [Compte rendu CTFHUB](evidence/hub-49647.txt) — origine : `hub:49647`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


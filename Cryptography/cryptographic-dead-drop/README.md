# Cryptographic Dead Drop

[Accueil](../../README.md) · [Cryptography](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Cryptographic Dead Drop |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Cryptography |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | AES-GCM, CBOR, X25519, HKDF, PCAP |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Récupérer les communications de l’agent avant son arrestation.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Le script exige /tmp/msgs.pkl, absent du projet ; l’étape PCAP → objets Python n’est pas conservée. Son commentaire affirme sept trames cohérentes avec un intervalle de 120 s, mais ce résultat n’a pas de journal associé. Un pickle externe ne doit pas être chargé sans confiance. Le libellé ne doit pas être fusionné avec le challenge OSINT Dead Drop du hub sur la seule ressemblance des noms.

## 2. Énoncé du challenge

- Recover the content of Agent AVALD’s communications to determine what he reported to HQ before going silent.

## 3. Analyse initiale

Cinq captures PCAPNG et les descriptions du protocole, du schéma CBOR, des sessions et de messages connus sont présents. Le protocole sérialise `[session_id, key_id, nonce, ciphertext, tag]`, utilise AES-256-GCM sans AAD et annonce un nonce de 12 octets.

La dérivation de clé dépend du secret maître, de l’identifiant de session et du canal. La reprise réutilise l’identifiant et le secret maître : le protocole exige donc explicitement de conserver les compteurs.

Sources : [protocole fourni](evidence/misc-deaddrop-challenge-protocol-v3-md.txt) et [briefing](evidence/misc-deaddrop-challenge-briefing-md.txt).

## 4. Reconnaissance et investigation

La reconnaissance conservée se limite aux fichiers décrits dans l’inventaire. Aucun journal de commandes permettant d’établir une chronologie plus fine n’a été retrouvé.

## 5. Identification du mécanisme

Si clé et nonce GCM sont réutilisés, les chiffrés partagent le flux CTR : C1 XOR C2 = P1 XOR P2. Un texte connu donne seulement le préfixe couvert du flux. Un JSON plausible ne vérifie pas le tag GCM et ne constitue pas une authentification du clair.

## 6. Exploitation ou résolution

Le solveur existant commence à partir d’objets Python sérialisés, pas directement à partir des captures. Il sélectionne le canal prioritaire, associe les nonces de `session_01` et `session_03`, puis reconstitue le flux à partir d’un heartbeat connu.

Pour les compteurs suivants, il essaie des intervalles de 30 à 600 secondes par pas de 30. Son commentaire annonce que 120 secondes rend les sept messages cohérents. Le code exige un candidat d’intervalle unique, mais ne vérifie pas explicitement que le nombre de paires est sept ; ce nombre apparaît dans les commentaires et le texte affiché. La méthode suppose aussi que le heartbeat connu est au moins aussi long que chaque clair recherché, car `zip` tronque le XOR au plus court.

Dépendance bloquante : `/tmp/msgs.pkl` n’est pas disponible. Le script n’a pas été exécuté et aucun résultat de déchiffrement n’est revendiqué. Pour une reproduction complète, il manque le parseur ou l’export qui produit les dictionnaires de trames depuis TCP/CBOR.

## 7. Scripts et automatisation

Les copies sont expurgées et peuvent nécessiter la remise en place de paramètres ou d’artefacts. **Analyse syntaxique uniquement, sans exécution des solveurs ni de leurs opérations réseau.** Les imports listés ne constituent pas un environnement de dépendances testé. Les chemins relatifs historiques peuvent nécessiter une adaptation.

| Script | Source | Imports / dépendances | Contrôle | Nature |
|---|---|---|---|---|
| [misc-deaddrop-challenge--solve.py](scripts/misc-deaddrop-challenge--solve.py) | `misc/deaddrop/challenge/solve.py` | datetime, json, pickle, sys | syntaxe Python valide | traitement local apparent |

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Recover the content of Agent AVALD’s communications to determine what he reported to HQ before going silent. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

Aucune tentative infructueuse n’est consignée dans les sources rattachées. Cela ne prouve pas qu’il n’y en a pas eu. Les limites matérielles sont indiquées dans l’introduction.

## 10. Analyse technique approfondie

Si clé et nonce GCM sont réutilisés, les chiffrés partagent le flux CTR : C1 XOR C2 = P1 XOR P2. Un texte connu donne seulement le préfixe couvert du flux. Un JSON plausible ne vérifie pas le tag GCM et ne constitue pas une authentification du clair. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Persister les compteurs ou renouveler la clé à chaque reprise de session ; tester explicitement les reconnexions et la non-réutilisation des nonces.

## 12. Conclusion

Récupérer les communications de l’agent avant son arrestation. La documentation disponible permet une documentation partielle. Statut retenu : Partial. Aucune validation plateforme exportée.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [BRIEFING.md](evidence/misc-deaddrop-challenge-briefing-md.txt) — origine : `misc/deaddrop/challenge/BRIEFING.md`.

- [protocol_v3.md](evidence/misc-deaddrop-challenge-protocol-v3-md.txt) — origine : `misc/deaddrop/challenge/protocol_v3.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


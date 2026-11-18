# Ghost Ratchet

[Accueil](../../README.md) · [Forensics](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Ghost Ratchet |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Forensics |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | Java, SQLite, X25519, HKDF, AES-CBC, HMAC |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Retrouver l’identité cryptographique du correspondant depuis une sauvegarde NordLink.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Le solveur est rangé dans forensic/ghot/solveur.py mais vise ghost/nordlink_device. Son code ne rejoue pas toutes les rotations du ratchet : il teste des chaînes de réception depuis une ancre fixe. Le rapport PDF annonce un rejeu des messages 7 à 25 ; cette couverture dépasse celle démontrée par le script conservé. La distinction est maintenue.

## 2. Énoncé du challenge

- Identifier l’empreinte PGP de l’officier traitant.

## 3. Analyse initiale

Le contrôle documentaire a ouvert la base SQLite en lecture seule : elle contient **25 messages**, dont 11 entrants et 14 sortants. Les deux archives `GHOST-RATCHET.zip` sont identiques au niveau SHA-256.

| Pièce | Rôle | Limite de publication |
|---|---|---|
| `NordLink.jar` | Implémentation Java du protocole | Binaire conservé dans les originaux. |
| `nordlink.db` | En-têtes et messages chiffrés | Données brutes non copiées. |
| `session_init.bak` | Ancre de reprise du ratchet | Contient du matériel privé ; exclu du dépôt. |
| `ratchet_state.dat` | État courant marqué effacé | Référencé uniquement. |
| Préférences Android | Contexte de la session et du correspondant | Référencées uniquement. |

Le rapport est conservé sous forme d’[extrait textuel expurgé](evidence/rapport-pdf-extrait.txt).

**Contrôle local réellement effectué pendant cette édition :** [résultats structurés](evidence/controle-documentaire.json). Les mesures ne comportent aucune réponse ni secret.

## 4. Reconnaissance et investigation

Le rapport situe la clé privée de la sauvegarde en comparant sa clé publique X25519 aux en-têtes des messages. Il décrit ensuite une reprise au changement de clé DH distante du message reçu numéro 7. Cette comparaison est une méthode d’alignement : commencer au mauvais point conduirait à un MAC incorrect même si les primitives étaient correctement implémentées.

Aucune commande de décompilation n’est conservée ; il serait trompeur de présenter une invocation de décompilateur comme réellement exécutée. Les fonctions du script existant corroborent néanmoins les constantes et la structure des dérivations décrites dans le rapport.

## 5. Identification du mécanisme

La sauvegarde conserve la clé racine et une clé privée DH. L’état effacé ne suffit donc pas à empêcher une reprise depuis une rotation distante compatible. Un HMAC valide sur AD || ciphertext est le contrôle déterminant avant le déchiffrement CBC.

## 6. Exploitation ou résolution

### Dérivation des clés

Le script définit une KDF racine HKDF-SHA256 sur le secret X25519, avec la clé racine comme sel et l’information `NORDLINK-root-kdf`. Les 64 octets sont séparés entre nouvelle racine et clé de chaîne.

La clé de chaîne produit deux HMAC-SHA256 : l’octet `0x01` pour la chaîne suivante, `0x02` pour le secret du message. HKDF avec `NORDLINK-msg-keys` étend ce dernier en 80 octets : 32 pour AES, 32 pour le MAC et 16 pour l’IV.

### Authentification avant déchiffrement

Les données associées concatènent trois entiers 32 bits big-endian — type, numéro, longueur de chaîne précédente — et la clé publique DH. Le script compare HMAC-SHA256 sur `AD || ciphertext` avant de déchiffrer avec AES-CBC, puis vérifie strictement PKCS#7. Cette comparaison sépare un déchiffrement authentifié d’un texte simplement plausible.

### Résultat historique et portée du script

Le rapport indique qu’un message reçu donne l’empreinte PGP attendue et qu’un message sortant la confirme. Le solveur conservé ne traite que la direction `recv` et ne reproduit pas ce rejeu complet. Son résultat ne doit donc pas être annoncé comme une vérification des 19 messages cités dans le rapport.

Utilisation déclarée par l’en-tête du script, **non exécutée pendant cette mission** :

```bash
python3 solveur.py /chemin/vers/nordlink_device
```

Le script affiche les textes déchiffrés : ils peuvent contenir la réponse. Le dépôt conserve le code expurgé, mais pas ces sorties.

## 7. Scripts et automatisation

Les copies sont expurgées et peuvent nécessiter la remise en place de paramètres ou d’artefacts. **Analyse syntaxique uniquement, sans exécution des solveurs ni de leurs opérations réseau.** Les imports listés ne constituent pas un environnement de dépendances testé. Les chemins relatifs historiques peuvent nécessiter une adaptation.

| Script | Source | Imports / dépendances | Contrôle | Nature |
|---|---|---|---|---|
| [forensic-ghot--solveur.py](scripts/forensic-ghot--solveur.py) | `forensic/ghot/solveur.py` | cryptography, pathlib, sys | syntaxe Python valide | traitement local apparent |

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Identifier l’empreinte PGP de l’officier traitant. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

Aucune tentative infructueuse n’est consignée dans les sources rattachées. Cela ne prouve pas qu’il n’y en a pas eu. Les limites matérielles sont indiquées dans l’introduction.

## 10. Analyse technique approfondie

La sauvegarde conserve la clé racine et une clé privée DH. L’état effacé ne suffit donc pas à empêcher une reprise depuis une rotation distante compatible. Un HMAC valide sur AD || ciphertext est le contrôle déterminant avant le déchiffrement CBC. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Éviter les sauvegardes persistantes d’anciens secrets de ratchet ; protéger les sauvegardes et ne pas dériver les nouvelles clés privées de manière prévisible.

## 12. Conclusion

Retrouver l’identité cryptographique du correspondant depuis une sauvegarde NordLink. La documentation disponible permet une documentation partielle. Statut retenu : Partial. Aucune validation plateforme exportée.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [Ghost Ratchet — write-up forensique.pdf](evidence/rapport-pdf-extrait.txt) — origine : `forensic/ghost/Ghost Ratchet — write-up forensique.pdf`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


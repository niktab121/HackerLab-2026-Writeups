# Memento

[Accueil](../../README.md) · [Forensics](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Memento |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Forensics |
| Difficulté | Non documentée |
| Points | 70 |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | OpenSSL, AES-CBC, EXIF, Python |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Relier neuf scellés et tenter d’ouvrir le conteneur chiffré P-7.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Le hub présente un Memento résolu au niveau du catalogue, mais sans valeur ni compte rendu associé. Les travaux locaux montrent un générateur de candidats et un fichier out.bin ; cela ne démontre pas un déchiffrement réussi. Le script teste AES-128/192/256 avec EVP_BytesToKey MD5/SHA-256 et PBKDF2. Padding valide et texte imprimable ne suffisent pas à prouver le bon mot de passe.

## 2. Énoncé du challenge

- Énoncé original de la carte absent ; tableau de neuf pièces et conteneur disponibles.

## 3. Analyse initiale

Les données JavaScript décrivent neuf pièces : carte d’embarquement, téléphone, note manuscrite, ordre de virement, réservation d’hôtel, reçu de change, clé USB chiffrée, carte topographique et carte de visite. Les images correspondantes sont présentes dans les originaux.

Le contrôle binaire du scellé P-7 confirme 64 octets, dont l’en-tête `Salted__`, huit octets de sel et 48 octets chiffrés. `work/out.bin` fait 32 octets : sa présence ne permet pas d’identifier le traitement qui l’a produit.

Les fichiers de la page référencent `assets/exhibit-...`, tandis que les téléchargements locaux portent des noms `assets_exhibit-...`. Une reproduction de l’interface nécessite de restaurer cette correspondance ; cela n’a pas été fait sur les originaux.

**Contrôle local réellement effectué pendant cette édition :** [résultats structurés](evidence/controle-documentaire.json). Les mesures ne comportent aucune réponse ni secret.

## 4. Reconnaissance et investigation

La reconnaissance conservée se limite aux fichiers décrits dans l’inventaire. Aucun journal de commandes permettant d’établir une chronologie plus fine n’a été retrouvé.

## 5. Identification du mécanisme

L’en-tête Salted__ identifie une enveloppe OpenSSL salée ; il ne décrit pas à lui seul l’algorithme, la fonction de dérivation ni le nombre d’itérations.

## 6. Exploitation ou résolution

La tentative conservée génère des candidats à partir des indices du dossier et de combinaisons de petits jetons. Pour chaque candidat, elle essaie trois tailles de clé AES-CBC et trois dérivations : EVP_BytesToKey avec MD5, EVP_BytesToKey avec SHA-256 et PBKDF2-HMAC-SHA256 à 10 000 itérations.

Le filtre retient un padding PKCS#7 valide et un corps ASCII imprimable, puis arrête la recherche au premier résultat. Sans MAC ni structure métier vérifiée, ce test peut produire un faux positif. Aucun journal `HIT` ou `FOUND` n’est conservé ; le script ne constitue donc pas une solution démontrée.

L’absence des options de chiffrement originales reste une limite : la signature OpenSSL ne les encode pas. La copie du script est disponible dans la section automatisation, sans avoir été exécutée.

## 7. Scripts et automatisation

Les copies sont expurgées et peuvent nécessiter la remise en place de paramètres ou d’artefacts. **Analyse syntaxique uniquement, sans exécution des solveurs ni de leurs opérations réseau.** Les imports listés ne constituent pas un environnement de dépendances testé. Les chemins relatifs historiques peuvent nécessiter une adaptation.

| Script | Source | Imports / dépendances | Contrôle | Nature |
|---|---|---|---|---|
| [forensic-memento-work--brute.py](scripts/forensic-memento-work--brute.py) | `forensic/memento/work/brute.py` | cryptography, hashlib | syntaxe Python valide | traitement local apparent |
| [forensic-memento-work--try.sh](scripts/forensic-memento-work--try.sh) | `forensic/memento/work/try.sh` | voir imports/commandes | non applicable | traitement local apparent |

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Énoncé original de la carte absent ; tableau de neuf pièces et conteneur disponibles. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

Aucune tentative infructueuse n’est consignée dans les sources rattachées. Cela ne prouve pas qu’il n’y en a pas eu. Les limites matérielles sont indiquées dans l’introduction.

## 10. Analyse technique approfondie

L’en-tête Salted__ identifie une enveloppe OpenSSL salée ; il ne décrit pas à lui seul l’algorithme, la fonction de dérivation ni le nombre d’itérations. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Aucune recommandation spécifique supplémentaire n’est établie au-delà des limites du mécanisme décrit. Pour les exercices purement documentaires, la priorité est la conservation des originaux, la provenance des pièces et la séparation des hypothèses et des constats.

## 12. Conclusion

Relier neuf scellés et tenter d’ouvrir le conteneur chiffré P-7. La documentation disponible permet une documentation partielle. Statut retenu : Partial. Aucune validation plateforme exportée.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


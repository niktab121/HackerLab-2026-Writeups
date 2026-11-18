# Broken Handshake

[Accueil](../../README.md) · [Network](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Broken Handshake |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Network |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Unsolved** |
| Technologies | TLS, X.509, SAN, CN, HMAC, CT |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Identifier le certificat d’interception et son origine opérationnelle.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Les pièces et le protocole de vérification existent, mais aucune note de résolution ni sortie de calcul n’est conservée. La procédure donnée par les organisateurs n’est pas présentée comme une manipulation effectuée.

## 2. Énoncé du challenge

- Identify the certificate used to intercept Agent AVALD’s TLS connection.

## 3. Analyse initiale

Le paquet comprend la capture TLS, des événements JSONL, 510 entrées CT annoncées dans le briefing, trois certificats d’autorité et un inventaire de certificats. Le contrôle documentaire confirme que la capture est lisible et contient 191 paquets.

La politique locale décrit la validation de la chaîne, des périodes, des usages et du nom de service. Le protocole d’attribution définit une extension privée d’OID `1.3.6.1.4.1.99999.1`. Aucune sortie d’extraction de cette extension n’est conservée.

## 4. Reconnaissance et investigation

La reconnaissance conservée se limite aux fichiers décrits dans l’inventaire. Aucun journal de commandes permettant d’établir une chronologie plus fine n’a été retrouvé.

## 5. Identification du mécanisme

Le scénario compare CN et SAN puis prévoit une vérification HMAC du numéro de série. La clé publiée est une convention d’identification du challenge, pas une preuve d’attribution utilisable dans un incident réel.

## 6. Exploitation ou résolution

Le document fourni prescrit d’extraire les certificats du handshake, sélectionner ceux qui portent l’OID privé, recalculer HMAC-SHA256 sur le numéro de série en hexadécimal minuscule sans préfixe ni remplissage, puis comparer le jeton. Les champs SAN du certificat ainsi identifié déterminent l’attribution selon les règles du jeu.

Ce protocole est une instruction des organisateurs, non une trace de résolution. Les conditions de rejet doivent être testées séparément : validité de chaîne, identité SAN/CN et égalité du jeton n’établissent pas la même propriété. Sans rapport d’exécution, le certificat retenu et la réponse restent inconnus.

Sources : [protocole d’attribution](evidence/misc-deaddrop-broken-challenge-verification-protocol-md.txt) et [politique locale](evidence/misc-deaddrop-broken-challenge-trust-policy-md.txt).

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Identify the certificate used to intercept Agent AVALD’s TLS connection. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

Aucune tentative infructueuse n’est consignée dans les sources rattachées. Cela ne prouve pas qu’il n’y en a pas eu. Les limites matérielles sont indiquées dans l’introduction.

## 10. Analyse technique approfondie

Le scénario compare CN et SAN puis prévoit une vérification HMAC du numéro de série. La clé publiée est une convention d’identification du challenge, pas une preuve d’attribution utilisable dans un incident réel. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Valider la chaîne et l’identité du service selon la politique attendue ; ne pas utiliser CN lorsqu’un SAN pertinent est présent ; contrôler les usages, dates et autorités autorisées.

## 12. Conclusion

Identifier le certificat d’interception et son origine opérationnelle. La documentation disponible permet une documentation partielle. Statut retenu : Unsolved. Aucune validation plateforme exportée.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [BRIEFING.md](evidence/misc-deaddrop-broken-challenge-briefing-md.txt) — origine : `misc/deaddrop/broken/challenge/BRIEFING.md`.

- [trust_policy.md](evidence/misc-deaddrop-broken-challenge-trust-policy-md.txt) — origine : `misc/deaddrop/broken/challenge/trust_policy.md`.

- [verification_protocol.md](evidence/misc-deaddrop-broken-challenge-verification-protocol-md.txt) — origine : `misc/deaddrop/broken/challenge/verification_protocol.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


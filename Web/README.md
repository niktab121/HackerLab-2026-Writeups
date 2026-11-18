# Web — accès, contrôle d’accès et services internes

[Accueil](../README.md) · [Index général](../INDEX.md) · [Couverture](../reports/coverage.md)

Dix dossiers Web, regroupés en quatre ensembles :

- **Northline Transit** : THE GATE → INTERNAL DISPATCH → THE PASSENGER → WINDOW → PICKUP, une chaîne de codes partenaires et de SSRF. Les outils partagés sont documentés dans THE GATE.
- **Tervalis** : Opération Tervalis (relais ActiveMQ), Subject File et Restricted Zone (SMB, LDAP, NTLM) décrivent trois angles de la même infrastructure.
- **FEU** : recherche d’identité dans une base de personnes.
- **AIZEN** : traversée de fichiers, JWT HS256 et SSRF vers le service d’audit interne.

Tous les dossiers sont en statut **Partial** : aucune acceptation plateforme n’est certifiée par un export primaire. Les récits d’acceptation restent attribués à leurs notes.

## Par où commencer

1. **[THE GATE](the-gate/README.md)** pour la mécanique commune de la série Northline Transit, puis les quatre suivants dans l’ordre.
2. **[Opération Tervalis](operation-tervalis/README.md)** pour le dossier le plus détaillé du dépôt (relais, ActiveMQ, OpenWire).
3. **[AIZEN](aizen/README.md)** pour un enchaînement web complet : double encodage, lecture de `.env`, forge de JWT.
4. **[FEU](feu/README.md)** pour un exercice court de corrélation d’identité.

## Dossiers

| Challenge | Objectif | Techniques | Documentation | Statut |
|---|---|---|---|---|
| [FEU](feu/README.md) | Retrouver l’identité associée à un alias et à un numéro. | HTTP, MD5, IDOR | Reconstruction détaillée | Partial |
| [THE GATE](the-gate/README.md) | Atteindre le service interne de coordination Northline Transit. | HTTP, codes partenaires, SSRF, JSON | Reconstruction détaillée | Partial |
| [INTERNAL DISPATCH](internal-dispatch/README.md) | Obtenir la session partenaire correspondant au reçu. | HTTP, codes partenaires, SSRF, JSON | Reconstruction détaillée | Partial |
| [THE PASSENGER](the-passenger/README.md) | Identifier la personne rattachée à l’opération de transport. | HTTP, codes partenaires, SSRF, JSON | Reconstruction détaillée | Partial |
| [WINDOW](window/README.md) | Déterminer la fenêtre active de prise en charge. | HTTP, codes partenaires, SSRF, JSON | Reconstruction détaillée | Partial |
| [PICKUP](pickup/README.md) | Déterminer le point de prise en charge associé à l’affectation active. | HTTP, codes partenaires, SSRF, JSON | Reconstruction détaillée | Partial |
| [Opération Tervalis](operation-tervalis/README.md) | Accéder au relais interne pour retrouver la valeur d’instance attendue. | ActiveMQ, OpenWire, Spring, HTTP | Reconstruction détaillée | Partial |
| [Subject File](subject-file/README.md) | Retrouver le dossier du sujet dans un partage accessible au compte de service. | SMB, LDAP, ActiveMQ | Reconstruction détaillée | Partial |
| [Restricted Zone](restricted-zone/README.md) | Lire le partage réservé à l’aide du compte de sauvegarde. | SMB, LDAP, NTLM, pass-the-hash | Reconstruction détaillée | Partial |
| [AIZEN](aizen/README.md) | Atteindre le service d’audit interne depuis la console Vantage Hosting. | Flask, JWT HS256, WeasyPrint, SSRF | Reconstruction détaillée | Partial |

## Repères de lecture

- Les paramètres d’accès, cookies, jetons et réponses d’instance sont expurgés : les commandes sont historiques, pas directement rejouables.
- Les contradictions entre Subject File et Restricted Zone sur l’authentification NTLM sont conservées et expliquées dans chaque fiche.
- Voir la [couverture](../reports/coverage.md) pour les questions non résolues et les pièces manquantes.

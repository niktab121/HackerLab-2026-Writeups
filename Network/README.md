# Network — TLS et interception

[Accueil](../README.md) · [Index général](../INDEX.md) · [Couverture](../reports/coverage.md)

Un seul dossier, **Unsolved** :

- **Broken Handshake** : identifier un certificat d’interception TLS et son origine opérationnelle (SAN, CN, HMAC, Certificate Transparency).

Les pièces et le protocole de vérification existent, mais aucune note de résolution ni sortie de calcul n’est conservée. La fiche décrit donc la procédure sans prétendre qu’elle a été exécutée.

## Dossier

| Challenge | Objectif | Techniques | Documentation | Statut |
|---|---|---|---|---|
| [Broken Handshake](broken-handshake/README.md) | Identifier le certificat d’interception et son origine opérationnelle. | TLS, X.509, SAN, CN, HMAC, CT | Documentation partielle | Unsolved |

## Repères de lecture

- La procédure des organisateurs est reproduite comme énoncé, pas comme manipulation effectuée.
- Le dossier complète utilement [Il Mandante](../Forensics/il-mandante/README.md) et [Last Known Position](../Forensics/last-known-position/README.md) pour les questions X.509.
- Voir la [couverture](../reports/coverage.md) pour les preuves absentes.

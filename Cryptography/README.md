# Cryptography — protocoles et paquets chiffrés

[Accueil](../README.md) · [Index général](../INDEX.md) · [Couverture](../reports/coverage.md)

Un seul dossier, **Partial** :

- **Cryptographic Dead Drop** : récupérer les communications d’un agent avant son arrestation, à partir d’un paquet AES-GCM/CBOR/X25519/HKDF.

La chaîne est décrite, mais l’étape PCAP → objets Python n’est pas conservée : le script exige un `msgs.pkl` absent du projet. Le libellé ne doit pas être confondu avec le challenge OSINT « Dead Drop » du hub, malgré la ressemblance des noms.

## Dossier

| Challenge | Objectif | Techniques | Documentation | Statut |
|---|---|---|---|---|
| [Cryptographic Dead Drop](cryptographic-dead-drop/README.md) | Récupérer les communications d’un agent avant son arrestation. | AES-GCM, CBOR, X25519, HKDF, PCAP | Documentation partielle | Partial |

## Repères de lecture

- Les clés, nonces et messages en clair sont expurgés ou absents ; la fiche décrit le format et la méthode, pas un paquet rejouable.
- Ne pas charger un pickle d’origine inconnue : la remarque figure aussi dans la fiche.
- Voir la [couverture](../reports/coverage.md) pour les pièces manquantes.

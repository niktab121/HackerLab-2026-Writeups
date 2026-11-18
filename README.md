# HackerLab Bénin 2026 — Write-ups

Collection documentaire des investigations conservées dans le projet HackerLab 2026. Les travaux portent notamment sur les scénarios Tervalis, Northline Transit, Janus et des dossiers d’investigation numérique. La compétition est présentée comme terminée par le propriétaire du projet ; ce dépôt n’est pas une publication officielle des organisateurs.

**29 dossiers documentés**, issus de **377 fichiers originaux** : **21 reconstructions détaillées** et **8 dossiers partiels ou sans éléments suffisants**. Les vingt-huit questions d’Enquete sont reproduites séparément. Les autres questions, objectifs reconstitués et énoncés manquants sont détaillés dans la [couverture](reports/coverage.md).

La résolution technique, le signalement au hub local et l’acceptation par la compétition sont distingués. Aucune acceptation plateforme n’est certifiée par un export primaire dans les sources disponibles : les mentions d’acceptation dans les notes restent attribuées à leurs auteurs. Le statut Partial est donc volontairement prudent, même lorsqu’une chaîne technique est détaillée.

## Par où commencer

Trois entrées selon le temps disponible :

1. **Cinq minutes** — le tableau des challenges ci-dessous, puis la fiche du dossier qui vous intéresse.
2. **Une heure** — [Kiss of Death](Forensics/kiss-of-death/README.md) (enquête complète), [AIZEN](Web/aizen/README.md) (chaîne web) et [Connecting the Dots](Blockchain/connecting-the-dots/README.md) (rectificatif d’un signalement).
3. **Lecture méthodique** — [THE GATE](Web/the-gate/README.md) puis les quatre volets Northline Transit, et [The hunt](Forensics/the-hunt/README.md) pour la gestion des récits contradictoires.

Les dossiers sont rangés par catégorie ; chaque page de catégorie indique son propre ordre de lecture.

## Carte du dépôt

| Catégorie | Dossiers | Entrée |
|---|---:|---|
| Web | 10 | [Web/README.md](Web/README.md) — accès, contrôle d’accès, services internes |
| Forensics | 11 | [Forensics/README.md](Forensics/README.md) — artefacts, images, chronologies |
| Blockchain | 2 | [Blockchain/README.md](Blockchain/README.md) — traçage de transactions |
| Cryptography | 1 | [Cryptography/README.md](Cryptography/README.md) — paquets chiffrés |
| Network | 1 | [Network/README.md](Network/README.md) — TLS et interception |
| OSINT | 1 | [OSINT/README.md](OSINT/README.md) — parcours et financement |
| Misc | 3 | [Misc/README.md](Misc/README.md) — systèmes simulés, dossiers incomplets |

## Navigation

- [Index par catégorie](INDEX.md)
- [Sommaire et parcours de lecture](SUMMARY.md)
- [Inventaire exhaustif et provenance](reports/inventory.md)
- [Couverture des questions et limites](reports/coverage.md)
- [Audit avant publication](reports/publication-audit.md)

## Challenges

| Challenge | Catégorie | Difficulté | Points | Statut | Documentation |
|---|---|---|---|---|---|
| [FEU](Web/feu/README.md) | Web | Non documentée | 300 | Partial | Reconstruction détaillée |
| [Kiss of Death](Forensics/kiss-of-death/README.md) | Forensics | Non documentée | 100 | Partial | Reconstruction détaillée |
| [Dreamer](Forensics/dreamer/README.md) | Forensics | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [Il Mandante](Forensics/il-mandante/README.md) | Forensics | Non documentée | Q2 : 100 ; Q3 : 200 ; Q5 : 200 | Partial | Reconstruction détaillée |
| [Ghost Ratchet](Forensics/ghost-ratchet/README.md) | Forensics | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [Broken relay](Forensics/broken-relay/README.md) | Forensics | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [Broken channel](Forensics/broken-channel/README.md) | Forensics | Non documentée | Non documentés | Partial | Documentation partielle |
| [The hunt](Forensics/the-hunt/README.md) | Forensics | Non documentée | 100 | Partial | Reconstruction détaillée |
| [The Gauntlet](Forensics/the-gauntlet/README.md) | Forensics | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [Node To Nowhere — 01](Blockchain/node-to-nowhere-01/README.md) | Blockchain | Non documentée | 50 | Partial | Reconstruction détaillée |
| [Connecting the Dots](Blockchain/connecting-the-dots/README.md) | Blockchain | Non documentée | 200 | Partial | Reconstruction détaillée |
| [THE GATE](Web/the-gate/README.md) | Web | Non documentée | 70 | Partial | Reconstruction détaillée |
| [INTERNAL DISPATCH](Web/internal-dispatch/README.md) | Web | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [THE PASSENGER](Web/the-passenger/README.md) | Web | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [WINDOW](Web/window/README.md) | Web | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [PICKUP](Web/pickup/README.md) | Web | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [Opération Tervalis](Web/operation-tervalis/README.md) | Web | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [Subject File](Web/subject-file/README.md) | Web | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [Restricted Zone](Web/restricted-zone/README.md) | Web | Non documentée | 100 | Partial | Reconstruction détaillée |
| [Last Known Position](Forensics/last-known-position/README.md) | Forensics | Non documentée | Non documentés | Partial | Reconstruction détaillée |
| [Cryptographic Dead Drop](Cryptography/cryptographic-dead-drop/README.md) | Cryptography | Non documentée | Non documentés | Partial | Documentation partielle |
| [Broken Handshake](Network/broken-handshake/README.md) | Network | Non documentée | Non documentés | Unsolved | Documentation partielle |
| [Enquete](OSINT/enquete/README.md) | OSINT | Non documentée | 400 dans l’interface locale (pas un score plateforme) | Partial | Documentation partielle |
| [Memento](Forensics/memento/README.md) | Forensics | Non documentée | 70 | Partial | Documentation partielle |
| [Furgitif — dossier confidentiel](Forensics/furgitif-dossier-confidentiel/README.md) | Forensics | Non documentée | Non documentés | Unsolved | Documentation partielle |
| [AIZEN](Web/aizen/README.md) | Web | Hard, selon le compte rendu | 200 | Partial | Reconstruction détaillée |
| [Canary](Misc/canary/README.md) | Misc | Non documentée | 200 | Partial | Reconstruction détaillée |
| [Conspiracy](Misc/conspiracy/README.md) | Misc | Non documentée | Non documentés | Unsolved | Documentation partielle |
| [Human After All — dossier vide](Misc/human-after-all-dossier-vide/README.md) | Misc | Non documentée | Non documentés | Unsolved | Documentation partielle |

## Technologies et compétences

Analyse d’images AD1 et de couches Docker ; corrélation SQLite, journaux Windows et captures réseau ; lecture de code JavaScript et Python ; investigation X.509, RSA, AES-GCM et ratchets ; analyse de contrôle d’accès, SSRF et ActiveMQ ; suivi de dépenses Bitcoin et de conversions Ethereum ; recoupement documentaire et géographique.

Les outils effectivement présents ou cités comprennent Python, OpenSSL, tshark, SQLite, tar, John, Pillow, NumPy, Impacket, smbclient et les consoles Elastic. Leur présence dans une note ne signifie pas que leur exécution a été rejouée pour cette édition.

## Reproduction et limites

Les chemins d’origine figurent dans chaque inventaire de pièces. Les fichiers lourds, images, bases, captures, clés, cookies et réponses restent dans l’espace privé original. Le dépôt contient des copies textuelles expurgées, les scripts retenus et des contrôles documentaires sans réponse. Il ne constitue donc pas un paquet autonome des challenges.

Les scripts historiques ont subi un contrôle syntaxique ; ils n’ont pas été exécutés contre les services. Les secrets, chemins locaux ou valeurs d’instance expurgés doivent être réintroduits uniquement depuis les artefacts autorisés. Les résultats qui ne sont étayés que par une note sont signalés comme tels.

## Usage éthique et publication

Utiliser ces méthodes uniquement dans un environnement de laboratoire ou avec une autorisation explicite. Les domaines et adresses des exemples sont ceux des notes historiques ; leur présence ne constitue pas une autorisation de les contacter.

Aucun scan ni exploitation externe n’a été lancé pour cette collection. Les originaux sont conservés hors du dépôt publié. Voir [LICENSE](LICENSE) pour le périmètre de la licence et [l’audit](reports/publication-audit.md) pour les réserves documentaires.

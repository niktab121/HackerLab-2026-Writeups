# Forensics — artefacts, images et chronologies

[Accueil](../README.md) · [Index général](../INDEX.md) · [Couverture](../reports/coverage.md)

Onze dossiers d’investigation numérique, regroupés en quatre ensembles :

- **Série Relay / Northline** : Broken relay (poste du suspect), Broken channel (déchiffrement des canaux), Ghost Ratchet (sauvegarde NordLink) et The hunt (pivot vers l’identité). Ces quatre dossiers partagent des pièces et se contredisent parfois ; les écarts sont conservés et expliqués dans chaque fiche.
- **Perquisition et documents** : Kiss of Death (simulation, scellés, téléphone), Dreamer (document numérisé), Il Mandante (PKI, RSA, CMS), Memento (neuf scellés et conteneur P-7) et Furgitif (trois documents opérationnels, objectif non retrouvé).
- **DFIR** : The Gauntlet, compromission d’un serveur Windows reconstituée depuis Elastic, Sysmon et Packetbeat.
- **Transport** : Last Known Position, registre falsifié et destination réelle d’un transport.

Dix dossiers sont en statut **Partial**, Furgitif en **Unsolved**. Aucune acceptation plateforme n’est certifiée par un export primaire : les récits d’acceptation restent attribués à leurs notes.

## Par où commencer

1. **[Kiss of Death](kiss-of-death/README.md)** : le dossier le plus volumineux (61 fichiers sources, 6 questions), bon point d’entrée pour la méthode d’enquête.
2. **[The hunt](the-hunt/README.md)** : le cas le plus instructif sur les contradictions entre récits de résolution.
3. **[Il Mandante](il-mandante/README.md)** : pour l’analyse X.509/RSA et les corrections de mesure (taille de module, indexation, datation CMS).
4. **[The Gauntlet](the-gauntlet/README.md)** : pour une chronologie DFIR Windows et ses limites de preuve.
5. **[Memento](memento/README.md)** et **[Broken Handshake](../Network/broken-handshake/README.md)** : dossiers volontairement laissés incomplets, utiles pour comprendre ce qui manque.

## Dossiers

| Challenge | Objectif | Techniques | Documentation | Statut |
|---|---|---|---|---|
| [Kiss of Death](kiss-of-death/README.md) | Perquisitionner une simulation, exploiter les scellés et le téléphone. | JavaScript, API HTTP, schéma Android, SHA-1 | Reconstruction détaillée | Partial |
| [Dreamer](dreamer/README.md) | Extraire date, heure et numéro de série d’un document numérisé. | Pillow, NumPy, PDF, points jaunes | Reconstruction détaillée | Partial |
| [Il Mandante](il-mandante/README.md) | Attribuer une AC, ouvrir un blob RSA, dater un dossier signé. | X.509, CT, RSA, PGCD, OAEP, CMS | Reconstruction détaillée | Partial |
| [Ghost Ratchet](ghost-ratchet/README.md) | Retrouver l’identité cryptographique d’un correspondant NordLink. | Java, SQLite, X25519, HKDF, AES-CBC, HMAC | Reconstruction détaillée | Partial |
| [Broken relay](broken-relay/README.md) | Retrouver l’URL de stockage utilisée depuis le poste du suspect. | AD1, Firefox, SQLite | Reconstruction détaillée | Partial |
| [Broken channel](broken-channel/README.md) | Déchiffrer les messages des canaux Relay. | Docker, scrypt, AES-GCM, xorshift32 | Documentation partielle | Partial |
| [The hunt](the-hunt/README.md) | Exploiter les artefacts Relay et une capture pour identifier le suspect. | Docker, SQLite, scrypt, AES-GCM, XOR, PCAP | Reconstruction détaillée | Partial |
| [The Gauntlet](the-gauntlet/README.md) | Reconstituer la compromission d’un serveur Windows. | Windows, Sysmon, IIS, PowerShell, Elastic, Packetbeat | Reconstruction détaillée | Partial |
| [Last Known Position](last-known-position/README.md) | Retrouver la destination réelle d’un transport au registre falsifié. | SQLite, historiques shell, GPS, SIGINT, EXIF | Reconstruction détaillée | Partial |
| [Memento](memento/README.md) | Relier neuf scellés et tenter d’ouvrir le conteneur P-7. | OpenSSL, AES-CBC, EXIF, Python | Documentation partielle | Partial |
| [Furgitif — dossier confidentiel](furgitif-dossier-confidentiel/README.md) | Dossier de trois documents opérationnels ; objectif non retrouvé. | ZIP, PDF | Documentation partielle | Unsolved |

## Repères de lecture

- Les images, bases SQLite, PCAP et archives restent hors dépôt ; seules des copies textuelles expurgées et des manifestes sont publiées.
- Les scripts n’ont pas été rejoués contre les services ; les résultats qui ne reposent que sur une note sont signalés comme tels.
- Voir la [couverture](../reports/coverage.md) pour les questions manquantes et les preuves absentes, dossier par dossier.

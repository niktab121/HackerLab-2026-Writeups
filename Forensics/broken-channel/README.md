# Broken channel

[Accueil](../../README.md) · [Forensics](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Broken channel |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Forensics |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | Docker, scrypt, AES-GCM, xorshift32 |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Déchiffrer les messages des canaux Relay.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Dossier partagé avec The hunt pour les couches Docker et Broken relay pour l’image du poste. La note seule donne une chaîne de déchiffrement, sans preuve d’acceptation.

## 2. Énoncé du challenge

- Énoncé original absent ; objectif reconstitué depuis la note de résolution.

## 3. Analyse initiale

1 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

## 4. Reconnaissance et investigation

La reconnaissance conservée se limite aux fichiers décrits dans l’inventaire. Aucun journal de commandes permettant d’établir une chronologie plus fine n’a été retrouvé.

## 5. Identification du mécanisme

Le code du canal sert à dériver une clé scrypt ; AES-GCM protège le stockage et le chiffrement client doit ensuite être inversé séparément.

## 6. Exploitation ou résolution

### Broken channel — solve

Source : [broken_channel.md](evidence/forensic-broken-broken-channel-md.txt)

1. Télécharger l’archive Mega.
2. L’extraire avec `tar xzf`.
3. Repérer `manifest.json`, puis extraire les layers Docker.
4. Utiliser `channel.pdf` et son mot de passe `<EXPURGE>` pour obtenir les codes des canaux.
5. Reproduire `derive_key`, `unseal` et les AAD de `app.py`.
6. Décoder les messages avec l’alphabet Base64 personnalisé et le générateur xorshift de `cipher.exe`.

Message final : `#n0rv3th_c1ph3r_1s_br0k3n`.

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

Les outils partagés sont inventoriés dans [The hunt](../the-hunt/README.md). Les arguments spécifiques à cette question sont ceux des notes historiques.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Énoncé original absent ; objectif reconstitué depuis la note de résolution. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

Aucune tentative infructueuse n’est consignée dans les sources rattachées. Cela ne prouve pas qu’il n’y en a pas eu. Les limites matérielles sont indiquées dans l’introduction.

## 10. Analyse technique approfondie

Le code du canal sert à dériver une clé scrypt ; AES-GCM protège le stockage et le chiffrement client doit ensuite être inversé séparément. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Aucune recommandation spécifique supplémentaire n’est établie au-delà des limites du mécanisme décrit. Pour les exercices purement documentaires, la priorité est la conservation des originaux, la provenance des pièces et la séparation des hypothèses et des constats.

## 12. Conclusion

Déchiffrer les messages des canaux Relay. La documentation disponible permet une documentation partielle. Statut retenu : Partial. Aucune validation plateforme exportée.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [broken_channel.md](evidence/forensic-broken-broken-channel-md.txt) — origine : `forensic/broken/broken_channel.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


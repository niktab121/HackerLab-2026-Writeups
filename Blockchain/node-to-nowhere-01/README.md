# Node To Nowhere — 01

[Accueil](../../README.md) · [Blockchain](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Node To Nowhere — 01 |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Blockchain |
| Difficulté | Non documentée |
| Points | 50 |
| Auteur | W1z4rd |
| Statut | **Partial** |
| Technologies | Ethereum, ERC-20, DEX |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Identifier la transaction convertissant environ la moitié des ETH d’un portefeuille en ERC-20.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** La note hésite entre transfert intermédiaire et swap : ce sont deux transactions différentes. Le swap est cohérent avec l’objectif de conversion, mais aucun reçu on-chain brut ni retour d’acceptation n’est conservé. Les montants sont rapportés, non interrogés de nouveau.

## 2. Énoncé du challenge

- Confirmez cette information en identifiant le hachage de la transaction ayant entraîné cette conversion.

## 3. Analyse initiale

1 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

## 4. Reconnaissance et investigation

La note historique répartit les fonds en deux branches : environ 1 009,63 ETH et 1 076,45 ETH. La première est décrite comme une séquence de fractionnement, la seconde comme un transfert vers une adresse intermédiaire suivi d’un swap DEX. Ces montants proviennent de la note ; les réponses d’explorateurs et reçus Ethereum ne sont pas archivés.

Aucune commande exacte de consultation n’est conservée. Les mentions Blockscout et Etherscan indiquent les outils utilisés, sans permettre de reconstruire la requête exécutée.

## 5. Identification du mécanisme

La comparaison des sorties distingue fractionnement et échange de jetons. L’appel smartSwapByOrderId doit être rapproché des événements Transfer des jetons reçus pour établir la conversion.

## 6. Exploitation ou résolution

La méthode rapportée consiste à partir des sorties du portefeuille d’intérêt, suivre les deux branches puis rechercher un appel de conversion. La branche d’environ 51,6 % mène à un appel `smartSwapByOrderId`, décrit comme convertissant 1 076,4385 ETH et recevant 2 397 936 DAI.

Ces événements constituent le type de preuve recherché : un transfert ETH intermédiaire n’est pas encore une conversion ERC-20. Il faudrait le reçu de la transaction et les événements de transfert DAI pour confirmer localement la conclusion.

La source propose deux réponses alternatives, l’une correspondant au swap et l’autre au transfert préalable. Elles ne sont pas interchangeables. Aucun retour du jury ne permet de lever cette ambiguïté dans les éléments conservés.

Source : [note originale expurgée](evidence/blockchain-wu1-md.txt).

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Confirmez cette information en identifiant le hachage de la transaction ayant entraîné cette conversion. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

Aucune tentative infructueuse n’est consignée dans les sources rattachées. Cela ne prouve pas qu’il n’y en a pas eu. Les limites matérielles sont indiquées dans l’introduction.

## 10. Analyse technique approfondie

La comparaison des sorties distingue fractionnement et échange de jetons. L’appel smartSwapByOrderId doit être rapproché des événements Transfer des jetons reçus pour établir la conversion. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Aucune recommandation spécifique supplémentaire n’est établie au-delà des limites du mécanisme décrit. Pour les exercices purement documentaires, la priorité est la conservation des originaux, la provenance des pièces et la séparation des hypothèses et des constats.

## 12. Conclusion

Identifier la transaction convertissant environ la moitié des ETH d’un portefeuille en ERC-20. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Aucune validation plateforme exportée.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [wu1.md](evidence/blockchain-wu1-md.txt) — origine : `blockchain/wu1.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


# Blockchain — traçage de transactions

[Accueil](../README.md) · [Index général](../INDEX.md) · [Couverture](../reports/coverage.md)

Deux dossiers de suivi on-chain, tous deux en statut **Partial** :

- **Node To Nowhere — 01** : identifier la transaction qui convertit environ la moitié des ETH d’un portefeuille en jetons ERC-20. La note hésite entre transfert intermédiaire et swap ; la distinction est conservée.
- **Connecting the Dots** : reconstituer les chemins de transactions entre un départ THORChain et une adresse cible. Le rectificatif du hub prime sur le récit local : le chemin de huit transactions a été refusé, un chemin de onze reste candidat.

## Par où commencer

1. **[Node To Nowhere — 01](node-to-nowhere-01/README.md)** : périmètre court, une seule transaction à caractériser.
2. **[Connecting the Dots](connecting-the-dots/README.md)** : plus long, et le seul dossier du dépôt où un signalement local est explicitement contredit.

## Dossiers

| Challenge | Objectif | Techniques | Documentation | Statut |
|---|---|---|---|---|
| [Node To Nowhere — 01](node-to-nowhere-01/README.md) | Identifier la transaction de conversion ETH → ERC-20. | Ethereum, ERC-20, DEX | Reconstruction détaillée | Partial |
| [Connecting the Dots](connecting-the-dots/README.md) | Reconstituer les chemins de transactions vers une adresse cible. | Bitcoin, UTXO, Blockstream, mempool.space | Reconstruction détaillée | Partial |

## Repères de lecture

- Aucune requête blockchain n’a été effectuée pour cette édition : les montants et hachages sont rapportés depuis les notes.
- Les flags sont expurgés dans les deux fiches ; les valeurs candidates sont étiquetées comme telles.
- Voir la [couverture](../reports/coverage.md) pour le détail des preuves manquantes.

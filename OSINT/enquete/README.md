# Enquete

[Accueil](../../README.md) · [OSINT](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Enquete |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | OSINT |
| Difficulté | Non documentée |
| Points | 400 dans l’interface locale (pas un score plateforme) |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | JavaScript, chronologie, graphe, CDR, données financières |
| Validation | Signalement local uniquement (reported) |

## 1. Introduction

Reconstituer le parcours, les identités et le financement d’un fugitif à partir du dossier Harmattan.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Vingt-huit questions et vingt-huit candidats sont conservés. Le script check.py envoie ces candidats à /api/check ; aucun journal de ses réponses n’est présent. Quatre valeurs ont été signalées au hub, sans association fiable aux vingt-huit questions. Ne pas assimiler ces signalements à vingt-huit acceptations.

## 2. Énoncé du challenge

Les vingt-huit libellés suivants proviennent de la table de questions de `harmattan-data.js`. Les points affichés sont ceux de l’interface locale.

### Q1 — Fil 1,Véhicule fantôme

> Quel véhicule Lindberg a-t-il utilisé pour quitter Zanthara ?

Barème local : 10 points. Indice conservé : pièce P-03, contrat AutoPlus, rubrique Véhicule.

### Q2 — Fil 1,Véhicule fantôme

> Sous quelle identité le véhicule a-t-il été loué ?

Barème local : 10 points. Indice conservé : pièce P-03, rubrique Locataire.

### Q3 — Fil 1,Véhicule fantôme

> Quel est le numéro du passeport utilisé pour la location ?

Barème local : 15 points. Indice conservé : pièce P-03, pièce d'identité du locataire.

### Q4 — Fil 2,Traversée frontière

> À quelle heure Lindberg a-t-il franchi la frontière kaltyrienne ?

Barème local : 10 points. Indice conservé : pièce P-04, cherchez le Kangoo ZN-6798-U.

### Q5 — Fil 2,Traversée frontière

> Par quel poste-frontière ?

Barème local : 10 points. Indice conservé : pièce P-04, intitulé du registre.

### Q6 — Fil 3,Séjour Mirova

> Où Lindberg a-t-il logé à Mirova ?

Barème local : 10 points. Indice conservé : pièce P-05, lieu de travail du témoin.

### Q7 — Fil 4,Gelashvili

> Quel est le vrai nom du visiteur de l'Hôtel Baobab le 14 octobre ?

Barème local : 15 points. Indice conservé : « M. Taro » est un alias : croisez P-05 et P-07.

### Q8 — Fil 4,Gelashvili

> Quelle est la société de Gelashvili ?

Barème local : 10 points. Indice conservé : pièce P-07 ou P-10, fiche 2.

### Q9 — Fil 4,Gelashvili

> Quel véhicule Lindberg utilise-t-il après le Kangoo ?

Barème local : 10 points. Indice conservé : pièce P-06, journée du 15 octobre.

### Q10 — Fil 4,Gelashvili

> À quelle société ce véhicule appartient-il ?

Barème local : 15 points. Indice conservé : pièce P-06 (carte grise) et P-09, article 14.

### Q11 — Fil 5,Réseau financier

> Quelle société reçoit les fonds de Nordic Shield en premier ?

Barème local : 15 points. Indice conservé : module Argent, premier lien sortant de Nordic Shield.

### Q12 — Fil 5,Réseau financier

> Qui est le directeur de Danube River Logistics ?

Barème local : 15 points. Indice conservé : pièce P-10, chaîne de détention, ligne 2.

### Q13 — Fil 5,Réseau financier

> Quelle est la source originale des fonds de JANUS ?

Barème local : 15 points. Indice conservé : module Argent, le bloc sans flux entrant.

### Q14 — Fil 5,Réseau financier

> Combien de sociétés-écrans composent le réseau ?

Barème local : 10 points. Indice conservé : pièce P-10 ; le prestataire n'en fait pas partie.

### Q15 — Fil 5,Réseau financier

> Quel exchange crypto a été utilisé en Géorgie ?

Barème local : 15 points. Indice conservé : module Crypto, destination des adresses intermédiaires.

### Q16 — Fil 5,Réseau financier

> Sous quelle identité le compte crypto géorgien est-il enregistré ?

Barème local : 15 points. Indice conservé : module Crypto, ouvrez le bloc de l'exchange géorgien.

### Q17 — Fil 6,Identité ECHEVERRIA

> Par quel moyen de transport Lindberg a-t-il quitté Mirova ?

Barème local : 10 points. Indice conservé : pièce P-06, soirée du 16 octobre.

### Q18 — Fil 7,Istanbul–Géorgie

> Dans quel quartier d'Istanbul Lindberg a-t-il séjourné ?

Barème local : 15 points. Indice conservé : Écoutes, cellule IST-3341, activée trois fois.

### Q19 — Fil 7,Istanbul–Géorgie

> Par quel poste-frontière Lindberg est-il entré en Géorgie ?

Barème local : 10 points. Indice conservé : Chrono du 21/10, ou premier message du forum.

### Q20 — Fil 8,Piste numérique

> Quel est le compte Instagram de Lindberg/ECHEVERRIA ?

Barème local : 15 points. Indice conservé : Traces, onglet Instagram, en-tête du profil.

### Q21 — Fil 8,Piste numérique

> Géolocalisez la photo du 19 octobre. Quel quartier ?

Barème local : 20 points. Indice conservé : Instagram du 19/10, lisez les indices, recoupez avec les écoutes.

### Q22 — Fil 8,Piste numérique

> Depuis quel site la photo du 23 octobre a-t-elle été prise ?

Barème local : 20 points. Indice conservé : Instagram du 23/10 : grande roue et tour de télévision.

### Q23 — Fil 8,Piste numérique

> Quel café Lindberg fréquente-t-il à Tbilissi ?

Barème local : 15 points. Indice conservé : Instagram du 27/10, l'enseigne.

### Q24 — Fil 8,Piste numérique

> Dans quelle rue se situe le logement de Lindberg d'après Strava ?

Barème local : 20 points. Indice conservé : Traces, onglet Strava : point commun des quatre départs.

### Q25 — Fil 9,Numéro norvéthien

> À qui appartient le numéro norvéthien contacté par Lindberg ?

Barème local : 10 points. Indice conservé : pièce P-11, annexe des correspondants.

### Q26 — Fil 9,Numéro norvéthien

> Près de quelle ville se trouve Ingrid ?

Barème local : 15 points. Indice conservé : pièce P-11, cellule de rattachement du +47.

### Q27 — Fil 10,Plan de fuite

> Quel est l'itinéraire de fuite prévu ? (villes dans l'ordre)

Barème local : 20 points. Indice conservé : pièce P-16, les trois segments du billet.

### Q28 — Fil 10,Plan de fuite

> Quelle est l'adresse actuelle de Erik Lindberg ?

Barème local : 30 points. Indice conservé : Strava : départs entre les n° 17 et 21. Le café du n° 15 est « 4 doors down ».


## 3. Analyse initiale

Le dossier contient une page HTML de pièces, un fichier de données JavaScript, le code de l’interface et un script de vérification de candidats. La table de questions contient 28 entrées ; les indices indiquent les pièces P-03 à P-16, les modules Argent, Crypto, Écoutes, Chrono et Traces.

Le script `check.py` possède également 28 entrées, mais aucun fichier de sortie. Un contrôle statique révèle notamment une divergence entre le candidat de passeport et le numéro présent dans les données du dossier. Ce constat empêche de considérer le dictionnaire de candidats comme un corrigé validé.

L’application publie les routes `/api/check` et `/api/submit`. Aucune n’a été appelée pendant la mission.

## 4. Reconnaissance et investigation

L’investigation se répartit en dix fils : véhicule de départ, frontière, séjour, facilitateur, sociétés, changement d’identité, déplacement international, traces sociales, correspondant norvégien et plan de fuite.

Les références de chaque question imposent une chaîne de preuve : commencer par la pièce indiquée, relever le fait pertinent, puis recouper une source indépendante lorsqu’elle existe. Une déclaration de témoin, un registre et une trace réseau n’ont pas la même portée ; deux documents provenant de la même source ne constituent pas deux confirmations indépendantes.

## 5. Identification du mécanisme

Chaque question comporte dans le JavaScript une référence de pièce ou de module. La méthode consiste à recouper documents, chronologie, communications et traces sociales ; les candidats du script restent des propositions tant que les preuves ou retours du serveur ne les confirment pas.

## 6. Exploitation ou résolution

La reconstruction disponible est documentaire. Les questions 1 à 10 se rattachent surtout aux contrats, registres et auditions ; les questions 11 à 16 aux relations financières ; les questions 17 à 24 aux déplacements et traces sociales ; les questions 25 à 28 aux communications et à la localisation finale.

Le script conservé envoie un JSON `{"id": ..., "answer": ...}` à `/api/check`, puis imprime la réponse avec le candidat. Cette présence démontre une automatisation prévue ; sans journal, elle ne démontre ni que toutes les requêtes ont été exécutées ni qu’elles ont réussi. Les candidats sont retirés des copies publiques.

Pour reproduire l’analyse sans service actif, ouvrir les originaux HTML comme documents, suivre les références des questions et consigner séparément fait observé, pièce et interprétation. Cette procédure est une recommandation éditoriale, pas un journal d’exécution historique.

## 7. Scripts et automatisation

Les copies sont expurgées et peuvent nécessiter la remise en place de paramètres ou d’artefacts. **Analyse syntaxique uniquement, sans exécution des solveurs ni de leurs opérations réseau.** Les imports listés ne constituent pas un environnement de dépendances testé. Les chemins relatifs historiques peuvent nécessiter une adaptation.

| Script | Source | Imports / dépendances | Contrôle | Nature |
|---|---|---|---|---|
| [forensic-enquete--check.py](scripts/forensic-enquete--check.py) | `forensic/enquete/check.py` | json | syntaxe Python valide | réseau ou interaction de service |

## 8. Questions et flags

| Question | Méthode / repère de preuve original | Réponse | Validation |
|---|---|---|---|
| Q1 | pièce P-03, contrat AutoPlus, rubrique Véhicule. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q2 | pièce P-03, rubrique Locataire. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q3 | pièce P-03, pièce d'identité du locataire. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q4 | pièce P-04, cherchez le Kangoo ZN-6798-U. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q5 | pièce P-04, intitulé du registre. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q6 | pièce P-05, lieu de travail du témoin. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q7 | « M. Taro » est un alias : croisez P-05 et P-07. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q8 | pièce P-07 ou P-10, fiche 2. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q9 | pièce P-06, journée du 15 octobre. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q10 | pièce P-06 (carte grise) et P-09, article 14. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q11 | module Argent, premier lien sortant de Nordic Shield. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q12 | pièce P-10, chaîne de détention, ligne 2. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q13 | module Argent, le bloc sans flux entrant. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q14 | pièce P-10 ; le prestataire n'en fait pas partie. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q15 | module Crypto, destination des adresses intermédiaires. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q16 | module Crypto, ouvrez le bloc de l'exchange géorgien. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q17 | pièce P-06, soirée du 16 octobre. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q18 | Écoutes, cellule IST-3341, activée trois fois. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q19 | Chrono du 21/10, ou premier message du forum. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q20 | Traces, onglet Instagram, en-tête du profil. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q21 | Instagram du 19/10, lisez les indices, recoupez avec les écoutes. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q22 | Instagram du 23/10 : grande roue et tour de télévision. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q23 | Instagram du 27/10, l'enseigne. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q24 | Traces, onglet Strava : point commun des quatre départs. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q25 | pièce P-11, annexe des correspondants. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q26 | pièce P-11, cellule de rattachement du +47. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q27 | pièce P-16, les trois segments du billet. | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |
| Q28 | Strava : départs entre les n° 17 et 21. Le café du n° 15 est « 4 doors down ». | Candidat conservé hors dépôt | Non vérifiée : retour /api/check absent |

Les quatre signalements locaux ne sont pas attribuables avec certitude à ces questions. Aucun total de questions acceptées n’en est déduit.

## 9. Difficultés rencontrées

Aucune tentative infructueuse n’est consignée dans les sources rattachées. Cela ne prouve pas qu’il n’y en a pas eu. Les limites matérielles sont indiquées dans l’introduction.

## 10. Analyse technique approfondie

Chaque question comporte dans le JavaScript une référence de pièce ou de module. La méthode consiste à recouper documents, chronologie, communications et traces sociales ; les candidats du script restent des propositions tant que les preuves ou retours du serveur ne les confirment pas. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Aucune recommandation spécifique supplémentaire n’est établie au-delà des limites du mécanisme décrit. Pour les exercices purement documentaires, la priorité est la conservation des originaux, la provenance des pièces et la séparation des hypothèses et des constats.

## 12. Conclusion

Reconstituer le parcours, les identités et le financement d’un fugitif à partir du dossier Harmattan. La documentation disponible permet une documentation partielle. Statut retenu : Partial. Signalement local uniquement (reported).

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


# OSINT — parcours, identités et financement

[Accueil](../README.md) · [Index général](../INDEX.md) · [Couverture](../reports/coverage.md)

Un seul dossier, **Partial** :

- **Enquete** : reconstituer le parcours, les identités et le financement d’un fugitif à partir du dossier Harmattan.

C’est le dossier le plus structuré en questions : **28 libellés** extraits de `harmattan-data.js`, avec 28 candidats conservés. Le script `check.py` envoie ces candidats à `/api/check`, mais aucun journal de réponses n’est présent. Quatre valeurs ont été signalées au hub, sans association fiable aux 28 questions : à ne pas lire comme 28 acceptations.

## Dossier

| Challenge | Objectif | Techniques | Documentation | Statut |
|---|---|---|---|---|
| [Enquete](enquete/README.md) | Reconstituer parcours, identités et financement d’un fugitif. | JavaScript, chronologie, graphe, CDR, données financières | Documentation partielle | Partial |

## Repères de lecture

- Chaque question est reproduite avec son barème local et son indice conservé ; les réponses restent des candidats non vérifiés.
- Les données personnelles du scénario sont fictives ou expurgées ; ne pas les réutiliser hors du laboratoire.
- Voir la [couverture](../reports/coverage.md) pour la liste des questions et l’état des candidats.

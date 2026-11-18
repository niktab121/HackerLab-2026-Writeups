# PICKUP

[Accueil](../../README.md) · [Web](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | PICKUP |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Web |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | HTTP, codes partenaires, SSRF, JSON |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Déterminer le point de prise en charge associé à l’affectation active.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

## 2. Énoncé du challenge

- Q5 — Objectif reconstitué de la note ; énoncé intégral de la carte absent.

### Objectif

Source : [writeup-PICKUP.md](evidence/web-depart-writeup-pickup-md.txt)

Identifier le lieu prévu pour la prise en charge de Thomas Crown, à partir des
données de coordination de l'opération `OP-24-7319`.

## 3. Analyse initiale

1 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### État initial

Source : [writeup-PICKUP.md](evidence/web-depart-writeup-pickup-md.txt)

- Cible : `http://172.28.38.2:8080`
- Session partenaire obtenue avec `PRT.<id>.<integrite>` (voir q:2).
- SSRF `/waybills` opérationnelle vers `http://2130706433:8081`
  (contournement du filtre loopback par notation décimale).
- Opération, expédition et fenêtre déjà connues : `OP-24-7319`,
  `NL-24-7K42`, affectation active `ASG-318`.

## 4. Reconnaissance et investigation

### Reconnaissance

Source : [writeup-PICKUP.md](evidence/web-depart-writeup-pickup-md.txt)

Le dossier d'opération expose un bloc `destination` :

```bash
curl -s -X POST http://172.28.38.2:8080/waybills \
     --cookie 'session=<...>' \
     -d 'source_url=http://2130706433:8081/api/operations/OP-24-7319'
```

```json
{
  "operation_id": "OP-24-7319",
  "shipment_reference": "NL-24-7K42",
  "destination": {
    "final_destination": "<destination finale>",
    "location": "<terminal>",
    "meeting_point": "Hangar C4 — quai de service nord"
  },
  "traveller": { "cover_name": "<couverture>" }
}
```

La sous-route `/api/operations/OP-24-7319/assignments` confirme le même point
de rendez-vous sur l'affectation active `ASG-318`, avec le véhicule
opérationnel. Le point de rendez-vous est donc cohérent entre le dossier et
l'affectation.

## 5. Identification du mécanisme

Le segment d’intégrité n’est pas lié au préfixe TRK/PRT. Après accès au portail partenaire, l’import de bordereau permet une lecture du service local via une adresse IPv4 numérique. Les questions suivantes utilisent les relations expédition → opération → affectation ; seule l’affectation active est pertinente.

### Interprétation

Source : [writeup-PICKUP.md](evidence/web-depart-writeup-pickup-md.txt)

Le champ `meeting_point` est une chaîne composée en deux parties séparées par
un tiret cadratin :

1. le **lieu principal** (`Hangar C4`) ;
2. une **précision d'accès** (`quai de service nord`).

L'énoncé demande « le lieu prévu pour la prise en charge », c'est-à-dire le
lieu principal. La forme longue (lieu + précision, avec le tiret cadratin) a
été refusée par le vérificateur ; la forme courte correspond au champ
exploitable dans la réponse.

## 6. Exploitation ou résolution

### Exploitation

Source : [writeup-PICKUP.md](evidence/web-depart-writeup-pickup-md.txt)

```bash
python3 solveur.py --target http://172.28.38.2:8080 \
  --code PRT.<id>.<integrite> --q5
```

Le script récupère le dossier et l'affectation active, vérifie que les deux
`meeting_point` sont identiques, puis isole la partie gauche du tiret
cadratin.

### Validation reproductible (sans la réponse)

Source : [writeup-PICKUP.md](evidence/web-depart-writeup-pickup-md.txt)

1. Rejouer la requête `/api/operations/OP-24-7319`.
2. Vérifier que `destination.meeting_point` est non vide.
3. Rejouer `/api/operations/OP-24-7319/assignments` et vérifier que
   l'affectation `status: "active"` porte exactement le même `meeting_point`.
4. Le lieu attendu est la partie du `meeting_point` située avant le tiret
   cadratin, sans espaces superflus.

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

Les outils partagés sont inventoriés dans [THE GATE](../the-gate/README.md). Les arguments spécifiques à cette question sont ceux des notes historiques.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Q5 — Objectif reconstitué de la note ; énoncé intégral de la carte absent. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

### Chemins qui ont échoué

Source : [writeup-PICKUP.md](evidence/web-depart-writeup-pickup-md.txt)

- Soumettre la chaîne complète `Hangar C4 — quai de service nord` (tiret
  cadratin inclus) : refusé par le vérificateur.
- Routes supposées `/pickup`, `/location`, `/dossier`, `/details` sur le
  sidecar : `404` — aucune route dédiée au lieu.
- Le reçu (`recu_northline.png`) ne porte que origine, destination, service et
  statut ; il ne contient pas le point de rendez-vous.
- `/api/shipments/NL-24-7K42` ne donne que `origin` / `destination` au niveau
  ville, pas le hangar.

## 10. Analyse technique approfondie

Le segment d’intégrité n’est pas lié au préfixe TRK/PRT. Après accès au portail partenaire, l’import de bordereau permet une lecture du service local via une adresse IPv4 numérique. Les questions suivantes utilisent les relations expédition → opération → affectation ; seule l’affectation active est pertinente. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Lier cryptographiquement le type de code à son identifiant ; appliquer une autorisation par opération et affectation. Normaliser et contrôler les adresses résolues avant toute requête serveur et isoler les services internes.

## 12. Conclusion

Déterminer le point de prise en charge associé à l’affectation active. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Aucune validation plateforme exportée.

### Leçons

Source : [writeup-PICKUP.md](evidence/web-depart-writeup-pickup-md.txt)

- Un champ peut contenir plusieurs niveaux d'information : l'énoncé indique
  lequel retenir.
- Ne pas recopier tel quel un champ de données : la plateforme peut attendre
  une forme normalisée ou tronquée.
- Croiser systématiquement dossier d'opération et affectation active avant de
  répondre : ici les deux sources concordent.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-PICKUP.md](evidence/web-depart-writeup-pickup-md.txt) — origine : `web/depart/writeup-PICKUP.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


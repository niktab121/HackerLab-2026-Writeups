# Restricted Zone

[Accueil](../../README.md) · [Web](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Restricted Zone |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Web |
| Difficulté | Non documentée |
| Points | 100 |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | SMB, LDAP, NTLM, pass-the-hash |
| Validation | Acceptation Correct rapportée dans la note ; capture absente |

## 1. Introduction

Lire le partage réservé à l’aide du compte de sauvegarde.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** La note rapporte un retour Correct. Il n’existe pas de capture primaire de cette acceptation. L’appartenance à Backup Operators ne donne pas universellement accès à tout partage : la réussite constatée dépend des autorisations de cette instance.

## 2. Énoncé du challenge

- Challenge 09 — Accéder aux zones inaccessibles avec les privilèges initiaux.

### Objectif

Source : [writeup-restricted-zone.md](evidence/operationtervalis-writeup-restricted-zone-md.txt)

Accéder aux zones de l'infrastructure inaccessibles avec les privilèges initiaux (`svc_web`), puis soumettre le flag de la carte *Restricted Zone* (100 pts).

## 3. Analyse initiale

1 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### État initial

Source : [writeup-restricted-zone.md](evidence/operationtervalis-writeup-restricted-zone-md.txt)

Instance VPN `172.28.5.0/24` :

| Hôte | IP VPN | Rôle |
|---|---|---|
| portail + ActiveMQ | `172.28.5.2` | Portail FBI (8080) + OpenWire (61616) |
| dc01 | `172.28.5.3` | Contrôleur de domaine Samba (LDAP 389 / SMB 445 / KDC 88) |
| fs01 | `172.28.5.5` | Serveur de fichiers |
| mgmt01 | `172.28.5.4` | Management (pas de SMB) |

Compte de service découvert : `svc_web` (LDAP bind, mot de passe dans `/opt/activemq/conf/ad-connector.properties`).

## 4. Reconnaissance et investigation

### Reconnaissance

Source : [writeup-restricted-zone.md](evidence/operationtervalis-writeup-restricted-zone-md.txt)

### 1. Partage `Recon-Data` (challenge 08) → hashes de service

Le partage caché `Recon-Data` sur le DC contient `ad_security_audit.txt`, qui expose les **hashes NT** des comptes de service :

```text
svc_mssql : <HEX_EXPURGE>
svc_backup: <HEX_EXPURGE>
svc_web   : <HEX_EXPURGE>  (périmé)
svc_certsvc: <HEX_EXPURGE>
```

### 2. Énumération LDAP (svc_web)

L'énumération LDAP confirme les groupes : `svc_backup` est membre de **Backup Operators** (`CN=Backup Operators,CN=Builtin,DC=valdoria,DC=fbi,DC=lab`), `svc_mssql` est membre de `DB-Admins` avec délégation contrainte.

### 3. Énumération des partages du DC

```bash
smbclient -L //172.28.5.3 -U 'VALDORIA/svc_web%<omis>'
#   sysvol, netlogon, IT-Share, IPC$
```

`IT-Share` est refusé pour `svc_web` (`NT_STATUS_ACCESS_DENIED`).

## 5. Identification du mécanisme

Un hash NT exposé peut suffire à une authentification NTLM. Le résultat doit être établi pour le couple compte/cible/partage précis, sans extrapolation aux autres hôtes.

### Raisonnement

Source : [writeup-restricted-zone.md](evidence/operationtervalis-writeup-restricted-zone-md.txt)

1. `svc_web` ne donne accès qu'à `Recon-Data` (challenge 08), pas à `IT-Share`.
2. Le hash NT de `svc_backup` (membre de **Backup Operators**) est fourni dans l'audit : il suffit d'un pass-the-hash, sans casser le mot de passe.
3. `Backup Operators` dispose des privilèges de lecture sur les partages administratifs : `IT-Share` devient accessible.

## 6. Exploitation ou résolution

### Exploitation : pass-the-hash `svc_backup`

Source : [writeup-restricted-zone.md](evidence/operationtervalis-writeup-restricted-zone-md.txt)

Le hash NT de `svc_backup` (Backup Operators) permet de s'authentifier sur le DC et d'accéder à `IT-Share` :

```bash
smbclient //172.28.5.3/IT-Share \
  -U 'VALDORIA/svc_backup%<HEX_EXPURGE>' --pw-nt-hash -c 'ls'
```

Contenu :

```text
flag-i26.txt
tims_digital_forensics.txt
tims_digital_forensics.pdf
delegation-notes.txt
```

`flag-i26.txt` contient le flag de la carte. Il est soumis tel quel.

### Validation reproductible (sans le flag)

Source : [writeup-restricted-zone.md](evidence/operationtervalis-writeup-restricted-zone-md.txt)

1. Lecture de `Recon-Data`/`ad_security_audit.txt` → hash NT de `svc_backup`.
2. `smbclient //172.28.5.3/IT-Share -U 'VALDORIA/svc_backup%<hash>' --pw-nt-hash -c 'ls'`.
3. Lecture de `flag-i26.txt` → flag.
4. Soumission : la note rapporte une réponse `Correct` ; aucune capture n’est conservée.

### Nettoyage

Source : [writeup-restricted-zone.md](evidence/operationtervalis-writeup-restricted-zone-md.txt)

Aucun compte n'a été modifié. Le hash NT et le flag ne sont pas reproduits dans ce document.

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

Les outils partagés sont inventoriés dans [Opération Tervalis](../operation-tervalis/README.md). Les arguments spécifiques à cette question sont ceux des notes historiques.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Challenge 09 — Accéder aux zones inaccessibles avec les privilèges initiaux. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Acceptation Correct rapportée dans la note ; capture absente |

## 9. Difficultés rencontrées

### Pistes qui ont échoué

Source : [writeup-restricted-zone.md](evidence/operationtervalis-writeup-restricted-zone-md.txt)

- `svc_web` sur `IT-Share` : `ACCESS_DENIED`.
- `svc_backup` sur `fs01` (`172.28.5.5`) : `LOGON_FAILURE` (fs01 refuse explicitement `svc_backup`).
- AS-REP roasting de `svc_backup` : `KDC_ERR_PREAUTH_FAILED` (le KDC Samba exige la pré-authentification malgré le flag `DONT_REQUIRE_PREAUTH`).

## 10. Analyse technique approfondie

Un hash NT exposé peut suffire à une authentification NTLM. Le résultat doit être établi pour le couple compte/cible/partage précis, sans extrapolation aux autres hôtes. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Retirer les hashes des rapports, renouveler les secrets exposés, limiter NTLM et les permissions effectives des comptes de sauvegarde.

## 12. Conclusion

Lire le partage réservé à l’aide du compte de sauvegarde. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Acceptation Correct rapportée dans la note ; capture absente.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-restricted-zone.md](evidence/operationtervalis-writeup-restricted-zone-md.txt) — origine : `operationtervalis/writeup-restricted-zone.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


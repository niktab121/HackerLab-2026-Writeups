# Il Mandante

[Accueil](../../README.md) · [Forensics](../README.md) · [Index](../../INDEX.md)

## Informations générales

| Champ | Valeur |
|---|---|
| Nom | Il Mandante |
| Compétition | HackerLab Bénin 2026 |
| Catégorie de classement | Forensics |
| Difficulté | Non documentée |
| Points | Q2 : 100 ; Q3 : 200 ; Q5 : 200 |
| Auteur | Non documenté |
| Statut | **Partial** |
| Technologies | X.509, CT, RSA, PGCD, OAEP, CMS |
| Validation | Signalement local uniquement (reported) |

## 1. Introduction

Attribuer une autorité de certification, ouvrir un blob RSA et examiner la chronologie d’un dossier signé.

Cette édition reconstruit les travaux conservés. Les commandes citées sont historiques, sauf mention explicite d’un contrôle documentaire local. Aucune cible n’a été contactée lors de la rédaction. Les paramètres d’accès et les réponses sont expurgés ; les remplacer depuis les artefacts autorisés pour une reproduction en laboratoire.

**Limites et corrections de cette édition.** Corrections indispensables : une longueur hexadécimale mesurée avec wc -c ne fournit pas la taille exacte du module en bits ; utiliser int(...,16).bit_length(). Un module de 2047 bits ne prouve pas un RNG cassé : le facteur commun propre, 1 < gcd(n1,n2) < min(n1,n2), est la preuve utile. La note compte dix-huit modules plus deux alors qu’elle annonce dix-neuf feuilles. La période CT citée commence avant la validité de la racine : elle ne peut être décrite comme entièrement incluse dans celle-ci. Les indices des certificats doivent être recalculés : awk commence à 1 et la boucle publiée commence à 0. Le script de validation embarqué appelle openssl -ext sans nom d’extension ; il n’est pas exécutable tel quel. Enfin, CMS sans horodatage de confiance ne date pas la création du contenu : notBefore et SCT renseignent le certificat, pas une borne cryptographique absolue d’existence du PDF.

## 2. Énoncé du challenge

- Q1 — Énoncé absent ; capture du poste et autorités de confiance disponibles.
- Q2 — Pour le compte de quelle organisation cette autorité a-t-elle émis ses certificats ?
- Q3 — Que contient le blob ?
- Q4 — Énoncé absent ; dossier andwerso avec courriel, photographies et pages locales.
- Q5 — À partir de quand le dossier a-t-il réellement pu exister ?

### Objectif

Source : [writeup-il-mandante.md](evidence/forensic-ghot-il-mandante-writeup-il-mandante-md.txt)

Trois pièces sont fournies : le certificat racine d'une autorité de certification
inconnue (`borealisCA-root.pem`), un extrait de journal Certificate Transparency
(`ct-log.csv`, 7 020 entrées) et un extrait WHOIS (`whois-borealis.txt`).

La question : **pour le compte de quelle organisation cette autorité a-t-elle
émis ses certificats ?**

Il ne s'agit donc pas de nommer l'autorité elle-même, mais l'entité
bénéficiaire des certificats qu'elle a signés.

### Objectif

Source : [writeup-il-mandante.md](evidence/forensic-ghot-il-mandante-writeup-il-mandante-md.txt)

Deux pièces pour cette partie :

| Fichier | Taille | Nature |
|---|---|---|
| `crtsh-dump.pem` | 1019 blocs PEM | export Certificate Transparency « brut », contenant la flotte entière de l'AC noyée dans du bruit |
| `blob-capture-c2node.enc` | 256 octets | blob chiffré, « ramassé sur la flotte » |

La question : **que contient le blob ?** Le format de réponse attendu est
`<PREFIXE>{contenu}` : il faut donc produire le contenu en clair, pas le
déchiffrer « à moitié ».

Indice narratif décisif : « la marque de l'atelier qui les a tous forgés ».
Autrement dit, les certificats de la flotte ont été **générés par un outil
maison**, et cet outil a laissé une signature technique dans les clés
publiques. Trouver cette marque donne la clé privée d'un nœud, donc le moyen
d'ouvrir le blob.

### Objectif

Source : [writeup-il-mandante-q5.md](evidence/forensic-ghot-nishi-writeup-il-mandante-q5-md.txt)

Quatre pièces sont fournies dans le répertoire `nishi/` :

| Fichier | Taille | Nature |
|---|---|---|
| `dossier-varelcorp.pdf` | 5 326 octets | « Dossier de synthèse CDI-2026-0217 » attribuant la préparation de l'attaque du 15 mars 2026 à <EXPURGE> |
| `dossier-varelcorp.pdf.p7s` | 2 572 octets | signature détachée CMS/PKCS#7 du PDF, avec la chaîne de certification |
| `ct-log-hote.csv` | 95 622 octets | extrait de journal Certificate Transparency (1 200 entrées) |
| `wayback-cdx.txt` | 330 octets | deux captures d'archivage public du dossier |

La question : **à partir de quand le dossier a-t-il réellement pu exister ?**

Le piège annoncé par l'énoncé est explicite : le dossier revendique une
antériorité (« rédaction au 20 février 2026 »), donc une datation qui
précéderait l'incident. Il s'agit de trouver un **plancher technique
infalsifiable**, pas de croire une métadonnée déclarative.

## 3. Analyse initiale

21 fichiers rattachés directement à ce dossier. Voir l’[inventaire des pièces](evidence/manifest.md), qui indique leur chemin d’origine, leur taille et la décision de publication. Les pièces partagées sont référencées dans les questions apparentées, sans recopier les archives.

### État initial et première lecture des pièces

Source : [writeup-il-mandante.md](evidence/forensic-ghot-il-mandante-writeup-il-mandante-md.txt)

### Le certificat racine

```console
$ openssl x509 -in borealisCA-root.pem -noout -text | head -20
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            0b:06:d2:b2:f7:4e:80:41:f1:53:a1:a2:7d:bd:88:0e:90:e3:7c:c6
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: C=XX, O=Borealis Trust Services, CN=Borealis Certification Authority
        Validity
            Not Before: Feb  2 06:32:00 2026 GMT
            Not After : Feb  2 06:32:00 2029 GMT
        Subject: C=XX, O=Borealis Trust Services, CN=Borealis Certification Authority
```

Points relevants :

- racine **auto-signée** (Subject = Issuer), donc l'autorité est sa propre ancre ;
- `C=XX` : code pays volontairement neutre / non attribué ;
- `Basic Constraints: CA:TRUE` (critique), `Key Usage: Certificate Sign, CRL Sign` :
  c'est bien une AC qui émet des certificats feuilles ;
- politique de certification `1.3.6.1.4.1.62233.1.1` avec un CPS hébergé sur
  `cps.<domaine de l'AC>` ;
- SKI `9C:C5:7A:DB:B6:82:B1:9E:83:11:4B:FF:94:87:E4:98:11:84:54:37`
  (utile pour recouper les entrées du journal).

Le nom de l'AC (`Borealis Trust Services`) est un leurre évident : la question
demande **pour le compte de qui** elle émet, pas qui elle est.

### Le WHOIS

```console
$ cat whois-borealis.txt
domain:            <domaine de l'AC>
created:           2026-01-28
registrant-org:    Borealis Trust Services
registrant-country: XX
registrant-city:   Aurenvik
remarks:           Autorite recente. Aucune presence anterieure a 2026.
remarks:           Aucun point de contact enregistre en Varelia (C=VR).
```

Deux enseignements :

1. l'autorité est **très récente** (créée fin janvier 2026, racine émise le
   2 février 2026) : profil classique d'une AC éphémère créée pour un usage
   interne/offensif ;
2. la dernière remarque est une indication directionnelle forte : aucun contact
   au registre du pays **Varelia (`C=VR`)**, ce qui invite à chercher dans le
   journal CT une organisation rattachée à ce pays.

### État initial

Source : [writeup-il-mandante.md](evidence/forensic-ghot-il-mandante-writeup-il-mandante-md.txt)

- 1019 certificats, dont 38 émetteurs distincts : le dump est majoritairement
  du bruit, il faut d'abord isoler la flotte.
- 256 octets = 2048 bits : ordre de grandeur d'un chiffré RSA (et non d'un
  chiffré hybride, qui contiendrait une clé de session + un cryptogramme AES
  beaucoup plus long).
- Aucune clé privée fournie, aucun mot de passe, aucun endpoint : la seule
  attaque possible est **mathématique**, sur les clés publiques.

### État initial : ce que le document raconte

Source : [writeup-il-mandante-q5.md](evidence/forensic-ghot-nishi-writeup-il-mandante-q5-md.txt)

### Les métadonnées du PDF

```console
$ pdfinfo dossier-varelcorp.pdf
Title:           Dossier de synthèse CDI-2026-0217
Author:          Comité de Divulgation Indépendant
Creator:         Writer
Producer:        LibreOffice 24.8
CreationDate:    Fri Feb 20 10:00:00 2026 WAT
ModDate:         Fri Feb 20 10:00:00 2026 WAT
Pages:           1
File size:       5326 bytes
PDF version:     1.7
```

La thèse du document est construite sur ces deux champs : création et
modification au 20 février 2026, soit **avant** l'incident du 15 mars 2026.

### Le contenu

```console
$ pdftotext -layout dossier-varelcorp.pdf -
```

Le texte reprend la même affirmation en section 6 (« Datation du dossier ») :

> La compilation de ce dossier est antérieure à l'incident. Les propriétés du
> fichier (date de création et date de dernière modification) attestent d'une
> rédaction au 20 février 2026.

puis, en pied de page : « Dossier compilé le 20 février 2026, antérieurement à
l'incident. »

Or le document **décrit l'incident du 15 mars 2026 comme un fait accompli**
(« l'incident du 15 mars 2026 n'en est que l'aboutissement ») et détaille une
chronologie allant du 8 janvier au 18 février 2026. Un document ne peut pas
documenter un événement futur : l'antériorité revendiquée est donc déjà
logiquement douteuse. Mais la question demande une borne *réelle*, pas une
impression.

**Contrôle local réellement effectué pendant cette édition :** [résultats structurés](evidence/controle-documentaire.json). Les mesures ne comportent aucune réponse ni secret.

## 4. Reconnaissance et investigation

### Q2 — Distinguer l’autorité de son bénéficiaire

La note part de `borealisCA-root.pem`, `ct-log.csv` et `whois-borealis.txt`. Les commandes historiques examinent d’abord le sujet et l’émetteur de la racine, puis isolent les lignes du journal correspondant à cette autorité.

```bash
openssl x509 -in borealisCA-root.pem -noout -text | head -20
awk -F, 'NR>1 { print $6 }' ct-log.csv | sort -u | wc -l
awk -F, 'NR>1 && $6 == "Borealis Certification Authority"' ct-log.csv | wc -l
```

La note rapporte 38 émetteurs et 20 entrées de cette autorité, toutes associées à la même organisation. Le nom de l’autorité ne répond pas à la question du mandant : il faut lire l’organisation bénéficiaire dans les feuilles, puis la recouper dans la capture réseau. Le WHOIS est un indice contextuel, pas une preuve cryptographique d’attribution.

### Q3 — Inventorier les clés publiques

Le dump PEM compte 1 019 certificats. Le contrôle documentaire actuel confirme 19 certificats dont l’AKI correspond au SKI de la racine. Le blob mesure 256 octets, une taille compatible avec un bloc RSA sur un module de 2 048 bits. Cette seule taille ne prouve ni l’algorithme ni l’absence de métadonnées dans un autre fichier.

```bash
grep -c "BEGIN CERTIFICATE" crtsh-dump.pem
```

Les noms de fichiers issus d’un découpage awk commencent à 1 ; la boucle 0–1018 des notes comporte une erreur de décalage. Pour cette édition, le contrôle a chargé directement les blocs PEM et évité les indices historiques.

### Q5 — Séparer les horloges

La source examine les métadonnées PDF, la signature CMS détachée, les certificats, le SCT et l’archive publique fournie. Ces éléments ne datent pas tous le même événement. Un champ PDF est modifiable ; notBefore décrit le début de validité du certificat ; un SCT concerne un certificat ou précertificat ; une archive publique témoigne d’une observation sous réserve de confiance dans l’archive.

Les données du dossier `andwerso` n’ont pas de question ni de note de résolution associée. Elles ne sont pas converties artificiellement en solution Q4.

## 5. Identification du mécanisme

Deux modules RSA distincts partageant un premier permettent de reconstruire d par inversion modulo phi(n). Un module dupliqué ne suffit pas. L’ouverture OAEP doit être vérifiée séparément de la lisibilité du résultat. Un succès PKCS#1 v1.5 peut être un rejet implicite produisant une valeur de remplacement selon la bibliothèque ; ce schéma ne vérifie pas seulement deux octets.

## 6. Exploitation ou résolution

### Q2 — Corrélation de certificats

Objectif : identifier le bénéficiaire des émissions. La note filtre les lignes CT par émetteur, dénombre les organisations et compare le résultat au champ `O` d’un certificat feuille extrait du trafic.

```bash
awk -F, 'NR>1 && $6 == "Borealis Certification Authority" { print $5 }' \
  ct-log.csv | sort | uniq -c
tshark -r capture-poste.pcap -Y "tls.handshake.type==11" \
  -T fields -e tls.handshake.certificate > /tmp/tls-certs.hex
```

Le premier résultat rapporté est une organisation unique sur 20 entrées. Les valeurs attributives ne sont pas publiées. La capture est disponible, mais la note évoque aussi un carving DER lorsque l’extraction tshark ne suffit pas ; le script `carve_certs.py` n’est pas conservé. La corrélation complète reste donc historique.

### Q3 — Facteur commun puis choix du remplissage

Le calcul local réellement effectué a confirmé deux relations distinctes : deux certificats réutilisent le même module, et deux modules distincts partagent un facteur de 1 024 bits. La seconde relation est exploitable.

```python
g = math.gcd(n1, n2)
assert 1 < g < min(n1, n2)
p = g
q = n1 // p
assert p * q == n1
d = pow(e, -1, (p - 1) * (q - 1))
```

Cette expression de reconstruction figure dans la méthode historique. La mission documentaire s’est arrêtée au PGCD, sans reconstruire de clé privée. Un module identique ne donne pas, à lui seul, ses facteurs.

La note rapporte ensuite des essais OAEP-SHA256, OAEP-SHA1 et PKCS#1 v1.5 sur les clés reconstituables. Elle retient OAEP-SHA256 pour un nœud de la flotte et un texte structuré. Cette ouverture n’a pas été rejouée. Des octets renvoyés par une API PKCS#1 v1.5 ne suffisent pas à conclure : selon l’implémentation, un rejet implicite peut produire un résultat de remplacement. La phrase historique selon laquelle PKCS#1 v1.5 ne vérifierait que deux octets est incorrecte.

### Q5 — Vérifier la signature sans surinterpréter sa date

Commandes d’inspection présentes dans les notes :

```bash
openssl cms -cmsout -inform DER -in dossier-varelcorp.pdf.p7s -print
openssl pkcs7 -inform DER -in dossier-varelcorp.pdf.p7s -print_certs -noout
openssl x509 -in /tmp/q5-leaf.pem -noout -dates
```

La note rapporte une signature valide sur le PDF et propose une borne temporelle à partir du certificat et du CT. Une signature valide établit un lien entre le contenu et une clé ; elle ne suffit pas à dater la création du document. Sans horodatage de confiance lié au contenu signé, la borne présentée ne doit pas être décrite comme une preuve absolue de la première existence possible du dossier. La réponse historique reste signalée au hub, sans validation plateforme exportée.

Les [mesures locales](evidence/controle-documentaire.json) confirment uniquement le nombre de certificats, les tailles de modules, les relations PGCD et la taille du blob.

## 7. Scripts et automatisation

Aucun script autonome rattaché directement à cette question. Les commandes intégrées aux notes sont reproduites lorsqu’elles existent ; elles ne sont pas déclarées testées dans cette édition.

## 8. Questions et flags

Les réponses ne sont pas publiées, conformément à la règle locale de non-divulgation. Un signalement au hub ne vaut pas acceptation par la compétition.

| Question / objectif | Méthode et preuve | Réponse | Validation |
|---|---|---|---|
| Q1 — Énoncé absent ; capture du poste et autorités de confiance disponibles. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |
| Q2 — Pour le compte de quelle organisation cette autorité a-t-elle émis ses certificats ? | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |
| Q3 — Que contient le blob ? | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |
| Q4 — Énoncé absent ; dossier andwerso avec courriel, photographies et pages locales. | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |
| Q5 — À partir de quand le dossier a-t-il réellement pu exister ? | Voir la reconstruction et les sources de ce dossier. | Non reproduite / inconnue si non résolue | Signalement local uniquement (reported) |

## 9. Difficultés rencontrées

| Point de la note originale | Correction ou limite retenue |
|---|---|
| Dix-huit modules plus deux pour une flotte de dix-neuf | Le contrôle local donne 17 modules de 2 048 bits et 2 de 2 047 bits. |
| Déduire les bits de `wc -c` | Utiliser `int(hexadecimal, 16).bit_length()` ; compter les caractères et le saut de ligne ne suffit pas. |
| Module de 2 047 bits présenté comme preuve d’un RNG cassé | C’est au plus un indice ; le facteur propre partagé démontre la vulnérabilité. |
| Deux modules identiques présentés avec le facteur partagé | Réutilisation de clé et factorisation sont deux cas distincts. |
| Période CT annoncée incluse dans la validité de la racine | La date de début citée la précède ; contradiction documentaire explicite. |
| Boucle d’indices à partir de 0 après découpage à partir de 1 | Risque d’omettre un certificat et de comparer les mauvais indices. |
| `openssl -ext` sans nom d’extension dans le script publié | Exemple incomplet ; le contrôle ajouté lit directement les extensions avec cryptography. |
| Sortie RSA brute sans préfixe attendu considérée normale pour OAEP | Un bloc OAEP encodé correct commence par l’octet zéro ; l’absence de cette structure invite à revoir la clé, le blob ou la représentation. |
| NotBefore ou SCT assimilé à la date de création du PDF | Ces dates concernent le certificat, pas la première existence du contenu. |

Les notes historiques expurgées sont conservées pour permettre d’auditer ces corrections, sans les effacer des originaux.

## 10. Analyse technique approfondie

La faiblesse RSA vient de la factorisation commune, non de la taille nominale des clés. Avec `n1 = p*q1` et `n2 = p*q2`, le PGCD révèle `p` ; la suite est une inversion modulaire. Cette attaque ne réclame pas de recherche exhaustive et illustre l’impact d’une mauvaise génération ou réutilisation de facteurs.

L’attribution X.509 demande de séparer les identités : l’émetteur signe, le sujet désigne le titulaire, le SAN désigne les noms couverts. Une concentration d’émissions est un indice d’infrastructure ; elle ne prouve pas à elle seule l’identité de l’opérateur humain.

La chronologie distingue enfin intégrité et temps. Une vérification CMS peut confirmer que le contenu correspond à la signature tout en laissant inconnue la date réelle de signature. Une preuve de temps doit être rattachée au bon objet et reposer sur une source de temps de confiance.

## 11. Remédiations

Générer les clés avec un générateur aléatoire sûr et contrôler les facteurs partagés dans la flotte ; révoquer les clés compromises. Utiliser des horodatages de confiance pour établir une chronologie de signature.

## 12. Conclusion

Les pièces documentent trois opérations différentes : corrélation CT, analyse mathématique de clés RSA et critique d’un dossier signé. Le facteur partagé est confirmé localement ; les déchiffrements et réponses historiques ne sont pas revalidés par la plateforme. Les questions 1 et 4 restent incomplètes. Le dossier est classé Partial malgré une reconstruction détaillée des parties documentées.

## 13. Références

Les références sont les pièces locales ci-dessous. Les références Internet citées dans les notes restent historiques et n’ont pas été consultées pendant cette mission.

- [writeup-il-mandante.md](evidence/forensic-ghot-il-mandante-writeup-il-mandante-md.txt) — origine : `forensic/ghot/il mandante/writeup-il-mandante.md`.

- [writeup-il-mandante-q5.md](evidence/forensic-ghot-nishi-writeup-il-mandante-q5-md.txt) — origine : `forensic/ghot/nishi/writeup-il-mandante-q5.md`.

- [Inventaire local des pièces](evidence/manifest.md).
- [Retour à l’index](../../INDEX.md).


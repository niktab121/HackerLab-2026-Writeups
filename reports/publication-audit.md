# Audit de publication

Contrôle documentaire du 18 novembre 2026. Le dépôt est prêt pour une **relecture de publication**, avec les limites scientifiques explicites ci-dessous. Il ne certifie ni toutes les solutions, ni l’acceptation des réponses par la compétition.

## Bilan

- 29 dossiers indépendants et 29 README conformes au plan demandé.
- 21 reconstructions détaillées ; 8 dossiers partiels ou sans éléments suffisants.
- 60 emplacements de question ou objectifs recensés, selon la convention de [coverage.md](coverage.md), dont 28 questions d’Enquete extraites intégralement.
- 41 scripts historiques rattachés aux challenges, plus 1 script sans attribution certaine. Le contrôle documentaire ajouté est distinct.
- 377 fichiers originaux réhachés : **0 modification ou disparition**.
- Contrôle syntaxique Python : **0 erreur** ; contrôle `bash -n` : **0 erreur**. Cela ne démontre pas le fonctionnement des solveurs.
- TruffleHog, vérification distante et mise à jour désactivées : **0 détection**, code de sortie 0.

Liens Markdown locaux : **0 lien manquant**. Sections obligatoires : **0 dossier incomplet sur la structure**. Voir [audit-results.json](audit-results.json) pour les contrôles structurés.

## Cohérence technique et réponses

Le contrôle local a confirmé les 1 019 certificats du dump Il Mandante, les 19 certificats de la flotte et le facteur partagé de 1 024 bits. Il n’a pas déchiffré le blob. Il a confirmé les 25 messages NordLink, les 11 couches Docker et les caractéristiques structurelles du conteneur Memento. Les captures ont été lues hors ligne sans émission réseau.

Les résultats détaillés se trouvent dans [source-checks.json](source-checks.json). Les contradictions importantes ont été conservées et annotées : chemin Bitcoin refusé, script ICMP à réponse constante, différence entre ratchet complet et ancre fixe, datation CMS surestimée et conclusions d’exfiltration DFIR insuffisamment étayées.

Les flags ne sont pas publiés. Il n’existe pas d’export primaire certifiant les acceptations par question. Les mentions « Correct » ou « validé » dans une note sont attribuées à cette note et ne sont pas converties en nouvelle validation. Aucun flag n’a été soumis à une plateforme pendant la mission.

## Scripts et reproductibilité

Les copies expurgées préservent les méthodes mais peuvent nécessiter des paramètres d’instance, chemins ou artefacts privés. Les imports ne sont pas un environnement de dépendances installé et testé. Les scripts à effet réseau, scanners et exploitations n’ont pas été lancés.

Deux dérivés Impacket restent dans les originaux, car le fichier de licence auquel ils renvoient n’est pas fourni. Les scripts `trace.py`, `check_paths.py`, `carve_certs.py` et le parseur produisant `msgs.pkl` sont cités par des notes mais absents. Aucun script de remplacement n’a été présenté comme historique.

Pour reproduire les contrôles de structure réellement exécutés, avec Python, cryptography et tshark disponibles :

```bash
python3 reports/verify-sources.py /chemin/vers/hackerlab
```

Cette commande a été exécutée avec la racine locale réelle et a reproduit les mesures archivées. Elle lit les sources et imprime uniquement des mesures non sensibles. Elle ne lance pas de solveur ni de soumission.

Commandes de contrôle de publication exécutées : analyse AST des fichiers Python, `bash -n` sur les scripts shell, comparaison SHA-256 de tous les originaux, résolution des liens Markdown locaux et scan TruffleHog ci-dessous.

```bash
trufflehog filesystem HackerLab-2026-Writeups --no-verification --no-update --json --log-level=-1
```

## Données sensibles et métadonnées

Les configurations VPN, tickets Kerberos, cookies, états privés de session et fichiers de réponses sont exclus. Les valeurs connues, jetons, hashes d’authentification et adresses de contact ont été masqués dans les copies. Les données encodées des essais Base64/ROT13 ne sont pas publiées. Les en-têtes de session repérés ont été expurgés.

Aucun PDF, image, PCAP, base SQLite, archive ou exécutable binaire n’est livré. Cette exclusion évite de publier leurs secrets et métadonnées sans audit complet. Les images existantes sont inventoriées ; aucune capture n’a été inventée. Les noms et faits de scénario restants proviennent des documents du CTF, et ne sont pas présentés comme des informations sur des personnes réelles.

Le scan automatique n’est pas une garantie absolue d’absence de données sensibles ; il complète l’exclusion des classes à risque et la revue des copies. Les empreintes SHA-256 de l’inventaire sont des empreintes de fichiers, pas des secrets d’authentification.

Relecture finale : les jetons de rédaction mal fermés ont été corrigés dans `Web/aizen/README.md` et `Web/aizen/evidence/hub-49638.txt` (deux occurrences d’une apostrophe et d’un backtick manquants). Aucun contrôle automatisé ne détecte à lui seul ce type de défaut de forme ; la vérification reposait sur la recherche des marqueurs de rédaction non terminés et sur l’appariement des délimiteurs de blocs de code, qui sont désormais équilibrés dans tous les fichiers Markdown.

Un historique `.git` local existe désormais : la branche `main` pointe sur le commit `a0da971` et suit `origin/main` sur le même commit. La présente mission n’a exécuté aucun `push` et aucune publication ; la mise en ligne reste une décision du propriétaire. Les corrections apportées après ce commit sont locales et non commitées.

## Hub local et conservation des sources

Deux nouveaux comptes rendus ont été importés avec confirmation locale : **THE GATE** et **Enquete**. Leurs entrées ne possédaient pas de compte rendu avant l’import. Les autres comptes rendus du hub n’ont pas été remplacés : l’outil d’import met à jour l’entrée existante, ce qui aurait modifié une source originale utilisée dans cette mission.

Les chemins `writeup-*.md` sont des liens symboliques internes vers les README. Cela satisfait la convention de nommage sans multiplier les copies. Les PDF et notes originaux du projet n’ont pas été modifiés.

## État avant publication

La collection documentaire est organisée et navigable. Elle est publiable comme portfolio d’investigations **avec les limites déclarées**, et non comme corrigé officiel intégral. Les titres inférés, les catégories éditoriales et les difficultés inconnues sont signalés. Les droits des pièces historiques et scripts préexistants ne sont pas redéfinis par la licence des nouveaux textes.

À compléter pour lever les réserves scientifiques : retours de validation, énoncés manquants, journaux DFIR et pièces intermédiaires référencées mais absentes. Une relecture de bout en bout des 29 README a été effectuée : plan en 13 sections présent partout, aucun lien Markdown local rompu, aucune section vide, aucun bloc de code non fermé, aucun jeton de rédaction incomplet, aucune valeur de flag de la compétition dans les fichiers publiés. La publication sur un dépôt distant fait l’objet d’une autorisation distincte du propriétaire.

## Navigation finale

Sept pages de catégorie ont été ajoutées : `Web/README.md`, `Forensics/README.md`, `Blockchain/README.md`, `Cryptography/README.md`, `Network/README.md`, `OSINT/README.md` et `Misc/README.md`. Chacune rappelle le périmètre de la catégorie, propose un ordre de lecture, donne un tableau des dossiers avec objectif, techniques, profondeur de documentation et statut, puis signale les limites de preuve.

Chaque README de challenge commence par un fil d’Ariane vers l’accueil, la page de catégorie et l’index ; le plan en 13 sections reste inchangé. `README.md` porte une section « Par où commencer » et une carte du dépôt ; `INDEX.md` et `SUMMARY.md` renvoient aux pages de catégorie.

Contrôles après ces ajouts :

```bash
# 29 README de challenge, chacun avec 14 titres de niveau 2
# 1 060 liens Markdown locaux, 0 rompu
# 25 statuts Partial, 4 statuts Unsolved, conformes à reports/coverage.md
# compilation AST des scripts Python et bash -n des scripts shell : sans erreur
```

La seule occurrence de la chaîne `HLB2026{` dans les fichiers suivis est un test de détection dans `Web/operation-tervalis/scripts/operationtervalis--solveur.py` ; elle ne contient pas de flag.

L’affirmation antérieure selon laquelle l’historique conserverait des objets antérieurs aux expurgations a été vérifiée puis corrigée. Le dépôt local ne contient qu’un commit initial (`a0da971`), aucun objet pendant (`git fsck --lost-found --dangling`), aucun pack, et un `reflog` réduit à ce commit. L’historique est donc exactement l’arbre publié, sans état intermédiaire caché. En revanche, ce commit porte encore des valeurs que les corrections ultérieures ont expurgées : les blobs correspondants restent accessibles par leur SHA tant que l’historique n’est pas remplacé.

Les modifications postérieures au commit `a0da971` restent locales et non commitées : expurgations AIZEN, audit de publication, couverture, README principal, index, sommaire, les 29 fils d’Ariane et les sept pages de catégorie.

## Préparation du déploiement GitHub

Dépôt cible : `https://github.com/niktab121/HackerLab-2026-Writeups`. La branche distante `main` pointe déjà sur `a0da971`, donc la mission n’est pas une première publication mais une mise à jour d’un dépôt existant.

### Contrôles exécutés

```bash
git status                      # 35 fichiers modifiés, 7 ajouts, 0 suppression
git remote -v                   # origin -> https://github.com/niktab121/HackerLab-2026-Writeups.git
git branch -vv                  # main -> a0da971, suit origin/main
git rev-list --objects --all    # 287 objets, un seul commit
git fsck --lost-found --dangling
git ls-files | sed 's/.*\.//' | sort | uniq -c
```

État de l’arbre publié : 239 entrées suivies — 102 Markdown, 85 extraits texte, 40 scripts Python, 7 JSON, 3 scripts shell, `LICENSE`, `.gitignore` et 29 liens symboliques `writeup-*.md`. Aucun binaire, aucune archive, aucun PDF, aucune base, aucun PCAP : le plus gros fichier fait 99 Ko (`reports/source-inventory.json`) et l’arbre complet 1,5 Mo.

### Secrets trouvés lors de cet audit

Le scan limité à `HEAD` avait manqué trois occurrences d’un mot de passe de laboratoire, présent dans le README, la preuve textuelle et le script du challenge Canary. Il a été remplacé par `<SECRET_EXPURGE>` dans les trois fichiers. Un scan portant sur tous les blobs de l’historique a confirmé que ces trois fichiers étaient les seuls concernés.

Règle appliquée pour distinguer ce qui reste : les valeurs qui authentifient un service — mot de passe, jeton, session, paire de clés — sont expurgées ; les clés cryptographiques qui constituent l’objet même du challenge restent publiées et signalées comme données de laboratoire fictives, car elles portent la démonstration. C’est le cas de `n0rthstar_2024!!` (clé XOR de The hunt) et de `TVG-GRID-MK-…` (clé maître de Kiss of Death).

Le scan automatique ne prouve pas l’absence de secrets ; il ne remplace ni la règle ci-dessus ni la revue manuelle. Les adresses de contact du corpus sont des valeurs de remplacement `example.invalid`, et les IP publiques citées appartiennent au scénario (dont une adresse OVH utilisée comme C2 fictif) ou à des résolveurs et serveurs de temps publics.

### Contrôle de rendu après publication

Le premier envoi a révélé un défaut de rendu que les contrôles de liens ne pouvaient pas voir : dans 28 fiches, les lignes du tableau « Questions et flags » étaient séparées par une ligne vide, si bien que GitHub affichait l’en-tête puis les lignes en texte brut avec des barres verticales. Les lignes vides intercalées ont été supprimées dans `il-mandante` et `kiss-of-death`, et la ligne vide placée juste après la ligne de séparation a été retirée dans les 28 fiches concernées. Un contrôle automatique vérifie désormais, pour chaque bloc de lignes commençant par `|`, la présence du séparateur en deuxième position et l’égalité du nombre de colonnes. Les blocs de code sont exclus de ce contrôle, pour ne pas confondre une barre verticale de commande avec un tableau.

### Limite connue des liens symboliques

Les 29 fichiers `writeup-*.md` sont des liens symboliques vers `README.md`. Git les conserve comme tels : GitHub les affiche comme de petits fichiers contenant le chemin cible, sans redirection. La navigation réelle passe par les README, les pages de catégorie et l’index ; les liens restent fonctionnels dans un clone local et pour l’import du hub.

### Deux scénarios de publication

1. **Commit de correction puis `push` simple** (`git push origin main`) : rapide et sans réécriture, mais le commit `a0da971` conserve le mot de passe de laboratoire dans l’historique, accessible par son SHA.
2. **Historique propre** : reconstruire un dépôt à commit unique à partir de l’arbre corrigé, puis `git push --force-with-lease`. L’arbre publié est identique au contenu validé : l’empreinte d’arbre du commit reconstruit et celle de l’index du dépôt de travail ont été comparées et sont égales, et un `diff -r` des deux arbres ne renvoie aucune différence. L’ancien commit n’est plus référencé ; GitHub peut toutefois conserver l’objet non référencé un certain temps, la purge complète passant par le support GitHub.

Le second scénario a été préparé puis retenu, avec l’autorisation explicite du propriétaire. La reconstruction a été faite dans un répertoire temporaire distinct, sans toucher à l’historique du dépôt de travail. Le contenu du dépôt de travail est la source de vérité ; la publication en est un instantané à commit unique.

## Publication effectuée

Dépôt public : <https://github.com/niktab121/HackerLab-2026-Writeups>, branche `main`, un seul commit, publiée le 18 novembre 2026.

L’envoi a utilisé `--force-with-lease` en désignant explicitement le commit attendu sur le distant, afin qu’aucune mise à jour concurrente ne soit écrasée. Le commit antérieur, qui contenait encore le mot de passe de laboratoire du challenge Canary, n’est plus référencé : la branche `main` pointe sur l’instantané expurgé.

### Vérifications après publication

Les contrôles ont été exécutés sur un clone neuf, téléchargé depuis GitHub, et non sur le répertoire de travail.

- un seul commit dans tout l’historique ; auteur `niktab121`, date du 18 novembre 2026 ;
- 239 fichiers suivis, empreinte d’arbre identique à celle de l’index du dépôt de travail ;
- 29 fiches de challenge réparties en 7 catégories : Web 10, Forensics 11, Misc 3, Blockchain 2, Cryptography 1, Network 1, OSINT 1 ;
- 1 061 liens Markdown locaux, 0 rompu ;
- mot de passe de laboratoire absent de tous les objets de l’historique ;
- 1 061 liens vérifiés de nouveau après la correction des tableaux, sans régression ;
- côté serveur, les pages d’accueil, d’index, de catégorie et de challenge répondent en HTTP 200 et les tableaux se rendent en HTML (`<table>` et `<td>` présents, aucun paragraphe commençant par une barre verticale).

### Incident de rendu corrigé

Le premier envoi a montré que 28 fiches affichaient leur tableau « Questions et flags » en lignes de barres verticales. La cause était une ligne vide insérée juste après la ligne de séparation du tableau, et pour deux fiches une ligne vide entre chaque ligne du tableau. Les lignes vides ont été supprimées, un contrôle automatique de structure des tableaux a été ajouté, et l’instantané a été republié. La version en ligne est la version corrigée.

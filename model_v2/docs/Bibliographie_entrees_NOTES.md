# Bibliographie — notes de vérification

**Ce document ne fait pas partie du mémoire.** Il accompagne `Bibliographie_entrees_MEMOIRE.md`.

## 1. Ce qui a été vérifié, et où

Chaque entrée complétée a été obtenue d'une source primaire ou d'un registre d'identifiants, jamais de mémoire.

| Référence | Ce qui manquait | Source de la vérification |
| --- | --- | --- |
| Caudle et al. 2025 | volume, numéro, pages | API Crossref, DOI 10.1002/cpt.70005 |
| Chanfreau-Coffinier et al. 2019 | **tous les auteurs** (11) | API Crossref, DOI 10.1001/jamanetworkopen.2019.5345 |
| Hodel et al. 2024 | numéro d'article, DOI | API Crossref, recherche bibliographique |
| Jithesh et al. 2022 | **tous les auteurs** (19 + consortium), numéro d'article | DOAJ puis API Crossref pour le numéro d'article |
| Lim et al. 2025 | **tous les auteurs** (13), titre exact, pages, DOI | dépôt institutionnel James Cook University |

## 2. Marqueurs levés dans le mémoire

Cinq entrées portaient un marqueur. Après substitution, les marqueurs suivants disparaissent de la bibliographie :

- `**[à compléter : volume, pages, et le chiffre « 34 gènes et 164 médicaments » cité au chapitre 1]**` — la partie bibliographique est levée ; **le chiffre reste à vérifier** (voir § 4).
- `**[à compléter : numéro d'article et DOI]**` pour Hodel et al.
- Les trois `**[Auteurs à compléter]**` : Qatar, Veterans Health Administration, Kidney International Reports.

## 3. Points de vigilance sur les entrées complétées

**Jithesh et al. 2022** : le dix-neuvième signataire est un consortium (« The Qatar Genome Program Research Consortium »). La convention du mémoire pour citer un consortium en position d'auteur doit être vérifiée et appliquée de façon uniforme — la référence de l'IWPC au chapitre 7 présente le même cas et commence par « International Warfarin Pharmacogenetics Consortium ».

**Lim et al. 2025** : le dépôt institutionnel ne donne pas le numéro de fascicule, et il ne confirme ni les onze patients ni l'existence du Tableau S3. Ces deux éléments viennent de la lecture directe de l'article faite pour le chapitre 8 ; ils ne sont donc pas en cause, mais la pagination 4065-4068 et l'absence de numéro de fascicule sont à confirmer sur la page de l'éditeur.

**Kalinin et al. 2018** : le volume (19), le numéro (7) et les pages (629-650) proviennent de la convention de citation usuelle de cet article et **n'ont pas été vérifiés sur Crossref**. À confirmer avant le dépôt, ou à citer par son seul DOI.

## 4. Ce qui reste à vérifier

| Élément | Nature | Comment le lever |
| --- | --- | --- |
| Pagination de Geifman et El-Yaniv dans les actes NeurIPS 2017 | pagination | page de l'article sur papers.neurips.cc ou une base de citations |
| Métadonnées de Walsh et al. (DOME) | revue, volume, pages | préimpression arXiv:2006.16189 ; la version publiée est à retrouver |
| « 34 gènes et 164 médicaments » (chapitre 1) | **chiffre dans le texte, pas métadonnée** | lecture du texte de Caudle et al. 2025, inaccessible depuis ici (éditeur Wiley) |
| Date de consultation de la page CPIC Genes–Drugs | date | à fournir : c'est la date à laquelle la page a été consultée |
| Référence exacte du tableau GeT-RM V4 | référence complète | site du CDC ; le mémoire indique « tableau consolidé V4 du 22 janvier 2025 » |
| Confirmation de Farmaki et al. 2024 | conclusions de l'article | inaccessible : Europe PMC limite le débit, PubMed et les sites éditeurs refusent la requête |

**Le chiffre « 34 gènes et 164 médicaments » mérite une attention particulière** : il figure au chapitre 1 comme une affirmation chiffrée attribuée à une source. Si le texte de Caudle et al. ne peut pas être consulté, deux options conformes aux règles de rédaction : le remplacer par un décompte fait directement sur le site de CPIC, en citant la date de consultation, ou le retirer.

## 5. Méthode qui a fonctionné, à réutiliser

L'API Crossref interrogée par DOI (`api.crossref.org/works/<DOI>`) donne de façon fiable auteurs, titre, revue, volume, numéro, pages et numéro d'article. C'est la voie la plus sûre lorsque le DOI est connu.

Lorsque le DOI est inconnu, la recherche bibliographique de Crossref (`api.crossref.org/works?query.bibliographic=...&rows=3`) fonctionne, mais l'URL doit rester courte — une requête trop longue est rejetée.

Les voies qui ont échoué : PubMed et PMC (chargement par script, puis vérification anti-robot), les sites des éditeurs SAGE et Mary Ann Liebert (requête refusée), Europe PMC (limitation de débit répétée). Les dépôts institutionnels et DOAJ se sont révélés de bons substituts.

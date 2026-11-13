# Chapitre 2 — notes de vérification et de suivi

**Ce document ne fait pas partie du mémoire.** Il accompagne `Chapitre2_MEMOIRE.md` : statut de lecture de chaque référence, points bloquants, corrections à reporter dans la bibliographie, et vérifications de cohérence avec les autres chapitres.


### Statut de lecture des références du chapitre

| Référence | Métadonnées | Résumé | Texte intégral |
| --- | --- | --- | --- |
| Relling et Klein 2011 | déjà en bibliographie | — | non lu |
| Swen et al. 2011 | déjà en bibliographie | — | non lu |
| Abdullah-Koolmees et al. 2021 | déjà en bibliographie | — | non lu |
| Whirl-Carrillo et al. 2021 | vérifiées | lu | non lu |
| Caudle et al. 2025 | incomplètes (volume, pages) | — | non lu |
| Sangkuhl et al. 2020 | déjà en bibliographie | — | non lu |
| Sherman et al. 2024 | déjà en bibliographie | — | non lu |
| Gourraud et al. 2014 | déjà en bibliographie | — | non lu |
| Haidar et al. 2022 | vérifiées (PMC) | **lu en détail** | partiellement |
| Farmaki et al. 2024 | vérifiées (Crossref) | **non lu — inaccessible** | non lu |
| Swen et al. 2023 (PREPARE) | déjà en bibliographie | — | non lu |
| Tremmel et al. 2025 | vérifiées | lu | non lu |
| Kalinin et al. 2018 | vérifiées | lu | non lu |
| Truda et Marais 2021 | vérifiées (Crossref) | lu | non lu |
| Shwartz-Ziv et Armon 2022 | vérifiées (Crossref) | lu | non lu |
| Grinsztajn et al. 2022 | vérifiées (NeurIPS) | lu | non lu |
| Niculescu-Mizil et Caruana 2005 | vérifiées | lu | non lu |
| Guo et al. 2017 | vérifiées (PMLR) | lu | non lu |
| Geifman et El-Yaniv 2017 | vérifiées (NeurIPS) | lu | non lu |
| Kapoor et Narayanan 2023 | vérifiées (Crossref) | lu | non lu |
| Walsh et al. 2021 (DOME) | à compléter | non lu | non lu |
| Collins et al. 2024 (TRIPOD+AI) | vérifiées | non lu | non lu |

**Aucune affirmation chiffrée du texte ne provient d'une référence dont le résumé n'a pas été lu.** Les chiffres employés sont : quarante-cinq jeux de données et dix mille observations (Grinsztajn, résumé lu) ; dix-sept domaines, trois cent vingt-neuf articles, huit formes de fuite (Kapoor, résumé lu) ; plus de dix mille diplotypes CYP2D6 pour quatre phénotypes, taux d'acceptation supérieur à 90 % (Haidar, texte lu).

### Points bloquants

1. **Farmaki et al. 2024 est cité sans ses conclusions.** Europe PMC limite le débit des requêtes, PubMed ne se laisse pas lire par récupération de page, et les sites de l'éditeur refusent la requête. Un marqueur `[à compléter]` est posé à la section 2.3. Deux solutions : y accéder depuis le réseau de l'université, ou retirer la phrase, la section tenant sans elle puisqu'elle repose sur Haidar.
2. **Caudle et al. 2025** : volume, pages et le chiffre cité au chapitre 1 restent à compléter ; le marqueur existait déjà dans la bibliographie.
3. **Walsh et al. 2021 (DOME)** : métadonnées à vérifier avant citation.

### Corrections à apporter à la bibliographie existante

1. **Guo et al. 2017** — remplacer « ICML 2017. arXiv:1706.04599 » par : *Proceedings of the 34th International Conference on Machine Learning*, PMLR 70:1321-1330, 2017.
2. **Geifman et El-Yaniv 2017** — remplacer « arXiv:1705.08500, 2017 » par : *Advances in Neural Information Processing Systems 30* (NeurIPS 2017). Pagination des actes à vérifier. Citer une préimpression pour un article publié contrevient à la règle déjà appliquée au cas Truda et Marais.
3. **Grinsztajn et al. 2022** — le titre publié comporte le mot *typical* : « Why do tree-based models still outperform deep learning on **typical** tabular data? », *Advances in Neural Information Processing Systems 35* (NeurIPS 2022), piste Datasets and Benchmarks. Le titre actuellement en bibliographie est celui de la préimpression.
4. **Kapoor et Narayanan 2023** — la préimpression arXiv:2207.07048 porte un titre légèrement différent de la version publiée dans *Patterns*. Citer la version publiée.

### Références à ajouter à la bibliographie

Tremmel et al. 2025 ; Kalinin et al. 2018 ; Truda et Marais 2021 ; Shwartz-Ziv et Armon 2022 ; Niculescu-Mizil et Caruana 2005 ; Kapoor et Narayanan 2023 ; Walsh et al. 2021 ; Collins et al. 2024 ; Haidar et al. 2022 ; Farmaki et al. 2024. Cawley et Talbot 2010 et Grinsztajn et al. 2022 y figurent déjà.

### Cohérence avec le reste du mémoire

- **Redites évitées** : les chiffres de prévalence des variants actionnables (chapitre 1.1) et les résultats de PREPARE (chapitre 1.1) ne sont pas répétés en 2.3, qui y renvoie. Les outils d'appel d'allèles sont nommés en 1.2 ; la section 2.2 traite leurs limites et non leur énumération.
- **Fondations apportées** : 2.5 fonde 4.7 ; 2.6 fonde 4.4 et 4.5 ; 2.7 fonde 3.6, 3.8 et 4.3 ; 2.2 fonde le codage du chapitre 3 et la validation 8.2 ; 2.1 fonde le rapport par niveau de source de 4.8.
- **Justification nouvelle apportée au chapitre 3** : le codage par phénotype plutôt que par diplotype, actuellement présenté comme une convention du projet, trouve en 2.2 un appui publié (Haidar et al., 2022). Une phrase de renvoi peut être ajoutée en section 3.2.
- **Chiffre à recalculer après le passage au corpus v15** : « 209 415 » (section 2.5) est l'effectif de développement du corpus v14.

### À lire avant la soutenance

Par ordre de probabilité d'être interrogée : Grinsztajn et al. 2022 et Shwartz-Ziv et Armon 2022 ; Guo et al. 2017 ; Haidar et al. 2022 ; Truda et Marais 2021 ; Abdullah-Koolmees et al. 2021.

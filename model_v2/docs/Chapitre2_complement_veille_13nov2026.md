# Chapitre 2 — complément de veille, 13 novembre 2026

Complète `Chapitre2_veille_biblio_5nov2026.md` sans le remplacer. Le plan en huit sections validé le 5 novembre est inchangé.

## Pourquoi ces trois références précisément

La veille du 5 novembre laissait trois manques qui touchent directement des choix faits dans PharmaGeno :

1. **§ 2.6 n'avait aucune référence de calibration postérieure à 2005**, alors que la mise à l'échelle de la température est appliquée aux trois bras de la comparaison équitable.
2. **§ 2.6 mentionnait la classification sélective sans source**, alors que six règles conditionnelles sont délibérément non étiquetées et que l'application affiche des scores — c'est un dispositif de rejet.
3. **§ 2.3 ne contenait que des candidats « non ouverts, à ne pas citer »**, donc aucune source vérifiée pour situer l'outil dans la pratique clinique.

## Références ajoutées

### Guo C, Pleiss G, Sun Y, Weinberger KQ. On Calibration of Modern Neural Networks

*Proceedings of the 34th International Conference on Machine Learning*, PMLR vol. 70, p. 1321-1330, 2017. https://proceedings.mlr.press/v70/guo17a.html — préimpression arXiv:1706.04599.

**Statut : métadonnées vérifiées sur PMLR (source officielle des actes), résumé lu. Texte intégral non lu.**

Pour la **section 2.6**. Établit que les réseaux de neurones modernes sont mal calibrés, contrairement à ceux de la décennie précédente, et introduit la mise à l'échelle de la température comme variante à un paramètre de la mise à l'échelle de Platt.

**Pertinence particulière pour ce mémoire** : l'article relie la mauvaise calibration à la **profondeur, la largeur, la décroissance des poids et le BatchNorm**. Ces quatre grandeurs sont précisément des dimensions de l'espace de recherche d'hyperparamètres du DL (`recherche_hp_dl_v4.ESPACE` : `couches`, `largeur`, `wd`, `bn`). C'est donc la justification théorique de deux décisions déjà prises : calibrer, et calibrer les trois bras de la même façon.

### Geifman Y, El-Yaniv R. Selective Classification for Deep Neural Networks

*Advances in Neural Information Processing Systems 30* (NeurIPS 2017). https://papers.neurips.cc/paper_files/paper/2017/file/4a8423d5e91fda00bb7e46540e2b0cf1-Paper.pdf — préimpression arXiv:1705.08500.

**Statut : publication NeurIPS confirmée, résumé lu, texte intégral non lu. Pagination exacte des actes à vérifier avant citation finale.**

Pour la **section 2.6**. Introduit la classification sélective pour les réseaux profonds : l'utilisateur fixe un niveau de risque acceptable, le système rejette les entrées sur lesquelles il n'est pas assez confiant, et le compromis central est risque contre couverture.

**Pertinence** : c'est le cadre théorique du choix de ne pas étiqueter les six règles conditionnelles, et de l'affichage de scores plutôt que d'une décision binaire. Le vocabulaire « risque / couverture » peut structurer la discussion du chapitre 8.

Le titre est identique entre la préimpression et les actes — pas de piège de citation ici, contrairement au cas Truda & Marais signalé le 5 novembre.

### Farmaki A, Manolopoulos E, Natsiavas P. Will Precision Medicine Meet Digital Health? A Systematic Review of Pharmacogenomics Clinical Decision Support Systems Used in Clinical Practice

*OMICS: A Journal of Integrative Biology* 2024;28(9):442-460. doi:10.1089/omi.2024.0131

**Statut : métadonnées vérifiées sur Crossref (auteurs, titre, revue, volume, numéro, pages, DOI). Résumé NON encore lu — aucune affirmation chiffrée tirée de cet article avant lecture.**

Pour la **section 2.3**. Revue systématique des systèmes d'aide à la décision pharmacogénomique effectivement employés en pratique clinique — c'est-à-dire le cadre exact dans lequel PharmaGeno doit être situé, et la source qui permettra de dire ce que l'outil fait de comparable et ce qu'il ne fait pas.

## Obstacles rencontrés, à consigner

- **Europe PMC a de nouveau limité le débit des requêtes** (deux tentatives, erreur `RATE_LIMIT_EXCEEDED`), comme le 5 novembre. Le contournement qui a fonctionné est l'API Crossref (`api.crossref.org/works/<DOI>`), qui donne auteurs, titre, revue, volume, numéro, pages et DOI de façon fiable.
- **PubMed ne se laisse pas lire directement** par récupération de page (contenu chargé par script) ; passer par Crossref ou par la page de l'éditeur.
- **Le site de l'éditeur SAGE a refusé la requête** (erreur client) pour l'article OMICS.
- Conséquence : les résumés restent à lire pour plusieurs références. **Aucune affirmation chiffrée ne sera écrite dans le chapitre 2 à partir de métadonnées seules.**

## Candidat repéré, non retenu pour l'instant

Clinical implementation of preemptive pharmacogenomics testing for personalized medicine at an academic medical center, *JAMIA* 2025;32(3):566 et suivantes (PMID 39665424, préimpression medRxiv 2024.05.06.24306958). Utile à la **section 2.3** comme exemple d'implémentation préemptive, en complément de Haidar et al. 2022 déjà retenu. Métadonnées à confirmer sur Crossref avant citation.

## État des sections au 13 novembre

| Section | Sources vérifiées disponibles | Suffisant pour rédiger ? |
| --- | --- | --- |
| 2.1 Pharmacogénomique et recommandations | Whirl-Carrillo 2021, registre des sources du projet | oui |
| 2.2 Du VCF au phénotype | documentation PharmCAT et PyPGx, travaux propres du projet | oui |
| 2.3 Aide à la décision en pratique | Haidar 2022, **Farmaki 2024** | résumés à lire d'abord |
| 2.4 Apprentissage en pharmacogénomique | Tremmel 2025, Kalinin 2018, Truda & Marais 2021 | oui |
| 2.5 Profond contre arbres sur tabulaire | Grinsztajn 2022, Shwartz-Ziv & Armon 2022 | oui |
| 2.6 Calibration et classification sélective | Niculescu-Mizil 2005, **Guo 2017**, **Geifman & El-Yaniv 2017** | oui |
| 2.7 Validation, fuite, parenté | Kapoor & Narayanan 2023, DOME, TRIPOD+AI | oui |
| 2.8 Synthèse et positionnement | — (tableau construit à partir des précédentes) | oui |

Six sections sur huit peuvent être rédigées immédiatement. La 2.3 attend la lecture de deux résumés. La 2.8 se rédige en dernier, par construction.

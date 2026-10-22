# Journal de Bord du Projet PharmaGeno : 21 octobre 2026, addendum de 19 h 15

Complète `Journal_de_Bord_21oct2026_soir.md` (rien n'est écrasé). « Mesuré » = affiché sur la machine de Mouna ou par un test explicite.

## 1. Décisions
- Règle absolue (Mouna, 18 h 32, après des semaines de rappels) : le sujet est un WEBTOOL ; le DL prend TOUT le profil génétique et prédit ; l'ÉCRAN de l'application doit le montrer. Tout travail doit se voir à l'écran de l'application ; ne plus livrer de mesures, de sauvegardes ou de scripts sans lien visible avec l'application.
- Application v8f (DL profil branché) puis v8g (v8f + encadré « Le DL en action » : profil complet, un passage, conseils pour tous les médicaments ; + « Gènes qui font changer la prédiction du DL » par médicament, analyse de sensibilité par substitution par la valeur normale). Anciens fichiers intacts.
- Sauvegardes GitHub et Drive regroupées en fin de v8g (proposé à Mouna, non contesté).

## 2. Mesures
- v8g chez Mouna : 4 scripts vérifiés (md5 6da422d4…, 03c59f33…, da331bec…, 231c2a9a…), application lancée, capture de la page de résultats (HG00101.vcf, Cardiologie) : encadré « Le DL en action » et lignes de gènes décisifs visibles. Les 3 médicaments proposés sont les mêmes qu'en v8e/v8f (aspirine, ibuprofène, pravastatine) : normal, le DL reproduit les règles.
- Tests dans mon environnement (modèle identique à celui de Mouna : mêmes chiffres de validation interne) : 33 tests de pages passés ; 7 tests du moteur passés (6 280 substitutions de gène recalculées par un chemin indépendant, 0 différence, 116 changent la prédiction ; 0 changement d'avis sur 1 066 couples en remplaçant un gène non requis).
- Ancien DL / nouveau DL : 31 différences sur 125 178 cas appris (0,025 %) ; 13,1 % de différences sur 24 532 cas « jamais vus » (non affichés, aucune règle pour juger).
- Cause du trou « non évalué » : `construire_corpus_v3.py` écarte les règles « ambiguës » (59 règles à un gène, 35 médicaments ; 38 pour métaboliseurs lents, 13 pour ultra-rapides). Sur 21 872 cas à un gène non couverts, 12 206 concernent un phénotype « normal » (probablement silence de la guideline, à vérifier source par source).
- Escitalopram et citalopram : les deux DL répondent « standard » pour CYP2C19 lent, rapide, ultra-rapide (453 profils), car leurs étiquettes ne contiennent jamais autre chose ; la couche de sécurité masque ces cas (utile).
- Simvastatine « Éviter » (SLCO1B1 fonction diminuée) conforme à CPIC 2022, Table 2, p. 1016 (autre statine ; si simvastatine justifiée, < 20 mg/jour ; recommandation forte) : https://files.cpicpgx.org/data/guideline/publication/statins/2022/publication.pdf (lecture par l'outil web, texte identique à mon fichier de règles).
- Observation à examiner : pour l'atorvastatine (profil de démonstration), l'analyse de sensibilité signale SLCO1B1 comme gène décisif alors que l'atorvastatine est proposée « standard » : à comprendre (règle ou anomalie du DL).

## 3. Erreurs à ne plus reproduire
- Les erreurs des journaux précédents.
- Livrer des mesures, scripts et sauvegardes sans faire apparaître à l'écran de l'application ce que fait le DL (cause de la colère de Mouna à 18 h 25 – 18 h 37).
- Écrire « tu as raison, le sujet est un webtool » comme si c'était une découverte : l'objectif était déjà noté. Reconnaître la faute exacte (ne pas l'avoir rendu visible), sans prétendre avoir compris seulement maintenant.
- Compter des occurrences dans un test avec un motif qui ne correspond pas au HTML (balise `</b>` intercalée) : vérifier le motif sur la page réelle.
- Renvoyer une longue commande en bloc de heredoc dans un outil quand un fichier peut être écrit directement.

## 4. Plan restant (chaque étape validée par Mouna)
1. Décision de Mouna : classement d'affichage des médicaments proposés. Aujourd'hui : ordre de confiance du DL, quasi identique entre médicaments « standard », d'où aspirine et ibuprofène en tête (aucun gène du patient ne change la prédiction). Option recommandée : placer d'abord les médicaments dont un gène non normal du patient intervient (alternatives aux médicaments à éviter), puis les autres ; à décider avec un avis clinique.
2. Décision de Mouna : utiliser les 59 règles ambiguës comme étiquettes (action la plus prudente, étiquette « sources en désaccord ») ; puis reconstruire le corpus, réentraîner, refaire le test « combinaisons cachées ».
3. Audit de couverture règle par règle (CPIC/DPWG, fichier PharmCAT `prescribing_guidance.json`), avec liens des sources.
4. Corrections de l'application : accord du verbe « 1 médicament … est à éviter » ; message quand aucun gène requis n'est lisible ; faux message « aucun médicament à éviter » ; contradiction multi-gènes « non interprété » ; mots HLA « positif / négatif » (validés v8e).
5. Sauvegarde WSL -> Windows -> GitHub -> Drive de : `modele_final_profil_v1.py`, `modeles_v8f/`, v8f (4 scripts + `templates_v8f`), v8g (4 scripts + `templates_v8g`), journaux du soir.
6. Comparaison avec PharmCAT (`~/pharmcat_test/out/HG00101.report.json`) et une étude publiée (Nguyen et al. 2024, Table 2, 3 médicaments) ; correspondance de nos 4 classes avec les 3 couleurs ; évaluation finale unique sur les 12 524 lignes ; chapitres 3 à 8 ; mail à l'encadrant (brouillon prêt, non envoyé) ; date de dépôt (vers le 12 nov., non confirmée).

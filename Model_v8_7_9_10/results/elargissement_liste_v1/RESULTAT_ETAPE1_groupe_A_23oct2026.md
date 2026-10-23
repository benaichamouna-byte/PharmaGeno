# Étape 1 : lecture des directives du groupe A (23 octobre 2026)

Méthode : les 40 entrées du groupe A (38 médicaments + 2 entrées de classe : « antidépresseurs » RNPGx, « inhibiteurs de l'HMG-CoA réductase » RNPGx) ont été lues dans les fiches de directives (guide_json, texte et résumé) et classées. Rien n'a été entraîné ; aucun modèle touché.

## Résultat
- 3 médicaments ont une vraie règle par génotype : acénocoumarol, phenprocoumone (VKORC1), flucytosine (DPYD).
- 13 médicaments : la directive DPWG dit « pas d'interaction gène-médicament » ou « aucune action nécessaire » : prasugrel, ticagrelor, amiodarone, disopyramide, quinidine, clonidine, flupenthixol, mirtazapine, moclobémide, rabéprazole, gliclazide, glimépiride, paclitaxel -> étiquette STANDARD pour toutes les valeurs du gène.
- 22 médicaments : pas de recommandation utilisable (13 G6PD CPIC « pas de recommandation », 6 AINS CYP2C9 CPIC « pas de recommandation », cisplatine/fluindione/ivacaftor à part). Aucune étiquette n'est inventée pour eux.
- 2 entrées de classe : à traiter par médicament (non faits).

## Ce que cela change vraiment
- Médicaments couverts par le corpus : 117 -> 133 (si tout est validé).
- Médicaments où le DL a une vraie réponse qui change selon le génotype : 58 -> 61 (+3). Les 13 « STANDARD partout » s'affichent en vert avec la raison, mais le DL n'y choisit pas entre plusieurs actions : ce n'est pas un gain de décision.
- Le plus gros levier restant : les 59 règles ambiguës (35 médicaments) et le groupe B (27 médicaments qui demandent de nouveaux gènes).

## Points d'attention (à lire avant validation)
- VKORC1 : codage du profil = 0 allèle rs9923231 -> 1,0 ; 1 allèle -> 0,5 ; 2 allèles (TT, -1639 AA) -> 0,0 (construire_profils_genes_v3.py ligne 93). Donc TT = 0,0 (296 profils).
- DPYD : 1 seul profil du corpus a 0,0 (comme pour le fluorouracile, valeur « hors domaine » probable). 0,5 regroupe score 1 et 1,5 (même action DPWG).
- DPWG nomme aussi un cas FENO pour la flucytosine : non codé dans le profil.
- CYP2D6 n'est pas lisible depuis un VCF : pour les 6 médicaments CYP2D6, STANDARD ne dépend pas du génotype, mais le DL reçoit quand même CYP2D6 en entrée.
- Gliclazide et glimépiride apparaissent aussi dans la directive CPIC G6PD « pas de recommandation » : aucune règle G6PD n'est ajoutée.
- « Pas d'interaction » signifie « pas d'ajustement génétique recommandé » ; ce n'est pas une preuve d'innocuité.
- Cas à décider : prasugrel/ticagrelor deviennent des alternatives affichables pour le clopidogrel.

Fichiers : regles_proposees_groupe_A_v1.csv (67 lignes de règles, 16 médicaments), groupe_A_non_utilisables_v1.csv (22 médicaments).

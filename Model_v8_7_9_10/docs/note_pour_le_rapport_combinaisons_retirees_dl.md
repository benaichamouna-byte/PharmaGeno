# Test du DL par retrait de combinaisons de gènes (à intégrer au mémoire)

## Méthode (chapitre 3)
Pour les 14 médicaments dont la règle de guideline dépend de deux gènes, des combinaisons entières (valeur du gène A, valeur du gène B) sont retirées de l'entraînement. Chaque valeur prise séparément reste vue dans d'autres combinaisons. Le DL (configuration finale : modulation FiLM, identifiant de médicament, poids de classes en racine, EVITER x2) est entraîné sans ces lignes, puis évalué sur elles. Référence : classe majoritaire du médicament dans l'entraînement ; une table de règles n'a aucune réponse pour une combinaison absente. L'ensemble final (10 % des familles) n'est pas lu. Trois tirages de combinaisons retirées (graines 100 à 102). Deux variantes, rapportées toutes les deux : A (toute combinaison éligible) et B (la classe de la combinaison retirée reste vue pour ce médicament dans l'entraînement).
Script : `scripts/test_combinaisons_retirees_dl_v1.py` (option `--classe_vue` pour B). Résultats : `results/combinaisons_retirees_dl_v1*/`.

## Résultats (chapitre 5)
- Variante B (7 médicaments) : sur les lignes où la classe majoritaire se trompe (1 087 à 1 400 lignes par tirage), le DL prédit juste dans 100 % des cas pour les cinq antidépresseurs tricycliques (CYP2C19 + CYP2D6). Pour la rosuvastatine et la sertraline, la classe majoritaire est déjà correcte sur toutes les lignes retirées ; le DL fait 92,5 %, donc moins bien que cette référence.
- Variante A (10 médicaments) : le DL échoue totalement (0 %) sur les thiopurines (azathioprine, mercaptopurine, thioguanine ; NUDT15 + TPMT) : la seule combinaison « standard » (deux gènes normaux) est retirée dans les trois tirages, donc la classe « standard » n'est jamais vue pour ces médicaments.
- Exactitude du DL sur des combinaisons vues avec des familles inconnues, mêmes médicaments : 99,7 % (A) et 99,9 % (B).

## Limites
Dix médicaments sur 14 éligibles (A), sept (B). Étiquettes issues de règles de guideline (déterministes). Un seul modèle par tirage. Profils d'entraînement du corpus (1 000 Genomes). Une combinaison retirée n'est pas une variante nouvelle : le test ne montre pas la généralisation à des allèles inconnus.

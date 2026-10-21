# Note pour le rapport : le DL « profil -> médicaments » combine-t-il des gènes jamais vus ensemble ?

Date : 21 octobre 2026. Remplace pour la partie « combinaisons » la note `note_pour_le_rapport_combinaisons_retirees_dl.md`, qui reste en place (rien n'est supprimé) et doit être citée avec la réserve du paragraphe 1. Toutes les valeurs ci-dessous sont celles affichées sur la machine de Mouna (WSL, 3 tirages).

## 1. Correction de l'ancien test
`test_combinaisons_retirees_dl_v1.py` cachait une combinaison de gènes pour un seul médicament. Mesuré le 21 octobre avec la même fonction de tirage : 60 combinaisons cachées sur 60 (variante A) et 51 sur 51 (variante B) restaient visibles à l'entraînement sous un autre médicament. Ses résultats (« 100 % sur les tricycliques ») ne prouvent donc pas la combinaison de gènes ; ils montrent un transfert entre médicaments qui partagent les mêmes gènes.

## 2. Méthode du test corrigé (`test_combinaisons_cachees_profil_v1.py`, md5 4f2e1629d7679bd7f98c7dbba2d57bae)
- Modèle testé : DL « profil -> médicaments » (`train_dl_profil_v1.py`, md5 41234846692531ad23eb5b0d36e4b2f4) : entrée = profil génétique seul, sortie = un conseil par médicament (113 x 4 classes).
- Pour chacune des 8 paires de gènes dont dépendent des médicaments à deux gènes (CYP2C19+CYP2D6, NUDT15+TPMT, HLA-A*31:01+HLA-B*15:02, CYP2C9+SLCO1B1, CYP2B6+CYP2D6, CYP2C9+HLA-B*15:02, ABCG2+SLCO1B1, CYP2B6+CYP2C19), on cache des combinaisons (valeur du gène A, valeur du gène B) : tous les patients qui les portent, et leurs familles, sont retirés de l'entraînement pour TOUS les médicaments.
- Chaque valeur de gène prise seule reste vue dans d'autres combinaisons (« lettres » connues, « mot » inconnu). Combinaisons ni trop rares (< 8 profils) ni trop courantes (> 60) ; au plus 25 % des profils cachés ; ensemble final de 12 524 lignes jamais lu.
- Contrôle intégré dans le script : nombre de combinaisons cachées encore présentes à l'entraînement = 0 (affiché : 0 aux 3 tirages).
- Mesure principale : exactitude sur les cases « informatives » (étiquette différente de la classe majoritaire du médicament à l'entraînement), séparées en classe déjà vue à l'entraînement pour ce médicament / classe jamais vue (aucun modèle ne peut répondre).
- Réglages du DL fixés à l'avance, identiques à `train_dl_profil_v1.py`, non ajustés sur ces résultats. 3 tirages de combinaisons, 1 modèle par tirage.

## 3. Résultats (valeurs affichées)
| Tirage | Profils cachés | Cases de test | Informatives | Exactitude informatives | Informatives, classe vue | Exactitude (classe vue) | Classe jamais vue | EVITER détectés / réels |
|---|---|---|---|---|---|---|---|---|
| 1 | 305 | 268 | 87 | 0,5747 | 73 | 0,6849 | 14 | 50 / 64 |
| 2 | 309 | 440 | 367 | 0,8529 | 353 | 0,8867 | 14 | 313 / 344 |
| 3 | 299 | 173 | 50 | 1,0000 | 50 | 1,0000 | 0 | 50 / 50 |
- Moyennes sur les 3 tirages : exactitude sur les informatives 0,8092 ; informatives de classe vue 0,8572. Référence « majoritaire » : 0 sur les informatives par construction. Même DL, mêmes médicaments, combinaisons VUES (validation interne) : 0,999.
- Par médicament (moyenne des tirages où il a des cases de test ; exactitude du DL / de la classe majoritaire) : amitriptyline 1,000 / 0,000 ; clomipramine 0,985 / 0,000 ; doxépine 0,980 / 0,000 ; imipramine 0,975 / 0,000 ; trimipramine 0,975 / 0,000 ; rosuvastatine 0,804 / 0,804 (informatives de classe vue : 0,000) ; sertraline 0,820 / 0,820 (28 cases informatives de classe jamais vue au total) ; méthadone 1,000 / 1,000 ; fluvastatine 1,000 / 1,000.

## 4. Lecture
- Pour les 5 antidépresseurs tricycliques (paire CYP2C19+CYP2D6), le DL répond correctement à des combinaisons absentes de l'entraînement pour tous les médicaments (0,975 à 1,000 ; la classe majoritaire donne 0). C'est le seul cas où le test montre un apprentissage de la combinaison.
- Rosuvastatine : pas mieux que la classe majoritaire ; aucune case informative de classe vue n'est trouvée (0,000). Sertraline : les cas informatifs portent sur une classe jamais vue à l'entraînement ; méthadone et fluvastatine : cas triviaux (classe majoritaire).
- Écart avec les combinaisons vues (0,999) : cacher la combinaison coûte de la performance (0,8572 sur les informatives de classe vue).

## 5. Limites à écrire
- Couverture partielle : sur les 3 tirages, NUDT15+TPMT (thiopurines), carbamazépine et phénytoïne n'ont aucune case de test dans le résumé par médicament (aucune combinaison de ces paires n'a été cachée avec les critères choisis) ; elles ne sont donc pas évaluées ici.
- Petits effectifs (50 à 367 cases informatives par tirage) et variabilité forte entre tirages (0,5747 à 1,0000) ; 3 tirages seulement, aucun test statistique, un seul modèle par tirage.
- Les étiquettes des cas à plusieurs gènes sont une convention du moteur de règles (journal du 20 oct.) ; l'accord avec ces étiquettes n'est pas une validation clinique indépendante.
- Le moteur de règles CPIC peut probablement répondre lui-même à ces combinaisons (à vérifier) : l'intérêt du résultat est scientifique (le DL déduit la combinaison sans la règle), pas de couvrir des cas que les règles ne couvriraient pas. Une « table de règles » construite sur les mêmes données d'entraînement ne couvre pas une combinaison cachée.
- La sélection des combinaisons (min 8, max 60 profils, plafond 25 %) est un choix de protocole fixé à l'avance ; un premier essai sans plafond, écarté, cachait 1 187 profils sur environ 1 241 (mécanique seulement, aucun score retenu).

## 6. Fichiers
Scripts : `scripts/train_dl_profil_v1.py`, `scripts/test_combinaisons_cachees_profil_v1.py`, `scripts/tableau_profil_medicaments_v1.py`. Résultats chez Mouna : `results/dl_profil_v1/`, `results/combinaisons_cachees_profil_v1/` (`resume_par_tirage.csv`, `par_medicament.csv`, `resume.json`).

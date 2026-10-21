# Journal de Bord du Projet PharmaGeno : 21 octobre 2026, addendum de 15 h 40

Complète `Journal_de_Bord_21oct2026_apres-midi.md` (rien n'est écrasé). « Mesuré » = affiché par un script ; « validé » = validé par Mouna.

## 1. Mesures de Mouna sur sa machine (DL « profil -> médicaments », `train_dl_profil_v1.py`, somme de contrôle md5 41234846692531ad23eb5b0d36e4b2f4)
- Entrée : profil génétique seul (33 variables) ; sortie : 113 médicaments x 4 conseils ; 125 178 cases étiquetées sur 155 827 ; cases sans étiquette ignorées dans la perte.
- Protocole identique au DL actuel (mêmes plis, graine 42, ensemble final de 12 524 lignes non lu) ; 5 graines x 5 plis, 266 s au total chez elle.
- Résultat (moyenne sur les graines, écart-type entre graines) : F1 macro 0,9985 +/- 0,0002 ; EVITER manqués (CER strict) 0,0015 +/- 0,0002 ; précision EVITER 0,9970 ; exactitude 0,9995 ; ECE 0,0058.
- Référence du journal du 19 oct. (DL actuel : FiLM, identifiant de médicament, poids racine, EVITER x2, 5 graines) : F1 macro 0,9980 +/- 0,0010 ; EVITER manqués 0,0029 +/- 0,0010 ; précision EVITER 0,992 +/- 0,005.
- Lecture : le nouveau DL fait au moins aussi bien. Écarts petits ; aucun test statistique fait ; réglages du nouveau modèle fixés à l'avance, non ajustés. Les étiquettes sont les règles CPIC : ce score proche du maximum ne prouve pas que le DL combine mieux que les règles.

## 2. Faille découverte dans l'ancien test des combinaisons (à corriger dans la note du rapport)
- `test_combinaisons_retirees_dl_v1.py` cachait une combinaison de gènes pour UN médicament. Mesuré le 21 oct. avec la même fonction de tirage (3 tirages) : 60 combinaisons sur 60 (variante A) et 51 sur 51 (variante B) restaient visibles à l'entraînement sous un AUTRE médicament.
- Conséquence : « 100 % sur les tricycliques » ne prouve PAS que le DL combine des gènes jamais vus ensemble ; cela montre seulement un transfert entre médicaments qui partagent les gènes. Cette conclusion est retirée. Le 0 % sur les thiopurines reste valable comme limite de données (la classe n'était jamais vue à l'entraînement).
- Les fichiers de résultats de l'ancien test restent en place (rien n'est supprimé) ; ils doivent être cités avec cette réserve.

## 3. Nouveau test corrigé : `test_combinaisons_cachees_profil_v1.py` (md5 4f2e1629d7679bd7f98c7dbba2d57bae)
- On cache le PROFIL : tous les patients portant la combinaison cachée (et leurs familles) sont retirés de l'entraînement pour tous les médicaments ; une vérification intégrée contrôle qu'aucune combinaison cachée n'est présente à l'entraînement. Chaque valeur de gène prise seule reste vue ailleurs.
- Plafond de 25 % des profils cachés (sans plafond, le premier essai cachait 1 187 profils sur ~1 241 et laissait 54 profils pour apprendre : essai écarté, mécanique seulement).
- Résultats séparés : classe déjà vue à l'entraînement pour ce médicament / classe jamais vue (limite de données, aucun modèle ne peut répondre).
- Essai de mécanique dans mon environnement (2 époques, 1 tirage) : fonctionne, contrôle anti-fuite passé ; aucun score retenu.

## 4. Erreurs à ne plus reproduire
- Conclure d'un test de combinaisons sans vérifier que la combinaison n'est pas visible ailleurs dans l'entraînement (ici via les autres médicaments). Toujours ajouter un contrôle explicite de non-présence.
- Envoyer un script par carte de fichier : le zip n'a pas été téléchargé. Utiliser le terminal (heredoc) avec somme de contrôle md5.
- Tester sans plafond : cacher la majorité des patients rend le test inutilisable.

## 5. Plan
1. Mouna lance `test_combinaisons_cachees_profil_v1.py` ; je lis les résultats tels quels (y compris négatifs).
2. Corriger la note du rapport (méthode, faille, nouveaux résultats) ; défaut HLA-B*58:01 ; trou escitalopram (CYP2C19 lent/ultra-rapide sans conseil, constaté ; décision de Mouna).
3. Application v8f branchée sur le DL profil ; sortie 1 à 3 médicaments par spécialité.
4. Comparaison : Nguyen et al. 2024 (Front Pharmacol 15:1500235, Table 2) pour 3 médicaments ; PharmCAT ; évaluation finale unique ; chapitres 3 à 8.
5. Sauvegarde WSL -> Windows -> GitHub -> Drive de tous les fichiers du 21 oct. (après-midi) : tableau, `train_dl_profil_v1.py` et résultats, test corrigé, journaux.

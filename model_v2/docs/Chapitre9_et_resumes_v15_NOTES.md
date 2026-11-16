# Chapitre 9 et résumés v15 — notes

**Ce document ne fait pas partie du mémoire.** Il accompagne `Chapitre9_v15_MEMOIRE.md` (remplace la version précédente du même nom) et `Resumes_v15_MEMOIRE.md` (remplace le résumé et l'abstract de `Memoire_texte_v6.md`).

## 1. Provenance de chaque chiffre ajouté ou changé
| Chiffre | Source |
|---|---|
| Ensemble final : F1 0,9940 [0,9839 ; 0,9992] ; 10/816 EVITER manqués ; XGB 3 ; RF 0,9300 ; DL−XGB −0,0049 [−0,0152 ; +0,0007] | `Resultat_evaluation_finale_138_15nov2026.md`, § 6.7 du chapitre 6 v15 |
| Abstention finale : 263 lignes, 8/10 EVITER écartés ; 10 erreurs HG03684 à confiance ≥ 0,998 ; 26/35 erreurs sur HG03684 | idem |
| PharmCAT 95,9 % de 3 357 ; CPIC 99,1 % ; 99,73 % de 2 600 ; 136 lignes | chapitre 8 v15, § 8.3 et 8.4 |
| Réseau ≠ règle 10/6 322 (0,2 %) ; 50/439 (11,4 %) | chapitre 8 v15, § 8.4 et 8.5 |
| IWPC v15 post hoc : 0,559 / 0,828 ; 75 % / 32 % ; \*1/\*2 −16 % (0,837) | chapitre 7 v15, § 7.7 |
| 48 des 76 erreurs sur azathioprine, rosuvastatine, sertraline, fluvastatine | chapitre 6 v15, § 6.1 |
| 8 couples refaits v15 : 23 tests identiques | `Resultat_11_patients_et_8_couples_v15_15nov2026.md` |
| Résumés : 1 379 profils, 234 632 lignes, 189 médicaments | recomptés ce jour dans `phenotype_drug_dataset_v15.csv` |
| Résumés : F1 0,9982 (0,99820) | chapitre 6 v15, § 6.1 |
| Abstract : 18 gènes PyPGx, exécution locale | chapitre 5 v15 |

## 2. Ce qui a changé dans le chapitre 9
- 9.1 : ensemble final ajouté au 1er constat ; 95,9 % / 99,73 % ; règle v15 sur IWPC.
- RQ1 : le second marqueur est levé (répartition des erreurs v15 disponible au § 6.1) ; **RQ1 dit maintenant franchement qu'aucun modèle « un seul gène » n'a été fait** : la question reste sans réponse chiffrée. Le marqueur de l'audit de déterminisme reste.
- RQ2 : paragraphe sur l'ensemble final.
- RQ3 : phrase « la moitié des EVITER manqués » (chiffre v14) remplacée par une formulation sans nombre, avec renvoi au § 6.3 ; abstention sur l'ensemble final ajoutée.
- RQ5 : 0,2 % / 11,4 % ; HG03684.
- RQ6 : 95,9 % et causes réelles (formulation/structure ; codage CYP2C9 ; NUDT15).
- RQ7 : v14 → v15, analyse post hoc.
- 9.3 : marqueur des 8 couples levé ; IWPC non indépendant pour la règle v15.
- 9.4 : renvois de sections corrigés (6.9, 7.8) ; **point 3 réécrit** (défauts corrigés en v15, perte d'indépendance, défaut CYP2C9 restant) ; point 5 : 0,2 / 11,4 % + HG03684.
- 9.5 : « Corrections de règles identifiées » (faites) remplacé par « Codage de CYP2C9 par diplotype » et « Contrôle de domaine sur le profil complet ».
- Conclusion : ensemble final mentionné.

## 3. Résumés
- Français : **191 mots**, anglais : **179 mots** (limite ISBST : 200). 5 mots-clés chacun.
- Le résumé v6 citait 97,8 %, 0,830 et « 138 profils non évalués » : tout est remplacé.

## 4. Marqueurs restants
- Chapitre 9 : audit de déterminisme (RQ1) ; causes des désaccords GeT-RM (point 4).

## 5. À vérifier ailleurs (renvois)
- Chapitre 1 : résumé et § 1.3 / 1.9 parlent-ils encore du corpus v14 ? (tâche 9 de la liste : renvois).

## 6. Sauvegarde
WSL → Windows → GitHub → Drive (Docs › DOCs Memoire › docs).

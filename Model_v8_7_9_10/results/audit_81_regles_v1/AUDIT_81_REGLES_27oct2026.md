# Audit des 81 règles ambiguës — 27 octobre 2026

Méthode : texte publié complet de chaque règle (fiches ClinPGx/PharmGKB des directives CPIC et DPWG), classé par type de formulation. Aucun modèle touché. Fichier détaillé : audit_81_regles_texte_complet.csv (texte complet + liens).

## Résultat : 81 règles = 6 types
| Type | Règles | Ce que dit le texte | Proposition (à valider) |
|---|---|---|---|
| 1 Éviter d'abord | 36 (32 mono + 4 multi) | « Avoid… / choisir une alternative » ; dose réduite seulement si le médicament est indispensable | EVITER |
| 2 Dose d'abord | 20 (11 + 9) | « Prescrire ≤ X mg… ; si plus nécessaire, alternative » (statines, AINS PM, métoprolol) | ADAPTER_DOSE |
| 3 Deux options au choix | 14 (9 + 5) | « dose réduite OU alternative » sur le même plan | A DECIDER |
| 4 Dépend d'autre chose | 2 (mavacamten, quétiapine) | dépend de la co-médication / de l'indication | EXCLURE |
| 5 Dépend du score d'activité | 3 (méloxicam, piroxicam, ténoxicam, CYP2C9 intermédiaire) | AS 1,5 = dose standard ; AS 1,0 = dose réduite ou alternative (API CPIC vérifiée) | recoder CYP2C9 |
| 6 Standard d'abord | 6 (2 + 4) | « dose standard ; changer seulement si pas de réponse » | STANDARD |

## Découverte importante (vérifiée)
CPIC (guideline AINS, id 110058) distingue pour CYP2C9 intermédiaire : AS 1,5 = dose standard ; AS 1,0 = dose réduite ou alternative, pour les 7 AINS (célécoxib, flurbiprofène, ibuprofène, lornoxicam, méloxicam, piroxicam, ténoxicam).
Le codage du projet donne la même valeur 0,5 aux deux. Sur les 1 379 profils : 364 CYP2C9 intermédiaires = 218 AS 1,5 + 146 AS 1,0 (diplotypes PyPGx + valeurs d'activité de l'API CPIC des allèles).
Conséquence : les règles AINS actuelles (célécoxib, flurbiprofène, ibuprofène, lornoxicam = STANDARD pour 0,5) sont fausses pour les 146 patients AS 1,0.
A faire : recoder CYP2C9 avec le score d'activité, puis vérifier tous les autres gènes dont une classe regroupe plusieurs scores (warfarine, phénytoïne, siponimod…).
Non vérifié : les autres médicaments CYP2C9 intermédiaire (warfarine DPWG, phénytoïne, siponimod, gliclazide, glimépiride).

## Vérification étendue CYP2C9 (27 oct., API CPIC /recommendation, 78 lignes, 10 médicaments ; résumé de l'API, à recontrôler ligne à ligne avant corpus v9)
- 1,0 ≠ 1,5 (CPIC) : les 7 AINS (célécoxib 140587, lornoxicam 20890, ténoxicam 37790, méloxicam 41493, flurbiprofène 4502, ibuprofène 5640, piroxicam 8356) ; phénytoïne et fosphénytoïne (si HLA-B*15:02 négatif ou non rendu).
- 1,0 = 1,5 : fluvastatine.
- DPWG (fichiers lus : phénytoïne, siponimod, warfarine) : une seule classe intermédiaire, même action pour tout CYP2C9 intermédiaire → pas de contradiction avec le codage actuel.
- Pas encore vérifié : les autres gènes dont une classe regroupe plusieurs scores (DPYD, TPMT, NUDT15, SLCO1B1, UGT1A1…).

## Corpus v9 construit le 27 oct. (voir Journal_de_Bord_27oct2026.md)
157 809 lignes ; 5 224 nouvelles lignes ; 589 étiquettes corrigées ; AINS conformes à CPIC. Entraînement non refait.

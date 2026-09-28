# Audit de resolution des conflits de labels

Paires gene-medicament auditees : **309**
Lignes supprimees au total : **174**

## Procedure

Trois passes successives ont ete appliquees aux paires gene-medicament portant des actions contradictoires :

| Passe | Methode | Paires resolues |
|---|---|---|
| 1 | Recherche de guideline CPIC par paire | 58 |
| 2 | Recherche elargie, sources multiples | 111 |
| 3 | Suppression des lignes invalides | 75 |

## Etat final

| Statut | Paires | Interpretation |
|---|---|---|
| aucune_guideline | 150 | Aucune guideline CPIC identifiee pour cette paire |
| texte_sans_signal | 78 | Guideline trouvee mais aucune action extractible du texte |
| coherent_apres_nettoyage | 75 | Coherence retablie par suppression des lignes invalides |
| conflit_persiste_niveau3 | 6 | Actions multiples legitimes selon le phenotype — non reductible a une action unique |

## Conflits persistants — analyse

6 paires conservent plusieurs actions apres les trois passes. 
Ces cas ne constituent pas des erreurs de donnees : l action clinique recommandee 
depend du phenotype precis du patient, et non uniquement de la paire gene-medicament.

| Gene | Medicament | Actions | Justification clinique |
|---|---|---|---|
| CYP2C19 | mavacamten | ['ADAPTER_DOSE', 'EVITER'] | Guideline recente, recommandations variables selon la source. |
| CYP2C19 | voriconazole | ['ADAPTER_DOSE', 'EVITER', 'SURVEILLER'] | Ultrarapid : risque d echec therapeutique. Poor : risque de toxicite. Actions opposees. |
| CYP2C9 | fluvastatin | ['ADAPTER_DOSE', 'EVITER'] | Selon le degre de reduction d activite : dose reduite ou alternative. |
| CYP2D6 | tamoxifen | ['ADAPTER_DOSE', 'EVITER'] | Poor Metabolizer : alternative recommandee. Intermediate : surveillance ou dose ajustee. |
| CYP3A5 | tacrolimus | ['ADAPTER_DOSE', 'SURVEILLER'] | Expresseur : augmentation de dose requise. Non-expresseur : dose standard. |
| SLCO1B1 | fluvastatin | ['ADAPTER_DOSE', 'EVITER'] | Fonction de transport reduite : risque de myopathie variable selon le genotype. |

## Consequence methodologique

L existence de ces conflits legitimes justifie la formulation du probleme adoptee dans ce travail. 
Une table de correspondance gene -> action serait insuffisante : la meme paire gene-medicament 
appelle des actions differentes selon le phenotype. Le modele doit donc apprendre une fonction 
de la forme (profil genetique complet, medicament) -> action, ce qui correspond a l architecture 
dual-branch retenue.

## Tracabilite

Le fichier `conflict_audit.csv` conserve pour chaque paire le statut obtenu a chacune des trois passes 
ainsi que la source utilisee, permettant de retracer l origine de toute decision de label.
# Substitution des chiffres v14 → v15 — inventaire de travail

**Ce document ne fait pas partie du mémoire.** C'est une liste de contrôle pour la journée de substitution.

## Règle d'ordre, à respecter

Les chapitres se citent les uns les autres. Substituer dans le désordre produit des contradictions internes. **Ordre impératif :**

1. **Chapitre 3** — effectifs du corpus. Tout le reste en dépend.
2. **Chapitre 6** — résultats de l'apprentissage.
3. **Chapitre 8** — validation externe, après régénération de l'application.
4. **Chapitre 9** — ne contient aucun chiffre propre : il reprend ceux des chapitres 3, 6, 7 et 8.
5. **Résumé et abstract** — reprennent ceux des chapitres 3, 6, 7 et 8.
6. **Chapitre 1** (section 1.3) — reprend les effectifs du chapitre 3.

Un chiffre modifié au chapitre 6 doit l'être le même jour aux chapitres 9, 1 et dans le résumé. Ne pas s'arrêter entre les deux.

---

## A. Chapitre 3 — effectifs du corpus

Source des nouvelles valeurs : `Journal_de_Bord_12nov2026_regles_v15.md` § 4, et le corpus lui-même.

| Emplacement | Valeur v14 | Valeur v15 | État |
| --- | --- | --- | --- |
| Titre du chapitre | « corpus v14 » | « corpus v15 » | à changer partout |
| Tableau 3.1, lignes | 232 664 | **234 632** | connu |
| Tableau 3.1, médicaments | 189 | **189** | inchangé |
| Tableau 3.1, profils | 1 379 | **1 379** | inchangé |
| Tableau 3.1, lignes par profil | min 116, médiane 169, max 178 | à recalculer | **à mesurer** |
| Tableau 3.2, STANDARD | 199 133 (85,59 %) | **201 273 (85,78 %)** | connu |
| Tableau 3.2, ADAPTER_DOSE | 20 426 (8,78 %) | **20 272** | connu, % à recalculer |
| Tableau 3.2, EVITER | 8 049 (3,46 %) | **8 031** | connu, % à recalculer |
| Tableau 3.2, SURVEILLER | 5 056 (2,17 %) | **5 056** | inchangé, % à recalculer |
| Couples possibles | 260 631 | **260 631** | inchangé (1 379 × 189) |
| Couples sans ligne | 27 967 | **25 999** | = 260 631 − 234 632 |
| Lignes de warfarine | 394 | à recalculer | **à mesurer** — fortement modifié par la règle VKORC1 |
| Lignes d'abacavir | 508 | 508 | inchangé a priori, à vérifier |
| Niveaux de confiance | 144 008 haute / 88 656 moyenne | à recalculer | **à mesurer** |
| Nombre de règles par ligne | 217 807 une / 14 857 deux | à recalculer | **à mesurer** — augmente avec les règles multi-gènes |
| § 3.3, règles mono-gène | 704 | **709** | connu |
| § 3.3, règles multi-gènes | 97 | **124** | connu |
| § 3.3, paires de gènes (tableau 3.3) | 5 paires, 6 médicaments | à vérifier | **à mesurer** — la grille thiopurines ajoute TPMT × NUDT15 |
| § 3.4, SHA-256 du corpus | b876bb469e562d6e… | **68b564ce265728b6…** | connu |
| § 3.4, SHA des tables de règles | mono v14 39a73689…, multi v13 30eb3562… | **9d551254…** et **1cb99ff6…** | connu |
| § 3.6, ensemble final | 138 profils, 23 249 lignes | 138 profils, à recalculer | **à mesurer** |
| § 3.6, développement | 1 241 profils, 209 415 lignes | 1 241 profils, à recalculer | **à mesurer** |
| Tableau 3.4 | reprend les valeurs ci-dessus | idem | après les précédentes |
| Figure 3.1 | répartition des classes v14 | à régénérer | **à refaire** |

**Commandes pour les valeurs à mesurer** — à lancer demain, le corpus v15 étant déjà construit :

```bash
cd /home/mouna/projet_memoire/Model_v8_7_9_10
python3 - <<'PY'
import pandas as pd
d = pd.read_csv('data/corpus_v15/phenotype_drug_dataset_v15.csv')
print("lignes", len(d))
print(d['action'].value_counts())
print((d['action'].value_counts(normalize=True)*100).round(2))
g = d.groupby('profil_id').size() if 'profil_id' in d else d.groupby(d.columns[0]).size()
print("lignes par profil : min", g.min(), "mediane", int(g.median()), "max", g.max())
print("warfarine", (d['medicament']=='warfarin').sum(), (d['medicament']=='warfarine').sum())
print("abacavir", (d['medicament']=='abacavir').sum())
for c in ('niveau_confiance','confiance','n_regles','nb_regles'):
    if c in d: print(c, d[c].value_counts().to_dict())
PY
```

Les noms de colonnes sont à adapter : la commande affiche ce qu'elle trouve.

---

## B. Chapitre 4 — méthodes

| Emplacement | Valeur v14 | Changement |
| --- | --- | --- |
| § 4.3, « sur le corpus v14 : la configuration 35 est reprise telle quelle » | — | à réécrire : mentionner la v15 et renvoyer à l'amendement 2 |
| § 4.5, tableau 4.1, seuils d'abstention | 0,9895 / 0,9965 / 0,9988 / 0,9995 | **à recalculer** sur les prédictions hors-pli v15 |
| § 4.5, AUROC 0,870 ; 71,6 % ; 46,6 sur 60,2 | — | reprend le chapitre 6 |
| § 4.9, température T = 0,2328 | — | **à recalculer** si le modèle final est réentraîné |
| § 4.9, 1 116 profils, 125 de validation interne, 79 époques | — | **à recalculer** si réentraînement du modèle final |
| § 4.11, tableau 4.2 | reprend les valeurs ci-dessus | après les précédentes |
| § 4.2, 1 860 340 paramètres | — | **inchangé** : dépend de l'architecture, pas des données |

---

## C. Chapitre 6 — résultats

Source : les fichiers d'analyse produits par l'étape 7, `comparaison_equitable_v15_v1` et `_v2`.

| Emplacement | Valeur v14 | Où lire la valeur v15 |
| --- | --- | --- |
| Tableau 6.1, les dix mesures | F1 0,9979 ± 0,0012, etc. | sorties de `dl_imbrique_v15` |
| § 6.1, F1 macro par pli | 0,9979 / 0,9989 / 0,9992 / 0,9961 / 0,9972 | idem |
| § 6.1, arrêt anticipé | 83,8 époques (± 17,8) | idem |
| § 6.1, erreurs | 113,0 sur 209 415 | idem |
| § 6.1, EVITER manqués | 60,2 sur 7 227 (0,83 %) | idem — **le dénominateur 7 227 change aussi** |
| § 6.1, faux EVITER | 8,4 | idem |
| § 6.1, erreurs par médicament | rosuvastatine 16,0, sertraline 16,0, azathioprine 13,8, fluvastatine 11,6, méloxicam 9,6, mercaptopurine 5,6, thioguanine 5,6 | idem — **la liste elle-même peut changer**, les règles de la mercaptopurine et de la thioguanine ayant été corrigées |
| § 6.1, F1 par source | CPIC 0,9984, DPWG 0,9923, etc. | idem |
| § 6.1, comparaison au corpus v13 | — | à remplacer par une comparaison au v14, ou à supprimer |
| § 6.2, température moyenne 0,24 (0,16 à 0,31) | — | idem |
| § 6.3, tableau 6.2 entier | 5 lignes de seuils | à recalculer |
| § 6.3, AUROC 0,870 ± 0,025 ; 71,6 % ; 81,4 % | — | idem |
| § 6.3, taux d'erreur par niveau de confiance | 0,00071 / 0,00027 / 0,00232 / 0,00042 | idem |
| § 6.4, tableau 6.3, réseau de choix | 4 mesures | **seulement si le réseau de choix est réentraîné** — à décider |
| § 6.5, tableau 6.4, les quatre modèles | toutes les valeurs | `comparaison_equitable_v15_v2` |
| § 6.5, les trois différences et leurs intervalles | −0,00265, +0,00343, +0,00608 | idem |
| § 6.5, écart sur les EVITER manqués | 47,0 [22,2 ; 76,8] | idem |
| § 6.5, phrase de conclusion | « XGBoost reproduit les règles mieux que le réseau » | **à réécrire si le classement change** |
| Figures 6.1 et 6.2 | — | **à régénérer** |
| § 6.6, tableau 6.5, 8 couples | — | inchangé (modèles v8, marqueur déjà posé) |
| § 6.7, résultats négatifs | AUROC 0,774 / 0,817 / 0,781 | inchangé sauf réexécution |
| § 6.8, synthèse | reprend tout | en dernier |

**Point de vigilance** : si le classement des modèles change avec le v15, ce n'est pas une substitution de chiffres mais une réécriture — § 6.5, § 6.8, RQ2 du chapitre 9, résumé et abstract.

---

## D. Chapitre 7 — warfarine

**Aucun changement.** Les 5 774 patients, le rapport 0,830 [0,804 ; 0,857], les R² de 0,294 et 0,048 portent sur les données de l'IWPC, extérieures au corpus.

**Une seule chose à vérifier** : le § 7.2 dit que la directive DPWG fondée sur VKORC1 est absente du corpus et que c'est « une omission du corpus ». **Ce n'est plus vrai en v15**, où elle a été ajoutée. Le tableau 7.2 et le texte des § 7.2 et 7.6 doivent être réécrits : l'omission devient une correction apportée, et la limite se reformule.

C'est le changement de texte le plus important du chapitre 7, et il est facile à oublier puisqu'aucun chiffre ne bouge.

---

## E. Chapitre 8 — validation externe

Dépend de la régénération de l'application sur les modèles v15.

| Emplacement | Valeur v14 | Changement |
| --- | --- | --- |
| § 8.2, tableau 8.2, concordance GeT-RM | 65/65, 61/61, 63/66… | **inchangé** : ne dépend que du parseur |
| § 8.3, 97,8 % sur 3 534 lignes, 79 non retrouvées | — | **à refaire** — devrait s'améliorer, trois des défauts de règles étant corrigés |
| § 8.3, 98,0 % / 96,4 % selon la parenté | — | à refaire |
| § 8.3, liste des trois défauts de règles | thiopurines, CYP2C9, SLCO1B1 | **à réécrire** : corrigés en v15 |
| § 8.4, 2 598 sur 2 600 (99,92 %), 6 sur 6 172 | — | à refaire |
| § 8.5, tableau 8.3, 11 patients | 41/42, 36/36, 34+1+1 | à refaire |
| § 8.5, 8,0 % sur profils partiels (35 sur 437) | — | à refaire |
| § 8.7, NA06991 | tableau 8.5 et trois figures | **à refaire** — les captures aussi |
| Figures 8.1 et 8.2 | — | à régénérer |

---

## F. Chapitre 9 — discussion

Aucun chiffre propre. La table de correspondance complète est dans `Chapitre9_NOTES.md` § 1. Substituer après les chapitres 3, 6 et 8.

**Attention particulière** : le § 9.4 point 3 énumère quatre défauts de règles « non tous corrigés dans la version évaluée ». En v15, les quatre sont corrigés. Ce paragraphe doit être réécrit en profondeur, et c'est une bonne nouvelle à faire valoir : la validation externe a identifié les défauts, et ils ont été corrigés.

---

## G. Résumé et abstract

Quatre chiffres, de façon synchrone dans les deux langues : F1 macro 0,9979 ; 0,83 % ; 0,9994 et 0,9968 ; 232 664 lignes.

**Les chiffres 104, 97,8 % et 5 774 changent en partie** : 97,8 % est à refaire (chapitre 8), 104 et 5 774 sont fixes.

Après substitution, **recompter les mots** : le résumé français est à exactement 200.

---

## H. Ce qui ne change nulle part

- Les 1 379 profils, les 189 médicaments, les 138 profils de l'ensemble final, les 1 241 de développement.
- Les 34 colonnes d'entrée, les 20 variables génétiques, les 14 indicateurs.
- Les 1 860 340 paramètres du réseau.
- Tout le chapitre 7 sauf le texte sur VKORC1.
- Le chapitre 2 et le chapitre 5, sauf les captures d'écran.
- La concordance avec GeT-RM.

---

## I. Ordre de travail proposé pour demain

1. Lire `TERMINE` dans le journal, vérifier qu'aucune étape n'a échoué.
2. Lancer les mesures du bloc A sur le corpus v15 (dix minutes).
3. Substituer le chapitre 3, puis régénérer la figure 3.1.
4. Lire les fichiers d'analyse de l'étape 7 — **c'est le premier moment où les résultats se lisent**.
5. Substituer le chapitre 6, régénérer les figures 6.1 et 6.2.
6. Régénérer l'application sur les modèles v15, relancer les tests T1 à T68.
7. Refaire la comparaison sur les 104 personnes, substituer le chapitre 8.
8. Réécrire les passages de texte signalés : § 7.2 et 7.6 (VKORC1), § 8.3 (défauts corrigés), § 9.4 point 3.
9. Substituer le chapitre 9, le résumé et l'abstract, la section 1.3.
10. Recompter les mots du résumé.

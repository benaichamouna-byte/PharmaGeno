## Chapitre 7 : Validation externe sur patients réels : la règle de la warfarine

Les étiquettes du corpus viennent d'un moteur de règles (chapitre 3) : les scores du chapitre 6 mesurent l'accord du réseau avec ces règles, non la justesse clinique de ses avis. Ce chapitre confronte une de ces règles, celle de la warfarine, à des patients réels dont la dose d'entretien stable est connue. C'est la seule validation de ce type du mémoire : elle porte sur une molécule, non sur les 189 médicaments, et elle valide la règle que le réseau reproduit, non le réseau lui-même.

Le chapitre est placé avant la validation sur profil complet (chapitre 8) parce qu'il répond à une question plus fondamentale : avant de vérifier que l'application restitue fidèlement les directives, il faut savoir si une règle tirée de ces directives a un sens chez de vrais patients.

### 7.1 Données

Le jeu de données est le fichier « Ethnicity Data Set 2009 » de l'International Warfarin Pharmacogenetics Consortium (IWPC ; Klein et al., 2009), diffusé par ClinPGx sous l'identifiant PS215192 : 6 922 sujets. Le fichier « Combined Data Set 2008 » (5 700 sujets) y est inclus en totalité (5 700 identifiants sur 5 700 retrouvés) ; il n'a pas été utilisé, pour ne pas compter deux fois les mêmes patients. La grandeur étudiée est la dose d'entretien de warfarine en mg par semaine, analysée en logarithme, de sorte que les différences entre groupes s'expriment en rapports de dose.

La population principale comprend les sujets ayant atteint une dose stable, avec une dose renseignée et un génotype CYP2C9 parmi \*1/\*1, \*1/\*2, \*1/\*3, \*2/\*2, \*2/\*3 et \*3/\*3. Elle compte **5 774 patients** : 4 351 \*1/\*1 et 1 423 porteurs d'un autre de ces génotypes (772 \*1/\*2, 503 \*1/\*3, 59 \*2/\*2, 69 \*2/\*3 et 20 \*3/\*3). Ont été exclus 128 patients sans génotype CYP2C9 et 17 porteurs d'un autre génotype (\*5, \*6, \*11, \*13, \*14), parce que ces génotypes n'ont pas de valeur dans le codage du corpus utilisé pour cette analyse. Le nombre de 5 774 résulte donc entièrement de ces critères ; il n'a pas été choisi.

### 7.2 Règle confrontée aux patients

**Pourquoi la warfarine.** La warfarine est retenue parce qu'il existe pour elle un jeu public de patients réels avec génotype et dose observée (IWPC). Aucun jeu équivalent n'a été utilisé pour les 188 autres médicaments.

**Les directives disponibles.** Les sources du projet contiennent cinq directives sur la warfarine (tableau 7.1). Les deux directives DPWG s'écrivent sous la forme « un génotype, une action » et entrent donc dans les quatre classes du corpus. La directive CPIC n'est pas utilisée pour une raison de forme : elle donne la dose par un algorithme qui combine plusieurs gènes, l'ascendance et des variables cliniques, ce qui ne se ramène pas à l'une des quatre classes. C'est aussi pourquoi CYP4F2, qui n'intervient que dans cet algorithme, n'est pas une variable du réseau (section 3.5).

::: {custom-style="LegendeTableau"}
Tableau 7.1 : Directives sur la warfarine présentes dans les sources et usage dans le corpus
:::

| Directive | Gènes | Contenu | Corpus v14 | Corpus v15 | Raison |
| --- | --- | --- | --- | --- | --- |
| DPWG | CYP2C9 | 65 % de la dose initiale (intermédiaire), 20 % (lent) ; aucune action pour \*1/\*2 | Oui, \*1/\*2 compris dans les intermédiaires | Oui, \*1/\*2 sans action | Forme « un génotype, une action » |
| DPWG | VKORC1 | 60 % de la dose initiale pour le génotype rs9923231 TT ; aucune action pour CT | Non | Oui | Forme « un génotype, une action » ; omise dans le corpus v14 |
| CPIC | CYP2C9, VKORC1, CYP4F2 | Dose calculée par un algorithme, selon l'ascendance | Non | Non | Ne se ramène pas à l'une des quatre classes |
| CPNDS | CYP2C9, VKORC1 | Non examinée | Non | Non | \[à compléter\] |
| RNPGx | CYP2C9, VKORC1 | Non examinée pour la warfarine | Non | Non | \[à compléter\] |

**La règle confrontée aux patients est celle du corpus v14.** Dans ce corpus, la warfarine comptait 394 lignes, toutes ADAPTER\_DOSE (source DPWG, gène CYP2C9 seul, valeurs de profil 0 ; 0,25 ; 0,5 ; 0,75). Le texte de la règle donne 20 % de la dose initiale standard pour les métaboliseurs lents et 65 % pour les intermédiaires, et précise que la dose propre au génotype peut être calculée par un algorithme. Aucune ligne n'était STANDARD : le génotype \*1/\*1 (valeur 1,0) était la référence sans règle. La question « ADAPTER\_DOSE contre STANDARD » est donc remplacée par « patients ADAPTER\_DOSE contre patients \*1/\*1 ». L'absence de la directive DPWG fondée sur VKORC1 n'avait pas de justification : la règle équivalente figurait dans le corpus pour l'acénocoumarol et la phenprocoumone. C'était une omission.

Correspondance entre génotype IWPC et valeur de profil (score d'activité divisé par 2, section 3.2) : \*1/\*1 = 1,0 ; \*1/\*2 = 0,75 ; \*1/\*3 et \*2/\*2 = 0,5 ; \*2/\*3 = 0,25 ; \*3/\*3 = 0. Classes : lent (0 ; 0,25) et intermédiaire (0,5 ; 0,75).

**La règle du corpus v15.** Le corpus v15 a modifié cette règle sur deux points (section 3.3). Le génotype \*1/\*2 reçoit désormais l'action que lui donne le texte DPWG, « aucune action » (STANDARD), et la directive DPWG fondée sur VKORC1 a été ajoutée : un patient porteur de deux allèles rs9923231 reçoit ADAPTER\_DOSE quel que soit son CYP2C9, et l'action la plus prudente des deux règles s'applique. La warfarine compte désormais une ligne pour chacun des 1 378 profils dont CYP2C9 est typé : 938 STANDARD et 440 ADAPTER\_DOSE. Les sections 7.4 à 7.6 portent sur la règle du corpus v14, celle du protocole ; la section 7.7 confronte la règle du corpus v15 aux mêmes patients, dans une analyse post hoc.

### 7.3 Protocole

Le protocole a été écrit et enregistré avec son empreinte (e5be689f130bb8af) avant toute comparaison de dose entre groupes génétiques. Hypothèse principale H1 : les patients étiquetés ADAPTER\_DOSE ont une dose d'entretien plus basse que les \*1/\*1. L'estimateur est le rapport des moyennes géométriques (exponentielle de la différence des moyennes de log-dose), avec un intervalle à 95 % par bootstrap sur les patients (2 000 tirages, graine 0). H1 est soutenue si la borne haute de l'intervalle est inférieure à 1. Le nombre de tirages et la graine ont été fixés dans le protocole avant le calcul ; la graine assure la reproductibilité, mais le nombre de tirages n'a pas été justifié par un calcul de précision de l'intervalle \[à compléter\].

Analyses secondaires déclarées d'avance :

- S1, rapport par classe et par génotype ;
- S2, comparaison descriptive avec les pourcentages DPWG ;
- S3, régression de la log-dose ajustée sur l'âge, la taille, le poids, l'amiodarone, VKORC1 (-1639, nombre d'allèles A) et l'origine, avec erreurs robustes HC3, avec et sans VKORC1 ;
- S4, patients d'origine « White » seulement ;
- S5, proportion de doses basses (≤ 21 mg par semaine), sensibilité et spécificité de l'étiquette ;
- S6, exploratoire, part de variance (R²) de la log-dose expliquée par CYP2C9, par VKORC1 et par les deux.

Les résultats devaient être rapportés tels quels, y compris négatifs ; toute analyse ajoutée après coup est signalée comme post hoc. Les chiffres principaux ont été recoupés par un second calcul indépendant (pandas ; scikit-learn pour les R²).

### 7.4 Résultats favorables

**H1 est soutenue.** Les patients ADAPTER\_DOSE ont une dose d'entretien géométrique égale à **0,830 \[0,804 ; 0,857\]** fois celle des \*1/\*1 (médianes 25,0 contre 30,0 mg par semaine). La borne haute est inférieure à 1 : la règle va dans le bon sens.

::: {custom-style="LegendeTableau"}
Tableau 7.2 : Rapport de dose d'entretien par génotype ou classe, par rapport aux \*1/\*1 (IWPC)
:::

| Génotype ou classe | n | Rapport de dose vs \*1/\*1 | Médiane (mg/sem) |
| --- | --- | --- | --- |
| \*1/\*2 | 772 | 0,972 \[0,937 ; 1,008\] | 28,0 |
| \*1/\*3 | 503 | 0,727 \[0,689 ; 0,762\] | 21,0 |
| \*2/\*2 | 59 | 0,728 \[0,633 ; 0,837\] | 22,8 |
| \*2/\*3 | 69 | 0,534 \[0,461 ; 0,619\] | 15,0 |
| \*3/\*3 | 20 | 0,350 \[0,254 ; 0,477\] | 11,0 |
| Classe « lent » (\*2/\*3, \*3/\*3) | 89 | 0,486 \[0,422 ; 0,558\] | 14,0 |
| Classe « intermédiaire » | 1 334 | 0,860 \[0,833 ; 0,887\] | 26,2 |

La médiane des 4 351 patients \*1/\*1 est de 30,0 mg par semaine. Le gradient est celui attendu : plus le génotype est défavorable, plus la dose baisse (0,73, puis 0,53, puis 0,35). Après ajustement sur l'âge, la taille, le poids, l'amiodarone et l'origine, le rapport est de 0,771 \[0,747 ; 0,795\] (n = 3 641 ; la baisse d'effectif vient des valeurs manquantes) ; il est inchangé après ajout de VKORC1 : 0,770 \[0,747 ; 0,794\] (n = 3 095). Restreint aux patients d'origine « White » (S4), il vaut 0,735 \[0,709 ; 0,764\].

### 7.5 Résultats non soutenus ou défavorables

**Le génotype \*1/\*2 n'est pas soutenu tel que le corpus v14 le classait.** La valeur 0,75, classée « intermédiaire » et ADAPTER\_DOSE par le corpus v14, donne un rapport brut de 0,972 \[0,937 ; 1,008\] (tableau 7.2). Dans la population complète, la dose de ce groupe, le plus nombreux de la classe intermédiaire (772 patients), n'est pas distinguable de celle des \*1/\*1. Une analyse post hoc, non prévue au protocole et décidée après avoir vu S1 et S4, restreinte aux patients « White », donne pour \*1/\*2 un rapport de 0,833 \[0,800 ; 0,869\] (n = 644). Le rapport brut proche de 1 viendrait donc en grande partie de la composition de la population, les origines étant mélangées dans le groupe de référence, plutôt que d'une absence d'effet. L'explication est plausible, mais elle reste post hoc et n'a pas été testée formellement.

**Le pouvoir de discrimination de l'étiquette est faible (S5).** Parmi les patients ADAPTER\_DOSE, 39,6 % ont une dose basse (≤ 21 mg par semaine), contre 29,3 % parmi les \*1/\*1. La sensibilité de l'étiquette pour les doses basses est de 0,307 \[0,286 ; 0,328\] et sa spécificité de 0,782 \[0,769 ; 0,794\]. L'étiquette indique une direction moyenne ; elle ne prédit pas bien la dose individuelle. Le seuil de 21 mg par semaine n'est pas tiré d'une source : il a été fixé dans le protocole pour décrire, non pour conclure, et un autre seuil changerait la sensibilité et la spécificité.

**Les pourcentages de la règle ne sont pas des doses d'entretien (S2).** Les 20 % et 65 % de la règle DPWG concernent la dose initiale ; les rapports observés (0,49 pour la classe lente, 0,86 pour la classe intermédiaire) concernent la dose d'entretien. La comparaison reste descriptive, sans test.

### 7.6 Le déterminant principal de la dose était absent de la règle

La règle de la warfarine du corpus v14 n'utilisait que CYP2C9, alors que VKORC1 figure parmi les 20 variables génétiques d'entrée du réseau (section 3.5). Dans ces données, la part de variance de la log-dose (S6, exploratoire, n = 4 629) est de **R² = 0,048** pour CYP2C9 seul, **0,294** pour VKORC1 (-1639) seul et 0,356 pour les deux. Le rapport de dose est de 0,724 \[0,702 ; 0,748\] pour A/G contre G/G et de 0,478 \[0,463 ; 0,494\] pour A/A. VKORC1 explique ainsi environ six fois plus de variance que CYP2C9 : l'étiquette du corpus v14 passait à côté du déterminant génétique principal de la dose. C'était une limite de la règle du corpus, non du réseau, qui ne fait que la reproduire, et elle ne venait pas de la source, puisque la DPWG publie une recommandation fondée sur VKORC1 pour la warfarine (section 7.2).

**Ce que ces résultats ont changé.** Les deux constats de cette section et de la précédente correspondent aux deux modifications de la règle dans le corpus v15 : l'ajout de la règle DPWG fondée sur VKORC1, et le classement de \*1/\*2 selon le texte de la directive (section 7.2). Des algorithmes de dose combinant données cliniques et pharmacogénétiques sont décrits par le consortium (Klein et al., 2009) ; ils sortent du cadre des quatre classes d'action.

### 7.7 Analyse post hoc : la règle du corpus v15 sur les mêmes patients

**Nature de l'analyse.** Cette analyse n'était pas prévue au protocole : elle a été décidée après les résultats des sections 7.4 à 7.6, et la règle qu'elle examine a été modifiée après que ces résultats ont montré le rôle de VKORC1. Elle n'est donc pas une validation indépendante de la règle v15 : elle mesure ce que la correction change sur les patients mêmes qui l'ont motivée. Elle reprend la population, l'estimateur et le bootstrap du protocole (2 000 tirages, graine 0) ; seule l'étiquette change. Le même fichier redonne à l'identique les résultats des sections 7.4 à 7.6, ce qui garantit que les données sont les mêmes.

**Étiquette v15.** Un patient est ADAPTER\_DOSE si son CYP2C9 vaut au plus 0,5 (\*1/\*3, \*2/\*2, \*2/\*3, \*3/\*3) ou s'il porte deux allèles A de VKORC1 (-1639) ; sinon il est STANDARD. Pour 991 des 5 774 patients (CYP2C9 \*1/\*1 ou \*1/\*2, VKORC1 non renseigné), l'étiquette v15 ne peut pas être calculée : ils sont exclus, et il reste 4 783 patients, dont 2 011 ADAPTER\_DOSE et 2 772 STANDARD. Parmi les 2 011, 1 360 le sont par VKORC1 seul. L'étiquette v14 a été recalculée sur ces mêmes 4 783 patients pour comparer les deux règles à population égale.

::: {custom-style="LegendeTableau"}
Tableau 7.3 : Règle du corpus v14 et règle du corpus v15 sur les mêmes 4 783 patients (analyse post hoc)
:::

| Mesure | Règle v14 (CYP2C9 seul) | Règle v15 (CYP2C9 et VKORC1) |
| --- | --- | --- |
| Patients ADAPTER\_DOSE / STANDARD | 1 233 / 3 550 | 2 011 / 2 772 |
| Rapport de dose ADAPTER\_DOSE contre STANDARD | 0,828 \[0,799 ; 0,858\] | 0,559 \[0,545 ; 0,575\] |
| Médianes (mg par semaine) | 25,0 contre 29,8 | 21,0 contre 35,0 |
| Patients « White » seulement | 0,724 \[0,695 ; 0,755\] | 0,603 \[0,578 ; 0,629\] |
| Sensibilité pour les doses basses (≤ 21 mg/sem) | 0,318 \[0,294 ; 0,341\] | 0,749 \[0,729 ; 0,769\] |
| Spécificité | 0,772 \[0,758 ; 0,787\] | 0,745 \[0,730 ; 0,761\] |

**Résultat.** Avec la règle v15, l'écart de dose entre les deux groupes est beaucoup plus marqué : les patients ADAPTER\_DOSE reçoivent en moyenne 0,559 fois la dose des patients STANDARD, contre 0,828 avec la règle v14. L'étiquette détecte 75 % des doses basses au lieu de 32 %, pour une spécificité presque inchangée (0,745 contre 0,772). Le gain vient des 1 290 patients \*1/\*1 porteurs de deux allèles A, que la règle v14 classait STANDARD et dont la dose est de 0,533 \[0,517 ; 0,549\] fois celle des patients STANDARD dans les deux versions.

**Un résultat défavorable à la règle v15.** Les 512 patients \*1/\*2 sans deux allèles A, que la règle v15 classe désormais STANDARD, ont une dose de 0,837 \[0,805 ; 0,875\] fois celle des patients STANDARD dans les deux versions (\*1/\*1 sans deux allèles A). Une fois l'effet de VKORC1 A/A écarté, le génotype \*1/\*2 est donc associé à une dose plus basse d'environ 16 %, du même ordre que le rapport de 0,833 observé chez les patients « White » (section 7.5). Le classement STANDARD de \*1/\*2 est conforme au texte de la directive DPWG, qui ne prévoit aucune action pour ce génotype, mais il n'est pas soutenu par ces doses. La règle v15 ne distingue pas non plus les hétérozygotes A/G, dont la dose est réduite d'environ un quart (section 7.6), parce que la directive ne prévoit pas d'action pour eux.

### 7.8 Portée et limites

- Une seule molécule est validée, la warfarine, sur 189 médicaments ; ce résultat ne se transfère pas aux autres règles.
- La règle du protocole est celle du corpus v14 ; la règle du corpus v15 n'est examinée que dans une analyse post hoc, sur les patients mêmes qui ont motivé sa correction, et sans 991 patients dont VKORC1 n'est pas renseigné (section 7.7).
- Le réseau n'est pas testé directement : il reproduit les étiquettes, et valider la règle revient à valider ce qu'il reproduit. Un test direct, comparant la probabilité du réseau à la dose observée, n'a pas été fait.
- Les associations sont observationnelles ; les doses viennent de plusieurs centres ; l'analyse ajustée porte sur les cas complets.
- L'origine des patients confond les comparaisons : les fréquences alléliques de CYP2C9 et de VKORC1 diffèrent selon l'origine, d'où l'écart entre l'analyse brute et l'analyse restreinte aux patients « White ».
- Les patients porteurs d'allèles CYP2C9 rares (\*5, \*6, \*11, \*13, \*14) sont exclus ; or c'est précisément pour des génotypes de ce type que le codage par score d'activité produit un écart avec la directive (section 8.3).
- Ce chapitre valide une règle, non la chaîne complète depuis un VCF, qui est examinée au chapitre 8.

### 7.9 Synthèse

Sur 5 774 patients réels, la règle de la warfarine du corpus v14 va dans le bon sens : la dose d'entretien est inférieure de 17 % en moyenne chez les patients étiquetés ADAPTER\_DOSE (H1 soutenue), avec un gradient cohérent selon le génotype. Elle est cependant imprécise : le génotype \*1/\*2 n'est pas distinguable des \*1/\*1 dans la population complète, l'étiquette ne détecte qu'environ 31 % des doses basses, et elle ignorait VKORC1, qui explique davantage de variance que CYP2C9. Le corpus v15 ajoute la règle VKORC1 et classe \*1/\*2 selon la directive. Sur les mêmes patients, dans une analyse post hoc, l'étiquette v15 sépare beaucoup mieux les doses (rapport 0,559 au lieu de 0,828 ; 75 % des doses basses détectées au lieu de 32 %), mais le classement STANDARD de \*1/\*2 n'est pas soutenu par les doses observées. Ces résultats défavorables sont conservés tels quels.

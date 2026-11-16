## Annexe B : L'application en fonctionnement

### B.1 Parcours complet sur un exemple
Cette annexe montre l'application en fonctionnement, écran par écran, sur un exemple unique, et explique ce que chaque partie affiche. L'exemple est le fichier NA19472.vcf : un échantillon public du projet 1000 Genomes, reconstruit à partir du pypgx-bundle (génome GRCh38), qui n'est pas un patient réel et ne fait pas partie de l'ensemble final de 138 profils. La spécialité choisie est la cardiologie, parce qu'elle réunit des familles où le profil change l'avis (antivitamines K, statines) et d'autres où il ne le change pas. Toutes les captures viennent d'une même analyse, avec la lecture réelle du VCF par PyPGx. Cet exemple illustre le fonctionnement ; il ne mesure pas la performance, qui est traitée aux chapitres 6 à 8.

**Étape 1 : accueil et lancement de l'analyse (figure B.1).** L'utilisateur fournit un fichier VCF (.vcf ou .vcf.gz, un seul patient, génome GRCh37 ou GRCh38, 500 Mo au maximum) et choisit la spécialité du médecin parmi 17 spécialités. Un champ facultatif permet d'indiquer l'identifiant du patient quand le fichier en contient plusieurs. La page rappelle que l'outil est un outil de recherche non validé cliniquement, que le fichier VCF est supprimé du serveur à la fin de l'analyse, et elle liste les sources scientifiques des règles, de la lecture du génome et des modèles. Le libellé du bouton de choix du fichier est celui du navigateur utilisé pour la capture.

::: {custom-style="FigureImg"}
![](fig/cap_01_accueil.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.1 : Page d'accueil : dépôt du fichier VCF et choix de la spécialité (exemple NA19472).
:::

**Étape 2 : analyse en cours (figure B.2).** Après le lancement, une page de progression affiche l'étape en cours (ici « Lecture des gènes du patient », c'est-à-dire l'appel d'allèles par PyPGx) et une barre d'avancement. L'analyse de cet échantillon a pris 86 secondes (section 5.8). La page de résultat s'ouvre seule à la fin.

::: {custom-style="FigureImg"}
![](fig/cap_02_progression.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.2 : Page de progression pendant la lecture du génome.
:::

**Étape 3 : recommandation pour le patient (figure B.3).** La page de résultat commence par la recommandation pour la spécialité choisie, en blocs de couleur.

- Bloc vert, « À prescrire à la dose habituelle » : antivitamines K (phenprocoumone, acénocoumarol, warfarine), six statines, quatre antiagrégants plaquettaires (prasugrel, aspirine, ticagrélor, clopidogrel), et l'ibuprofène, hors groupe de choix. Les médicaments d'une même famille sont dits « au même niveau pour ce patient » : les gènes lus ne permettent pas de les départager et le choix revient au médecin (section 5.5).
- Bloc orange, « Dose à adapter ou à surveiller » : fluindione et fluvastatine, pour lesquelles la phrase « Ce qui change pour ce patient » nomme le gène responsable, CYP2C9 (score d'activité 1,5, génotype \*1/\*8) ; et l'hydralazine, hors groupe de choix, du fait du génotype NAT2 lent (\*5/\*6).
- Bloc rouge, « À éviter aussi pour ce patient (autres spécialités) » : six médicaments hors cardiologie (voriconazole et cinq antidépresseurs tricycliques), signalés parce que le patient est métaboliseur rapide pour CYP2C19 (\*1/\*17). Ce bloc existe pour qu'un avis « à éviter » ne soit jamais caché par le choix de la spécialité. La nuance sur ces avis (lecture la plus prudente de la directive) est décrite en section 5.8, point 2.

La ligne « Non évalués pour ce patient : 14 médicaments » est aussi importante que les avis : pour ces médicaments (par exemple métoprolol, flécaïnide, propafénone), l'application ne donne aucun avis parce que le gène CYP2D6 ne peut pas être lu dans un VCF de variants ponctuels. L'écran précise que « non évalué » ne veut pas dire « sans risque ». C'est la protection décrite en section 5.4 : le réseau n'est pas interrogé sur un médicament dont un gène nécessaire manque, situation où il est fragile (section 8.5).

::: {custom-style="FigureImg"}
![](fig/cap_03_resultats_haut.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.3 : Page de résultat : recommandation pour la spécialité, médicaments non évalués et médicaments à éviter dans les autres spécialités (NA19472, Cardiologie).
:::

**Étape 4 : avis et scores des trois modèles (figure B.4).** Un volet dépliable affiche, pour chaque médicament des groupes de la spécialité, l'avis du réseau (DL), la directive officielle, et les avis de XGBoost et de Random Forest, avec un score entre 0 et 1 sous chaque avis. Dans l'exemple, les quatre colonnes donnent le même avis pour les treize médicaments ; le score du réseau est supérieur ou égal à 0,999, celui de XGBoost va de 0,908 à 0,991 et celui de Random Forest de 0,494 à 0,716. Deux précautions de lecture sont écrites sous le tableau et valent pour tout le mémoire. D'abord, le score est la certitude du modèle dans son propre avis, pas la probabilité que l'avis soit juste cliniquement. Ensuite, seul le score du réseau est calibré dans l'application ; les scores bas de Random Forest (moyenne de 100 arbres) ne signalent pas un désaccord. L'accord des trois modèles n'est pas une confirmation indépendante : ils ont appris les mêmes règles (chapitre 6).

::: {custom-style="FigureImg"}
![](fig/cap_04_trois_modeles.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.4 : Avis et scores du réseau, de la directive officielle, de XGBoost et de Random Forest pour les médicaments de la spécialité.
:::

**Étape 5 : recherche d'un médicament (figure B.5).** Un champ de recherche donne la fiche d'un médicament précis, quelle que soit la spécialité. Pour la warfarine, le réseau, la directive, XGBoost (score 0,942) et Random Forest (score 0,656) donnent tous « À dose standard », sans alerte. Le volet « Pourquoi ? » montre les deux règles DPWG appliquées : celle de VKORC1, pour un patient sans allèle rs9923231, et celle de CYP2C9. Pour CYP2C9, la règle appliquée est celle de \*1/\*2, et l'écran précise que le génotype lu est \*1/\*8, de même score d'activité. **Cet avis illustre la limite décrite en section 5.8, point 6 :** pour deux personnes de ce même génotype, PharmCAT, qui lit la directive DPWG allèle par allèle, recommande 65 % de la dose initiale (chapitre 8). L'avis affiché est donc fidèle à la règle du corpus, mais pas à la lecture allèle par allèle de la directive ; la mention du génotype lu est ce qui permet à un lecteur averti de le remarquer.

::: {custom-style="FigureImg"}
![](fig/cap_06_recherche_warfarin.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.5 : Fiche d'un médicament recherché (warfarine), volet « Pourquoi ? » ouvert : la règle CYP2C9 appliquée est celle de \*1/\*2, de même score d'activité que le génotype lu \*1/\*8 (section 5.8, point 6).
:::

**Étape 6 : détails pour les experts (figure B.6).** Ce volet reprend chaque famille de médicaments (classe ATC de niveau 4) et explique l'avis médicament par médicament : tableau des quatre avis, gènes regardés avec ce qui a été lu chez le patient, texte de la directive officielle avec sa source et l'identifiant de sa fiche, et une phrase en langage simple. Il indique aussi quel gène change la recommandation : pour les antivitamines K, « si CYP2C9 était normal, le programme ajouterait fluindione ». Cette phrase vient d'un second calcul où un seul gène est remis à la valeur normale, le reste du profil restant identique.

::: {custom-style="FigureImg"}
![](fig/cap_07_experts_B01AA.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.6 : Détails pour les experts : explication des avis pour la famille des antivitamines K.
:::

**Étape 7 : comment le programme a travaillé (figure B.7).** Cet encadré résume le calcul en trois points : le réseau reçoit tous les gènes du patient en une seule fois (un gène non lu est signalé « non lu » et n'est jamais supposé normal) ; il calcule en un seul passage un avis pour chacun des 189 médicaments ; le décompte de ces avis est affiché. Pour NA19472, le réseau donne 140 « à dose standard », 17 « adapter la dose », 19 « surveiller » et 13 « éviter », soit 189 avis. Une partie de ces avis n'est pas affichée à l'utilisateur, par prudence, quand un gène nécessaire n'a pas été lu ou que la combinaison des gènes n'a jamais été vue.

::: {custom-style="FigureImg"}
![](fig/cap_08_comment_travaille.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.7 : Encadré « Comment le programme a travaillé » : profil lu et décompte des avis du réseau sur les 189 médicaments.
:::

**Étape 8 : gènes lus chez le patient (figure B.8).** Le tableau de vérification donne, pour chacune des 20 variables génétiques, la valeur de codage transmise au réseau, le phénotype et le génotype lus, et l'origine de la valeur. Pour NA19472, 15 gènes sont lus dans le VCF par PyPGx (par exemple CYP2C9 \*1/\*8, CYP2C19 \*1/\*17, CYP3A5 \*1/\*6, NAT2 \*5/\*6, TPMT \*3C/\*8) ; CYP2D6 est « non déterminé » et les quatre allèles HLA sont « non renseignés ». Les libellés y sont ceux du lecteur, en anglais, pour la traçabilité (section 5.6). Ce tableau permet de remonter d'un avis au génotype qui l'explique. Il faut le lire avec la réserve de la section 8.2 : la concordance du génotype avec la référence GeT-RM est élevée pour CYP2C9, CYP3A5, TPMT et CYP2C19, et faible pour CYP2B6, SLCO1B1, UGT1A1 et DPYD.

::: {custom-style="FigureImg"}
![](fig/cap_09_genes_lus.png){width=14.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.8 : Tableau de vérification des gènes lus chez le patient : valeur de codage, phénotype et génotype lus, origine.
:::

**Étape 9 : compléter avec un test de laboratoire (figures B.9 et B.10).** Le gène CYP2D6 et les allèles HLA ne se lisent pas dans un VCF de variants ponctuels (section 5.3). Si le patient dispose d'un résultat de laboratoire, l'utilisateur peut le saisir dans un formulaire facultatif : phénotype CYP2D6 (métaboliseur lent, intermédiaire, normal ou ultra-rapide) et, pour chacun des quatre allèles HLA, « négatif » ou « positif ». Le formulaire explique à quoi sert la saisie, ce qu'elle change et quels médicaments sont concernés ; il précise que « non testé » n'est pas « négatif » et que les valeurs saisies ne sont pas vérifiées par l'application.

Pour la démonstration, deux valeurs fictives ont été saisies (elles ne décrivent pas l'échantillon NA19472) : CYP2D6 « métaboliseur lent » et HLA-B\*57:01 « positif » (figure B.9). Après la mise à jour (figure B.10) :

- les médicaments non évalués de la spécialité passent de 14 à 7 ;
- disopyramide et quinidine rejoignent le bloc vert, ainsi que l'amiodarone et la clonidine, hors groupe de choix ; flécaïnide, propafénone et métoprolol rejoignent le bloc orange (adapter la dose) ;
- les médicaments à éviter dans les autres spécialités passent de 6 à 14 : sept médicaments dépendant de CYP2D6 (codéine, désipramine, nortriptyline, tamoxifène, thioridazine, tramadol, venlafaxine) et l'abacavir (HLA-B\*57:01 positif) s'ajoutent ;
- les avis qui ne dépendent pas des valeurs saisies ne changent pas ;
- les valeurs saisies sont signalées « saisi par l'utilisateur » partout où elles sont citées.

Ce comportement est celui attendu : la saisie ne modifie que les médicaments liés au gène renseigné, et l'avis sur l'abacavir correspond à la directive et à l'étude clinique de référence (section 6.6). Sur l'ensemble des 189 médicaments, le résumé passe de 6 à 14 médicaments à éviter, de 110 à 144 compatibles, de 1 à 6 à vérifier et de 72 à 25 non évalués.

::: {custom-style="FigureImg"}
![](fig/cap_05b_completer_rempli.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.9 : Formulaire « Compléter avec un test de laboratoire » avec deux valeurs fictives saisies pour la démonstration.
:::

::: {custom-style="FigureImg"}
![](fig/cap_12_apres_completion.png){width=14.2cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.10 : Page de résultat après la saisie des deux valeurs de laboratoire fictives.
:::

**Étape 10 : vue patient (figure B.11).** Une page séparée reformule le résultat pour le patient, sans score ni tableau technique : un avertissement (« n'arrêtez et ne changez aucun traitement de votre propre initiative »), puis les médicaments à éviter ou à discuter en priorité, puis les médicaments de la spécialité avec une phrase simple pour chacun.

::: {custom-style="FigureImg"}
![](fig/cap_10_vue_patient.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.11 : Vue patient : résultat reformulé en langage simple (extrait).
:::

**Étape 11 : rapport PDF, fiche JSON et suppression des données (figure B.12).** Le bouton « Télécharger le PDF » produit un rapport de 6 pages et 11 sections pour cet exemple, avant la saisie de laboratoire. Sa première page donne le fichier, la spécialité, la date, l'avertissement, puis un résumé sur les 189 médicaments : 6 à éviter, 110 compatibles (réseau, XGBoost et règle d'accord), 1 à vérifier et 72 non évalués, dont 60 dépendent de CYP2D6. Le médicament à vérifier est le citalopram, hors cardiologie, écarté par l'abstention (confiance du réseau sous le seuil). Le rapport reprend ensuite le tableau des gènes, les médicaments à éviter, les médicaments proposés pour la spécialité, les médicaments non évalués, une explication en langage simple, la lecture des scores, les directives utilisées, les références, la méthode et les limites. La « Fiche JSON » exporte les mêmes informations sous forme structurée. Le bouton « Supprimer mes données » efface le résultat immédiatement ; sans action, il est effacé après 24 heures (section 5.7).

::: {custom-style="FigureImg"}
![](fig/cap_11_pdf-1.png){width=12.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.12 : Première page du rapport PDF produit par l'application.
:::

**Ce que montre et ne montre pas cet exemple.** Le parcours montre que la chaîne complète fonctionne, du fichier VCF au rapport, que chaque avis est accompagné de sa source et de ce qui a été lu chez le patient, et que l'application préfère ne pas répondre plutôt que de répondre sans le gène nécessaire (72 médicaments sur 189 non évalués tant que CYP2D6 et les allèles HLA manquent). Il montre aussi une limite : l'avis sur la warfarine reproduit fidèlement la règle du corpus, sans reproduire la lecture allèle par allèle de la directive DPWG. Il ne montre pas que les avis sont justes : un seul échantillon public est utilisé, les valeurs de laboratoire sont fictives, et les avis reproduisent les directives. La fidélité aux directives est mesurée au chapitre 6 et la comparaison à des références externes au chapitre 8.

### B.2 Illustration sur une personne de validation externe

Cette annexe montre, sur une personne, ce que l'application lit et prédit, et comment chaque sortie est confrontée à sa référence. La personne est NA06991. Elle est choisie par une règle fixe, pour ne pas sélectionner un cas favorable : parmi les 104 personnes, huit ont le plus grand nombre de gènes comparables à GeT-RM (11 gènes), et NA06991 est la première dans l'ordre des identifiants. Elle a un lien parent-enfant avec un profil du corpus ; c'est l'une des 18 personnes de la section 8.3. Un seul cas illustre la méthode ; les résultats d'ensemble sont ceux des sections 8.2 à 8.4. Les écrans ci-dessous ont été produits par l'application actuelle à partir du fichier VCF de cette personne (spécialité Cardiologie, analyse en environ 85 secondes).

**Étape 1 : sortie du parseur, comparée à GeT-RM.** La figure B.13 montre le tableau « Gènes lus chez ce patient » produit par l'application. Le tableau B.1 compare ces génotypes à la référence GeT-RM.

::: {custom-style="FigureImg"}
![](fig/cap8_genes.png){width=14.2cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.13 : Sortie du parseur pour NA06991 : gènes lus dans le fichier VCF.
:::

::: {custom-style="LegendeTableau"}
Tableau B.1 : Génotypes lus par le parseur pour NA06991, comparés à GeT-RM
:::

| Gène | GeT-RM | Parseur (PyPGx) | Résultat |
| --- | --- | --- | --- |
| CYP2C19 | \*1/\*1 | \*1/\*1 | Identique |
| CYP2C9 | \*1/\*1 | \*1/\*1 | Identique |
| CYP3A4 | \*1/\*1 | \*1/\*1 | Identique |
| CYP3A5 | \*3/\*3 | \*3/\*3 | Identique |
| CYP4F2 (hors modèle) | \*1/\*1 | \*1/\*1 | Identique |
| TPMT | \*1/\*1 | \*1/\*1 | Identique |
| DPYD | c.1601G>A / c.2846A>T | c.1601G>A (\*4)/c.2846A>T | Référence écrite autrement qu'en diplotype : non comptée |
| NAT2 | \*4/\*5 ou \*5/\*6 | \*5/\*6 | Référence incertaine : non comptée |
| CYP2B6 | \*1/\*6 | \*1/\*9 | Discordant |
| SLCO1B1 | \*15/\*15 | \*15/\*46 | Discordant |
| UGT1A1 | \*60/\*60 | \*1/\*1 | Discordant |

Pour cette personne, six gènes sont identiques, deux ont une référence incertaine et trois sont discordants. Les trois gènes discordants sont parmi ceux dont la concordance d'ensemble est faible (tableau 8.2). Pour SLCO1B1, les trois sources s'accordent pourtant sur la fonction : GeT-RM donne \*15/\*15, PyPGx \*15/\*46 avec le phénotype « Poor Function », et PharmCAT \*15/\*45, lui aussi « Poor Function ». Le génotype \*15/\*46 étant absent de la table CPIC utilisée par le parseur, l'application déclare le gène « non déterminé » au lieu de le supposer normal, et les médicaments qui en dépendent ne reçoivent pas d'avis (figure B.15). C'est la règle de prudence de la section 5.3 : elle évite une erreur, au prix d'un avis manquant.

**Étape 2 : avis du réseau et des deux modèles de contrôle.** La figure B.14 montre les avis pour la spécialité Cardiologie, retenue pour rester comparable à l'exemple du chapitre 5. Sur les 31 médicaments de la spécialité, 9 sont évalués et 22 ne le sont pas, principalement faute de CYP2D6 et de SLCO1B1. Pour les 7 médicaments des groupes de choix, le réseau donne le même avis que la directive, avec un score supérieur ou égal à 0,999 : « adapter la dose » pour la phenprocoumone, l'acénocoumarol, la warfarine et la fluindione, en raison des deux allèles rs9923231 de VKORC1 ; dose standard pour le clopidogrel, le prasugrel et le ticagrélor (CYP2C19 \*1/\*1). XGBoost donne les sept mêmes avis, avec des scores de 0,891 à 0,998. Random Forest s'écarte de la directive pour la phenprocoumone et l'acénocoumarol (dose standard, scores 0,490 et 0,477), ce qui est cohérent avec son F1 plus faible (section 6.5). Les deux autres médicaments évalués sont l'hydralazine (adapter la dose, NAT2 \*5/\*6) et l'ibuprofène (dose standard).

::: {custom-style="FigureImg"}
![](fig/cap8_modeles.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.14 : Avis et scores du réseau, de la directive, de XGBoost et de Random Forest pour NA06991 (Cardiologie).
:::

::: {custom-style="FigureImg"}
![](fig/cap8_fluvastatine.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.15 : Fluvastatine pour NA06991 : médicament non évalué, car le gène SLCO1B1 est non déterminé.
:::

**Étape 3 : la warfarine, cas corrigé par le corpus v15.** Avec le corpus v14, la warfarine n'apparaissait pas dans les avis de cette personne : son CYP2C9 est normal, et la règle du corpus ne lisait que ce gène, alors que la directive DPWG recommande 60 % de la dose initiale pour deux allèles rs9923231 de VKORC1 (section 7.2). Avec la règle VKORC1 ajoutée au corpus v15, l'application affiche « adapter la dose », et le volet « Pourquoi ? » montre les deux règles DPWG appliquées : celle de CYP2C9 (aucune action) et celle de VKORC1 (60 % de la dose initiale), qui fixe l'avis (figure B.16). Le réseau, XGBoost et Random Forest donnent tous les trois cet avis.

::: {custom-style="FigureImg"}
![](fig/cap8_warfarine.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure B.16 : Warfarine pour NA06991 : avis « adapter la dose » fondé sur la règle DPWG de VKORC1 (deux allèles rs9923231).
:::

**Étape 4 : recommandations affichées, comparées à PharmCAT.** Pour NA06991, l'application affiche 39 recommandations CPIC ou DPWG. PharmCAT n'a pas de recommandation pour 10 d'entre elles ; sur les 29 comparables, 26 sont retrouvées et 3 ne le sont pas. Pour la flucytosine, le texte du projet est la traduction française de la recommandation DPWG que donne PharmCAT : le contenu est le même. Pour la warfarine, la ligne non retrouvée est la règle CYP2C9 « aucune action », qui n'a pas de vis-à-vis chez PharmCAT, lequel n'affiche que la recommandation VKORC1 ; celle-ci est retrouvée. Pour la fluvastatine, la règle CPIC appliquée par l'application ne lit que CYP2C9 (dose de départ habituelle), parce que SLCO1B1 est non déterminé, alors que PharmCAT, qui appelle SLCO1B1 « Poor Function », limite la dose de départ à 40 mg par jour. L'écran principal ne donne d'ailleurs aucun avis pour ce médicament (figure B.15).

**Ce que ce cas montre.** Il réunit les types d'écart mesurés dans ce chapitre : des génotypes discordants avec la référence, un médicament non évalué par prudence, et des écarts de comparaison dus à la formulation ou à la structure plutôt qu'au contenu. Il montre aussi l'effet d'une correction de règle : la warfarine, absente des avis avec le corpus v14, reçoit maintenant l'avis que donne la directive DPWG.

## Chapitre 8 : Validation externe sur profil complet : génotype, recommandation et patients publiés

Ce chapitre compare ce que l'application produit à partir d'un profil génétique complet, lu dans un fichier VCF, à des références indépendantes de notre code. Les fichiers VCF des personnes de validation passent par la chaîne complète de l'application, en commençant par le parseur du fichier VCF (section 5.3). Trois questions sont posées, dans l'ordre de la chaîne : l'application lit-elle le bon génotype ? Affiche-t-elle, pour ce profil complet, la recommandation des directives ? Le réseau de neurones prédit-il la même décision que la référence ? Le chapitre 7 traite une quatrième question, distincte : une règle isolée, celle de la warfarine, va-t-elle dans le bon sens chez des patients réels ? Les résultats défavorables sont conservés tels quels.

L'ordre des sections suit celui de la chaîne, parce qu'une erreur en amont se propage en aval : un génotype mal lu (section 8.2) produit une recommandation fausse même si la règle est juste (section 8.3), et une règle mal codée produit une étiquette fausse que le réseau reproduit fidèlement (section 8.4).

### 8.1 Sources et niveaux de preuve

::: {custom-style="LegendeTableau"}
Tableau 8.1 : Niveaux de preuve de la validation externe
:::

| Niveau | Référence | Ce qu'elle valide |
| --- | --- | --- |
| Génotype | GeT-RM (CDC), tableau consolidé V4 du 22 janvier 2025 | Appel des allèles à partir du VCF, 104 personnes hors corpus |
| Profil complet | PharmCAT 3.4.0 (logiciel de référence) | Recommandation par personne et par médicament (CPIC, DPWG) |
| Patients publiés | Étude pilote de 11 patients (Lim et al., 2025), tableau S3 | Génotypes multi-gènes avec recommandations publiées |
| Associations publiées | Fichiers bruts ClinPGx (annotations de variants) | Concordance du sens de chaque règle avec les études |
| Effet clinique | IWPC (chapitre 7) | Sens d'une règle chez des patients réels, pas la prédiction sur profil complet |

Le tableau GeT-RM compte 363 personnes. Les 104 retenues sont celles dont le fichier VCF figure dans le pypgx-bundle (génome GRCh38) et qui n'appartiennent pas aux 1 379 profils du corpus ; aucune autre sélection n'a été faite, et le nombre de 104 découle donc de ces deux conditions. Leur liste a été figée avant la première comparaison.

Deux limites structurelles s'appliquent à tout le chapitre. D'abord, l'application, le réseau, PharmCAT et CPIC reposent sur les mêmes textes de directives, et le réseau a été entraîné sur des étiquettes issues de nos règles : les comparaisons des sections 8.3 à 8.5 montrent une restitution fidèle des directives partagées, non la justesse clinique de ces directives. Ensuite, deux corrections de règles du corpus v15 (thiopurines, CYP2C9 selon la DPWG ; section 3.3) et la vérification de la fluvastatine ont été décidées en examinant les écarts avec PharmCAT sur ces mêmes 104 personnes : pour ces règles, la comparaison de la section 8.3 ne constitue plus une validation indépendante, puisqu'elle vérifie ce que les corrections ont changé.

### 8.2 Génotype contre GeT-RM

Cette section valide la première étape de la chaîne, le parseur du fichier VCF. Pour les 104 personnes, le génotype que le parseur obtient par PyPGx a été comparé à celui du tableau GeT-RM, gène par gène. GeT-RM est retenu comme référence parce que ses génotypes sont publiés par un programme de référence (CDC) et ont été établis indépendamment de notre chaîne. Le parseur n'a pas changé entre les deux versions du corpus en ce qui concerne l'appel des génotypes : seul le codage de CYP2C9 a été modifié (section 5.3). Les résultats ci-dessous valent donc pour l'application actuelle ; le génotype lu pour la personne de l'annexe B.2 a d'ailleurs été relu directement par la version actuelle, avec un résultat identique pour les 22 gènes.

::: {custom-style="LegendeTableau"}
Tableau 8.2 : Concordance du génotype appelé par PyPGx avec GeT-RM, par gène
:::

| Gène | Concordants / comparés |
| --- | --- |
| CYP2C9 | 65 / 65 |
| CYP3A5 | 61 / 61 |
| TPMT | 63 / 66 |
| CYP2C19 | 59 / 65 |
| CYP2B6 | 22 / 50 |
| SLCO1B1 | 17 / 60 |
| UGT1A1 | 11 / 41 |
| DPYD | 18 / 58 (plus 17 sous-allèles) |

Le nombre de personnes comparées varie d'un gène à l'autre parce que GeT-RM ne publie pas un génotype pour chaque personne et chaque gène. La concordance est élevée pour CYP2C9 (65/65) et CYP3A5 (61/61), élevée mais imparfaite pour TPMT (63/66) et CYP2C19 (59/65), et faible pour CYP2B6, SLCO1B1, UGT1A1 et DPYD. Les causes des désaccords n'ont pas été établies cas par cas. Les hypothèses, appuyées par les notes du tableau GeT-RM mais non vérifiées, sont une nomenclature publiée à des dates différentes et des allèles récents absents des panels testés par GeT-RM : un désaccord ne prouve donc pas une erreur de l'outil. Attribuer la cause de chaque désaccord demanderait de reprendre cas par cas la définition des allèles dans les deux nomenclatures ; ce travail n'a pas été fait et reste une limite (section 8.8).

::: {custom-style="FigureImg"}
![](fig/fig_8_1.png){width=15cm}
:::

::: {custom-style="LegendeFigure"}
Figure 8.1 : Concordance du génotype appelé par PyPGx avec GeT-RM, par gène (104 personnes hors corpus).
:::

### 8.3 Profil complet contre PharmCAT

**Méthode.** Pour chaque personne, chaque recommandation CPIC ou DPWG affichée par l'application est recherchée parmi les recommandations que PharmCAT 3.4.0 produit à partir du même fichier VCF. Une recommandation est « retrouvée » si le texte normalisé est le même, ou s'il figure dans une liste d'équivalences de formulation établie avant le calcul. Elle est « comparable » si PharmCAT donne au moins une recommandation pour ce médicament et cette source. Les scripts de comparaison sont ceux du protocole figé, utilisés sans modification ; ils redonnent à l'identique les chiffres obtenus avec la version précédente de l'application, ce qui garantit que les écarts ci-dessous viennent de l'application et non de la méthode.

::: {custom-style="LegendeTableau"}
Tableau 8.3 : Recommandations affichées par l'application et retrouvées chez PharmCAT (104 personnes)
:::

| Mesure | Résultat |
| --- | --- |
| Recommandations affichées avec un texte | 4 589 |
| Comparables (PharmCAT a une recommandation) | 3 357 |
| Retrouvées chez PharmCAT | 3 221 (95,9 %) |
| dont CPIC | 2 950 / 2 976 (99,1 %) |
| dont DPWG | 271 / 381 (71,1 %) |
| Non retrouvées | 136 lignes, 21 motifs |
| Personnes sans aucune ligne non retrouvée | 34 / 104 |

Avec le corpus v14, la proportion retrouvée était de 97,8 % (3 455 sur 3 534) et 70 personnes sur 104 n'avaient aucune ligne en désaccord. **La concordance globale baisse.** La baisse est entièrement due à la warfarine : avec la règle VKORC1 ajoutée au corpus v15, la warfarine a désormais une règle DPWG pour chaque personne, et ses lignes non retrouvées passent de 22 à 98.

**Lecture des 136 lignes non retrouvées.** Chaque motif a été lu après le calcul. La warfarine en porte 98, dont 91 sans aucune différence d'action ou de dose : elles viennent de la formulation ou de la structure des textes. Les écarts de contenu ont deux causes seulement. La première est le codage de CYP2C9 par score d'activité, qui applique à des génotypes rares la règle d'un génotype fréquent de même score : c'est le cas de 7 lignes de warfarine et des 8 lignes de siponimod. La seconde tient à des différences d'appel de génotype, non de règle : pour les trois thiopurines, PyPGx et PharmCAT n'appellent pas le même phénotype NUDT15 chez 6 personnes. Les lignes restantes concernent la flucytosine, où le texte du projet est une traduction française absente de la liste d'équivalences, ainsi qu'une ligne de fluvastatine, pour laquelle l'application déclare SLCO1B1 non déterminé (cas détaillé en annexe B.2), et une ligne de sertraline. Le détail motif par motif est en annexe G.10.

**Action finale de la warfarine.** Une analyse décidée après le résultat compare l'action affichée par l'application à l'action DPWG la plus forte de PharmCAT. L'action est la même pour 65 des 70 personnes comparables (34 personnes n'ont pas de recommandation PharmCAT pour la warfarine). Les 5 écarts sont les 5 personnes citées plus haut, toutes avec un VKORC1 de référence : l'application affiche « dose standard », PharmCAT « 65 % de la dose initiale ». La correction de la règle de \*1/\*2 (section 3.3) a donc déplacé l'erreur vers des allèles plus rares de même score d'activité. Cette limite est la conséquence directe du choix de coder CYP2C9 par son score d'activité (section 3.2) ; elle est désormais mesurée.

**Parenté avec le corpus.** D'après le pedigree du projet 1000 Genomes, 18 des 104 personnes ont un parent ou un membre de la fratrie parmi les 1 379 profils du corpus. La proportion retrouvée est de 95,9 % (2 657 sur 2 771) pour les 86 personnes sans apparenté et de 96,2 % (564 sur 586) pour les 18 autres. La parenté ne gonfle donc pas le résultat. Elle n'est contrôlée que par le pedigree déclaré.

### 8.4 Concordance du réseau avec l'action soutenue par PharmCAT

Sur les 2 600 unités personne × médicament dont les règles sont retrouvées chez PharmCAT, l'action prédite par le réseau est la même que l'action soutenue par PharmCAT dans 2 593 cas (99,73 %), contre 2 598 (99,92 %) avec le corpus v14.

::: {custom-style="LegendeTableau"}
Tableau 8.4 : Désaccords entre le réseau et l'action soutenue par PharmCAT
:::

| Personne | Médicament | Action soutenue par PharmCAT | Action du réseau | Confiance du réseau |
| --- | --- | --- | --- | --- |
| NA10847 | fluvastatine | ADAPTER\_DOSE | STANDARD | 0,945 |
| NA10847 | pravastatine | ADAPTER\_DOSE | STANDARD | 0,563 |
| NA10855 | tacrolimus | STANDARD | ADAPTER\_DOSE | 0,734 |
| NA18642 | siponimod | ADAPTER\_DOSE | EVITER | 0,612 |
| NA18642 | tacrolimus | STANDARD | ADAPTER\_DOSE | 0,609 |
| NA19122 | sertraline | EVITER | ADAPTER\_DOSE | 1,0 |
| NA21095 | sertraline | EVITER | ADAPTER\_DOSE | 1,0 |

Cinq des sept désaccords ont une confiance inférieure au seuil d'abstention de l'application (0,9981, section 4.5) : l'application les afficherait « à vérifier ». Les deux erreurs restantes, sur la sertraline, sont prononcées avec une confiance maximale ; ce sont les mêmes qu'avec le corpus v14. Ce sont des erreurs confiantes du type décrit en section 6.3, que l'abstention ne peut pas écarter. Dans l'application, l'avis EVITER de la règle suffit cependant à classer la sertraline « à éviter » pour ces deux personnes (section 5.4).

Sur l'ensemble des lignes évaluées pour les 104 profils complets, le réseau diverge de la règle dans 10 lignes sur 6 322 (0,2 %), contre 6 sur 6 172 (0,1 %) avec le corpus v14. Comme le réseau reproduit le moteur de règles sur lequel il a été entraîné, ce résultat mesure la fidélité de la reproduction, non une indépendance vis-à-vis des directives.

### 8.5 Patients publiés (tableau S3, 11 patients)

Une étude pilote publiée donne, pour 11 patients, les génotypes de 4 à 7 gènes et les recommandations de prescription correspondantes. Les génotypes de chaque patient ont été saisis à la main puis passés dans le moteur de l'application, sans lecture de VCF. Ce jeu est retenu parce qu'il fournit, pour des patients réels, des recommandations multi-gènes rédigées par une équipe indépendante de ce travail.

::: {custom-style="LegendeTableau"}
Tableau 8.5 : Onze patients publiés, concordance des phénotypes et des recommandations
:::

| Mesure | Résultat |
| --- | --- |
| Phénotype calculé identique à celui de l'article | 41 gènes sur 42 (1 non déterminé : SLCO1B1 \*1/\*21, allèle absent de la table) |
| Lignes patient–médicament évaluables | 36 |
| Règle de l'application conforme à l'article | 36 / 36 |
| Avis du réseau | 32 conformes, 1 compatible, 3 erronés |

Le cas compatible est le pantoprazole (CYP2C19 \*1/\*17) : le réseau et la règle donnent STANDARD, l'article une adaptation de dose, avec un texte identique à celui de CPIC. Les trois cas erronés concernent le tacrolimus chez trois patients de génotype CYP3A5 \*3/\*3 : le réseau prédit ADAPTER\_DOSE, alors que l'article et la règle donnent STANDARD. Dans les trois cas, l'application affiche « à vérifier », parce que le réseau et la règle sont en désaccord. Avec le corpus v14, le seul cas erroné était le tacrolimus d'un patient \*1/\*3 (réseau STANDARD, article ADAPTER\_DOSE) ; il est corrigé avec le corpus v15. Le changement de corpus a donc déplacé l'erreur du réseau sur ce médicament sans la faire disparaître. Les règles de l'application, elles, sont inchangées et toutes conformes.

Sur ces profils partiels, le réseau diverge de la règle dans 11,4 % des lignes (50 sur 439), contre 0,2 % sur les profils complets lus dans un VCF (figure 8.2). Avec le corpus v14, ces proportions étaient de 8,0 % et 0,1 %. Le réseau est donc fragile hors de la distribution de ses données d'entraînement, où tous les profils portent la quasi-totalité des gènes, et le réseau du corpus v15 l'est davantage que celui du corpus v14. La protection de l'application tient à la règle affichée à côté de chaque avis et à l'alerte « à vérifier » en cas de désaccord. La majorité des lignes qui changent entre les deux versions pour ces patients ne change que de statut, à action identique : c'est l'effet du seuil d'abstention plus élevé (0,9981 au lieu de 0,9965) et des désaccords avec XGBoost. Les recommandations de l'étude viennent d'un panel commercial fondé sur CPIC : l'indépendance de cette référence n'est que partielle.

::: {custom-style="FigureImg"}
![](fig/fig_8_2.png){width=14cm}
:::

::: {custom-style="LegendeFigure"}
Figure 8.2 : Divergence entre le réseau et la règle : profils complets lus dans un VCF (104 personnes) contre profils partiels saisis à la main (11 patients publiés).
:::

### 8.6 Associations publiées : analyse exploratoire

Les 285 règles de l'application ont été comparées aux études publiées pour le même gène, le même état et le même médicament, à partir des fichiers bruts ClinPGx (27 590 lignes, résultats nuls inclus). Le protocole a été figé avant le calcul ; un amendement écrit, décidé après la première analyse, précise le traitement des hétérozygotes sans fonction, la lecture du sens de la dose et un indicateur descriptif de la part concordante.

::: {custom-style="LegendeTableau"}
Tableau 8.6 : Verdicts des 285 règles confrontées aux études publiées (analyse exploratoire)
:::

| Verdict | Règles |
| --- | --- |
| Soutenue | 44 |
| Mixte | 63 |
| Non soutenue | 23 |
| Signal non orienté | 32 |
| Non tranchable | 2 |
| Non appariées | 51 |
| Aucune étude | 70 |

Le verdict automatique a été corrigé à la main pour 4 règles sur 30 d'un échantillon aléatoire (13 %). Ces chiffres doivent donc être lus comme ceux d'une analyse exploratoire : les 51 règles non appariées et les règles EVITER à « signal non orienté » n'ont pas été relues une à une, et aucune relecture par un second lecteur pharmacologue n'a été conduite dans le cadre de ce travail. Cette analyse a été faite sur la table de règles du corpus v14 ; les règles modifiées dans le corpus v15 (warfarine, siponimod, thiopurines) n'ont pas été confrontées de nouveau aux études, ce qui reste une limite. La définition exacte de chaque verdict est donnée en annexe G.8.


### 8.7 Limites

1. Les textes des directives sont les mêmes dans l'application et chez PharmCAT, et le réseau a été entraîné sur des étiquettes issues des mêmes règles : la comparaison mesure une restitution fidèle, non la justesse clinique.
2. Deux corrections du corpus v15 et la vérification de la fluvastatine ont été décidées sur ces 104 personnes : pour les médicaments concernés, la comparaison n'est plus indépendante (section 8.1).
3. Le codage de CYP2C9 par score d'activité applique à des génotypes rares la règle d'un génotype fréquent de même score ; l'écart est mesuré pour la warfarine et le siponimod.
4. Les génotypes des 11 patients ont été saisis à la main, et leurs recommandations viennent d'un panel fondé sur CPIC ; l'appel de génotype est par ailleurs incertain pour SLCO1B1, UGT1A1, CYP2B6 et DPYD (section 8.2).
5. 79 textes de directive sur 709 sont tronqués dans la table de règles, sans effet sur la classe prédite.
6. La lecture de la littérature a été faite par un seul lecteur, la parenté n'est contrôlée que par le pedigree déclaré, et aucun essai clinique de profil complet, par exemple PREPARE, n'a été lu en détail.

### 8.8 Synthèse

Pour un profil complet lu dans un VCF, l'application restitue les recommandations CPIC presque sans écart (99,1 %) et les recommandations DPWG avec des écarts surtout dus à la formulation et à la structure des textes (71,1 %), soit 95,9 % au total. Le seul écart de contenu systématique tient au codage de CYP2C9 par score d'activité. Le réseau prédit la même action que la référence dans 99,73 % des cas, et cinq de ses sept désaccords seraient signalés « à vérifier ». Sur 11 patients publiés, les règles de l'application sont toutes conformes, mais le réseau diverge davantage sur des profils partiels (11,4 % des lignes), ce qui confirme qu'il ne doit pas être utilisé sans la règle à côté. La justesse clinique des directives elles-mêmes n'est pas démontrée par ce travail ; elle reste appuyée sur les études primaires citées.

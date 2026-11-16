## Chapitre 5 : L'application web PharmaGeno

Ce chapitre décrit l'application dans la version utilisée pour toutes les mesures des chapitres 6 à 8, fondée sur le corpus v15 ; chaque élément a été vérifié dans le code et dans les sorties de test. Les modules, les routes, le détail des contrôles, la liste des tests et la description complète des limites sont en annexe E ; un parcours illustré est en annexe B.

### 5.1 Rôle et périmètre

L'application prend en entrée le fichier VCF d'un patient et une spécialité médicale. Elle affiche, pour chaque sous-groupe ATC de niveau 4 de la spécialité, un avis en feux tricolores (dose habituelle, dose à adapter ou à surveiller, à éviter), les gènes qui expliquent l'avis, et un rapport PDF. C'est un outil de recherche : il n'est pas un dispositif médical et ne remplace ni un médecin ni un pharmacien.

### 5.2 Architecture et exécution

L'application est écrite en Python avec Flask, des gabarits Jinja2 et ReportLab pour le PDF ; les quatre modèles finaux du chapitre 4 sont chargés au démarrage. Le serveur n'écoute que l'adresse locale et n'a pas d'authentification, et PyPGx s'exécute dans un environnement Python séparé, ses versions de bibliothèques étant incompatibles avec celles des modèles (annexe E.1).

### 5.3 Du fichier VCF au profil génétique

La chaîne commence par le lecteur du fichier VCF (figure 5.1). Toutes les étapes suivantes en dépendent : un génotype mal lu donne un avis faux même si le réseau et les règles sont corrects. C'est pourquoi sa sortie est la première chose validée au chapitre 8 (section 8.2).

::: {custom-style="FigureImg"}
![](fig/fig_5_1.png){width=9.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure 5.1 : Chaîne de traitement de l'application, du fichier VCF aux sorties.
:::

Le fichier est refusé s'il est illisible, non trié, s'il ne désigne pas un patient unique ou si l'assemblage du génome (GRCh37 ou GRCh38) ne peut pas être établi sans ambiguïté. PyPGx 0.27.0 (Sherman, Claw et Lee, 2024) lit ensuite 18 gènes, avec le VCF pour unique entrée : aucun appel de variation structurale n'est revendiqué, et le choix du pipeline est explicité en annexe E.2. CYP2D6, dont le phénotype dépend de délétions et de duplications, et les quatre allèles HLA ne se lisent pas dans un VCF de variants ponctuels : l'utilisateur peut les saisir à partir d'un test de laboratoire. Chaque génotype est converti en la valeur numérique utilisée à l'entraînement (section 3.2) ; un gène non lu vaut « manquant » et n'est jamais remplacé par la valeur normale. Sur les échantillons 1000 Genomes, le lecteur reproduit le codage du corpus à partir du même génotype (annexe E.2), l'exactitude du génotype lui-même étant mesurée au chapitre 8. Le codage de CYP2C9 par score d'activité a une conséquence : des génotypes différents de même score, comme \*1/\*2 et \*1/\*8, reçoivent la même valeur et donc la même règle (section 5.8, point 6).

### 5.4 Moteur de prédiction et couche de sécurité

Le réseau de profil donne pour chacun des 189 médicaments une probabilité calibrée sur les quatre actions ; si la confiance est inférieure ou égale au seuil d'abstention de 0,9981 (section 4.5), le médicament passe en « à vérifier ». XGBoost fournit un second avis, le Random Forest un avis informatif sans effet sur les statuts. La règle CPIC, DPWG ou RNPGx applicable est affichée à côté de l'avis, avec sa source : elle n'entre pas dans la prédiction du réseau, mais la couche de sécurité l'utilise.

Chaque médicament reçoit un statut : ok ; à vérifier (abstention, désaccord avec XGBoost ou avec la règle) ; gène requis non déterminé ; hors domaine, c'est-à-dire combinaison des gènes requis jamais vue à l'entraînement ; règle seule. Le recommandeur en déduit une catégorie : **à éviter** dès qu'un seul avis — réseau, XGBoost ou règle — indique EVITER ; **proposable** si le statut est ok et qu'aucun avis n'indique EVITER ; à vérifier ; non évalué ; règle seule. Les médicaments proposés en remplacement d'un médicament à éviter sont ceux du même sous-groupe ATC4 dont le statut est ok et l'action STANDARD. Ce regroupement est chimique, pharmacologique et thérapeutique, et non une équivalence clinique : la méthodologie officielle de la classification précise que le classement d'une substance n'est pas une recommandation d'usage et ne convient pas pour décider d'une substitution thérapeutique (WHO Collaborating Centre for Drug Statistics Methodology, 2026). L'application présente donc ces médicaments comme des candidats à examiner par le prescripteur, non comme des équivalents. Pour expliquer un avis, l'écran indique le génotype lu chez le patient et signale quand la règle appliquée a été écrite pour un autre génotype de même valeur de codage.

### 5.5 Recommandation par groupe de médicaments

Pour chaque classe ATC4 de la spécialité contenant au moins deux médicaments du modèle, le réseau de choix (section 4.6) propose un ensemble de médicaments, dont la couche de sécurité retire tout médicament « à éviter ». Les gènes qui expliquent l'avis sont trouvés par substitution : la valeur du patient est remplacée par la valeur normale, et l'on regarde si l'ensemble proposé change. Un médicament n'apparaît qu'une fois dans la synthèse, dans la ligne la plus prudente, et aucun médicament évalué ne disparaît de l'écran, ce qu'un test vérifie pour toutes les spécialités.

### 5.6 Sorties et protection des données

La page de résultats place en premier la recommandation, puis les alertes de sécurité, et replie le contenu scientifique dans des « Détails pour les experts ». Un score n'y est jamais affiché comme une certitude de 100 %, et la légende précise qu'il mesure la certitude de reproduire la règle, non la justesse clinique. L'application produit aussi une vue en langage simple pour le patient, un rapport PDF et une sortie JSON (annexe E.3). Le fichier VCF et les fichiers intermédiaires sont supprimés à la fin de l'analyse ; seules les valeurs du profil par gène sont conservées, jusqu'à la demande de suppression ou pendant 24 heures au plus, ce que des tests vérifient.

### 5.7 Tests, installation et reproductibilité

La suite compte 76 tests (86 contrôles), qui réussissent tous : un médicament à éviter n'est jamais affiché comme recommandé, un médicament dépendant de CYP2D6 n'est jamais classé compatible sans CYP2D6, l'affichage correspond à un recalcul indépendant du réseau, et aucun profil de l'ensemble final n'est utilisé (annexe E.4). La chaîne complète, exécutée sur le VCF de l'échantillon NA19472 dans deux environnements indépendants, donne des génotypes identiques ; cet exemple vérifie la logique et la reproductibilité, non la performance clinique.

Elle est distribuée sous forme d'une archive avec un manifeste de sommes de contrôle et un script de vérification ; elle demande Python 3.12 ou plus récent et PyTorch, et n'a été testée que sous Linux (annexe E.5).

### 5.8 Limites de l'application

Les neuf limites sont énumérées ici ; leur description complète est en annexe E.6.

1. **Médicaments à règle seule** : 21 médicaments ne sont pas intégrés aux réseaux, et l'ibuprofène apparaît dans une famille de cardiologie trompeuse.
2. **Lecture la plus prudente** : pour certains antidépresseurs tricycliques et le voriconazole, l'étiquette EVITER sur-affirme une recommandation de force « Optional » ou « Moderate ».
3. **Domaine par médicament** : un profil atypique dans son ensemble n'est pas repéré (section 6.7).
4. **Saisies nécessaires** : CYP2D6 et les allèles HLA ne se lisant pas dans un VCF de variants ponctuels, les médicaments qui en dépendent restent non évalués tant que l'utilisateur ne saisit pas un résultat de laboratoire. Sur l'exemple de l'annexe B, 72 des 189 médicaments sont non évalués, dont 60 pour CYP2D6 ; la saisie de deux valeurs ramène ce nombre à 25. L'outil préfère ne pas répondre plutôt que répondre sans le gène nécessaire.
5. **Références** : la publication précise de chaque directive n'a pas été associée dans le cadre de ce travail.
6. **Codage de CYP2C9** : pour la warfarine, des génotypes de score 1,5 autres que \*1/\*2 reçoivent la règle de \*1/\*2, alors que PharmCAT recommande 65 % de la dose initiale (chapitre 8).
7. **Sécurité et usage** : pas d'authentification, seuils d'abstention non cliniques, aucune évaluation d'utilisabilité.
8. **Textes tronqués** : 79 textes de directive sur 709 sont tronqués à l'affichage.
9. **Refus prudents** : un VCF valide peut être refusé si l'assemblage ne peut pas être établi.

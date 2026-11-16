## Chapitre 5 : L'application web PharmaGeno

Ce chapitre décrit l'application dans la version utilisée pour toutes les mesures des chapitres 6 à 8, fondée sur le corpus v15 : son architecture, la chaîne qui mène d'un fichier VCF à un avis, la couche de sécurité, les sorties, la protection des données, les tests, l'installation et ses limites, puis un parcours illustré. L'ordre suit celui de la chaîne de traitement, parce qu'une erreur à une étape se propage à toutes les suivantes. Chaque élément décrit a été vérifié dans le code et dans les sorties de test ; ce chapitre ne mesure pas la performance des modèles, qui est l'objet du chapitre 6.

### 5.1 Rôle et périmètre

L'application prend en entrée le fichier VCF d'un patient et une spécialité médicale. Elle affiche, pour chaque groupe de médicaments interchangeables de la spécialité, un avis en feux tricolores (à prescrire à la dose habituelle, dose à adapter ou à surveiller, à éviter), les gènes qui expliquent l'avis, et un rapport PDF. C'est un outil de recherche : il n'est pas un dispositif médical, n'a pas été validé cliniquement et ne remplace ni un médecin ni un pharmacien. Ses avis reproduisent les recommandations CPIC, DPWG et RNPGx (Relling et Klein, 2011 ; Swen et al., 2011 ; Abdullah-Koolmees et al., 2021) et les étiquettes réglementaires sur lesquelles le corpus a été étiqueté (chapitre 3).

### 5.2 Architecture et exécution

L'application est écrite en Python avec le cadriciel Flask (Pallets), des gabarits Jinja2 et la bibliothèque ReportLab pour le PDF. Les quatre modèles finaux du chapitre 4 sont chargés au démarrage : réseau de profil (189 médicaments × 4 actions), réseau de choix (44 classes ATC de niveau 4), XGBoost et Random Forest.

::: {custom-style="LegendeTableau"}
Tableau 5.1 : Modules de l'application et rôle de chacun
:::

| Module | Rôle |
| --- | --- |
| lecteur de VCF (vcf\_to\_profile\_v9) | contrôle du fichier, appel de PyPGx, conversion en profil |
| moteur (moteur\_v10j) | prédictions des modèles, alertes, couche de sécurité, gènes décisifs, choix dans une classe |
| recommandeur (recommandation\_v8r) | catégories, alternatives, textes pour le clinicien et pour le patient |
| rapport (rapport\_pdf\_v8u) | rapport PDF de 11 à 13 sections |
| références (references\_v8r) | références et sources affichées à l'écran et dans le PDF |

Le serveur écoute uniquement l'adresse locale 127.0.0.1 (port 5000 par défaut) ; il n'a pas d'authentification et ne doit pas être exposé sur Internet. La taille maximale d'un fichier téléversé est de 500 Mo par défaut. Une seule analyse VCF est traitée à la fois, les autres attendent, parce que l'appel des génotypes par PyPGx occupe la machine pendant environ une minute et demie. PyPGx s'exécute dans un environnement Python séparé (option --pgx-python), parce qu'il exige des versions de bibliothèques incompatibles avec celles des modèles (section 5.9). Chaque réponse porte les en-têtes Cache-Control: no-store, X-Content-Type-Options: nosniff, Referrer-Policy: no-referrer et une Content-Security-Policy restrictive. Les routes sont les suivantes.

::: {custom-style="LegendeTableau"}
Tableau 5.2 : Routes du serveur et fonction de chacune
:::

| Route | Fonction |
| --- | --- |
| / | accueil : fichier VCF, spécialité, saisies facultatives |
| /analyser (POST) | lance l'analyse et renvoie vers la page de progression |
| /progression/{id}, /etat/{id} | avancement de l'analyse |
| /resultats/{id} | page de résultats pour le clinicien |
| /completer/{id} (POST) | ajout facultatif de CYP2D6 et des allèles HLA après l'analyse |
| /patient/{id} | vue en langage simple pour le patient |
| /pdf/{id}, /json/{id} | rapport PDF, sortie JSON |
| /supprimer/{id} (POST) | suppression des données de l'analyse |
| /references, /apropos | références scientifiques ; méthode et limites |
| /demo (POST) | route interne utilisée par les tests, non reliée à l'écran |

### 5.3 Du fichier VCF au profil génétique

La première étape de la chaîne est le parseur du fichier VCF, appelé « lecteur » dans la suite. Il contrôle le fichier, appelle les génotypes des gènes avec PyPGx, puis convertit chaque génotype en la valeur numérique attendue par le réseau. Toutes les étapes suivantes dépendent de lui : un génotype mal lu donne un avis faux même si le réseau et les règles sont corrects. C'est pourquoi sa sortie est la première chose validée au chapitre 8 (section 8.2).

::: {custom-style="FigureImg"}
![](fig/fig_5_1.png){width=15cm}
:::

::: {custom-style="LegendeFigure"}
Figure 5.1 : Chaîne de traitement de l'application, du fichier VCF aux sorties.
:::

**Contrôles du fichier.** Avant tout appel, le fichier est refusé avec un message s'il est illisible, s'il n'est pas trié par chromosome et position (il est alors impossible de le compresser et de l'indexer), s'il ne contient aucun échantillon ou plusieurs échantillons sans que l'un soit désigné (un seul patient par analyse), ou si l'assemblage du génome (GRCh37 ou GRCh38) ne peut pas être établi ou est contradictoire. L'assemblage est lu de deux façons : dans l'en-tête, par la longueur déclarée du chromosome 1, et par la position des enregistrements, comptés dans les régions des gènes selon les coordonnées de chacun des deux assemblages. Le décompte n'est retenu que s'il penche au moins cinq fois plus vers un assemblage que vers l'autre ; en dessous, et sans longueur de chromosome dans l'en-tête, le fichier est refusé plutôt que lu sur une hypothèse (section 5.10, point 10). Un fichier non compressé est copié sous forme compressée et indexée. Un gène n'est « couvert » que si le VCF contient au moins un enregistrement dans sa région ; sinon il est déclaré non déterminé, car un VCF de variants ne distingue pas un gène normal d'un gène non séquencé. Cette heuristique est prudente mais imparfaite pour un gène court : sur les VCF 1000 Genomes, le minimum observé est de 0 à 3 variants selon les gènes. Les génotypes haploïdes du chromosome X (hommes) sont convertis en homozygotes diploïdes.

**Appel des génotypes.** PyPGx 0.27.0 (Sherman, Claw et Lee, 2024), pipeline run-chip-pipeline, avec le paquet de référence pypgx-bundle 0.27.0 et Java, lit 18 gènes : ABCG2, CFTR, CYP2B6, CYP2C19, CYP2C9, CYP2D6, CYP3A4, CYP3A5, CYP4F2, DPYD, F5, G6PD, NAT2, NUDT15, SLCO1B1, TPMT, UGT1A1 et VKORC1. CFTR et CYP4F2 ne font pas partie des 20 variables du réseau de profil (section 3.5). CYP2D6 n'est jamais appelé depuis un VCF de variants ponctuels, car son phénotype dépend de délétions et de duplications : il est toujours « non déterminé » tant que l'utilisateur ne saisit pas un résultat de test externe. Les quatre allèles HLA (HLA-B\*15:02, HLA-B\*57:01, HLA-B\*58:01, HLA-A\*31:01) ne se lisent pas non plus dans un VCF de ce type : l'utilisateur les saisit (positif, négatif, non testé) dans un formulaire facultatif.

**Codage en valeurs.** Chaque génotype est converti en la valeur numérique utilisée à l'entraînement, selon une méthode propre au gène : phénotype PyPGx pour ABCG2, CYP2B6, CYP2C19, CYP3A5, DPYD, F5 et UGT1A1 ; moyenne des scores d'activité CPIC des deux allèles, divisée par 2, pour CYP2C9 (table data/cyp2c9\_alleles\_cpic\_v1.csv ; un allèle absent de la table donne « non déterminé ») ; génotype puis table CPIC pour NAT2, CYP3A4, NUDT15, TPMT et SLCO1B1 ; phénotype G6PD de PyPGx (0 ; 0,5 ; 1) ; nombre d'allèles rs9923231 pour VKORC1 (0 allèle : 1 ; 1 allèle : 0,5 ; 2 allèles : 0). Un gène non déterminé vaut « manquant » : il n'est jamais remplacé par la valeur normale et il active l'indicateur d'absence du réseau (section 3.5). Une valeur saisie par l'utilisateur (CYP2D6 : 0 ; 0,5 ; 1 ; 2 ; allèles HLA) est tracée comme telle et jamais présentée comme lue dans le VCF.

**Concordance avec les profils d'entraînement.** Trois contrôles ont été faits sur les échantillons 1000 Genomes.

- Sur les 1 379 profils du corpus, les valeurs obtenues à partir du génotype PyPGx enregistré sont identiques à celles du profil d'entraînement pour G6PD, NAT2, CYP3A4, NUDT15, TPMT, SLCO1B1 et VKORC1 (1 379 sur 1 379), ainsi que pour CFTR et CYP4F2 (hors modèle).
- Pour les gènes codés par phénotype, la concordance avec les valeurs d'origine du corpus est de 95,7 % pour ABCG2 et de 92,8 % pour CYP2B6 ; elle est de 99,8 % ou plus pour CYP2C19 (99,85 %), CYP3A5 (99,93 %), F5 et UGT1A1 (100 %). DPYD n'a pas été mesuré. Ce n'est donc pas une identité.
- Pour CYP2C9, codé par score d'activité, le lecteur redonne la valeur du profil d'entraînement pour 1 378 profils sur 1 378 à partir du génotype PyPGx enregistré (un profil est non déterminé des deux côtés).

Ces contrôles montrent que le lecteur reproduit le codage du corpus à partir du même génotype ; ils ne mesurent pas l'exactitude du génotype PyPGx lui-même, qui est comparée à une référence indépendante au chapitre 8. Le codage de CYP2C9 par score d'activité a une conséquence mesurée à ce même chapitre : des génotypes différents de même score, comme \*1/\*2 et \*1/\*8, reçoivent la même valeur et donc la même règle (section 5.10, point 7).

### 5.4 Moteur de prédiction et couche de sécurité

**Prédiction.** Le profil est standardisé avec la moyenne et l'écart-type enregistrés dans le modèle, puis le réseau de profil donne pour chacun des 189 médicaments une probabilité calibrée sur les quatre actions. La confiance est la probabilité maximale. Si elle est inférieure ou égale au seuil d'abstention de l'application, 0,9981, le médicament passe en « à vérifier » avec l'alerte « incertain ». Ce seuil est le quantile à 1 % de la confiance hors pli sur le corpus v15 (section 4.5) : il écarte par construction 1 % des prédictions de la validation croisée, et 1,12 % sur l'ensemble final avec les modèles de même configuration évalués en section 6.7. Le réseau est le moteur de l'avis.

**Avis de contrôle.** XGBoost fournit un second avis. Le Random Forest (100 arbres, feuilles d'au moins 2 lignes, même entrée que XGBoost) fournit un avis informatif, sans effet sur les statuts ni sur les alertes. Ces réglages ont été fixés sur la validation interne de la version antérieure du corpus, non sur l'ensemble final, après trois essais : 300 arbres avec des feuilles d'une ligne donnaient un fichier de 298 Mo, écarté pour sa taille ; 100 arbres avec des feuilles de 5 lignes, une précision de la classe EVITER de 0,58, écartée. La règle CPIC, DPWG ou RNPGx applicable est affichée à côté, avec sa source ; elle n'entre pas dans le calcul de la prédiction du réseau, mais la couche de sécurité l'utilise. Les valeurs obtenues sur la validation interne des modèles finaux (F1 macro de 0,9997 pour le réseau de profil, avec une température de 0,222 ; 1,0 pour XGBoost ; 0,9358 pour le Random Forest) ont servi à l'arrêt anticipé ou aux contrôles de fabrication : elles ne mesurent pas la performance, qui est l'objet du chapitre 6. Le Random Forest est nettement moins bien calibré que les deux autres modèles sur cette validation (ECE de 0,1544) et ses scores, non calibrés, sont plus bas ; il est présenté comme une information et non comme un avis de poids égal.

**Statuts.** Chaque médicament reçoit un statut :

- ok ;
- a\_verifier : une alerte a été levée parmi incertain (abstention), désaccord avec XGBoost, désaccord avec la règle ;
- non\_determine\_gene : un gène requis est manquant ;
- hors\_domaine : la combinaison de valeurs des gènes requis n'a jamais été vue dans les 1 241 profils de développement ;
- dl\_indisponible : médicament sans sortie du réseau (règle seule) ;
- medicament\_non\_couvert.

Le domaine qui définit « hors domaine » est construit sur les seuls profils de développement : les 138 profils de l'ensemble final n'y contribuent pas, pour que l'application ne déclare pas « vue » une combinaison qui n'a été observée que dans des données réservées à l'évaluation. Un gène requis manquant n'est jamais remplacé par « normal ». Pour un gène non requis sans indicateur d'absence, la valeur neutre est utilisée dans le calcul et la substitution est listée dans la sortie.

**Catégories pour l'utilisateur.** À partir du statut et des avis, le recommandeur classe chaque médicament :

- à éviter : le réseau, XGBoost ou la règle indique EVITER (un seul avis suffit) ;
- proposable : statut ok et aucun avis EVITER ; il s'agit de compatibilité pharmacogénétique uniquement ;
- à vérifier ;
- non évalué ;
- règle seule : pas de prédiction du réseau.

Les alternatives proposées à un médicament à éviter sont les médicaments de la même classe ATC4 dont le statut est ok et l'action STANDARD. Le texte affiché pour chaque directive est celui de la table de règles du projet, en anglais ou en français selon la règle ; la fiche de la directive, liée par son identifiant ClinPGx, fait foi.

**Ce qui est affiché pour expliquer un avis.** Pour chaque médicament, l'écran indique ce qui a été lu chez le patient (phénotype et génotype) pour les gènes de la règle. Quand la règle appliquée a été écrite pour un autre génotype de même valeur de codage, l'écran le dit explicitement, par exemple « règle appliquée à la valeur de codage du patient ; génotype lu chez ce patient : \*1/\*8 ». Cette mention rend visible, au moment de la lecture, la limite du codage de CYP2C9 décrite en section 5.3.

### 5.5 Recommandation par groupe de médicaments

Pour chaque classe ATC4 de la spécialité qui contient au moins deux médicaments du modèle, le réseau de choix (section 4.6) propose l'ensemble des médicaments dont la probabilité atteint la moitié de la probabilité maximale. La couche de sécurité retire de cet ensemble tout médicament que la section 5.4 classe « à éviter » ; les médicaments retirés et écartés restent visibles. Les gènes qui expliquent l'avis sont déterminés par substitution : pour chaque gène, la valeur du patient est remplacée par la valeur normale et l'on regarde si l'ensemble proposé change ; un test vérifie que cet affichage est identique à un recalcul indépendant.

Un médicament n'apparaît que dans une ligne de la synthèse en feux tricolores, la plus prudente : rouge avant orange avant vert. Vert : recommandé par le réseau de choix avec le conseil STANDARD ; orange : ADAPTER\_DOSE ou SURVEILLER ; rouge : à éviter. Un médicament évalué de la spécialité qui n'appartient à aucun groupe de choix, ou qui est le seul évaluable de son groupe, est placé dans le bloc de son avis avec la mention « hors groupe de choix », ou dans un bloc « À faire vérifier par un professionnel » si son statut l'exige. Cette règle garantit qu'aucun médicament évalué ne disparaît de l'écran ; elle est vérifiée pour toutes les spécialités par un test. L'ordre des médicaments proposés (action, puis intervention d'un gène du patient, puis probabilité) est une règle d'affichage, pas une validation clinique ; les probabilités de médicaments équivalents sont quasi égales.

### 5.6 Sorties

La page de résultats place en premier la recommandation pour le patient, puis les alertes de sécurité, et replie le contenu scientifique dans « Détails pour les experts » (glossaire, tableau « Qui donne l'avis » avec le réseau, la directive, XGBoost et le Random Forest, score de 0 à 1 de chaque modèle). Les scores sont arrondis vers le bas et un score de 0,999 ou plus s'écrit « ≥ 0,999 » : un modèle n'est jamais présenté comme certain à 100 %. La légende précise que ces scores mesurent la certitude de reproduire la règle et non la justesse clinique. Les libellés de phénotype sont traduits en français, sauf dans le « Tableau complet pour vérification », qui garde volontairement la sortie brute du lecteur afin qu'un avis puisse être rapproché du génotype exact qui l'a produit.

La vue patient reformule en langage simple. Le PDF compte de 11 à 13 sections, numérotées sans saut : deux sections n'apparaissent que si elles ont un contenu (médicaments à règle seule, médicament recherché). Il reprend les gènes, les médicaments à éviter, les médicaments proposés, les médicaments à vérifier et non évalués, une explication pour le patient, la lecture des scores, les directives utilisées (liens ClinPGx pour les identifiants PA…), les références et la méthode avec ses limites. Le JSON contient le profil, la lecture du VCF, les catégories, la recommandation et la synthèse en feux tricolores.

### 5.7 Protection des données

Le fichier VCF téléversé et tous les fichiers intermédiaires sont supprimés à la fin de l'analyse, que celle-ci réussisse ou non. Seules les valeurs du profil par gène sont conservées dans un fichier de tâche, jusqu'au clic sur « Supprimer mes données » ou pendant 24 heures au plus (purge automatique). Ces trois comportements sont vérifiés par des tests. L'application n'a pas d'authentification : la confidentialité repose sur l'usage en local. Pour un accès réseau, la documentation d'installation recommande un serveur mandataire avec authentification et HTTPS.

### 5.8 Tests

La suite de tests compte 76 tests numérotés (T1 à T68, puis T79 à T86), soit 86 contrôles, qui réussissent tous. Ils vérifient notamment que :

- tout médicament avec au moins un avis EVITER figure dans les alertes de sécurité ;
- un médicament à éviter n'est jamais affiché comme recommandé ;
- un médicament dépendant de CYP2D6 n'est jamais classé compatible sans CYP2D6 ;
- l'affichage correspond à un recalcul indépendant du réseau ;
- le câblage du choix est sensible : sur des profils d'entraînement, l'ensemble proposé contient 2 médicaments étiquetés EVITER sur 2 712 avec les bonnes probabilités, et 77 quand les probabilités sont attribuées aux mauvais médicaments ;
- aucun profil de l'ensemble final de 138 profils n'est utilisé dans ces tests ;
- le Random Forest n'a aucun effet sur les statuts ;
- les pages ne contiennent ni jargon technique interdit, ni « 1,000 » ;
- le codage de CYP2C9 est correct pour les six génotypes de \*1/\*1 à \*3/\*3, et un allèle absent de la table donne « non déterminé » ;
- pour VKORC1 homozygote variant, l'écran et le PDF affichent pour l'acénocoumarol le texte de la directive (« 50 % de la dose initiale standard ») et jamais un libellé de règle interne ;
- dans toutes les spécialités, chaque médicament évalué apparaît à l'écran ;
- le domaine utilisé est celui des profils de développement.

Quatre tests ont été adaptés au cours du développement, parce que le texte qu'ils attendaient a été corrigé (numéro de version du bandeau et du PDF, formulation de l'accord entre modèles, libellé des règles sans phénotype nommé) ; aucun test n'a été retiré.

La chaîne complète a aussi été exécutée sur le VCF réel de l'échantillon NA19472 (section 5.11), reconstruit à partir des fichiers 1000 Genomes du pypgx-bundle, hors ensemble final. L'analyse prend 86 secondes. Elle a été faite dans deux environnements indépendants, avec les mêmes versions de PyPGx et du pypgx-bundle : les génotypes lus sont identiques pour les 22 gènes, dont CYP2C9 \*1/\*8 (score d'activité 1,5, valeur de profil 0,75). Ces tests vérifient la logique de l'application et la reproductibilité de la lecture, non la performance clinique : un échantillon est une illustration, pas une statistique. La comparaison sur 104 personnes est présentée au chapitre 8.

### 5.9 Installation et reproductibilité

L'application est distribuée sous la forme d'une archive qui contient le code, les modèles, les données nécessaires à l'exécution et un manifeste de sommes de contrôle. Elle demande Python 3.12 ou plus récent et PyTorch ; la suite de tests a été exécutée avec PyTorch 2.11.0. Un script de vérification contrôle les sommes de contrôle, le chargement des modèles et du domaine de 189 médicaments, puis le parcours complet de chaque spécialité (page, PDF, JSON, vue patient). Un second script installe PyPGx 0.27.0 dans un environnement séparé, avec pandas en version inférieure à 3 : PyPGx 0.27.0 échoue avec pandas 3 sur une erreur peu lisible (« setting an array element with a sequence »). L'application détecte ce cas et affiche la cause et la commande à lancer, plutôt que l'erreur brute. Le script vérifie aussi la présence de Java. L'application a été testée sous Linux ; elle n'a pas été testée sous macOS, sous Windows natif ni sur une machine sans Java. Le code d'entraînement et le corpus sont conservés dans le dépôt du projet.

### 5.10 Limites de l'application

1. **Médicaments à règle seule.** 21 médicaments dont la décision repose sur une règle seule (gènes mitochondriaux, RYR1 et CACNA1S, CFTR, certains allèles HLA) ne sont pas intégrés aux réseaux.
2. **Lecture la plus prudente.** Pour les antidépresseurs tricycliques tertiaires et le voriconazole avec CYP2C19 rapide ou ultrarapide, l'étiquette du corpus est EVITER, c'est-à-dire la lecture la plus prudente, alors que la force de la recommandation source est « Optional » (clomipramine) ou « Moderate » (voriconazole) ; l'écran rouge « à éviter » sur-affirme. Les règles à un gène du corpus ne portent pas la force de la recommandation.
3. **Classement ATC.** L'ibuprofène (code ATC C01EB16) apparaît dans « autres préparations cardiaques » de la spécialité Cardiologie, ce qui est trompeur pour un adulte ; cela n'affecte pas les étiquettes génétiques.
4. **Domaine par médicament.** Le contrôle « hors domaine » porte sur la combinaison des gènes de chaque médicament. Il ne repère pas un profil atypique dans son ensemble : sur l'ensemble final, un seul profil porteur de valeurs rares (G6PD non typé, CYP2C9 à 0,25, F5 et G6PD à 0) concentre 26 des 35 erreurs du réseau, alors que la combinaison des gènes de chaque médicament concerné avait été vue (section 6.7). L'abstention en écarte 16 ; les 10 autres seraient affichées avec une confiance d'au moins 0,998. Il reste deux protections : la règle affichée à côté de l'avis, et le second avis de XGBoost, juste pour ce profil, qui ferait apparaître un désaccord. Un contrôle portant sur le profil complet n'a pas été mis en œuvre.
5. **Saisies obligatoires.** CYP2D6 et les allèles HLA doivent être saisis par l'utilisateur ; sans saisie, les médicaments concernés sont non évalués.
6. **Références.** La référence affichée pour une directive est la publication générale de la source ; la publication précise de chaque directive (environ 152 identifiants PA) n'est pas encore associée.
7. **Codage de CYP2C9 et comparaison à PharmCAT.** Sur 104 personnes, la recommandation affichée est retrouvée chez PharmCAT pour 95,9 % des lignes comparables (chapitre 8). Une partie des écarts tient à la formulation (règle « aucune action » écrite différemment) et à la structure (une règle par gène dans l'application, une seule chez PharmCAT). Un écart est réel : pour la warfarine, des génotypes de score d'activité 1,5 autres que \*1/\*2 (\*1/\*5, \*1/\*8, \*1/\*11) reçoivent la règle DPWG de \*1/\*2, « aucune action », alors que PharmCAT, qui lit la directive allèle par allèle, recommande 65 % de la dose initiale (5 personnes sur 70 comparables). C'est la conséquence du codage par score d'activité (section 5.3) ; l'écran l'indique par la mention du génotype lu (section 5.4), mais ne corrige pas l'avis.
8. **Sécurité et usage.** Le serveur n'a pas d'authentification ; les seuils d'abstention sont des quantiles et non des seuils de risque clinique ; aucune évaluation d'utilisabilité auprès de cliniciens n'a été faite.
9. **Textes tronqués.** Dans la table des règles à un gène, 79 textes de directive sur 709 sont tronqués à 260 caractères ; la classe prédite n'en dépend pas, mais le texte affiché est incomplet et la fiche liée de la directive doit être consultée.
10. **Refus prudents et messages.** Un VCF valide peut être refusé si l'assemblage ne peut pas être établi. C'est le cas d'un fichier sans longueur de chromosome dans l'en-tête dont les enregistrements, concentrés dans les régions des gènes, ne penchent pas assez vers un assemblage : pour un fichier GRCh38 extrait d'un VCF multi-échantillons, le rapport observé est de 4,7 pour un seuil de 5. Le refus est voulu ; le message, en revanche, renvoie à une option de la ligne de commande (« --assembly ») que l'interface web ne propose pas. Le seuil de 5 n'a pas été modifié : le régler au vu d'un seul fichier aurait été arbitraire.

### 5.11 Parcours de l'application sur un exemple

Cette section montre l'application en fonctionnement, écran par écran, sur un exemple unique, et explique ce que chaque partie affiche. Les écrans principaux sont reproduits ici ; les écrans complémentaires sont en annexe B. L'exemple est le fichier NA19472.vcf : un échantillon public du projet 1000 Genomes, reconstruit à partir du pypgx-bundle (génome GRCh38), qui n'est pas un patient réel et ne fait pas partie de l'ensemble final de 138 profils. La spécialité choisie est la cardiologie, parce qu'elle réunit des familles où le profil change l'avis (antivitamines K, statines) et d'autres où il ne le change pas. Toutes les captures viennent d'une même analyse, avec la lecture réelle du VCF par PyPGx. Cet exemple illustre le fonctionnement ; il ne mesure pas la performance, qui est traitée aux chapitres 6 à 8.

**Étape 1 : accueil et lancement de l'analyse (figure 5.2).** L'utilisateur fournit un fichier VCF (.vcf ou .vcf.gz, un seul patient, génome GRCh37 ou GRCh38, 500 Mo au maximum) et choisit la spécialité du médecin parmi 17 spécialités. Un champ facultatif permet d'indiquer l'identifiant du patient quand le fichier en contient plusieurs. La page rappelle que l'outil est un outil de recherche non validé cliniquement, que le fichier VCF est supprimé du serveur à la fin de l'analyse, et elle liste les sources scientifiques des règles, de la lecture du génome et des modèles. Le libellé du bouton de choix du fichier est celui du navigateur utilisé pour la capture.

::: {custom-style="FigureImg"}
![](fig/cap_01_accueil.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure 5.2 : Page d'accueil : dépôt du fichier VCF et choix de la spécialité (exemple NA19472).
:::

**Étape 2 : analyse en cours (figure B.1).** Après le lancement, une page de progression affiche l'étape en cours (ici « Lecture des gènes du patient », c'est-à-dire l'appel d'allèles par PyPGx) et une barre d'avancement. L'analyse de cet échantillon a pris 86 secondes (section 5.8). La page de résultat s'ouvre seule à la fin.

**Étape 3 : recommandation pour le patient (figure 5.3).** La page de résultat commence par la recommandation pour la spécialité choisie, en blocs de couleur.

- Bloc vert, « À prescrire à la dose habituelle » : antivitamines K (phenprocoumone, acénocoumarol, warfarine), six statines, quatre antiagrégants plaquettaires (prasugrel, aspirine, ticagrélor, clopidogrel), et l'ibuprofène, hors groupe de choix. Les médicaments d'une même famille sont dits « au même niveau pour ce patient » : les gènes lus ne permettent pas de les départager et le choix revient au médecin (section 5.5).
- Bloc orange, « Dose à adapter ou à surveiller » : fluindione et fluvastatine, pour lesquelles la phrase « Ce qui change pour ce patient » nomme le gène responsable, CYP2C9 (score d'activité 1,5, génotype \*1/\*8) ; et l'hydralazine, hors groupe de choix, du fait du génotype NAT2 lent (\*5/\*6).
- Bloc rouge, « À éviter aussi pour ce patient (autres spécialités) » : six médicaments hors cardiologie (voriconazole et cinq antidépresseurs tricycliques), signalés parce que le patient est métaboliseur rapide pour CYP2C19 (\*1/\*17). Ce bloc existe pour qu'un avis « à éviter » ne soit jamais caché par le choix de la spécialité. La nuance sur ces avis (lecture la plus prudente de la directive) est décrite en section 5.10, point 2.

La ligne « Non évalués pour ce patient : 14 médicaments » est aussi importante que les avis : pour ces médicaments (par exemple métoprolol, flécaïnide, propafénone), l'application ne donne aucun avis parce que le gène CYP2D6 ne peut pas être lu dans un VCF de variants ponctuels. L'écran précise que « non évalué » ne veut pas dire « sans risque ». C'est la protection décrite en section 5.4 : le réseau n'est pas interrogé sur un médicament dont un gène nécessaire manque, situation où il est fragile (section 8.5).

::: {custom-style="FigureImg"}
![](fig/cap_03_resultats_haut.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure 5.3 : Page de résultat : recommandation pour la spécialité, médicaments non évalués et médicaments à éviter dans les autres spécialités (NA19472, Cardiologie).
:::

**Étape 4 : avis et scores des trois modèles (figure 5.4).** Un volet dépliable affiche, pour chaque médicament des groupes de la spécialité, l'avis du réseau (DL), la directive officielle, et les avis de XGBoost et de Random Forest, avec un score entre 0 et 1 sous chaque avis. Dans l'exemple, les quatre colonnes donnent le même avis pour les treize médicaments ; le score du réseau est supérieur ou égal à 0,999, celui de XGBoost va de 0,908 à 0,991 et celui de Random Forest de 0,494 à 0,716. Deux précautions de lecture sont écrites sous le tableau et valent pour tout le mémoire. D'abord, le score est la certitude du modèle dans son propre avis, pas la probabilité que l'avis soit juste cliniquement. Ensuite, seul le score du réseau est calibré dans l'application ; les scores bas de Random Forest (moyenne de 100 arbres) ne signalent pas un désaccord. L'accord des trois modèles n'est pas une confirmation indépendante : ils ont appris les mêmes règles (chapitre 6).

::: {custom-style="FigureImg"}
![](fig/cap_04_trois_modeles.png){width=15.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure 5.4 : Avis et scores du réseau, de la directive officielle, de XGBoost et de Random Forest pour les médicaments de la spécialité.
:::

**Étape 5 : recherche d'un médicament (figure B.2).** Un champ de recherche donne la fiche d'un médicament précis, quelle que soit la spécialité. Pour la warfarine, le réseau, la directive, XGBoost (score 0,942) et Random Forest (score 0,656) donnent tous « À dose standard », sans alerte. Le volet « Pourquoi ? » montre les deux règles DPWG appliquées : celle de VKORC1, pour un patient sans allèle rs9923231, et celle de CYP2C9. Pour CYP2C9, la règle appliquée est celle de \*1/\*2, et l'écran précise que le génotype lu est \*1/\*8, de même score d'activité. **Cet avis illustre la limite décrite en section 5.10, point 7 :** pour deux personnes de ce même génotype, PharmCAT, qui lit la directive DPWG allèle par allèle, recommande 65 % de la dose initiale (chapitre 8). L'avis affiché est donc fidèle à la règle du corpus, mais pas à la lecture allèle par allèle de la directive ; la mention du génotype lu est ce qui permet à un lecteur averti de le remarquer.

**Étape 6 : détails pour les experts (figure B.3).** Ce volet reprend chaque famille de médicaments (classe ATC de niveau 4) et explique l'avis médicament par médicament : tableau des quatre avis, gènes regardés avec ce qui a été lu chez le patient, texte de la directive officielle avec sa source et l'identifiant de sa fiche, et une phrase en langage simple. Il indique aussi quel gène change la recommandation : pour les antivitamines K, « si CYP2C9 était normal, le programme ajouterait fluindione ». Cette phrase vient d'un second calcul où un seul gène est remis à la valeur normale, le reste du profil restant identique.

**Étape 7 : comment le programme a travaillé (figure B.4).** Cet encadré résume le calcul en trois points : le réseau reçoit tous les gènes du patient en une seule fois (un gène non lu est signalé « non lu » et n'est jamais supposé normal) ; il calcule en un seul passage un avis pour chacun des 189 médicaments ; le décompte de ces avis est affiché. Pour NA19472, le réseau donne 140 « à dose standard », 17 « adapter la dose », 19 « surveiller » et 13 « éviter », soit 189 avis. Une partie de ces avis n'est pas affichée à l'utilisateur, par prudence, quand un gène nécessaire n'a pas été lu ou que la combinaison des gènes n'a jamais été vue.

**Étape 8 : gènes lus chez le patient (figure B.5).** Le tableau de vérification donne, pour chacune des 20 variables génétiques, la valeur de codage transmise au réseau, le phénotype et le génotype lus, et l'origine de la valeur. Pour NA19472, 15 gènes sont lus dans le VCF par PyPGx (par exemple CYP2C9 \*1/\*8, CYP2C19 \*1/\*17, CYP3A5 \*1/\*6, NAT2 \*5/\*6, TPMT \*3C/\*8) ; CYP2D6 est « non déterminé » et les quatre allèles HLA sont « non renseignés ». Les libellés y sont ceux du lecteur, en anglais, pour la traçabilité (section 5.6). Ce tableau permet de remonter d'un avis au génotype qui l'explique. Il faut le lire avec la réserve de la section 8.2 : la concordance du génotype avec la référence GeT-RM est élevée pour CYP2C9, CYP3A5, TPMT et CYP2C19, et faible pour CYP2B6, SLCO1B1, UGT1A1 et DPYD.

**Étape 9 : compléter avec un test de laboratoire (figures 5.5 et 5.6).** Le gène CYP2D6 et les allèles HLA ne se lisent pas dans un VCF de variants ponctuels (section 5.3). Si le patient dispose d'un résultat de laboratoire, l'utilisateur peut le saisir dans un formulaire facultatif : phénotype CYP2D6 (métaboliseur lent, intermédiaire, normal ou ultra-rapide) et, pour chacun des quatre allèles HLA, « négatif » ou « positif ». Le formulaire explique à quoi sert la saisie, ce qu'elle change et quels médicaments sont concernés ; il précise que « non testé » n'est pas « négatif » et que les valeurs saisies ne sont pas vérifiées par l'application.

Pour la démonstration, deux valeurs fictives ont été saisies (elles ne décrivent pas l'échantillon NA19472) : CYP2D6 « métaboliseur lent » et HLA-B\*57:01 « positif » (figure 5.5). Après la mise à jour (figure 5.6) :

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
Figure 5.5 : Formulaire « Compléter avec un test de laboratoire » avec deux valeurs fictives saisies pour la démonstration.
:::

::: {custom-style="FigureImg"}
![](fig/cap_12_apres_completion.png){width=14.2cm}
:::

::: {custom-style="LegendeFigure"}
Figure 5.6 : Page de résultat après la saisie des deux valeurs de laboratoire fictives.
:::

**Étape 10 : vue patient (figure B.6).** Une page séparée reformule le résultat pour le patient, sans score ni tableau technique : un avertissement (« n'arrêtez et ne changez aucun traitement de votre propre initiative »), puis les médicaments à éviter ou à discuter en priorité, puis les médicaments de la spécialité avec une phrase simple pour chacun.

**Étape 11 : rapport PDF, fiche JSON et suppression des données (figure 5.7).** Le bouton « Télécharger le PDF » produit un rapport de 6 pages et 11 sections pour cet exemple, avant la saisie de laboratoire. Sa première page donne le fichier, la spécialité, la date, l'avertissement, puis un résumé sur les 189 médicaments : 6 à éviter, 110 compatibles (réseau, XGBoost et règle d'accord), 1 à vérifier et 72 non évalués, dont 60 dépendent de CYP2D6. Le médicament à vérifier est le citalopram, hors cardiologie, écarté par l'abstention (confiance du réseau sous le seuil). Le rapport reprend ensuite le tableau des gènes, les médicaments à éviter, les médicaments proposés pour la spécialité, les médicaments non évalués, une explication en langage simple, la lecture des scores, les directives utilisées, les références, la méthode et les limites. La « Fiche JSON » exporte les mêmes informations sous forme structurée. Le bouton « Supprimer mes données » efface le résultat immédiatement ; sans action, il est effacé après 24 heures (section 5.7).

::: {custom-style="FigureImg"}
![](fig/cap_11_pdf-1.png){width=12.5cm}
:::

::: {custom-style="LegendeFigure"}
Figure 5.7 : Première page du rapport PDF produit par l'application.
:::

**Ce que montre et ne montre pas cet exemple.** Le parcours montre que la chaîne complète fonctionne, du fichier VCF au rapport, que chaque avis est accompagné de sa source et de ce qui a été lu chez le patient, et que l'application préfère ne pas répondre plutôt que de répondre sans le gène nécessaire (72 médicaments sur 189 non évalués tant que CYP2D6 et les allèles HLA manquent). Il montre aussi une limite : l'avis sur la warfarine reproduit fidèlement la règle du corpus, sans reproduire la lecture allèle par allèle de la directive DPWG. Il ne montre pas que les avis sont justes : un seul échantillon public est utilisé, les valeurs de laboratoire sont fictives, et les avis reproduisent les directives. La fidélité aux directives est mesurée au chapitre 6 et la comparaison à des références externes au chapitre 8.

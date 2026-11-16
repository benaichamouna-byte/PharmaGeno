## Annexe E : Compléments sur l'application

Cette annexe donne le détail du chapitre 5 : modules et routes, lecture du fichier VCF, moteur et sorties, tests, installation et description complète des limites. Les numéros de section entre parenthèses renvoient au chapitre 5 ou aux autres chapitres.

### E.1 Architecture et exécution

L'application est écrite en Python avec le cadriciel Flask (Pallets), des gabarits Jinja2 et la bibliothèque ReportLab pour le PDF. Les quatre modèles finaux du chapitre 4 sont chargés au démarrage : réseau de profil (189 médicaments × 4 actions), réseau de choix (44 classes ATC de niveau 4), XGBoost et Random Forest.

::: {custom-style="LegendeTableau"}
Tableau E.1 : Modules de l'application et rôle de chacun
:::

| Module | Rôle |
| --- | --- |
| lecteur de VCF (vcf\_to\_profile\_v9) | contrôle du fichier, appel de PyPGx, conversion en profil |
| moteur (moteur\_v10j) | prédictions des modèles, alertes, couche de sécurité, gènes décisifs, choix dans une classe |
| recommandeur (recommandation\_v8r) | catégories, alternatives, textes pour le clinicien et pour le patient |
| rapport (rapport\_pdf\_v8u) | rapport PDF de 11 à 13 sections |
| références (references\_v8r) | références et sources affichées à l'écran et dans le PDF |

Le serveur écoute uniquement l'adresse locale 127.0.0.1 (port 5000 par défaut) ; il n'a pas d'authentification et ne doit pas être exposé sur Internet. La taille maximale d'un fichier téléversé est de 500 Mo par défaut. Une seule analyse VCF est traitée à la fois, les autres attendent, parce que l'appel des génotypes par PyPGx occupe la machine pendant environ une minute et demie. PyPGx s'exécute dans un environnement Python séparé (option --pgx-python), parce qu'il exige des versions de bibliothèques incompatibles avec celles des modèles (section E.5). Chaque réponse porte les en-têtes Cache-Control: no-store, X-Content-Type-Options: nosniff, Referrer-Policy: no-referrer et une Content-Security-Policy restrictive. Les routes sont les suivantes.

::: {custom-style="LegendeTableau"}
Tableau E.2 : Routes du serveur et fonction de chacune
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

### E.2 Lecture du fichier VCF

**Contrôles du fichier.** Avant tout appel, le fichier est refusé avec un message s'il est illisible, s'il n'est pas trié par chromosome et position (il est alors impossible de le compresser et de l'indexer), s'il ne contient aucun échantillon ou plusieurs échantillons sans que l'un soit désigné (un seul patient par analyse), ou si l'assemblage du génome (GRCh37 ou GRCh38) ne peut pas être établi ou est contradictoire. L'assemblage est lu de deux façons : dans l'en-tête, par la longueur déclarée du chromosome 1, et par la position des enregistrements, comptés dans les régions des gènes selon les coordonnées de chacun des deux assemblages. Le décompte n'est retenu que s'il penche au moins cinq fois plus vers un assemblage que vers l'autre ; en dessous, et sans longueur de chromosome dans l'en-tête, le fichier est refusé plutôt que lu sur une hypothèse (section E.6, point 9). Un fichier non compressé est copié sous forme compressée et indexée. Un gène n'est « couvert » que si le VCF contient au moins un enregistrement dans sa région ; sinon il est déclaré non déterminé, car un VCF de variants ne distingue pas un gène normal d'un gène non séquencé. Cette heuristique est prudente mais imparfaite pour un gène court : sur les VCF 1000 Genomes, le minimum observé est de 0 à 3 variants selon les gènes. Les génotypes haploïdes du chromosome X (hommes) sont convertis en homozygotes diploïdes.

**Appel des génotypes.** PyPGx 0.27.0 (Sherman, Claw et Lee, 2024), pipeline run-chip-pipeline, avec le paquet de référence pypgx-bundle 0.27.0 et Java, lit 18 gènes : ABCG2, CFTR, CYP2B6, CYP2C19, CYP2C9, CYP2D6, CYP3A4, CYP3A5, CYP4F2, DPYD, F5, G6PD, NAT2, NUDT15, SLCO1B1, TPMT, UGT1A1 et VKORC1. CFTR et CYP4F2 ne font pas partie des 20 variables du réseau de profil (section 3.5). CYP2D6 n'est jamais appelé depuis un VCF de variants ponctuels, car son phénotype dépend de délétions et de duplications : il est toujours « non déterminé » tant que l'utilisateur ne saisit pas un résultat de test externe. Les quatre allèles HLA (HLA-B\*15:02, HLA-B\*57:01, HLA-B\*58:01, HLA-A\*31:01) ne se lisent pas non plus dans un VCF de ce type : l'utilisateur les saisit (positif, négatif, non testé) dans un formulaire facultatif.

**Choix du pipeline.** La documentation de PyPGx décrit `run-chip-pipeline` comme le pipeline des données de puces à ADN et `run-ngs-pipeline` comme celui des données de séquençage, ce dernier acceptant un VCF seul pour les gènes sans variation structurale et exigeant une profondeur de couverture pour les gènes qui en comportent (PyPGx, documentation de l'interface en ligne de commande, consultée le 16 novembre 2026). Les fichiers traités ici sont des VCF de variants ponctuels, sans fichier d'alignement ni profondeur de couverture ; c'est le pipeline de puces qui a été employé, avec le VCF comme unique entrée et sans l'option d'imputation. Deux conséquences sont assumées et déclarées : aucun appel de variation structurale n'est revendiqué, ce qui est cohérent avec le fait que CYP2D6 est toujours laissé « non déterminé » ; et le pipeline de séquençage n'a pas été exécuté sur ces mêmes fichiers, de sorte que l'écart éventuel entre les deux pipelines n'est pas mesuré. Ce choix n'est donc pas justifié par une comparaison interne : la seule garantie apportée est externe, à savoir la concordance des génotypes obtenus avec les matériaux de référence GeT-RM sur 104 personnes (section 8.2).

**Codage en valeurs.** Chaque génotype est converti en la valeur numérique utilisée à l'entraînement, selon une méthode propre au gène : phénotype PyPGx pour ABCG2, CYP2B6, CYP2C19, CYP3A5, DPYD, F5 et UGT1A1 ; moyenne des scores d'activité CPIC des deux allèles, divisée par 2, pour CYP2C9 (table data/cyp2c9\_alleles\_cpic\_v1.csv ; un allèle absent de la table donne « non déterminé ») ; génotype puis table CPIC pour NAT2, CYP3A4, NUDT15, TPMT et SLCO1B1 ; phénotype G6PD de PyPGx (0 ; 0,5 ; 1) ; nombre d'allèles rs9923231 pour VKORC1 (0 allèle : 1 ; 1 allèle : 0,5 ; 2 allèles : 0). Un gène non déterminé vaut « manquant » : il n'est jamais remplacé par la valeur normale et il active l'indicateur d'absence du réseau (section 3.5). Une valeur saisie par l'utilisateur (CYP2D6 : 0 ; 0,5 ; 1 ; 2 ; allèles HLA) est tracée comme telle et jamais présentée comme lue dans le VCF.

**Concordance avec les profils d'entraînement.** Trois contrôles ont été faits sur les échantillons 1000 Genomes.

- Sur les 1 379 profils du corpus, les valeurs obtenues à partir du génotype PyPGx enregistré sont identiques à celles du profil d'entraînement pour G6PD, NAT2, CYP3A4, NUDT15, TPMT, SLCO1B1 et VKORC1 (1 379 sur 1 379), ainsi que pour CFTR et CYP4F2 (hors modèle).
- Pour les gènes codés par phénotype, la concordance avec les valeurs d'origine du corpus est de 95,7 % pour ABCG2 et de 92,8 % pour CYP2B6 ; elle est de 99,8 % ou plus pour CYP2C19 (99,85 %), CYP3A5 (99,93 %), F5 et UGT1A1 (100 %). DPYD n'a pas été mesuré. Ce n'est donc pas une identité.
- Pour CYP2C9, codé par score d'activité, le lecteur redonne la valeur du profil d'entraînement pour 1 378 profils sur 1 378 à partir du génotype PyPGx enregistré (un profil est non déterminé des deux côtés).

Ces contrôles montrent que le lecteur reproduit le codage du corpus à partir du même génotype ; ils ne mesurent pas l'exactitude du génotype PyPGx lui-même, qui est comparée à une référence indépendante au chapitre 8. Le codage de CYP2C9 par score d'activité a une conséquence mesurée à ce même chapitre : des génotypes différents de même score, comme \*1/\*2 et \*1/\*8, reçoivent la même valeur et donc la même règle (section E.6, point 6).

### E.3 Moteur, recommandation et sorties

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

Les médicaments proposés en remplacement d'un médicament à éviter sont ceux du même sous-groupe ATC4 dont le statut est ok et l'action STANDARD ; ce sont des candidats à examiner et non des équivalents thérapeutiques (section 5.4). Le texte affiché pour chaque directive est celui de la table de règles du projet, en anglais ou en français selon la règle ; la fiche de la directive, liée par son identifiant ClinPGx, fait foi.

**Ce qui est affiché pour expliquer un avis.** Pour chaque médicament, l'écran indique ce qui a été lu chez le patient (phénotype et génotype) pour les gènes de la règle. Quand la règle appliquée a été écrite pour un autre génotype de même valeur de codage, l'écran le dit explicitement, par exemple « règle appliquée à la valeur de codage du patient ; génotype lu chez ce patient : \*1/\*8 ». Cette mention rend visible, au moment de la lecture, la limite du codage de CYP2C9 décrite en section E.2.

Pour chaque classe ATC4 de la spécialité qui contient au moins deux médicaments du modèle, le réseau de choix (section 4.6) propose l'ensemble des médicaments dont la probabilité atteint la moitié de la probabilité maximale. La couche de sécurité retire de cet ensemble tout médicament que la section 5.4 classe « à éviter » ; les médicaments retirés et écartés restent visibles. Les gènes qui expliquent l'avis sont déterminés par substitution : pour chaque gène, la valeur du patient est remplacée par la valeur normale et l'on regarde si l'ensemble proposé change ; un test vérifie que cet affichage est identique à un recalcul indépendant.

Un médicament n'apparaît que dans une ligne de la synthèse en feux tricolores, la plus prudente : rouge avant orange avant vert. Vert : recommandé par le réseau de choix avec le conseil STANDARD ; orange : ADAPTER\_DOSE ou SURVEILLER ; rouge : à éviter. Un médicament évalué de la spécialité qui n'appartient à aucun groupe de choix, ou qui est le seul évaluable de son groupe, est placé dans le bloc de son avis avec la mention « hors groupe de choix », ou dans un bloc « À faire vérifier par un professionnel » si son statut l'exige. Cette règle garantit qu'aucun médicament évalué ne disparaît de l'écran ; elle est vérifiée pour toutes les spécialités par un test. L'ordre des médicaments proposés (action, puis intervention d'un gène du patient, puis probabilité) est une règle d'affichage, pas une validation clinique ; les probabilités de médicaments équivalents sont quasi égales.

La page de résultats place en premier la recommandation pour le patient, puis les alertes de sécurité, et replie le contenu scientifique dans « Détails pour les experts » (glossaire, tableau « Qui donne l'avis » avec le réseau, la directive, XGBoost et le Random Forest, score de 0 à 1 de chaque modèle). Les scores sont arrondis vers le bas et un score de 0,999 ou plus s'écrit « ≥ 0,999 » : un modèle n'est jamais présenté comme certain à 100 %. La légende précise que ces scores mesurent la certitude de reproduire la règle et non la justesse clinique. Les libellés de phénotype sont traduits en français, sauf dans le « Tableau complet pour vérification », qui garde volontairement la sortie brute du lecteur afin qu'un avis puisse être rapproché du génotype exact qui l'a produit.

La vue patient reformule en langage simple. Le PDF compte de 11 à 13 sections, numérotées sans saut : deux sections n'apparaissent que si elles ont un contenu (médicaments à règle seule, médicament recherché). Il reprend les gènes, les médicaments à éviter, les médicaments proposés, les médicaments à vérifier et non évalués, une explication pour le patient, la lecture des scores, les directives utilisées (liens ClinPGx pour les identifiants PA…), les références et la méthode avec ses limites. Le JSON contient le profil, la lecture du VCF, les catégories, la recommandation et la synthèse en feux tricolores.

Le fichier VCF téléversé et tous les fichiers intermédiaires sont supprimés à la fin de l'analyse, que celle-ci réussisse ou non. Seules les valeurs du profil par gène sont conservées dans un fichier de tâche, jusqu'au clic sur « Supprimer mes données » ou pendant 24 heures au plus (purge automatique). Ces trois comportements sont vérifiés par des tests. L'application n'a pas d'authentification : la confidentialité repose sur l'usage en local. Pour un accès réseau, la documentation d'installation recommande un serveur mandataire avec authentification et HTTPS.

### E.4 Tests

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

La chaîne complète a aussi été exécutée sur le VCF réel de l'échantillon NA19472 (annexe B), reconstruit à partir des fichiers 1000 Genomes du pypgx-bundle, hors ensemble final. L'analyse prend 86 secondes. Elle a été faite dans deux environnements indépendants, avec les mêmes versions de PyPGx et du pypgx-bundle : les génotypes lus sont identiques pour les 22 gènes, dont CYP2C9 \*1/\*8 (score d'activité 1,5, valeur de profil 0,75). Ces tests vérifient la logique de l'application et la reproductibilité de la lecture, non la performance clinique : un échantillon est une illustration, pas une statistique. La comparaison sur 104 personnes est présentée au chapitre 8.

### E.5 Installation et reproductibilité

L'application est distribuée sous la forme d'une archive qui contient le code, les modèles, les données nécessaires à l'exécution et un manifeste de sommes de contrôle. Elle demande Python 3.12 ou plus récent et PyTorch ; la suite de tests a été exécutée avec PyTorch 2.11.0. Un script de vérification contrôle les sommes de contrôle, le chargement des modèles et du domaine de 189 médicaments, puis le parcours complet de chaque spécialité (page, PDF, JSON, vue patient). Un second script installe PyPGx 0.27.0 dans un environnement séparé, avec pandas en version inférieure à 3 : PyPGx 0.27.0 échoue avec pandas 3 sur une erreur peu lisible (« setting an array element with a sequence »). L'application détecte ce cas et affiche la cause et la commande à lancer, plutôt que l'erreur brute. Le script vérifie aussi la présence de Java. L'application a été testée sous Linux ; elle n'a pas été testée sous macOS, sous Windows natif ni sur une machine sans Java. Le code d'entraînement et le corpus sont conservés dans le dépôt du projet.

### E.6 Limites de l'application (description complète)

1. **Médicaments à règle seule.** 21 médicaments dont la décision repose sur une règle seule (gènes mitochondriaux, RYR1 et CACNA1S, CFTR, certains allèles HLA) ne sont pas intégrés aux réseaux. L'ibuprofène (code ATC C01EB16) apparaît dans « autres préparations cardiaques » de la spécialité Cardiologie, ce qui est trompeur pour un adulte ; cela n'affecte pas les étiquettes génétiques.
2. **Lecture la plus prudente.** Pour les antidépresseurs tricycliques tertiaires et le voriconazole avec CYP2C19 rapide ou ultrarapide, l'étiquette du corpus est EVITER, c'est-à-dire la lecture la plus prudente, alors que la force de la recommandation source est « Optional » (clomipramine) ou « Moderate » (voriconazole) ; l'écran rouge « à éviter » sur-affirme. Les règles à un gène du corpus ne portent pas la force de la recommandation.
3. **Domaine par médicament.** Le contrôle « hors domaine » porte sur la combinaison des gènes de chaque médicament. Il ne repère pas un profil atypique dans son ensemble : sur l'ensemble final, un seul profil porteur de valeurs rares (G6PD non typé, CYP2C9 à 0,25, F5 et G6PD à 0) concentre 26 des 35 erreurs du réseau, alors que la combinaison des gènes de chaque médicament concerné avait été vue (section 6.7). L'abstention en écarte 16 ; les 10 autres seraient affichées avec une confiance d'au moins 0,998. Il reste deux protections : la règle affichée à côté de l'avis, et le second avis de XGBoost, juste pour ce profil, qui ferait apparaître un désaccord. Un contrôle portant sur le profil complet n'a pas été mis en œuvre.
4. **Saisies obligatoires.** CYP2D6 et les allèles HLA doivent être saisis par l'utilisateur ; sans saisie, les médicaments concernés sont non évalués.
5. **Références.** La référence affichée pour une directive est la publication générale de la source ; la publication précise de chaque directive (environ 152 identifiants PA) n'a pas été associée dans le cadre de ce travail.
6. **Codage de CYP2C9 et comparaison à PharmCAT.** Sur 104 personnes, la recommandation affichée est retrouvée chez PharmCAT pour 95,9 % des lignes comparables (chapitre 8). Une partie des écarts tient à la formulation (règle « aucune action » écrite différemment) et à la structure (une règle par gène dans l'application, une seule chez PharmCAT). Un écart est réel : pour la warfarine, des génotypes de score d'activité 1,5 autres que \*1/\*2 (\*1/\*5, \*1/\*8, \*1/\*11) reçoivent la règle DPWG de \*1/\*2, « aucune action », alors que PharmCAT, qui lit la directive allèle par allèle, recommande 65 % de la dose initiale (5 personnes sur 70 comparables). C'est la conséquence du codage par score d'activité (section E.2) ; l'écran l'indique par la mention du génotype lu (section E.3), mais ne corrige pas l'avis.
7. **Sécurité et usage.** Le serveur n'a pas d'authentification ; les seuils d'abstention sont des quantiles et non des seuils de risque clinique ; aucune évaluation d'utilisabilité auprès de cliniciens n'a été faite.
8. **Textes tronqués.** Dans la table des règles à un gène, 79 textes de directive sur 709 sont tronqués à 260 caractères ; la classe prédite n'en dépend pas, mais le texte affiché est incomplet et la fiche liée de la directive doit être consultée.
9. **Refus prudents et messages.** Un VCF valide peut être refusé si l'assemblage ne peut pas être établi. C'est le cas d'un fichier sans longueur de chromosome dans l'en-tête dont les enregistrements, concentrés dans les régions des gènes, ne penchent pas assez vers un assemblage : pour un fichier GRCh38 extrait d'un VCF multi-échantillons, le rapport observé est de 4,7 pour un seuil de 5. Le refus est voulu ; le message, en revanche, renvoie à une option de la ligne de commande (« --assembly ») que l'interface web ne propose pas. Le seuil de 5 n'a pas été modifié : le régler au vu d'un seul fichier aurait été arbitraire.

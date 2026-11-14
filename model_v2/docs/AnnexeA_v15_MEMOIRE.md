## Annexe A : Essais négatifs, abandonnés ou corrigés

Cette annexe récapitule les essais qui ont été abandonnés, corrigés ou qui ont donné un résultat négatif, les versions successives de l'application et les erreurs de méthode relevées pendant le projet. Trois précautions de lecture s'appliquent. Les scores obtenus sur des versions différentes du corpus ne sont pas comparables entre eux, car le corpus, le découpage et les modèles ont changé d'un essai à l'autre ; chaque ligne indique donc la version sur laquelle elle porte. Tous ces scores mesurent un accord avec les règles, pas une exactitude clinique (chapitre 3). Enfin, une conclusion établie sur une version du corpus n'est pas transportée aux suivantes : lorsqu'elle a changé, le tableau le dit.

### A.1 Synthèse des essais

::: {custom-style="LegendeTableau"}
Tableau A.1 : Essais abandonnés, négatifs ou corrigés
:::

| Essai | Ce qui s'est passé | Section du mémoire |
| --- | --- | --- |
| Jeu v2 de 145 303 lignes | F1 0,736, moins bon que le jeu à 31 gènes ; étiquettes non validées par CPIC pour 7 gènes ; abandonné au profit d'un corpus construit sur les règles | — |
| DL sur le corpus v4 | F1 0,9642 contre 0,9993 en v7 ; cause non établie | — |
| DL sans poids de classes | F1 0,7374 : la classe SURVEILLER n'est jamais apprise | section 4.2 |
| Poids EVITER ×4 et ×8 | Moins d'EVITER manqués mais F1 plus bas (0,9880 ; 0,9651) ; coefficient ×1 retenu en v13 après recherche | section 4.3 |
| Test des combinaisons retirées (version 1) | Faille de conception ; conclusion retirée | — |
| Test des combinaisons jamais vues sur le moteur de règles | Annulé avant lancement | — |
| Abstention présentée comme un avantage du réseau | Constat établi sur un corpus antérieur : la capacité à écarter ses propres erreurs n'est pas propre au réseau. Non refait sur la v15 | section 6.3 |
| Classement écrit à la main présenté comme une prédiction du réseau (application v8h) | Erreur de présentation, remplacée par le réseau de choix | tableau A.2 |
| Règle « Optional = standard » (corpus v11) | 159 erreurs pour la sertraline ; abandonnée en v12 | — |
| Codage des gènes en une colonne par valeur | Plus d'EVITER manqués (76 contre 55) ; non retenu | — |
| Seuil sur la probabilité de la classe EVITER calculé après coup | Biais de sélection ; inutilisable sans seuil fixé a priori sur la validation interne | section 6.3 |
| Second tour de recherche d'hyperparamètres | Interrompu, jamais utilisé | section 4.3 |
| Niveau « association » | Signal faible ; une loi a priori simple fait aussi bien ou mieux sur les couples jamais vus | section 6.7 |
| Généralisation à un médicament jamais vu | Négatif : le réseau ne dépasse pas des références simples ; architecture non intégrée à l'application | section 6.7 |
| Règle warfarine : génotype \*1/\*2 et VKORC1 | \*1/\*2 non soutenu en analyse brute ; VKORC1 explique environ six fois plus de variance de la dose que CYP2C9 | chapitre 7 |
| Corpus v14 provisoire (183 médicaments) et v14b | Remplacés par le corpus gelé de 189 médicaments | — |
| Réseau contre XGBoost sur étiquettes de règles | Sur les corpus v12 et v14, XGBoost reproduisait les règles mieux que le réseau (F1 0,9996 contre 0,9974 en v12). **Sur le corpus v15, la différence n'est plus tranchée et les deux modèles sont déclarés équivalents pour la configuration déployée** ; XGBoost conserve l'avantage sur les situations à éviter manquées | section 6.5 |
| Règles du corpus corrigées en v15 | Trois corrections à partir du texte des directives (règle VKORC1 de la warfarine, actions DPWG des diplotypes CYP2C9, grille à deux gènes TPMT × NUDT15 des thiopurines) ; 433 lignes modifiées et 1 968 ajoutées, aucune supprimée. La conclusion de la comparaison des modèles en est changée | sections 3.3 et 6.5 |
| Programme d'analyse de couverture-risque perdu | Réécrit, puis accepté seulement après avoir reproduit exactement les valeurs publiées sur la version antérieure du corpus | section 6.3 |
| Répertoire de la recherche d'hyperparamètres de la v13 perdu | Le dossier définissant la configuration 35 n'existe plus ; la configuration a été retrouvée dans le dossier de la version suivante et son contenu vérifié avant tout lancement de calcul | section 4.3 |
| Réseau de choix non réentraîné sur la v15 | Ses résultats portent sur une version antérieure du corpus et ne sont pas transposables, la cible étant construite à partir des actions du moteur de règles | section 6.4 |

### A.2 Versions de l'application

::: {custom-style="LegendeTableau"}
Tableau A.2 : Versions de l'application
:::

| Version | Changement principal |
| --- | --- |
| v7 | Première application, sur 76 médicaments |
| v8 | Moteur du réseau, second avis et référence CPIC, 117 médicaments ; lecteur de VCF à 18 gènes |
| v8b à v8e | Écran simplifié, vocabulaire clinique sourcé, HLA et CYP2D6 facultatifs |
| v8f, v8g | Réseau « profil vers médicaments » branché ; encadré explicatif et gènes décisifs |
| v8h à v8l | v8h : classement écrit à la main (erreur) ; v8i : réseau de choix ; v8j à v8l : langage clair, spécialités, feux tricolores |
| v8m | Corpus v8 (133 médicaments), 46 tests |
| v8n à v8p | Évolutions intermédiaires avant le passage au corpus v14 |
| v8q | Corpus v14 (189 médicaments), configuration 35 calibrée |
| v8r | Quatre avis avec score, références, rapport PDF refondu, archive d'installation |
| v8s | Lecture de CYP2C9 conforme au codage du corpus ; textes d'information corrigés |

### A.3 Erreurs de méthode relevées et corrigées

Ces erreurs sont listées parce qu'elles montrent le contrôle exercé sur les données et sur les résultats. Les signaler fait partie du résultat : un travail dont les erreurs ne sont pas visibles n'est pas un travail sans erreurs.

- **Intégrité de l'ensemble final.** Un test de câblage a lu les étiquettes d'un profil de l'ensemble final ; l'incident a été corrigé et protégé par une liste figée de 138 profils et un test d'intersection vide.
- **Erreurs de codage trouvées par vérification croisée** : CYP4F2, G6PD haploïde sur le chromosome X, CYP2C9 mélangeant deux scores d'activité.
- **Décomptes ou gains annoncés sans mesure, puis retirés** : plafond de couverture, warfarine et quinze médicaments présentés comme récupérés, « 133 × 1 379 lignes », « 210 médicaments ».
- **Tests dont la conception ne mesurait pas ce qu'ils prétendaient** : combinaisons retirées ; métrique « choix dans l'ensemble » dont la référence sans profil atteint déjà 99 %.
- **Règles lues à partir d'un mot-clé plutôt que du texte publié** : vingt règles étaient de fausses ambiguïtés.
- **Chiffres de bibliothèques ou dates non prouvés**, retirés du chapitre 3.
- **Lancement d'un calcul long après l'échec du script de vérification, puis double lancement** : corrigé par l'obligation d'un essai complet à échelle réduite avant chaque lancement.
- **Mot « famille » employé pour un identifiant de profil** : vocabulaire corrigé.
- **Audit de parenté** : des couples formés du père et de la mère d'un même enfant absent du corpus avaient d'abord été comptés comme apparentés ; après correction, le pedigree ne contient qu'une paire parent-enfant parmi les 1 379 profils (section 3.8).
- **Écart entre le codage de CYP2C9 du corpus (score d'activité) et celui que l'application lisait dans un VCF (phénotype)** : constaté dans la version 8r, corrigé dans la version 8s et couvert par des tests (section 5.8).
- **Textes d'information périmés dans l'application** (nombres de classes et de médicaments d'un corpus antérieur) : corrigés dans la version 8s.
- **Conclusion de comparaison transportée d'une version du corpus à la suivante.** La supériorité de XGBoost, établie sur les corpus v12 et v14, ne vaut plus sur la v15. Les énoncés concernés ont été réécrits plutôt que corrigés dans leurs seuls chiffres, parce que c'est la conclusion elle-même qui change, et chaque énoncé porte désormais la version sur laquelle il est établi.

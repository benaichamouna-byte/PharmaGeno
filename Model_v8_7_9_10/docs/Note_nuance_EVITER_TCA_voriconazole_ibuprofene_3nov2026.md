# Note : trois affichages à nuancer dans l'application (3 novembre 2026)

## 1. Antidépresseurs tricycliques tertiaires (amitriptyline, clomipramine, doxépine, imipramine, trimipramine) avec CYP2C19 rapide ou ultrarapide
- Corpus v14 (`regles_v14_monogene.csv`, table ClinPGx PA1661050xx) : EVITER pour CYP2C19 rapide (1,5) et ultrarapide (2,0), texte « Avoid tertiary amine use due to potential for sub-optimal response. Consider alternative drug not metabolized by CYP2C19 ... If a tertiary amine is warranted, utilize therapeutic drug monitoring ».
- API CPIC, clomipramine (lue le 3 nov. via WebFetch, résumé en morceaux ; le shell n'a pas accès à api.cpicpgx.org) : CYP2C19 rapide ou ultrarapide avec CYP2D6 normal : « Consider alternative drug not metabolized by CYP2C19 ; if clomipramine is warranted, utilize therapeutic drug monitoring », classification **Optional**. « Avoid » n'apparaît que pour CYP2D6 lent.
- Conséquence : l'étiquette EVITER est la lecture la plus prudente ; la force de la recommandation source est « Optional ». L'écran « à éviter » en rouge sur-affirme. Les données sources ne distinguent pas la force dans les règles à un gène du corpus (colonne absente).

## 2. Voriconazole avec CYP2C19 rapide
- Corpus : EVITER (« Choose an alternative agent ... »).
- API CPIC (3 nov.) : deux recommandations publiées pour « Rapid », toutes deux Moderate : (a) choisir un agent alternatif ; (b) dose standard puis suivi des concentrations. Ultrarapide : alternative seulement (Moderate). Le corpus a retenu (a) pour le rapide.
- Conséquence : même schéma que ci-dessus, pour le rapide uniquement (ultrarapide cohérent).

## 3. Ibuprofène en vert dans « autres préparations cardiaques » (Cardiologie)
- Cause : code ATC C01EB16 (ibuprofène) présent dans `atc_mapping_medicaments_v1/v14.csv` ; c'est un code OMS réel (fermeture du canal artériel chez le nouveau-né prématuré, d'après mon souvenir de l'index ATC ; à reconfirmer sur le site de l'OMS avant citation). Sans effet sur les étiquettes génétiques, mais trompeur en cardiologie adulte.

## Options (aucune appliquée ; corpus v14 gelé)
A. Laisser tel quel et l'écrire dans les limites du mémoire (recommandé par défaut : aucun risque de régression avant le dépôt du 25 nov.).
B. Nuancer l'affichage seulement : pour ces règles, afficher « Alternative à envisager (recommandation CPIC de force faible) » au lieu de « À éviter », sans réentraîner (nécessite un petit fichier de correspondance règle -> libellé).
C. Corriger les étiquettes dans un corpus v15 (CYP2C19 rapide : TCA et voriconazole) puis réentraîner : plus lourd, hors délai raisonnable.
D. Ibuprofène : filtre d'affichage documenté pour C01EB16 (hors spécialité Cardiologie adulte).

# 59 règles ambiguës (mono-gène) : proposition de décision (23 octobre 2026, 13 h) — NON VALIDÉE, rien d'entraîné

Pourquoi « ambiguës » : le texte publié propose deux options (ex. « éviter, ou réduire la dose »). L'extraction automatique garde la famille de la 1re instruction. Ces 59 règles (35 médicaments) sont donc exclues du corpus : le DL ne voit jamais ces génotypes.

## Règle de décision proposée
Classe = la 1re instruction du texte publié par CPIC/DPWG ; l'option de repli (« si X est nécessaire... ») ne change pas la classe. Chaque règle a été relue contre le texte (fichier `regles_ambigues_mono_decisions_proposees_v1.csv`, avec le début du texte).

## Résultat de la relecture
- 53 gardées telles quelles (classes : 36 éviter, 15 adapter la dose, 2 standard, voir csv) ; dont 5 « conditionnelles » dont la condition ne change pas la classe de départ (citalopram et escitalopram CYP2C19 rapide, métoprolol CYP2D6 ultra-rapide, fluvastatine et pravastatine SLCO1B1 fonction nulle).
- 1 CORRIGÉE : halopéridol CYP2D6 ultra-rapide. Le texte dit « Use 1.5 times the normal dose or choose an alternative » ; l'extraction avait lu « normal dose » comme STANDARD. Classe proposée : ADAPTER_DOSE.
- 5 EXCLUES (restent hors corpus) :
  - quétiapine CYP3A4 lent : la classe dépend de l'indication (dépression : alternative ; autres : 30 % de la dose) ;
  - mavacamten CYP2C19 lent : dépend d'un médicament associé (inhibiteur CYP3A4 fort : contre-indiqué) ;
  - méloxicam, piroxicam, ténoxicam CYP2C9 intermédiaire : CPIC sépare le score d'activité 1,5 (dose standard) et 1 (dose réduite ou alternative) ; notre code 0,5 mélange les deux.

## Effet mesuré sur le corpus (aperçu en dehors des fichiers officiels)
- Lignes : 152 600 -> 156 696 (+4 096) ; 30 médicaments touchés ; 0 étiquette existante modifiée.
- Médicaments dont l'étiquette varie selon le génotype : 63 -> 74 (+ célécoxib, citalopram, escitalopram, flurbiprofène, fluvoxamine, ibuprofène, lornoxicam, métoprolol, pitavastatine, pravastatine, vortioxétine) ; dans le modèle : 61 -> environ 72.
- Vrais profils : NA19472 récupère 3 médicaments sur 25 sans ligne (citalopram, escitalopram, fluvastatine) ; NA19085 : 0 sur 15. Les autres manques ont d'autres causes (valeurs CYP2D6/G6PD sans règle, 22 règles multi-gènes encore exclues) : à analyser ensuite.

## Corrections de ce que j'avais écrit plus tôt
- Faux : « les 59 règles rendraient la warfarine testable » : la warfarine n'est pas parmi ces 35 médicaments.
- Faux : « elles récupèrent les 15 médicaments disparus » : 3 sur 25 pour NA19472, 0 pour NA19085.

## Suite
Les 22 règles multi-gènes ambiguës (sertraline, amitriptyline, rosuvastatine, fluvastatine) seront relues avec la même règle de décision, puis UN SEUL réentraînement.

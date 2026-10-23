# Test du DL avec 2 vrais VCF (23 octobre 2026)

## Le sujet (rappel)
PharmaGeno est un webtool de RECOMMANDATION. Le clinicien envoie le VCF du patient et sa spécialité ; le DL lit tout le profil et combine les gènes ; la page recommande avec une réponse claire en haut. Ce test passe la chaîne COMPLÈTE : VCF -> lecteur PyPGx -> DL profil + DL choix -> écran v8l.

## Comment les 2 profils ont été choisis
Script `scripts/choisir_profils_test_vcf_v1.py` (critères écrits avant, graine 2026, tirage aléatoire) : hors des 138 profils finaux, hors HG00101, hors les 19 échantillons déjà validés, au moins 3 gènes lisibles non normaux dont 2 gènes clés. Résultat : NA19472 et NA19085 (1 091 profils éligibles sur 1 223 candidats). Le jeu final (138 profils) n'a pas été lu.
VCF reconstruits depuis les VCF 1KGP du pypgx-bundle (méthode de `valider_vcf_v8.py`), 46 968 enregistrements chacun. Sans HLA ni CYP2D6 (comme un clinicien sans test de laboratoire).

## Résultats mesurés (fichiers : sortie_*.json, tableau_moteur_2_profils.csv)
| | NA19472 | NA19085 |
|---|---|---|
| Gènes lus identiques au corpus (sur 17) | 16 | 16 |
| Gène différent | CYP2B6 (lu 1,5 ; corpus 1,0) | ABCG2 (lu 0,5 ; corpus 1,0) |
| Médicaments avec prédiction du DL | 54 | 65 |
| DL = règle CPIC/DPWG sur ces médicaments | 54 sur 54 | 65 sur 65 |
| Sans prédiction : gène non lisible (CYP2D6, HLA) | 44 | 44 |
| Sans prédiction : combinaison jamais vue à l'entraînement | 15 | 4 |
| Cardiologie : écran | tout vert (aspirin, clopidogrel, 6 statines) | vert : aspirin, mavacamten, ibuprofen, 7 statines ; rouge : clopidogrel |

Les 2 écarts de lecture (CYP2B6, ABCG2) sont des écarts déjà documentés : ces gènes ont un profil d'entraînement issu du corpus v3, pas de PyPGx (voir docs/BILAN_validation_vcf_v8.txt).

## Ce que ça montre
1. La chaîne complète fonctionne sur 2 nouveaux VCF : l'écran donne une réponse claire en haut. Pour NA19085 : clopidogrel ✖ « À éviter » à cause de CYP2C19 (métaboliseur intermédiaire).
2. Cas publié concordant (clopidogrel, CYP2C19 intermédiaire) : l'API officielle de CPIC (api.cpicpgx.org, lue le 23 oct.) donne, pour le syndrome coronarien aigu / angioplastie, « éviter la dose standard de 75 mg si possible ; prasugrel ou ticagrelor à dose standard » (classification Strong). C'est ce que dit notre règle (corpus) et ce que fait le DL.
   Limite : CPIC sépare par indication (hors SCA/angioplastie : pas de recommandation ; neurovasculaire : « envisager un autre antiagrégant », Moderate). L'application ne demande pas l'indication.
3. « DL = règle » n'est PAS une validation indépendante : les étiquettes d'entraînement viennent de ces règles. Ce test montre que le DL reproduit les règles sur de vrais VCF, pas que les patients vont mieux.

## Problèmes trouvés (à traiter)
1. Combinaisons jamais vues : NA19472 perd 15 médicaments (méloxicam, piroxicam, ténoxicam, fluvastatine, citalopram, escitalopram, dapsone, primaquine, etc.). Constaté dans `data/domaine_v8.json` : par exemple, pour le méloxicam, seules les valeurs CYP2C9 0,0 et 1,0 ont été vues alors que 367 profils du corpus ont CYP2C9 = 0,5. La cause probable est l'exclusion des 59 règles ambiguës (à confirmer règle par règle). Conséquence : un profil réel avec plusieurs gènes non normaux perd des médicaments.
2. Rouge trop sévère ? Pour NA19472 (CYP2C19 « rapide »), l'écran liste en rouge « à éviter » les tricycliques (clomipramine, doxépine, imipramine, trimipramine, amitriptyline) et le voriconazole, parce que notre règle dit EVITER. D'après l'API officielle CPIC (résumé fourni par l'outil de lecture, à reconfirmer sur le JSON brut) : clomipramine avec CYP2C19 rapide et CYP2D6 normal : « envisager un médicament non métabolisé par CYP2C19 ; si la clomipramine est nécessaire, suivi des concentrations », classification Optional ; voriconazole CYP2C19 rapide : deux lignes publiées, « alternative » ou « dose standard puis suivi des concentrations », toutes deux Moderate. Notre règle prend l'option la plus prudente et la montre comme « à éviter ». À corriger ou à nuancer dans l'écran (ex. « envisager une alternative »).
3. Ibuprofène affiché en vert dans « autres préparations cardiaques » (code ATC C01EB, usage particulier) : trompeur en cardiologie adulte.
4. Aucune alternative n'est proposée pour clopidogrel (prasugrel/ticagrelor sont dans la recommandation CPIC mais pas parmi les médicaments du modèle).

## Limites
- VCF « propres » (1000 Genomes, déjà phasés), pas un VCF clinique épars. CYP2D6 et HLA non lisibles.
- Modèles utilisés ici : ceux de mon environnement, de mêmes tailles que ceux déposés sur Drive (780 733 octets pour le DL profil) ; empreintes md5 non comparées. À refaire chez Mouna avec ses modèles : `lancer_test_vcf_reel_v1.py` ou envoi du VCF dans l'application.
- Pas encore comparé à PharmCAT sur ces 2 VCF.
- 2 profils seulement : illustration, pas statistique.
- Source CPIC lue via l'API officielle ; je n'ai pas pu lire les directives en PDF ni PubMed/PMC (blocage anti-robot).

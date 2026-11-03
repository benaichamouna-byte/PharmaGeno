# Test de la chaîne complète v8q avec 2 vrais VCF (3 novembre 2026)

Méthode : mêmes 2 profils que le test du 23 oct. (NA19472, NA19085 ; VCF reconstruits depuis les VCF 1KGP du pypgx-bundle ; hors ensemble final de 138 familles), même lecteur PyPGx, script `lancer_test_vcf_reel_v3.py` (copie de v2 branchée sur `app_pharmageno_v8q`, `modeles_v10`, `modeles_v10x`). Sorties : `results/test_vcf_reel_v8q/` (sortie_*.json, pages HTML) ; journaux `results/test_vcf_reel_v8q_NA19472.log`, `..._NA19085.log`.

## Mesures (v8m du 23 oct. -> v8q)
| | NA19472 | NA19085 |
|---|---|---|
| Gènes lus (non nuls) | 17 -> 17, profil strictement identique | 17 -> 17, identique |
| Médicaments dans le moteur | 117 -> 189 | 117 -> 189 |
| Avec prédiction du DL | 54 -> 112 | 65 -> 118 |
| DL = règle CPIC/DPWG (parmi ces prédictions) | 54/54 -> 112/112 | 65/65 -> 118/118 |
| Sans prédiction : gène non lisible (CYP2D6, HLA, etc.) | 44 -> 66 | 44 -> 66 |
| Sans prédiction : combinaison jamais vue | 15 -> 11 | 4 -> 5 |
| « à vérifier » | 6 (deuruxolitinib, erdafitinib, glyburide, lesinurad, meloxicam, nateglinide) | 0 |
- NA19085, cardiologie : clopidogrel en rouge (CYP2C19 intermédiaire), comme le 23 oct. NA19472 : aucun rouge en cardiologie.
- Warfarine de NA19085 : « combinaison jamais vue » -> non évaluée (aucune réponse du DL pour ce profil).

## Lecture
1. La chaîne fonctionne de bout en bout sur 2 VCF avec le corpus v14 : mêmes gènes lus, 2 fois plus de médicaments avec réponse du DL.
2. « DL = règle » n'est PAS une validation indépendante : les étiquettes viennent de ces règles. Le test montre que la chaîne reproduit les règles sur de vrais VCF.
3. Problèmes ouverts du 23 oct. toujours présents (non traités en v8q) : tricycliques et voriconazole en rouge pour CYP2C19 rapide (règle la plus prudente affichée comme « à éviter ») ; ibuprofène en vert dans « autres préparations cardiaques » (NA19085) ; pas d'alternative proposée hors médicaments du modèle.

## Limites
2 profils seulement (illustration, pas statistique) ; VCF 1KGP propres ; CYP2D6 et HLA non lisibles ; PyPGx exécuté dans l'environnement de cette session (pas encore sur l'installation de Mouna) ; pas de comparaison à PharmCAT.

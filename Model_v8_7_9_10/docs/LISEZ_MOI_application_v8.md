# Application web PharmaGeno v8 (20 octobre 2026)

Nouvelle application, à côté de la v7 (la v7 n'est pas modifiée).

## Ce qu'elle fait
1. Lit un fichier VCF (PyPGx 0.27.0, gène par gène) ou un profil de démonstration.
2. Le réseau de neurones (DL, FiLM + identifiant du médicament) produit la recommandation : c'est le moteur.
3. La règle CPIC/DPWG est affichée à côté avec sa source ; XGBoost donne un second avis ; une alerte signale tout désaccord.
4. « Non évalué » quand le modèle ne peut pas répondre de façon fiable (gène non déterminé, médicament inconnu, combinaison jamais vue). Jamais présenté comme sans risque.
5. Sorties : page de résultats par spécialité, page patient (langage simple), PDF, JSON.

## Lancer
Depuis le dossier `scripts/` :
    python3 app_pharmageno_v8.py --bundle ~/pypgx-bundle --pgx-python ~/pgxenv/bin/python
puis http://127.0.0.1:5000 . Le bouton « profil de démonstration » marche sans VCF.
Environnement : flask, reportlab, torch, xgboost ; pysam + PyPGx 0.27.0 + Java seulement pour analyser un VCF.

## Données du patient
Le VCF et les fichiers intermédiaires sont supprimés à la fin de l'analyse ; le profil (valeurs par gène) reste jusqu'au clic « Supprimer mes données » ou 24 h. Le serveur écoute seulement sur 127.0.0.1.

## Tests
- `scripts/test_app_v8.py` : 22 tests, 23 contrôles, tous PASS (`results/test_app_v8_sortie.txt`).
- Test réel avec un VCF (HG00101, via le formulaire, PyPGx) : `results/test_vcf_reel_app_v8.txt`. 20 gènes comparés au profil d'entraînement : 19 identiques ; la seule différence vient de la saisie HLA-B*57:01 faite à la main pour le test.

## Limites (écrites aussi dans l'application, page « Méthode, performances et limites »)
- Outil de recherche, non validé cliniquement.
- Les étiquettes viennent d'un moteur de règles CPIC/DPWG : la fiabilité mesurée est un accord avec les règles, pas une exactitude clinique.
- Aucune mesure ne montre, à ce jour, un avantage du DL sur XGBoost avec ces étiquettes (validation croisée : DL 0,9980 ± 0,0010 ; XGBoost 0,9999). Écrit tel quel.
- CYP2D6 (variants structuraux) et HLA ne se lisent pas dans un VCF de variants ponctuels : saisie manuelle, sinon « non évalué ».
- Le test avec VCF porte sur des données 1000 Genomes propres, pas sur des patients réels ni des VCF cliniques épars.
- L'ensemble final mis de côté (12 524 lignes) n'a pas été utilisé.

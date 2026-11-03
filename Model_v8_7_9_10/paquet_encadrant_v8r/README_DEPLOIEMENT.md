# PharmaGeno : paquet de déploiement (version 8r, corpus v14)

Outil de recherche d'aide à la décision en pharmacogénomique : à partir du profil génétique d'un patient (fichier VCF) et d'une spécialité médicale, il propose pour chaque groupe de médicaments interchangeables un avis en feux tricolores (à prescrire / dose à adapter / à éviter), avec les gènes qui expliquent l'avis.
**Ce n'est pas un dispositif médical et il n'a pas été validé cliniquement.** Les avis reproduisent les recommandations CPIC et DPWG ; ils ne remplacent pas le jugement du prescripteur.

Thèse : « A Deep Learning based Webtool for Mutation-Aware Drug Recommendation » (M.Sc. Bioinformatique, ENSI).

## 1. Contenu
| Dossier | Contenu |
|---|---|
| `scripts/` | application Flask (`app_pharmageno_v8r.py`), moteur, modules, gabarits `templates_v8r/` |
| `modeles_v10/` | réseau « profil génétique -> conseil pour chacun des 189 médicaments » (calibré), réseau « choix du médicament » (44 groupes), seuils d'abstention |
| `modeles_v10x/` | second avis XGBoost (comparaison affichée à l'expert) |
| `modeles_v10rf/` | troisième avis Random Forest (comparaison affichée à l'expert ; ne déclenche aucune alerte) |
| `data/` | domaine de validité, règles CPIC/DPWG utilisées pour l'affichage, codes ATC (OMS), spécialités, profils de contrôle (1000 Genomes), utilisés seulement par le vérificateur d'installation |
| `MANIFESTE.sha256` | somme de contrôle de chaque fichier |

## 2. Installation (Linux, macOS, Windows/WSL)
Python 3.12 ou plus récent (testé avec 3.12 et 3.13).
```bash
python3 -m venv .venv && source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python3 verifier_installation.py                           # doit afficher : INSTALLATION CORRECTE
./lancer.sh                                                # Windows : lancer.bat
```
Pour pouvoir analyser un VCF : `bash installer_vcf.sh` (section 5). Ouvrir ensuite http://127.0.0.1:5000 . Tant que la lecture des VCF n'est pas installée, l'accueil l'indique et grise le bouton « Lancer l'analyse ». Deux VCF d'exemple sont dans `exemples/`.

## 3. Ce qui fonctionne sans VCF
Démarrage de l'application et contrôle d'installation (`verifier_installation.py`, qui parcourt les écrans de résultats avec un profil interne de contrôle). L'analyse d'un VCF demande `bash installer_vcf.sh` (section 5).

## 3 bis. Lire les scores 0-1
Sous chaque avis, un nombre entre 0 et 1 donne la certitude du modèle dans son propre avis (arrondi vers le bas ; « ≥ 0,999 » au-delà). Réseau DL : probabilité calibrée par un réglage de température. XGBoost et Random Forest : scores non calibrés (le Random Forest, moyenne de 100 arbres, donne souvent des valeurs plus basses). Les étiquettes d'entraînement sont les règles CPIC/DPWG : ces nombres mesurent la certitude de reproduire la règle, **pas la probabilité que l'avis soit juste cliniquement**.
Références : chaque directive affiche sa source, la référence générale de cette source (DOI) et le lien vers la fiche de la directive (ClinPGx). La publication précise de chaque directive CPIC/DPWG par médicament n'est pas encore associée : travail en cours.

## 4. Sécurité et données
Le serveur n'écoute que sur 127.0.0.1. **Il n'a pas d'authentification** : ne pas l'exposer sur Internet. Pour un accès réseau interne, le placer derrière un proxy inverse avec authentification et HTTPS. Le VCF téléversé est supprimé à la fin de l'analyse ; seul le profil (valeurs par gène) reste dans `pharmageno_travail/jobs/` jusqu'au clic sur « Supprimer mes données » ou 24 h.

## 5. Analyser un fichier VCF (facultatif)
**La façon la plus simple : `bash installer_vcf.sh`** (installe pysam, l'environnement PyPGx, le panel de référence ; Java et git doivent être présents). Détail de ce que fait le script : la lecture d'un VCF utilise **pysam** (à installer aussi dans l'environnement principal : `pip install pysam==0.24.1`), PyPGx 0.27.0, Java et le « bundle » de référence de PyPGx (ces deux derniers dans un environnement séparé) :
```bash
python3 -m venv ~/pgxenv && ~/pgxenv/bin/pip install -r requirements_vcf_optionnel.txt
# Java (ex. sudo apt install default-jre) et bundle PyPGx : ~/pypgx-bundle
./lancer.sh --bundle ~/pypgx-bundle --pgx-python ~/pgxenv/bin/python
```
Limites de lecture : CYP2D6 et les allèles HLA ne sont pas lisibles depuis un VCF court (à saisir après les résultats) ; les gènes non lus rendent les médicaments concernés « non évalués », jamais « normaux ».

## 6. Résultats mesurés (corpus v14, sans l'ensemble final de 138 familles)
- Réseau « profil » : F1 macro 0,9979 ± 0,0012 (25 entraînements, validation croisée groupée par famille) ; log-loss 0,0030 ; ECE 0,0003.
- Réseau « choix » : choix dans l'ensemble recommandé 99,99 % sur les cas informatifs (référence sans le profil : 99,09 %) ; ensemble exact retrouvé 98,99 % (référence : 38,9 %).
- Ces scores mesurent la reproduction des règles CPIC/DPWG (les étiquettes viennent de ces règles), pas un bénéfice clinique. Validation externe partielle : warfarine, cohorte IWPC (6 922 sujets, 5 774 analysables) : voir le mémoire.

- Modèles de contrôle (validation interne seulement, aucune validation croisée refaite) : XGBoost exactitude 1,0, log-loss 0,0157 ; Random Forest F1 macro 0,9341, exactitude 0,9766, précision EVITER 0,77, rappel EVITER 0,97 (réglages : 100 arbres, feuilles d'au moins 2 lignes, poids de classes équilibrés ; trois essais lus sur la validation interne, voir l'en-tête de `scripts/modele_final_rf_v3.py`).
- Références scientifiques (DOI vérifiés) : page « Références » de l'application.

## 7. Limites connues
- 189 médicaments ; 21 médicaments « règle seule » (MT-RNR1, RYR1/CACNA1S, CFTR, HLA) ne sont pas intégrés.
- Tricycliques et voriconazole pour CYP2C19 rapide : affichés « à éviter » alors que la force de la recommandation source est « Optional »/« Moderate ».
- Ibuprofène affiché dans « autres préparations cardiaques » (code ATC C01EB16).
- Combinaisons génétiques jamais vues à l'entraînement : médicament « hors domaine », non évalué.

## 8. Reproductibilité
Les entraînements (scripts `modele_final_*_v3.py` dont `modele_final_rf_v3.py`, `train_dl_choix_v3.py`) et le corpus v14 sont dans le dépôt GitHub du projet (branche `sauvegarde-2026-11-02`) ; ce paquet contient seulement ce qui est nécessaire pour exécuter l'application.

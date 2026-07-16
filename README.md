# PharmaGeno — A Deep Learning based Webtool for Mutation-Aware Drug Recommendation
Projet de mémoire Master Bioinformatique
Auteur : Mouna Ben Aicha
Encadrant : Pr. Kais Ghedira

## Description
PharmaGeno est une application web qui analyse le profil génétique d'un patient (fichier VCF) et génère des recommandations médicamenteuses personnalisées via un pipeline combinant Deep Learning et Machine Learning classique.

## Architecture du pipeline
VCF patient → Parseur VCF → Vote majoritaire DL v5 + RF v3 → Moteur PharmGKB + CPIC + DPWG → Interface Flask → Rapport PDF

## Performances des modèles (cross-validation 5-fold)
- Deep Learning v5 : 79.0% ± 0.7%
- Random Forest v3 : 81.4% ± 1.0%
- XGBoost          : 78.0% ± 1.4%

## Prérequis
- Python 3.10+
- WSL (Ubuntu) recommandé

## Installation
pip install flask pandas torch scikit-learn imbalanced-learn xgboost joblib reportlab

## Structure du projet
PharmaGeno/
├── scripts/
│   ├── vcf_parser.py           # Parseur VCF
│   ├── drug_recommender.py     # Moteur recommandation PharmGKB+CPIC+DPWG
│   ├── predict_phenotype.py    # Prédiction phénotype DL+RF vote majoritaire
│   ├── generate_report.py      # Génération rapport PDF
│   ├── deep_learning_v5.py     # Modèle DL v5
│   ├── random_forest_v2.py     # Modèle RF
│   ├── xgboost_model.py        # Modèle XGBoost
│   ├── cross_validation.py     # Cross-validation 5-fold
│   └── save_dl_v5.py           # Sauvegarde modèle DL v5
├── app/
│   ├── app.py                  # Application Flask
│   └── templates/
│       ├── index.html
│       └── results.html
├── data/
│   └── synthetic/              # VCF synthétiques pour tests de robustesse
│       ├── patient_sans_mutation.vcf
│       ├── patient_dpyd.vcf
│       └── patient_multi_gene.vcf
└── results/                    # Modèles entraînés + résultats

## Données requises (disponibles sur Google Drive partagé)
- data/var_drug_ann.tsv         # PharmGKB
- data/clinicalVariants.tsv     # Variants cliniques
- data/guidelineAnnotations.json.zip  # Guidelines CPIC + DPWG
- data/pharmacat.example2.vcf   # VCF de test

## Lancer l'application
cd app
python3 app.py

## Accès
http://127.0.0.1:5000

## Tests de robustesse
3 scénarios testés et validés :
1. Patient sans aucune mutation → affichage propre sans crash
2. Patient avec gène jamais testé (DPYD) → pipeline complet fonctionnel
3. Patient avec gène inconnu → prédiction honnête "Non déterminé"

# PharmaGeno — Mutation-Aware Drug Recommendation
Projet de mémoire Master Bioinformatique
Auteur : Mouna Ben Aicha
Encadrant : Pr. Kais Ghedira

## Prérequis
- Python 3.10+
- WSL (Ubuntu) recommandé

## Installation
pip install flask pandas

## Structure du projet
PharmaGeno_Memoire/
├── scripts/
│   ├── vcf_parser.py
│   ├── drug_recommender.py
│   └── clean_results.py
├── app/
│   ├── app.py
│   └── templates/
│       ├── index.html
│       └── results.html
└── data/
    ├── pharmacat.example2.vcf
    ├── var_drug_ann.tsv
    ├── clinicalVariants.tsv
    └── guidelineAnnotations.json.zip  ← décompresser ici

## Avant de lancer
Décompresser guidelineAnnotations.json.zip dans le dossier data/
unzip data/guidelineAnnotations.json.zip -d data/

## Lancer l'application
cd app
python3 app.py

## Accès
http://127.0.0.1:5000

## Test
Uploader data/pharmacat.example2.vcf
Résultat attendu : 5 variants, 46 recommandations
Tester la recherche : taper "clopidogrel"

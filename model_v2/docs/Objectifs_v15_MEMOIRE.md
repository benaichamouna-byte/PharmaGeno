## Objectifs

Cette section précise le verrou étudié, les questions de recherche qui en découlent et les objectifs du travail. Chaque question s'appuie sur un constat de l'état de l'art : la divergence entre sources de recommandations (section 2.1), l'avantage fréquent des modèles à arbres sur données tabulaires (section 2.5), et la nécessité de probabilités fiables et d'une option d'abstention (section 2.6).

**Verrou scientifique.** Déterminer si un modèle prédictif peut exploiter l'ensemble du profil multi-gènes d'un patient pour produire, en une lecture, une classe d'action pour de nombreux médicaments, avec une traçabilité vers les recommandations de référence, et si le Deep Learning est justifié face à des modèles à arbres sur des données structurées de volume limité.

**Questions de recherche.**

- **RQ1 — Profil multi-gènes.** Le profil complet améliore-t-il la prédiction par rapport au seul gène associé au médicament ?
- **RQ2 — Deep Learning.** Le réseau est-il plus performant que Random Forest et XGBoost, en F1 macro et en situations à éviter manquées ?
- **RQ3 — Calibration.** Les probabilités sont-elles calibrées et un seuil de confiance signale-t-il les cas incertains ?
- **RQ4 — Représentation moléculaire.** La description du médicament améliore-t-elle la prédiction, notamment pour un médicament jamais vu ?
- **RQ5 — Généralisation.** Les performances se conservent-elles hors des conditions d'entraînement : profils non vus, médicaments absents, combinaisons de gènes jamais observées ?
- **RQ6 — Concordance.** Les actions produites sont-elles concordantes avec l'interprétation attendue des références ?
- **RQ7 — Validité hors règles.** Les règles qui servent d'étiquettes sont-elles cohérentes avec des données de patients réels (cas de la warfarine) ?

**Objectifs.** L'objectif général est de concevoir, entraîner, évaluer et intégrer dans une application web un système expérimental d'aide à la décision combinant VCF, profil multi-gènes, Deep Learning et connaissances de référence. Il se décline ainsi.

1. Construire et auditer un corpus multi-source : traçabilité des étiquettes, valeurs manquantes, conflits entre sources.
2. Développer un réseau qui lit le profil complet et prédit l'action pour chaque médicament, avec des probabilités calibrées.
3. Comparer le Deep Learning à Random Forest et XGBoost sous un protocole identique, et réserver un ensemble final de 138 profils à une évaluation unique.
4. Mesurer l'apport du profil multi-gènes par rapport à une représentation limitée au gène associé à chaque médicament.
5. Évaluer la généralisation à des médicaments et à des combinaisons de gènes non vus.
6. Confronter les règles du corpus à des données de patients réels.
7. Déployer le pipeline dans une application web qui analyse un VCF et en affiche une sortie structurée et sourcée.

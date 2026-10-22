# Journal de Bord du Projet PharmaGeno : 22 octobre 2026, addendum de 23 h 15

Complète `Journal_de_Bord_22oct2026_soir.md` (rien n'est écrasé).

## 1. Sauvegarde du lot v8f-v8l terminée (mesuré)
- WSL -> Windows : 66 fichiers de `A_deposer_Drive` comparés un à un (`cmp`) à `C:\Users\MSI\Desktop\memoire\Model_v8_7_9_10\` : 66 sur 66 identiques. `templates_v8l` inclus. 3 journaux et 2 tests contrôlés par `diff`.
- GitHub : commits 595ba44 (code v8f, v8g, v8i-v8l), 707c320 (modèles, résultats DL choix), 93c0b82 (tests moteurs v8f et v8g, 3 journaux).
- Drive : 71 fichiers retrouvés, tailles identiques aux miennes (comptage dossier par dossier, pas un comptage récursif de tout le Drive).
- Erreur de dépôt corrigée : 2 tests moteurs d'abord déposés dans un ancien dossier `scripts` (créé en avril, sous « A Deep Learning based Webtool… ») ; re-déposés dans le bon `scripts` (id 10Zp3EOlGPYVhS7ah5FGUfVqE0PrQXRdt). Les 2 copies mal placées restent dans l'ancien dossier : à supprimer.

## 2. Erratum d'intégrité (ensemble final)
- Constat : le test de câblage T27 (test_app_v8i, v8k, v8l) échantillonnait 25 profils avec `RandomState(9)` dans tout le corpus, ensemble final compris. Un des 25, HG00632, appartient à l'ensemble final (138 profils, 12 524 lignes) : ses étiquettes ont été comparées à la prédiction (75 médicaments prédits, 0 EVITER). Aucun réglage ni choix de modèle ou de seuil n'a utilisé ce résultat ; la règle « ensemble final lu une seule fois à la fin » n'a pas été respectée à la lettre pour 1 profil sur 138.
- Profil de démonstration et fichier d'essai : HG00101 n'est PAS dans l'ensemble final (vérifié par `protocole_commun_v8.decouper`, graine 42).
- Audit des autres tests (recherche de texte, à confirmer par lecture du code) : `test_moteur_v8f.py` et `test_moteur_v8g.py` ne comparent pas d'étiquettes ; `test_moteur_v8.py` compare le moteur de règles CPIC aux étiquettes sur tout le corpus (aucun modèle appris, mais lecture des étiquettes de l'ensemble final).
- Correction : `data/profils_ensemble_final_v1.txt` (138 identifiants, aucune étiquette, généré par `protocole_commun_v8`, intersection avec la validation croisée = 0) et `scripts/test_app_v8l_b.py` (copie de test_app_v8l.py : T27 exclut ces profils ; nouveau T36 : liste de 138 profils et intersection vide). 46 tests passés dans mon environnement.
- Résultat T27 corrigé : 8 médicaments étiquetés EVITER sur 1 776 prédits (0,45 %, critère <= 1 %), contre-épreuve 38. L'ancien chiffre (3 sur 1 814 = 0,17 %) dépendait de l'échantillon. Ce test mesure le DL « choix » seul ; l'application retire en plus les médicaments à éviter selon un autre avis.

## 3. Règle à appliquer désormais
- Aucun test, aucune mesure ni aucun échantillon ne tire ou ne compare des profils de l'ensemble final : exclure `data/profils_ensemble_final_v1.txt` avant tout échantillonnage.

## 4. Plan restant
1. Sauvegarde du correctif : Windows, GitHub, Drive (3 fichiers : `data/profils_ensemble_final_v1.txt` -> dossier `data`, `scripts/test_app_v8l_b.py` -> `scripts`, cet addendum -> `journal de bord`).
2. Supprimer les 2 copies mal placées dans l'ancien dossier `scripts` sur Drive.
3. Appliquer l'exclusion de l'ensemble final aux anciens tests moteurs (`test_moteur_v8*.py`) à leur prochaine révision.
4. Corrections de l'application : accord des verbes, message quand aucun gène requis n'est lisible, test sur un autre VCF que HG00101, anomalie atorvastatin / SLCO1B1.
5. Le reste du plan du journal du 22 octobre (science, chapitres, mail à l'encadrant, ménage GitHub).

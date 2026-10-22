# Journal de Bord du Projet PharmaGeno : 21 octobre (soir) au 22 octobre 2026 (19 h 25)

Complète `Journal_de_Bord_21oct2026_soir_addendum_19h15.md` (rien n'est écrasé). « Mesuré » = affiché sur la machine de Mouna ou par un test explicite dans mon environnement. Les résultats de validation reproduisent des règles CPIC/DPWG : ce n'est pas une validation clinique indépendante.

## 1. Décisions validées ou prises
- Règle absolue, enregistrée en mémoire du projet : le sujet est un WEBTOOL de RECOMMANDATION. Le clinicien envoie le VCF (+ spécialité) ; le DL lit tout le profil génétique, combine les gènes ; la page recommande le ou les médicaments avec une réponse claire en haut. Ce n'est ni un test de médicaments un par un, ni un écran de chercheur. À chaque livraison : vérifier ces 4 points et le dire.
- Nouveau DL « choix du médicament » (DLChoix : 33 entrées, 2 couches 256, BN, dropout 0,3, scores par médicament, softmax par classe sur les candidats évaluables, perte = entropie croisée avec cible uniforme sur l'ensemble S). Convention de cible (NON une guideline) : pour un profil et une classe ATC4 à au moins 2 médicaments étiquetés, S = médicaments du meilleur niveau disponible (STANDARD > SURVEILLER > ADAPTER_DOSE), EVITER jamais dans S. 30 classes ATC4 (75 des 113 médicaments). Ensemble prédit à l'inférence = candidats avec p >= 0,5 x p max. Les médicaments à éviter selon un autre avis sont retirés (« retirés par sécurité »).
- Livraisons de l'application : v8i (sélecteur de classe) -> v8j (réponse en langage clair, détails repliés) -> v8k (spécialité rétablie, groupes de médicaments par spécialité) -> v8l (écran en feux tricolores). Chaque version à côté des anciennes, rien n'est écrasé.
- v8l : résumé unique « À prescrire à la dose habituelle (vert) / Dose à adapter ou à surveiller (orange) / À éviter (rouge) », raison en une ligne, termes en français, un seul compteur « non évalués », encadré rouge limité aux médicaments à éviter des autres spécialités, détails scientifiques repliés. Un médicament n'apparaît que dans une couleur (la plus prudente).
- Retour de Mouna sur v8l (19 h 25, capture sur VCF réel HG00101) : « much better ».

## 2. Mesures
- Validation croisée du DL choix (5 graines x 5 plis, StratifiedGroupKFold par famille ; cas informatifs ~6,5 % des cas) : ensemble exact 0,9955 +/- 0,0006 contre 0,069 pour la ligne de base aveugle au profil ; Jaccard 0,9983 +/- 0,0004 contre 0,599 ; premier choix EVITER : 0 ; hasard dans S : 0,5646. L'écart-type ne couvre que les graines. Modèle final, validation interne : 0,9954 contre 0,0741.
- Test de câblage : 3 médicaments sur 1 814 prédits étiquetés EVITER (0,17 %) ; contre-épreuve (probabilités mélangées) : 27.
- DL profil par médicament (modeles_v8f) : F1 macro CV 0,9985 +/- 0,0002 ; EVITER manqués 0,0015 +/- 0,0002.
- Tests de l'application dans mon environnement : v8k 39 tests, v8l 45 tests passés. Contre-épreuve : en cassant volontairement la logique « orange », le test T31 échoue ; restaurée, tout passe.
- v8l : md5 app `f4cf11257be31bf8c3e9c6cf9ef3ead3`, test `7efe624d2ba0de9a5edf6e4d94bd5499`, zip `189917265ccaf86ca2cc5a73a9d99750`.
- Sur la capture de Mouna (VCF réel HG00101.vcf, Cardiologie) : statines pravastatin / rosuvastatin / fluvastatin en vert, antiagrégants en vert, atorvastatin en orange, simvastatin en rouge, 11 médicaments non évalués (CYP2D6 et HLA non lisibles depuis un VCF de variants ponctuels).
- Sauvegardes du 22 oct. : Windows v8l (md5 identiques) puis lot v8f-v8k + modèles + résultats (26 éléments identiques) ; GitHub : commits 595ba44 (code v8f, v8g, v8i-v8l, 53 fichiers) et 707c320 (modèles, résultats DL choix, 13 fichiers).
- Littérature lue : aucune publication consultée ne classe des médicaments à partir d'un profil génétique complet avec des règles seules ; la vraie sélection demande des données de réponse clinique, absentes de notre corpus. Sources : https://www.nature.com/articles/s41746-026-02590-w ; https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2023.1189976/full ; https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2024.1500235/full ; https://genesight.com/white-papers/interpreting-the-genesight-psychotropic-report/ ; https://www.nature.com/articles/s41398-021-01488-3

## 3. Erreurs à ne plus reproduire
- Présenter un classement écrit à la main comme une prédiction du DL (v8h).
- Retirer le sélecteur de spécialité sans le dire à Mouna (v8i/v8j) : toute décision de direction lui est annoncée.
- Mal lire une réponse ambiguë et agir sur ma lecture (« ce png reflète le sujet ») : énoncer ma lecture ET être prêt à me tromper.
- Livrer un écran de chercheur (probabilités, trois avis, anglais, lignes « pas de choix possible ») : l'écran principal doit être compris par un clinicien sans explication.
- Répondre par une explication ligne à ligne quand la demande est de rendre l'écran compréhensible.
- Enchaîner de longs appels d'outils silencieux (interrompus deux fois) : une ligne d'état d'abord, chaînes courtes.
- Métrique triviale (« choix dans S » : ligne de base à 100 %) et tests qui passent toujours : toujours une contre-épreuve.
- Poser des questions de validation répétées : au plus une question concrète.
- Supposer qu'un fichier existe chez Mouna (v8h n'a jamais été livré) : utiliser des boucles qui signalent les fichiers absents.

## 4. Plan restant
1. Fin de la sauvegarde : Drive à la main (scripts v8f-v8l, moteurs, scripts DL choix, modèles, résultats dl_choix_v1, journaux), puis comptage récursif.
2. Corrections de l'application : accord des verbes (« 1 médicament ... est à éviter ») ; message quand aucun gène requis n'est lisible ; contradiction multi-gènes « non interprété » ; revoir les noms français des classes ; tester un autre VCF que HG00101 ; comprendre l'anomalie atorvastatin / SLCO1B1 (gène décisif alors que l'atorvastatine est proposée).
3. Science : utiliser les 59 règles ambiguës (corpus, réentraînement, test des combinaisons cachées) ; audit de couverture CPIC/DPWG vs PharmCAT `prescribing_guidance.json` avec liens ; comparaison PharmCAT ; petite recherche d'hyperparamètres sur validation seulement ; évaluation finale unique sur les 12 524 lignes (138 familles) lue une seule fois à la fin.
4. Mémoire : chapitres 3 à 8 ; tableau de suivi Excel ; mail à Pr. Kais Ghedira (brouillon prêt, non envoyé ; disponible dès le 15 nov.) ; date de dépôt (vers le 12 nov., non confirmée) ; soutenance en décembre 2026.
5. Ménage : fichier parasite à la racine GitHub `rf, columns, classes = load_rf_model()` ; fichiers `??` non suivis ; commit 494a50e « Unverified » ; uploads Drive en attente (Tableau_de_bord_PharmaGeno_15oct2026.pdf, pharmageno_app_v7b.zip) ; zips à nettoyer côté Windows après liste (doublon `pharmageno_v8j (1).zip` laissé).
6. Limites à garder dans le texte de la thèse : cibles = règles CPIC/DPWG (pas de réponse clinique mesurée) ; le DL ne départage pas des médicaments équivalents ; classes = 75 des 113 médicaments ; 4 spécialités sans groupe interchangeable (Douleur et anesthésie-réanimation, Gynécologie-obstétrique, Immunologie et transplantation, Urologie) ; noms français des groupes = traduction libre des noms OMS ATC ; CYP2D6 et HLA non lisibles depuis un VCF de variants ponctuels.

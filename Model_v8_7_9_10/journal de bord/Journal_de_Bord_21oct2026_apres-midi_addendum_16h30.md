# Journal de Bord du Projet PharmaGeno : 21 octobre 2026, addendum de 16 h 30

Complète les deux journaux de l'après-midi (rien n'est écrasé). « Mesuré » = affiché sur la machine de Mouna.

## 1. Décisions
- Objectif du DL (règle absolue, déjà notée) : profil génétique en entrée, médicament(s) en sortie ; gènes et médicaments = lettres ; le DL doit combiner les gènes, pas recopier CPIC.
- Test corrigé des combinaisons cachées : lancé par Mouna, résultats ci-dessous.

## 2. Mesures (3 tirages, chez Mouna ; contrôle « combinaisons cachées présentes à l'entraînement » = 0 aux 3 tirages)
- Informatives, exactitude du DL : 0,5747 ; 0,8529 ; 1,0000 (moyenne 0,8092) ; informatives de classe vue : 0,6849 ; 0,8867 ; 1,0000 (moyenne 0,8572) ; combinaisons vues, mêmes médicaments : 0,999.
- Tricycliques (CYP2C19+CYP2D6) : DL 0,975 à 1,000 contre 0,000 pour la classe majoritaire : le DL répond à des combinaisons jamais vues. Rosuvastatine : égal à la classe majoritaire (0,804), 0,000 sur les informatives de classe vue. Sertraline : 28 cas informatifs de classe jamais vue. Thiopurines, carbamazépine, phénytoïne : non évalués dans ce test (aucune combinaison cachée de ces paires dans les 3 tirages).
- EVITER détectés / réels : 50/64, 313/344, 50/50.

## 3. Erreurs à ne plus reproduire
- Les erreurs des deux journaux précédents de l'après-midi (redemander un objectif déjà donné ; garder le médicament en entrée du DL ; conclure d'un test de combinaisons sans contrôle de non-présence ; envoyer un script par carte de fichier sans somme de contrôle).
- Présenter comme prouvé un résultat obtenu sur 3 tirages et quelques dizaines à centaines de cas, sans le dire.

## 4. Plan restant (chaque étape validée par Mouna)
1. Sauvegarde WSL -> Windows -> GitHub -> Drive des fichiers du 21 oct. (après-midi) : 3 scripts, résultats `dl_profil_v1` et `combinaisons_cachees_profil_v1`, note du rapport, 3 journaux.
2. Application v8f branchée sur le DL profil (1 à 3 médicaments par spécialité) ; corrections listées au journal de midi ; trou escitalopram (décision de Mouna).
3. Étendre le test des combinaisons : plus de tirages, thiopurines et paires non couvertes ; comprendre l'échec rosuvastatine ; défaut HLA-B*58:01.
4. Réglage léger des hyperparamètres du DL profil sur validation seule ; évaluation finale unique sur l'ensemble final de 12 524 lignes.
5. Comparaison avec Nguyen et al. 2024 (Table 2, 3 médicaments) et PharmCAT ; test `HG00101.vcf` chez Mouna ; mail à l'encadrant ; chapitres 3 à 8 ; date de dépôt.

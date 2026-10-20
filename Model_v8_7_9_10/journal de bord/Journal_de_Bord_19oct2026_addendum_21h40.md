# Addendum au Journal de Bord du 19 octobre 2026 (21h40) - à lire avec Journal_de_Bord_19oct2026_soir.md

## Nouveaux constats mesurés (sans nouvel entraînement ; probabilités hors-pli déjà calculées, 112 654 lignes dont 5 323 EVITER ; médicaments connus, patients nouveaux)
Abstention sur les 1 % de prédictions les moins sûres (confiance = probabilité maximale), moyenne des 5 graines pour le DL :
- DL (identifiant + EVITER x2) : EVITER manqués 15,6 lignes (0,29 %) sans abstention -> 4,6 lignes avec abstention (11 écartés sur 1 127 lignes mises de côté) ; erreur sur les cas décidés 0,084 % -> 0,009 %.
- XGBoost : 6 EVITER manqués -> 0 ; RF : 260 -> 138.
- Conclusion honnête : l'abstention est utile à l'application mais n'est PAS un avantage propre au DL (XGBoost fait mieux et est mieux calibré : ECE 0,0002 contre 0,0055 pour le DL). Limite : le seuil d'abstention est pris sur l'ensemble d'évaluation ; en usage réel, à fixer sur la validation.
- Seuil sur P(EVITER) (DL, moyenne 5 graines) : seuil 0,5 -> rappel EVITER 99,67 % et 0,70 % de fausses alertes ; seuil 0,1 -> rappel 99,89 % et 5,1 % de fausses alertes.
- Bilan : sur ces étiquettes issues de règles, aucune mesure à ce jour ne montre un avantage du DL sur XGBoost ; à écrire tel quel dans le mémoire. Le DL reste le moteur de l'application.

## Test annulé après vérification de conception
- « Combinaisons de gènes jamais vues » : retirer une combinaison revient à retirer une case de la table ; pour les cas multi-gènes l'étiquette est la convention du moteur (« l'action la plus sévère gagne »), pas une vérité clinique. Un succès montrerait que le DL imite le moteur de règles. Non lancé.

## Piste « médicament nouveau avec relations médicament-gène » : état de la vérification
- ClinPGx (ex-PharmGKB) : la page des téléchargements exige JavaScript ; depuis la session, impossible de lister les fichiers et leurs conditions d'utilisation. Rien n'est vérifié. N'utiliser que des relations qui ne définissent pas les étiquettes (sinon fuite : les règles CPIC définissent déjà les étiquettes).

## Contexte
- Décision de rôle du DL toujours ouverte : pistes 1 (médicament nouveau + relations médicament-gène), 2 (niveau variants, lourd pour le délai), 3 (DL = moteur de l'application, évalué contre CPIC/XGBoost/RF avec abstention, position honnête).

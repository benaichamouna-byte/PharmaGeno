# Résultat : application v8r et paquet de déploiement pour l'encadrant (3 novembre 2026)

## Ce qui a été fait
- Application v8r = v8q + affichage revu (consignes de Mouna du 3 nov.) : tableau « Qui donne l'avis » par famille de médicaments (DL, directive officielle, XGBoost, Random Forest) avec le score de 0 à 1 de chaque modèle ; pas de décompte de gènes ; pas de pourcentage « médiocre » du DL ; références et sources de directives affichées ; explication du formulaire de laboratoire (à quoi ça sert / ce que ça change / quoi faire) ; profil de démonstration retiré de l'interface (le téléversement d'un VCF est le chemin principal ; la route /demo reste interne, utilisée par les tests).
- Export PDF refondu (rapport_pdf_v8r.py, v8 intact) : quatre avis avec score, sections « Lire les scores 0-1 », « Directives utilisées », « Références scientifiques », « Méthode et limites » ; plus de « confiance x % ».
- Lecture des VCF : message clair si un composant manque (pysam, PyPGx, Java, panel) ; bouton désactivé tant que l'installation n'est pas faite ; script installer_vcf.sh (pysam, PyPGx 0.27.0 dans un environnement séparé avec pandas<3, panel pypgx-bundle 0.27.0, vérification de Java).
- Paquet de déploiement : requirements.txt avec `torch>=2.14.1` (la version épinglée remplaçait le torch CPU par une version CUDA de 3 Go), Python 3.12 ou plus récent.

## Vérifications
- Tests de l'application : T1 à T63, 73 contrôles, tous réussis (results/test_app_v8r_sortie.txt).
- Paquet final (zip « (3) », 45 026 792 octets, sha256 c582882ba6d6fb0c9b8d71a4b8b9fb26828d08dcd277de0a51b1fef1ed06c0aa) : somme de contrôle vérifiée chez Mouna (OK) ; vérificateur « INSTALLATION CORRECTE » ; vraie analyse de NA19472.vcf (Cardiologie, environ 90 s, PDF de 6 pages relu page par page).
- La v4 de Mouna (installation, vérificateur, installer_vcf.sh, vrai VCF) avait été testée OK sur sa machine WSL ; la v5 (finale) n'a pas été réinstallée chez elle, seulement vérifiée par somme de contrôle et testée dans le bac à sable.

## Envoi à l'encadrant (3 nov., soir)
- Dossier Drive séparé `PharmaGeno_Webtool_Deploiement_Encadrant` (zip + 2 captures d'écran), lien envoyé par mail (sans pièce jointe) puis message WhatsApp. Décisions de Mouna : PDF d'exemple non envoyé, pas de somme de contrôle dans le mail, pas de partage d'écran proposé.

## Limites (à garder dans le mémoire)
- Les scores 0-1 mesurent la certitude de reproduire la règle CPIC/DPWG, pas la justesse clinique ; DL calibré (ECE 0,0003 en validation croisée), XGBoost et Random Forest non calibrés (Random Forest : scores nettement plus bas, parfois en désaccord).
- Référence affichée = référence générale de la source (CPIC : Relling & Klein 2011 ; DPWG : Swen 2011 ; RNPGx : Abdullah-Koolmees 2021) + fiche ClinPGx ; la publication précise de chaque directive (environ 152 identifiants PA) n'est pas encore associée.
- 21 médicaments « règle seule » non intégrés ; combinaisons jamais vues = « hors domaine » ; CYP2D6 et HLA non lisibles depuis un VCF de variants ponctuels (formulaire de laboratoire) ; TCA/voriconazole « à éviter » vs CPIC Optional/Moderate ; ibuprofène (C01EB16) en Cardiologie.
- Testé sur WSL et Linux ; pas sur macOS ni Windows natif ; pas sur une machine sans git ni Java.

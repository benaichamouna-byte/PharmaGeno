# PharmaGeno v8r : essai pas à pas

PharmaGeno est un outil de recherche (mémoire de master, ENSI) : le clinicien téléverse le fichier VCF d'un patient, choisit sa spécialité, et l'outil propose des médicaments en feux tricolores (à prescrire / dose à adapter / à éviter), avec les gènes qui expliquent chaque avis. **Il n'est pas validé cliniquement.**

## Installation (Linux, macOS ou WSL ; Python 3.12 ou plus récent ; environ 15 minutes)
1. Ouvrir un terminal dans le dossier du paquet décompressé, puis :
   `python3 -m venv .venv && source .venv/bin/activate`
2. `pip install torch --index-url https://download.pytorch.org/whl/cpu` puis `pip install -r requirements.txt` (dans cet ordre).
3. `python3 verifier_installation.py` doit afficher **INSTALLATION CORRECTE**.
4. `bash installer_vcf.sh` installe la lecture des VCF (pysam, PyPGx 0.27.0, panel de référence 1000 Genomes téléchargé depuis GitHub). Prérequis : `git` et Java (`sudo apt install git default-jre-headless` si absents ; le script le dit).
5. `bash lancer.sh`, puis ouvrir http://127.0.0.1:5000

## Essai
Sur l'accueil : « Choisir un fichier » -> `exemples/NA19472.vcf` (échantillon public 1000 Genomes, aucun patient réel), spécialité **Cardiologie**, « Lancer l'analyse ». La lecture des gènes par PyPGx prend plusieurs minutes. Ensuite : les trois feux, le tableau « Qui donne l'avis » par famille de médicaments (DL, directive officielle, XGBoost, Random Forest avec leur score de 0 à 1), les références, le PDF, le formulaire facultatif de laboratoire (CYP2D6 et HLA, non lisibles dans un VCF).

## À savoir
- Les scores 0-1 mesurent la certitude de chaque modèle à reproduire la directive CPIC/DPWG ; ce n'est pas une probabilité que l'avis soit juste cliniquement. Détails : README_DEPLOIEMENT.md, section 3 bis.
- Limites : 21 médicaments de règles sans modèle ne sont pas intégrés ; une combinaison de génotypes jamais vue à l'entraînement est signalée « hors domaine » ; la publication précise de chaque directive par médicament n'est pas encore associée (référence générale de la source + fiche ClinPGx affichées).
- Données : le serveur n'écoute que sur 127.0.0.1, sans authentification ; le VCF est supprimé à la fin de l'analyse.

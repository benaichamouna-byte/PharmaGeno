# Migration application v14 — étape 1 : table ATC (2 novembre 2026)
Nouveau fichier : `data/atc_mapping_medicaments_v14.csv` (560 lignes = 530 de la v1, INCHANGÉES, + 30 ajouts). `atc_mapping_medicaments_v1.csv` reste intact. Fichier d'appui : `data/atc_mapping_medicaments_v14_ajouts_a_valider.csv` (56 médicaments ajoutés au corpus depuis v8, avec statut).
## Bilan des 56 médicaments à intégrer (v14 moins les 133 de l'application)
- 18 étaient déjà dans la table v1 (code ATC de l'index OMS, snapshot 25 avr. 2026) : conservés. Les exports ClinPGx concordent pour 17 ; **désaccord pour nilotinib** (ClinPGx L01XE08, table v1 L01EA03) : la valeur OMS de la v1 est conservée.
- 30 ajoutés depuis les exports ClinPGx (champ « ATC Identifiers »), fiabilité « élevée », noms ATC non renseignés, à recouper avec l'index OMS (le code ClinPGx peut être plus ancien que celui de l'OMS, voir nilotinib).
- **8 NON intégrés, à valider** : aripiprazole lauroxil (code incomplet N05AX), ascorbic acid plain (A11GA) et combinations (A11GB) (codes incomplets), deuruxolitinib et sodium ascorbate (aucun code), dextromethorphan / bupropion, lidocaine / prilocaine (8 codes), lidocaine and tetracaine (codes multiples). Sans code de référence, ils n'apparaissent dans aucune spécialité ; le DL peut les couvrir.
- Résultat : 181 des 189 médicaments v14 sont dans la table.
## Rattachement aux spécialités (même règle que `recommandation_v8n.medicaments_de_specialite` : préfixe ATC)
- Les 48 médicaments prêts sont rattachés automatiquement par les 86 lignes de `specialite_atc_v1.csv` (inchangées) : Neurologie +9, Douleur et anesthésie-réanimation +8, Oncologie +8, Psychiatrie +6, Endocrinologie +5, Hématologie +4, Gastro-entérologie +3, Gynécologie-obstétrique +2, Cardiologie +1, Dermatologie +1, Pneumologie +1, Rhumatologie +1 (certains médicaments comptent dans deux spécialités).
- **3 médicaments prêts sans spécialité** : lonafarnib (A16A), relugolix / estradiol / noréthistérone (H01CC54), sodium nitrite (V03AB08). 9 médicaments de l'application actuelle sont déjà dans ce cas (aminosalicylic acid, dimercaprol, eliglustat, methylene blue, sulfamethazine, sulfamethoxazole / trimethoprim, sulfisoxazole, toluidine blue, vitamin K and analogues). Ajouter des spécialités serait un choix de conception : non fait, à décider.
- Les spécialités restent « proposé (choix de conception, à valider) » (statut de la v1).
## Limites
- `alternatives_atc4_v1.csv` n'est pas lu par la logique de recommandation (les alternatives sont recalculées depuis la table ATC) : pas de v14 à produire pour l'instant.
- Aucun médicament n'a été retiré ; aucun modèle n'a été modifié à cette étape.
## Suite
Domaine v14 (189 médicaments) et règles, réentraînement du DL, moteur, application v8q (voir `Plan_migration_app_v14_2nov2026.md`).

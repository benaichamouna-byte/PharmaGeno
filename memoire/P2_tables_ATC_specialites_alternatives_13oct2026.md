# P2 — Médicament ↔ ATC, spécialité ↔ ATC, alternatives (13 oct 2026)

Statut : **brouillon à valider**. Les tables sont construites et contrôlées (comptes, doublons, cas connus). Aucune validation clinique n'a été faite.

## 1. Source et méthode
- Source ATC : index ATC/DDD de l'OMS (WHO Collaborating Centre), copie du 25/04/2026 publiée sur https://github.com/fabkury/atcd (fichier `WHO ATC-DDD 2026-04-25.csv`, 6 996 codes). Site d'origine : https://atcddd.fhi.no/atc_ddd_index/. Licence du dépôt : CC BY-NC-SA 4.0 (usage non commercial : compatible avec un mémoire, à citer).
- Les sources en ligne (RxNorm, PharmGKB, ChEMBL, PubChem, whocc.no) sont bloquées depuis mon environnement : aucune n'a été utilisée.
- Correspondance médicament → ATC, dans cet ordre, avec la méthode notée ligne par ligne (`match_type`) :
  1. `exact` : nom du corpus identique à un nom ATC de niveau 5.
  2. `synonyme_source_wikipedia` : paires USAN→INN lues sur https://en.wikipedia.org/wiki/United_States_Adopted_Name (glyburide→glibenclamide, meperidine→pethidine, rifampin→rifampicin…).
  3. `sel_ou_forme_retire` : retrait d'un mot de sel ou de forme (hydrochloride, sodium, tartrate…) puis correspondance exacte.
  4. `synonyme_INN_a_valider` : variantes d'orthographe INN que je connais mais **non vérifiées en ligne** (cyclosporine→ciclosporin, succinylcholine→suxamethonium, thioguanine→tioguanine, aspirin→acetylsalicylic acid…).
  5. `candidat_a_valider` : préfixe ou orthographe proche trouvés dans le fichier ATC (olmesartan→olmesartan medoxomil, dabigatran→dabigatran etexilate, flupenthixol→flupentixol…).
  6. `non_trouve` : rien n'est inventé.

## 2. Résultats (fichier `atc_mapping_medicaments_v1.csv`)
- 530 noms de médicaments du corpus. Pour les 437 avec empreinte : **368 reçoivent un code ATC** (310 fiabilité élevée, 36 moyenne, 22 « à valider ») ; 69 n'en reçoivent pas.
- Parmi les 69 : 38 métabolites probables, 2 classes de médicaments, 1 nom corrompu (catégories par règle, donc à confirmer) et 28 à examiner (apatinib, lopinavir, lumefantrine, metaxalone, quinacrine, sulfisoxazole, uracil…).
- Lignes du corpus couvertes : 45 939 sur 46 371 (99,1 %) pour les médicaments avec empreinte et ATC.
- Attention : le sel « sulfate » d'`estrone sulfate` est un conjugué, pas un sel : marqué « à valider ».
- Colonne `principe_actif` : un seul nom par principe actif (par exemple `citalopram` et `citalopram hydrobromide` → `citalopram`), pour ne pas proposer deux fois le même médicament.

## 3. Spécialité ↔ ATC (fichier `specialite_atc_v1.csv`)
- 17 spécialités, rattachées à des classes ATC (noms officiels vérifiés dans le fichier OMS : tous les codes existent).
- **Le choix de rattacher une classe ATC à une spécialité est une décision de conception, pas une donnée issue d'une source.** À faire valider par un clinicien ou ton encadrant.
- Une classe peut appartenir à plusieurs spécialités (B01, G03, S03, A04).
- 362 des 368 médicaments avec ATC sont couverts par au moins une spécialité. Non couverts : deferasirox, dimercaprol, eliglustat, glucose, methylene blue, nitisinone.
- **Limite importante :** l'ATC range un médicament selon son usage principal. La codéine (corpus) n'a que le code R05DA04 (toux et rhume) : elle n'apparaîtrait donc pas pour la spécialité « Douleur et anesthésie ». Il faudra une table de **corrections d'usage clinique**, médicament par médicament, validée.
- La spécialité « médecine générale / toutes » n'est pas incluse : elle balaierait tous les médicaments, ce qui contredit la spécification (liste courte).

## 4. Alternatives (fichier `alternatives_atc4_v1.csv`)
- Règle : deux principes actifs sont alternatives s'ils partagent le même sous-groupe pharmacologique ATC (4e niveau, 5 caractères). Exemple : citalopram, escitalopram, fluoxetine, fluvoxamine, paroxetine, sertraline (N06AB).
- 210 classes ; 99 ont au moins 2 principes actifs ; 111 principes actifs sur 431 n'ont aucune alternative dans le corpus.
- **L'équivalence clinique n'est pas affirmée** : même classe ATC ne veut pas dire interchangeable pour tel patient. Le classement final restera celui du modèle, avec la mention que l'ordre est une confiance du modèle, non validée cliniquement.

## 5. À valider par toi (ou l'encadrant)
1. Les 22 correspondances « à valider » (feuille filtrable : `fiabilite = à valider`).
2. Les 28 noms « à examiner » : médicament réel (à compléter à la main) ou à exclure.
3. La liste des 17 spécialités et leurs classes ATC.
4. Quels médicaments nécessitent une correction d'usage (codéine, tamoxifène, etc.).

## Journal de Bord (extrait)
1) Décisions validées : option A pour les gènes absents (« normal » si couvert par des 0/0, sinon « non déterminé ») — **réponse à confirmer** car la question « d'autres options ? » est restée ouverte ; ATC OMS comme référence de classification.
2) Erreurs à ne plus reproduire : annoncer un chiffre sans le recalculer ; interpréter « pas autre options » comme une instruction (c'était une question).
3) Reste à faire : validation des tables P2 ; P3 corpus v3 ; P4 entraînement ; P5–P7.

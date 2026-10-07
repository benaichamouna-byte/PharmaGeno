# CORRECTIONS — `PharmaGeno_Memoire_Chapitres_1_2_FINAL.docx`

**Vérifié le 7 octobre 2026.** Document : 7 643 mots, chapitre 1 (9 références) + chapitre 2 (35 références).

`✔` = vérifié par mes soins sur une page éditeur, dépôt institutionnel ou DOAJ.
`⚠` = non vérifié — à contrôler toi-même avant de figer.

---

## CE QUI EST RÉGLÉ

Les onze points du feedback précédent sont traités. Vérifications positives :

- **« 61 publications revues par les pairs »** (§2.5.1) — corrigé, conforme au texte de Partin et al. ✔
- **DeepCDR** — `2020;36(Supplement_2):i911-i918, doi:10.1093/bioinformatics/btaa822` ✔ exact
- **URL PharmCAT Research Mode** — `pharmcat.clinpgx.org` ✔ correcte dans [15] du chapitre 2
- **DL-ADR intégré** (§2.4.2) avec la distinction explicite — la revendication de nouveauté du §2.9.2 est désormais protégée
- **Kebir et al. 2026** (§2.4.4 et §2.9.3), **Zack et al. 2025** (§2.4.3), **DGANet** (§2.4.2), **Sherman et al. 2024** (§2.2.5, §2.3.2, §2.9.2.1) — tous intégrés et correctement décrits
- **Praski et al. 2025** (§2.6.3) avec signalement du statut de préprint
- **§2.8.4 Asymétrie des erreurs cliniques** — section créée
- **§2.3.4 Matériaux de référence GeT-RM** — section créée, ce qui ancre enfin méthodologiquement le test sur cas réel
- **Niveaux de preuve nommés** : 1A–4 pour PharmGKB (§2.2.1), A/B/C/D pour CPIC (§2.2.2)

Nouvelles vérifications sur les références que tu as **ajoutées ou complétées** :

| Réf. | Statut |
|---|---|
| ch.1 [1] Hodel et al. 2024, *Clin Transl Sci* 17(9) | ✔ auteurs, revue, volume confirmés. **« 97,3 % » confirmé mot pour mot** dans la source |
| ch.1 [2] Jithesh et al. 2022, *npj Genom Med* 7(1), doi 10.1038/s41525-022-00281-5 | ✔ **« 3,6 génotypes actionnables » et « 99,5 % » confirmés tous les deux** |
| ch.2 [20] Gaedigk et al. 2019, *J Mol Diagn* 21(6):1034-1052, doi 10.1016/j.jmoldx.2019.06.007 | ✔ **exact, y compris les 179 échantillons** (137 recaractérisés + 42 nouveaux) |
| ch.2 [35] Araf, Idri, Chairi 2024, *Artif Intell Rev* 57:80, doi 10.1007/s10462-023-10652-8 | ✔ **référence réelle ET contenu adéquat** — l'article traite explicitement du coût asymétrique faux négatifs / faux positifs en médecine |
| ch.2 [33] Lundberg & Lee, NeurIPS 2017 | ✔ présent dans les actes officiels |

La référence [35] était celle que je redoutais le plus, puisqu'elle était entièrement nouvelle. Elle est solide et soutient réellement le §2.8.4.

---

## 1. DÉFAUTS BLOQUANTS — à corriger avant toute diffusion

### 1.1 Les titres de chapitre ne sont pas des styles de titre

C'est le défaut structurel principal du document fusionné.

- `CHAPITRE 1 — INTRODUCTION GÉNÉRALE` est un **paragraphe en gras**, pas un *Titre 1*.
- `CHAPITRE 2 — ÉTAT DE L'ART ET VERROUS SCIENTIFIQUES` est un **paragraphe normal, même pas en gras**.
- Les sections `1.1`, `2.1` sont en *Titre 1* ; les sous-sections `1.4.1`, `2.1.1` en *Titre 2*.

Trois conséquences :
1. La table des matières listera `1.1, 1.2 … 2.1, 2.2` au niveau supérieur, **sans aucune entrée de chapitre**.
2. Les deux titres de chapitre n'ont pas la même apparence — visible immédiatement à la lecture.
3. La hiérarchie entière est décalée d'un niveau.

**Correction :**
- `CHAPITRE 1 — …` et `CHAPITRE 2 — …` → style **Titre 1**
- toutes les sections `X.Y` → **Titre 2**
- toutes les sous-sections `X.Y.Z` → **Titre 3**
- les trois `2.9.2.1 / .2 / .3` → **Titre 4**

Puis `Références → Table des matières → Mettre à jour la table`.

### 1.2 Deux références sans URL

- **ch.1 [7]** : `PharmCAT Documentation. Using PharmCAT; Calling CYP2D6; Outside Call Format. PharmCAT. Consulté en octobre 2026.` → **aucune URL**. Une référence web sans URL n'est pas vérifiable. Ajoute `https://pharmcat.clinpgx.org/using/Calling-CYP2D6/`. Incohérent avec ch.2 [15], où tu as bien mis l'URL.
- **ch.2 [19]** : `Centers for Disease Control and Prevention. GeT-RM Reference Materials — Pharmacogenetics and HLA. CDC Laboratory Quality. Consulté le 6 octobre 2026.` → **aucune URL**. L'adresse officielle est `https://www.cdc.gov/lab-quality/php/get-rm/reference-materials.html`.

### 1.3 Contradiction entre le chapitre 1 et le chapitre 2

**§1.2** affirme : « *Une synthèse publiée en 2025 rapporte une couverture de 34 gènes et 164 médicaments [5]* ».
**§2.2.2** affirme l'inverse comme règle : « *Les dénombrements de gènes et médicaments couverts évoluant dans le temps, ils doivent être rattachés à une date ou à une version du référentiel [6,7]* ».

Le chapitre 2 énonce une règle méthodologique que le chapitre 1 enfreint deux pages plus tôt. Un rapporteur qui lit les deux chapitres le relèvera.

**Correction :** garde le chiffre dans le §1.2 mais rattache-le explicitement — « *une synthèse publiée en 2025 rapportait, à cette date, une couverture de 34 gènes et 164 médicaments [5,7]* » — et cite [7] (le portail CPIC avec date de consultation) à côté de [5]. Le passé « rapportait » et la double citation suffisent.

**Et vérifie le chiffre lui-même** : je n'ai toujours pas pu accéder au texte de Caudle et al. (Wiley bloque l'accès automatisé). Tu as ajouté la pagination `118(6):1512-1522`, ce qui suggère que tu as ouvert l'article — confirme-moi que la phrase portant « 34 gènes et 164 médicaments » y figure bien.

### 1.4 Le chiffre clé du §2.9.2.1 ne dit pas ce qui a été mesuré

Texte actuel : « *l'audit interne identifie 186 médicaments sur 530 pour lesquels plusieurs déterminants génétiques **doivent être pris en compte** dans la construction des actions.* »

Ce que ton audit a réellement établi : sur les 530 médicaments du corpus, **87 portent une action constante, 257 ont une action déterminée par un seul gène, et 186 requièrent au moins deux gènes** (87 + 257 + 186 = 530).

« Doivent être pris en compte » énonce une obligation clinique. Le fait mesuré est une propriété du corpus. La nuance est exactement celle qu'un jury attaque.

**Formulation à employer :** « *l'analyse de déterminisme du corpus établit que pour 186 des 530 médicaments, l'action n'est pas déterminée par un gène unique — 87 médicaments portent une action constante et 257 une action déterminée par un seul gène (chapitre 3).* »

Avantage : le chiffre devient vérifiable, la décomposition prouve qu'il vient d'un calcul et non d'une impression, et le renvoi au chapitre 3 indique où il est démontré.

---

## 2. À VÉRIFIER TOI-MÊME (⚠)

Ces paginations et DOI, tu les as complétés ; je n'ai pas pu les confirmer. Aucun n'est suspect, mais aucun n'est validé.

| Réf. | Élément non vérifié |
|---|---|
| ch.1 [1] Hodel | numéro d'article `e70009` et DOI `10.1111/cts.70009` |
| ch.1 [3] Chanfreau-Coffinier | référence entière + le chiffre de 99 % |
| ch.1 [5] / ch.2 [6] Caudle | pagination `118(6):1512-1522` **et** le chiffre 34/164 |
| ch.1 [9] PubChem 2025 | pages `D1516-D1525`. L'article existe (Kim S, Chen J, Cheng T, et al.), mis en ligne le 18 novembre 2024 pour le numéro *Database Issue* `2025;53(D1)` — l'année et le volume que tu cites sont donc cohérents |
| ch.2 [4] Whirl-Carrillo | DOI `10.1002/cpt.2350` et pages `563-572` |
| ch.2 [5] Relling & Klein | pages `89(3):464-467` (le DOI `10.1038/clpt.2010.279` est ✔) |
| ch.2 [10] ClinVar | DOI `10.1093/nar/gkx1153` et pages `46(D1):D1062-D1067` |
| ch.2 [29] HiDRA | pages `3858-3867` |
| ch.2 [30] Rogers & Hahn | `50(5):742-754` |
| §1.1 | le « **6 045 génomes qataris** » : la source confirme les 3,6 génotypes et les 99,5 %, mais je n'ai pas vu la taille de cohorte |

**Méthode la plus rapide :** pour chacune, ouvre `https://doi.org/<le DOI>` et relève volume, numéro et pages sur la page de l'éditeur. Dix vérifications, une dizaine de minutes.

Pour [33] Lundberg & Lee, je recommande de remplacer la pagination par l'URL des actes — les numéros de page diffèrent entre l'édition NIPS et l'édition Curran : `https://papers.nips.cc/paper_files/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf`.

---

## 3. RÉDACTION ET PRÉSENTATION

### 3.1 Deux formules orphelines en gras

- **§2.5.1** : la ligne `profil tumoral ou cellulaire + médicament → sensibilité thérapeutique` flotte entre deux paragraphes.
- **§2.6.4** : la section **commence** par `512 bits Morgan + 6 descripteurs physico-chimiques`, puis la phrase suivante dit « *Ce choix constitue une baseline…* » — le référent de « ce choix » est un fragment en gras, pas une phrase.

Dans un mémoire, ces lignes doivent être soit des formules centrées correctement légendées, soit intégrées à la phrase. Pour le §2.6.4 : « *PharmaGeno retient une empreinte de Morgan de 512 bits complétée par six descripteurs physico-chimiques. Ce choix constitue une baseline structurale contrôlable, et non…* »

### 3.2 Titres des deux bibliographies incohérents

`Références du chapitre` (ch.1) et `Références du chapitre 2` (ch.2). Uniformise en `Références du chapitre 1` / `Références du chapitre 2`.

### 3.3 §2.3.4 — une phrase vague juste avant une phrase précise

« *La ressource consolidée couvre actuellement plusieurs centaines d'échantillons et plusieurs dizaines de gènes/loci [19].* »

Trois problèmes : « plusieurs centaines » et « plusieurs dizaines » ne sont pas des quantités ; « actuellement » n'est pas daté ; et `gènes/loci` avec une barre oblique relève de la note de travail. D'autant que la phrase suivante donne un chiffre exact et désormais vérifié (179 échantillons) — le contraste souligne le flou.

Donne le nombre avec sa date de consultation, ou supprime la quantification et garde seulement la nature de la ressource.

### 3.4 §2.6.3 — tu affaiblis ton meilleur argument

Texte actuel : « *la baseline ECFP reste extrêmement compétitive et qu'une amélioration neuronale significative n'est pas systématiquement observée [31]* ».

Ce que le benchmark établit réellement : **la quasi-totalité des approches neuronales n'apporte aucune amélioration, ou une amélioration négligeable, par rapport à la baseline ECFP ; seul CLAMP — lui-même fondé sur les empreintes — se distingue statistiquement.**

C'est plus fort que ta formulation, et c'est exact. Comme c'est la seule source qui justifie le choix central du §2.6.4, autant l'énoncer à sa vraie portée.

### 3.5 §2.6.2 — attribution de l'empreinte (facultatif)

Tu écris « *Les empreintes ECFP/Morgan … ont été introduites … [30]* », avec [30] = Rogers & Hahn 2010. Exact pour **ECFP**. Mais le nom « Morgan » renvoie à l'algorithme de Morgan (1965), et ton code appelle `GetMorganFingerprint`. Si tu veux être rigoureux sur la filiation, une incise suffit : les empreintes circulaires dérivent de l'algorithme de canonisation de Morgan, formalisées sous le nom ECFP par Rogers et Hahn. Ce n'est pas une erreur, seulement une précision.

---

## 4. UNE DÉCISION À FIGER MAINTENANT

Tu as choisi **une bibliographie par chapitre**, avec numérotation qui repart de [1]. Conséquence : un même travail porte des numéros différents selon le chapitre — Caudle est [5] au chapitre 1 et [6] au chapitre 2 ; PREPARE est [4] puis [9] ; PharmCAT [6] puis [14] ; RDKit [8] puis [32].

C'est un choix légitime et courant. Mais il faut le **verrouiller pour les huit chapitres**, parce que basculer vers une bibliographie globale unique au chapitre 8 impose de renuméroter l'intégralité des appels de citation du mémoire.

Deux options, à trancher maintenant :
- **Bibliographie par chapitre** (ton choix actuel) : simple à maintenir, mais ~8 listes avec des recouvrements, et un lecteur qui suit une référence d'un chapitre à l'autre doit changer de repère.
- **Bibliographie globale unique** en fin de mémoire : une seule numérotation, usage dominant en mémoire de master. Exige un gestionnaire de références (Zotero + plugin Word) pour éviter la renumérotation manuelle.

**Ma recommandation : bibliographie globale, gérée sous Zotero.** Tu as 44 références après deux chapitres et six chapitres à écrire — tu finiras entre 90 et 130. À ce volume, une numérotation manuelle sur huit listes produira des erreurs, et une erreur de numéro de référence dans un mémoire est un défaut que le jury relève systématiquement. Si tu passes à Zotero maintenant, la bascule coûte une soirée ; au chapitre 6, elle coûtera une semaine.

---

## 5. ORDRE D'EXÉCUTION

1. Styles de titre (§1.1 ci-dessus) + mise à jour de la table des matières
2. Les deux URL manquantes — ch.1 [7] et ch.2 [19]
3. La contradiction §1.2 / §2.2.2 sur le dénombrement CPIC
4. La reformulation du 186/530 au §2.9.2.1
5. Les dix vérifications de la section 2
6. Les points de rédaction de la section 3
7. Trancher la question de la bibliographie (section 4) **avant d'attaquer le chapitre 3**

Les points 1 à 4 sont des défauts réels. Les points 5 à 7 sont ce qui sépare un mémoire correct d'un mémoire sans reproche.

---

## 6. SAUVEGARDE / ÉTAT D'AVANCEMENT

**Acquis**
- Chapitres 1 et 2 fusionnés en un document unique, 7 643 mots, 44 références (9 + 35).
- Les onze points du feedback précédent sont traités ; les deux erreurs factuelles sont corrigées.
- Cinq références nouvelles vérifiées en profondeur : Hodel (97,3 % confirmé), Jithesh (3,6 et 99,5 % confirmés), Gaedigk GeT-RM (179 échantillons confirmés), Araf (référence réelle et contenu adéquat), Lundberg & Lee (présent dans les actes NeurIPS).
- Le §2.9.2 énonce désormais explicitement le caractère étroit de la revendication, ce qui la rend défendable.
- Le §2.3.4 ancre méthodologiquement le test sur matériaux de référence GeT-RM.

**Erreurs à ne plus reproduire**
- Un titre de chapitre doit être un style *Titre 1*, jamais un paragraphe en gras.
- Toute référence web porte une URL **et** une date de consultation — sans exception.
- Ne jamais énoncer dans un chapitre une règle méthodologique qu'un autre chapitre enfreint.
- Un chiffre issu de l'audit interne doit être formulé exactement comme il a été mesuré, pas reformulé en obligation clinique.
- Ne pas affaiblir une source quand sa conclusion réelle est plus favorable et tout aussi exacte.

**Décisions en attente**
- Bibliographie par chapitre ou bibliographie globale sous Zotero — **à trancher avant le chapitre 3**.

**Rappels inchangés**
- `train_neg.py` : diagnostiquer progression réelle contre blocage (`ps -o pid,etime,time,%cpu,%mem`), puis lancer `train_final.py`.
- Expériences non lancées : mono-gène vs multi-gènes (RQ1), ablation attention (RQ3), leave-one-drug-out (RQ5), SHAP + concordance CPIC (RQ6).
- Application Flask : règle écrite à la main `app.py:61`, `predict_v2.py` à basculer sur le profil complet, modèles `*_31genes` à remplacer.
- Test sur cas réel documenté (GeT-RM) : désormais justifié dans le §2.3.4, mais toujours non exécuté.

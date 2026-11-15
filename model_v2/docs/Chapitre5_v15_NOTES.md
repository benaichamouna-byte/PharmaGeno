# Chapitre 5 v15 — notes

**Ce document ne fait pas partie du mémoire.** Il accompagne `Chapitre5_v15_MEMOIRE.md` et `AnnexeB_v15_MEMOIRE.md`, qui remplacent le chapitre 5 et l'annexe B de `Memoire_texte_v6.md`.

## 1. Ce qui a changé par rapport au texte v6 (v8s, corpus v14)
- Version décrite : v8u révision 3 (corpus v15). Le numéro de version a été retiré du titre du chapitre (registre jury : la version est un détail de développement ; elle reste dans l'annexe A, tableau A.2, **à compléter avec v8t et v8u**).
- Seuil d'abstention 0,9965 → **0,9981** (quantile à 1 % v15).
- Domaine « hors domaine » construit sur les **1 241 profils de développement** (et plus sur les 1 379).
- Random Forest : F1 et ECE de validation interne v15 (**0,9358 / 0,1544**, valeurs de ta machine, qui font foi) ; justification des réglages ajoutée (trois essais, faits sur la version antérieure du corpus).
- Texte des directives : « en anglais, non traduit » était faux → « en anglais ou en français selon la règle ; la fiche fait foi ».
- Nouveau paragraphe « Ce qui est affiché pour expliquer un avis » (révision 3 : génotype lu, mention du diplotype).
- § 5.5 : règle « aucun médicament évalué ne disparaît » (révision 3).
- § 5.6 : PDF « 11 à 13 sections numérotées sans saut » (au lieu de « 13 sections ») ; libellés traduits sauf tableau de vérification.
- § 5.8 : **76 tests, 86 contrôles** (au lieu de 68 / 78) ; T27 v15 : 2 sur 2 712 contre 77 ; NA19472 en Cardiologie, 86 s, deux environnements identiques sur 22 gènes (au lieu de « Hématologie, 63 s »).
- § 5.9 : exigence pandas < 3 et message de diagnostic.
- § 5.10 : point 4 (domaine par médicament, cas HG03684 du § 6.7) ; point 7 réécrit sur les résultats v8t (95,9 %, écart réel warfarine 5/70) ; l'ancienne mention « VKORC1 omis pour la warfarine » est supprimée (corrigé en v15) ; point 9 : **79 textes sur 709** tronqués (au lieu de 81 sur 704) ; point 10 remplacé (les deux défauts d'affichage de v8s sont corrigés) par le refus prudent de l'assemblage et le message « --assembly ».
- § 5.11 : tous les chiffres relus sur les captures et les JSON de l'analyse (voir `Captures_v8u_MANIFESTE_NOTES.md`). Changements visibles : **warfarine en vert** (règle v15), hydralazine en orange, 13 médicaments dans le tableau des avis, décompte 140/17/19/13, résumé PDF 110 / 1 / 72, citalopram « à vérifier ».

## 2. Numérotation des figures (corrigée)
Le texte v6 mélangeait les numéros (une figure « B.1 » dans le corps du chapitre, deux « Figure 5.4 »). Nouvelle numérotation, cohérente avec le texte :
- Corps : 5.1 chaîne de traitement, 5.2 accueil, 5.3 résultat, 5.4 trois modèles, 5.5 formulaire rempli, 5.6 après saisie, 5.7 PDF page 1.
- Annexe B : B.1 progression, B.2 fiche warfarine, B.3 experts B01AA, B.4 comment le programme a travaillé, B.5 gènes lus, B.6 vue patient.
- **À vérifier dans les autres chapitres** : les renvois vers « figure 5.x » et « section 5.10, point x » (chapitres 6, 7, 8). Ancien point 7 de 5.10 → nouveau point 7 (contenu changé) ; ancien point 10 → nouveau point 10 (contenu changé) ; nouveau point 4.

## 3. Points d'honnêteté à garder en tête pour la soutenance
- **Avis warfarine de NA19472** : l'écran affiche « dose standard » pour CYP2C9 \*1/\*8. PharmCAT recommande 65 % pour ce génotype (NA12815, NA19226 au chapitre 8). Le texte le dit ; ne pas le présenter comme un « bon » avis. C'est l'exemple le plus parlant de la limite du codage par score d'activité.
- **Révision 3** : elle a été écrite hors de la conversation principale et adoptée après vérification (86/86). Rien à écrire dans le mémoire sur cette provenance (règle 3 : pas d'historique de travail), mais le document `Application_v8u_corrections_test_manuel_15nov2026.md` la trace.
- **Bouton « Choose File »** de la figure 5.2 : libellé du navigateur de capture ; une phrase du § 5.11 le signale sans détail technique.
- **ABCG2 95,7 %, CYP2B6 92,8 %** : contrôle fait avec le lecteur v8 sur le corpus v14 ; le lecteur v9 ne change que CYP2C9, ces valeurs restent donc valables, mais elles ne sont pas recalculées sur v15 (le génotype PyPGx enregistré est le même).
- **« PyTorch 2.14.1 ou plus récent »** et la durée de la vérification sont repris du texte v6, non revérifiés aujourd'hui.

## 4. Longueur
Environ 5 900 mots, soit de l'ordre de 13 à 14 pages avec les 7 figures du corps. Avec les chapitres 3 et 4, « Matériel et méthodes » dépasse largement les 5 à 10 pages du formulaire ISBST : c'est la **décision n° 10 à demander au Pr. Ghedira** (réduire, passer en annexe, ou assumer). Si la réduction est demandée, la coupe la moins coûteuse est le § 5.11 entier en annexe B (≈ 4 pages), en gardant dans le chapitre trois phrases et la figure 5.3.

## 5. Sauvegarde
WSL → Windows (`C:\Users\MSI\Desktop\memoire\`) → GitHub → Drive (`PharmaGeno_Memoire/`) :
`bash ~/sauver_v2.sh "chapitre 5 v15 (v8u) + annexe B" chapitre5_v15.zip`

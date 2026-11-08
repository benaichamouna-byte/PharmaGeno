#!/usr/bin/env python3
"""Étape A (grille v1.1) : étiquettes écrites A LA MAIN d'après les seuls textes PharmCAT 3.4.0 (aucune réponse de l'application consultée).
Colonnes : uid ; label (STANDARD|SURVEILLER|ADAPTER_DOSE|EVITER|AUCUNE) ; mixte (oui = plusieurs actions de catégories différentes dans le texte, on garde la plus sévère) ;
indication (oui = le texte lui-même donne des catégories différentes selon l'indication/la période) ; alt (lecture alternative si une action conditionnelle ou adoucie était comptée) ;
ambigu (oui = texte descriptif ou ambigu, cause 5 de la grille) ; cue (extrait du texte qui justifie, vérifié par le script).
Usage : python3 -I etapeA_etiquettage.py uniques.json etapeA_textes_pharmcat.csv SORTIE_etiquettes_lignes.csv"""
import csv, json, re, sys
E='EVITER'; A='ADAPTER_DOSE'; S='SURVEILLER'; N='STANDARD'; X='AUCUNE'
# uid: (label, mixte, indication, alt, ambigu, cue)
T = {}
def d(uids, label, cue, mixte='', ind='', alt='', amb=''):
    for u in uids: T[u]=(label,mixte,ind,alt,amb,cue)
d([1,3,10,11,29,41,43,50,152],X,'No recommendation')
d([59],X,'(texte vide)')
d([12,32,33,36,44,45,52,55],X,'enzyme activity must be measured')
d([60,61,63,65,67,68,69,70,71,72,73,74,76,77,78,80,81,82,84,85,88,92,93,95,97,175,185,189,191,193,195],X,'does not provide a recommendation')
d([62,64,75,86,87,89],X,'No recommendation')
d([0,8,14,24,56],E,'Avoid tertiary amine use')
d([57],E,'Choose an alternative agent')
d([25],E,'Ivacaftor is not recommended')
d([139],E,'Avoid standard dose',mixte='oui')
d([140],E,'Consider an alternative P2Y12 inhibitor',alt=S,amb='oui')
d([178],E,'choose an alternative or double the dose',mixte='oui',ind='oui')
d([120,125,128,132],E,'contraindicated')
d([105,111,112,113,134,135],E,'non-sulfonylurea alternative',mixte='oui',alt=S)
d([130],E,'alternative therapeutic approaches should be considered',alt=S)
d([2,5,6,9,16,17,23,27,28,30,39,40,42,46,47,48,49,53,141,146,147,153,155,156,157,160,163,164,165,167,168,169,170,171,136,138,143,197],N,'')
d([20,21,37,38,148,149,161,162],N,'No adjustments needed')
d([58],N,'standard of care dosing',alt=S)
d([7,15],N,'Initiate therapy with recommended starting dose',alt=A)
d([172,177,181,182,183,186,187,188,190,196],N,'action')
d([4,31,54],A,'starting doses (30')
d([66,79,174,184,192],A,'50% of the')
d([94],A,'75% of the standard')
d([51],A,'Increase starting dose 1.5 to 2 times')
d([22],A,'total daily dose of 40 to 75 mg')
d([150,151],A,'starting total daily dose of at least 75 mg')
d([18,19],A,'prescribe')
d([13,26,34,35],A,'Consider increasing dose by 50-100%',mixte='oui',ind='oui')
d([142,154,158,159],A,'consider 50% reduction',mixte='oui')
d([137,145,166],A,'lower maintenance dose',mixte='oui')
d([144],A,'400 mg/day')
d([173],A,'1.25 times the standard dose')
d([176],A,'Do not exceed')
d([180],A,'Do not exceed')
d([83],A,'70-75% of the standard dose',mixte='oui')
d([90],A,'Use 50% of the normal maintenance dose')
d([91],A,'Use 1.5 times the normal initial dose')
d([96],A,'use 65% of the standard initial dose')
d([98,99],A,'starting dosage')
d([101],A,'use a reduced dose',mixte='oui')
d([102],A,'dosage reduction is recommended')
d([110],A,'consider starting at the low end of the dosage range',mixte='oui')
d([114],A,'require lower doses',amb='oui')
d([126],A,'require lower doses',amb='oui')
d([119,133],A,'Reduce the',amb='oui')
d([198],A,'expected maintenance daily dose',amb='oui')
d([179],S,'Determine the efavirenz plasma concentration',alt=A)
d([194],S,'Monitor the plasma concentration')
d([100,103,116,117,118,124,129],S,'close monitoring')
d([104,106,115,108,109],S,'onitor')
d([107],S,'caution')
d([121,122],S,'caution')
d([127],S,'risks and benefits')
d([131],S,'observed closely')
d([123],S,'indication for discontinuing',alt=E,amb='oui')

def norm(s): return re.sub(r'\s+',' ',s).lower()
if __name__=='__main__':
    U=json.load(open(sys.argv[1])); R=list(csv.DictReader(open(sys.argv[2])))
    manque=[i for i in range(len(U)) if i not in T]; extra=[i for i in T if i>=len(U)]
    assert not manque and not extra,(manque,extra)
    assert len({*T})==len(U)
    # vérification des extraits
    bad=[]
    for i,(k,ids) in enumerate(U):
        c=T[i][5]
        if c and norm(c) not in norm(k[3]) and c!='(texte vide)' and c!='action': bad.append((i,c))
        if c=='action' and 'action' not in k[3].lower(): bad.append((i,c))
        if c=='(texte vide)': assert k[3].strip()==''
    assert not bad,bad
    idmap={}
    for i,(k,ids) in enumerate(U):
        for r in ids: idmap[r]=i
    w=csv.writer(open(sys.argv[3],'w',newline=''))
    w.writerow(['id','uid','sample','source','drug','population','label','mixte','indication','alt','ambigu','cue'])
    for r in R:
        i=idmap[r['id']]; t=T[i]
        w.writerow([r['id'],'U%03d'%i,r['sample'],r['source'],r['drug'],r['population'],*t[:5],t[5]])
    from collections import Counter
    print('textes uniques étiquetés :',len(U),'| lignes :',len(R))
    print(Counter(T[i][0] for i in range(len(U))))

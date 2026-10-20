#!/usr/bin/env python3
"""
analyser_vcf_v8.py : chaîne complète de l'application v8 en ligne de commande (sans interface web) :
  VCF patient (+ HLA saisis)  ->  vcf_to_profile_v8.lire_vcf  ->  moteur_v8.MoteurPGx (DL = moteur, XGBoost = second avis, règle CPIC affichée, sécurité)
                              ->  recommandation_v8.Recommandeur (fiche par spécialité)  ->  un fichier JSON.
--profil_json permet de partir d'un profil déjà lu (sortie de vcf_to_profile_v8.py) sans relancer PyPGx.
Usage : python3 analyser_vcf_v8.py patient.vcf.gz --specialite "Cardiologie" --hla "HLA-B*57:01=non_porteur" --sortie fiche.json \
          --bundle ~/pypgx-bundle --workdir travail --pgx-python ~/pgxenv/bin/python
"""
import argparse, json, sys
import vcf_to_profile_v8 as lecteur
from moteur_v8 import MoteurPGx
from recommandation_v8 import Recommandeur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vcf', nargs='?'); ap.add_argument('--profil_json'); ap.add_argument('--specialite', required=True); ap.add_argument('--sortie', default='fiche.json')
    ap.add_argument('--hla', default=''); ap.add_argument('--bundle'); ap.add_argument('--workdir'); ap.add_argument('--assembly', choices=['GRCh37', 'GRCh38']); ap.add_argument('--echantillon')
    ap.add_argument('--pgx-python', default=None, dest='pgx_python')
    ap.add_argument('--codage', default='codage_pypgx_valeur_v7.csv'); ap.add_argument('--tables', default='tables_cpic_v8.json')
    ap.add_argument('--modeles', default='resultats_final_v8'); ap.add_argument('--domaine', default='domaine_v8.json')
    ap.add_argument('--regles_mono', default='corpus_v7/regles_v7_monogene.csv'); ap.add_argument('--regles_multi', default='regles_v2_corrigees_multigene_v7.csv')
    a = ap.parse_args()
    if a.profil_json:
        lu = json.load(open(a.profil_json, encoding='utf-8'))
    elif a.vcf and a.bundle and a.workdir:
        try:
            lu = lecteur.lire_vcf(a.vcf, a.bundle, a.workdir, a.codage, a.tables, a.hla, a.assembly, a.echantillon, pgx_python=a.pgx_python)
        except lecteur.VCFRefuse as e: print('FICHIER REFUSÉ :', e); sys.exit(2)
        except lecteur.PyPGxIndisponible as e: print('PYPGX INDISPONIBLE :', e); sys.exit(3)
        except ValueError as e: print('ENTRÉE INVALIDE :', e); sys.exit(4)
    else:
        ap.error('donner soit un VCF avec --bundle et --workdir, soit --profil_json')
    M = MoteurPGx(a.modeles, a.domaine, a.regles_mono, a.regles_multi)
    R = Recommandeur('atc_mapping_medicaments_v1.csv', 'specialite_atc_v1.csv', 'alternatives_atc4_v1.csv', sorted(M.dom))
    if a.specialite not in R.specialites(): ap.error('spécialité inconnue ; choix : %s' % ', '.join(R.specialites()))
    res = M.predire(lu['profil'])
    fiche = R.recommander(res, a.specialite)
    json.dump(dict(profil=lu['profil'], lecture_vcf=lu.get('detail'), assemblage=lu.get('assemblage'), specialite=a.specialite, recommandation=fiche, moteur=res),
              open(a.sortie, 'w'), indent=1, ensure_ascii=False, default=str)
    print('Spécialité :', a.specialite, '| proposés', len(fiche['proposes']), '| à éviter', len(fiche['a_eviter']), '| à vérifier', len(fiche['a_verifier']),
          '| non évalués', len(fiche['non_evalues']), '| référence seule', len(fiche['reference_seule']), '| fiche écrite dans', a.sortie)

if __name__ == '__main__': main()

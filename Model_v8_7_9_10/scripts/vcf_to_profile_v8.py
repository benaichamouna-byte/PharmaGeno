#!/usr/bin/env python3
"""
vcf_to_profile_v8.py : lecteur de VCF de l'application PharmaGeno v8. Transforme un VCF (un patient) en profil pour moteur_v8.py.
vcf_to_profile.py (v7, 12 gènes) reste intact ; ce fichier réutilise ses contrôles de fichier (VCFRefuse, PyPGxIndisponible, verifier_installation,
preparer_vcf, detecter_assemblage, gene_couvert) sans les recopier.

Gènes du modèle (22) :
  18 gènes lus depuis le VCF par PyPGx 0.27.0 (run-chip-pipeline) : ABCG2, CFTR, CYP2B6, CYP2C19, CYP2C9, CYP2D6*, CYP3A4, CYP3A5, CYP4F2, DPYD, F5, G6PD, NAT2, NUDT15, SLCO1B1, TPMT, UGT1A1, VKORC1
     (* CYP2D6 : jamais appelé depuis un VCF de SNV -> toujours « non déterminé »)
  4 allèles HLA (HLA-B*15:02, HLA-B*57:01, HLA-B*58:01, HLA-A*31:01) : NON lisibles depuis un VCF de SNV -> saisis par l'utilisateur (porteur / non porteur / probable / inconnu).

Le codage valeur (0 / 0,5 / 1 / 1,5 / 2) reproduit, gène par gène, celui des profils d'entraînement (construire_profils_genes_v3.py et _v4.py) :
  G6PD                               phénotype PyPGx (G6PD Deficient 0 / Variable 0,5 / Normal 1 ; Indeterminate -> non déterminé)
  NAT2, CYP3A4                       génotype PyPGx -> table CPIC (PharmCAT) -> Poor 0 / Intermediate 0,5 / Normal 1 / Rapid 1,5 (autre phénotype -> non déterminé)
  CFTR                               génotype PyPGx -> table CPIC ivacaftor : non-responsive 0 / responsive 0,5 ; sinon Reference/Reference -> 1 ; sinon non déterminé
  NUDT15, TPMT, SLCO1B1              génotype PyPGx -> table CPIC -> codage_pypgx_valeur_v7.csv ; diplotype absent de la table ou « Indeterminate » -> non déterminé
  VKORC1                             nombre d'allèles rs9923231 : 0 -> 1 / 1 -> 0,5 / 2 -> 0
  CYP4F2                             nombre d'allèles *3 ou *4 : 0 -> 1 / 1 -> 0,5 / 2 -> 0
  ABCG2, CYP2B6, CYP2C19, CYP2C9, CYP3A5, DPYD, F5, UGT1A1
                                     phénotype PyPGx -> codage_pypgx_valeur_v7.csv (comme vcf_to_profile.py v7)
Pour ces 8 derniers gènes, les profils d'entraînement viennent du corpus v3 (valeurs d'origine) : la concordance avec PyPGx 0.27.0 est mesurée dans
concordance_pypgx_corpus_v7_resume.csv (ABCG2 95,7 %, CYP2B6 92,8 %, les autres >= 99,8 %). Ce n'est pas une identité.

Un gène « non déterminé » vaut None (jamais « normal »). Il alimente l'indicateur d'absence du modèle (moteur_v8.vecteur).
Limites déclarées : voir LISEZ_MOI_lot_vcf_v8_20oct2026.txt (G6PD sur chrX, VCF épars, heuristique « gène couvert », CYP2D6, HLA).

Usage : python3 vcf_to_profile_v8.py patient.vcf.gz --bundle ~/pypgx-bundle --workdir travail --codage codage_pypgx_valeur_v7.csv --tables tables_cpic_v8.json \
            --sortie profil.json [--hla "HLA-B*57:01=non_porteur,HLA-B*15:02=inconnu"] [--assembly GRCh38] [--echantillon NOM] [--pgx-python ~/pgxenv/bin/python]
"""
import argparse, io, json, math, os, subprocess, sys, zipfile
import pandas as pd
import pysam
import vcf_to_profile as v7
from vcf_to_profile import VCFRefuse, PyPGxIndisponible, verifier_installation, preparer_vcf, detecter_assemblage, gene_couvert

GENES_VCF = ['ABCG2', 'CFTR', 'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP2D6', 'CYP3A4', 'CYP3A5', 'CYP4F2', 'DPYD', 'F5', 'G6PD', 'NAT2', 'NUDT15', 'SLCO1B1', 'TPMT', 'UGT1A1', 'VKORC1']
GENES_HLA = ['HLA-B*15:02', 'HLA-B*57:01', 'HLA-B*58:01', 'HLA-A*31:01']
METHODE = {'G6PD': 'g6pd', 'NAT2': 'cpic_court', 'CYP3A4': 'cpic_court', 'CFTR': 'cftr', 'NUDT15': 'cpic_csv', 'TPMT': 'cpic_csv', 'SLCO1B1': 'cpic_csv',
           'VKORC1': 'compte_vkorc1', 'CYP4F2': 'compte_cyp4f2', 'CYP2D6': 'non_appelable'}   # tout autre gène : 'pypgx_phenotype'
CODAGE_COURT = {'Poor Metabolizer': 0.0, 'Intermediate Metabolizer': 0.5, 'Normal Metabolizer': 1.0, 'Rapid Metabolizer': 1.5}   # construire_profils_genes_v3.py
CODAGE_G6PD = {'G6PD Deficient': 0.0, 'G6PD Variable': 0.5, 'G6PD Normal': 1.0}
HLA_VALEURS = {'porteur': 1.0, 'probable': 0.5, 'non_porteur': 0.0, 'inconnu': None}


def charger_codage(chemin):
    return {r.phenotype_pypgx: (None if pd.isna(r.valeur) else float(r.valeur)) for r in pd.read_csv(chemin).itertuples()}


def charger_tables(chemin):
    """{gène: {frozenset(comptage des allèles): phénotype}} + métadonnées"""
    d = json.load(open(chemin, encoding='utf-8'))
    return {g: {frozenset(k.items()): ph for k, ph in lignes} for g, lignes in d['tables'].items()}, d['meta']


def _comptage(genotype):
    """'*1/*3' -> frozenset({('*1',1),('*3',1)}) ; 'A/A' -> {('A',2)} ; None si ce n'est pas une paire d'allèles"""
    if not isinstance(genotype, str): return None
    a = genotype.split('/')
    if len(a) != 2: return None
    c = {}
    for x in a: c[x] = c.get(x, 0) + 1
    return frozenset(c.items())


def _phenotype_cpic(tables, gene, genotype):
    k = _comptage(genotype)
    return None if k is None else tables[gene].get(k)


def coder_gene(gene, genotype, phenotype, tables, codage):
    """Retourne (valeur ou None, motif ou None, phénotype utilisé pour le codage). Aucune lecture de fichier ; testé sur les profils d'entraînement (test_codage_vcf_v8.py)."""
    m = METHODE.get(gene, 'pypgx_phenotype')
    if m == 'non_appelable':
        return None, "CYP2D6 : variants structuraux (délétions, duplications) non analysables depuis un VCF de SNV.", None
    if m == 'pypgx_phenotype':
        if phenotype not in codage: return None, "Phénotype PyPGx non prévu dans le codage : « %s »." % phenotype, phenotype
        if codage[phenotype] is None: return None, 'PyPGx : phénotype indéterminé.', phenotype
        return codage[phenotype], None, phenotype
    if m == 'g6pd':
        if phenotype not in CODAGE_G6PD: return None, 'PyPGx : phénotype G6PD « %s » (non codé).' % phenotype, phenotype
        return CODAGE_G6PD[phenotype], None, phenotype
    if m in ('compte_vkorc1', 'compte_cyp4f2'):
        if not isinstance(genotype, str) or len(genotype.split('/')) != 2: return None, 'PyPGx : génotype absent ou illisible (« %s »).' % genotype, None
        al = genotype.split('/'); cible = ('rs9923231',) if m == 'compte_vkorc1' else ('*3', '*4')
        n = sum(1 for x in al if x in cible)
        note = None
        if m == 'compte_vkorc1' and any(x not in ('Reference', 'rs9923231') for x in al): note = 'autre allèle que rs9923231 présent (%s) : non pris en compte, comme à l\'entraînement' % genotype
        return {0: 1.0, 1: 0.5, 2: 0.0}[n], note, '%d allèle(s) %s' % (n, '/'.join(cible))
    ph = _phenotype_cpic(tables, gene, genotype)
    if ph is None:
        if m == 'cftr' and isinstance(genotype, str) and set(genotype.split('/')) == {'Reference'}: return 1.0, None, 'Reference/Reference (aucune variation CFTR de la table)'
        return None, 'Génotype PyPGx « %s » absent de la table CPIC : non déterminé (jamais « normal »).' % genotype, None
    if m == 'cpic_court':
        if ph not in CODAGE_COURT: return None, 'Phénotype CPIC « %s » non codé.' % ph, ph
        return CODAGE_COURT[ph], None, ph
    if m == 'cpic_csv':
        if ph not in codage: return None, "Phénotype CPIC non prévu dans le codage : « %s »." % ph, ph
        if codage[ph] is None: return None, 'Table CPIC : phénotype indéterminé pour %s.' % genotype, ph
        return codage[ph], None, ph
    if m == 'cftr':   # construire_profils_genes_v3.py : « responsive » (sans « non ») 0,5 ; « non-responsive » 0 ; sinon Reference/Reference 1 ; sinon manquant
        v = 0.5 if ('responsive' in ph and 'non' not in ph) else (0.0 if 'non' in ph else None)
        if v is None and set(genotype.split('/')) == {'Reference'}: v = 1.0
        return v, (None if v is not None else 'Phénotype CFTR « %s » non codé.' % ph), ph
    raise AssertionError(m)


def lire_hla(texte_ou_dict):
    """'HLA-B*57:01=non_porteur,HLA-B*15:02=inconnu' ou dict -> {allèle: valeur ou None}. Les allèles non renseignés restent None (non typé)."""
    d = {}
    if isinstance(texte_ou_dict, str):
        for part in [p for p in texte_ou_dict.split(',') if p.strip()]:
            k, _, v = part.partition('='); d[k.strip()] = v.strip()
    elif texte_ou_dict: d = dict(texte_ou_dict)
    out = {}
    for g in GENES_HLA: out[g] = None
    for k, v in d.items():
        if k not in GENES_HLA: raise ValueError("Allèle HLA inconnu : %s (attendus : %s)" % (k, ', '.join(GENES_HLA)))
        if v not in HLA_VALEURS: raise ValueError("Valeur HLA invalide pour %s : « %s » (attendues : %s)" % (k, v, ', '.join(HLA_VALEURS)))
        out[k] = HLA_VALEURS[v]
    return out


def regions_genes(pgx_python=None, genes=GENES_VCF):
    t = pd.read_csv(os.path.join(v7._data_pypgx(pgx_python), 'gene-table.csv')); out = {'GRCh37': {}, 'GRCh38': {}}
    for b in out:
        for _, r in t[t.Gene.isin(genes)].iterrows():
            reg = r[b + 'Region']
            if isinstance(reg, str) and ':' in reg:
                c, se = reg.split(':'); s, e = se.split('-'); out[b][r.Gene] = (c.replace('chr', ''), int(s), int(e))
    return out


def normaliser_chrX_haploide(vcf, workdir):
    """Un patient de sexe masculin a un génotype HAPLOÏDE (« 1 ») sur chrX hors régions pseudo-autosomiques (G6PD : Xq28). PyPGx attend deux allèles : un allèle haploïde est
    écrit en homozygote diploïde (« 1|1 » ; hémizygote = un seul allèle, présent deux fois pour l'appel). Mesuré : sans cette conversion, un homme hémizygote pour un allèle déficient
    (HG00698, appel d'entraînement « Kaiping.../Kaiping... », G6PD Deficient) est lu « B/Kaiping... » (G6PD Variable) par run-chip-pipeline, donc moins sévère. Retourne (chemin du VCF, nombre de génotypes convertis)."""
    v = pysam.VariantFile(vcf); noms = list(v.header.samples); n_conv = 0; dest = os.path.join(workdir, 'patient_chrX_diploide.vcf.gz')
    contigs_x = [c for c in ('chrX', 'X') if c in v.header.contigs]
    if not contigs_x: v.close(); return vcf, 0
    avec_haploide = False
    for r in v.fetch(contigs_x[0]):
        if any(r.samples[s]['GT'] is not None and len(r.samples[s]['GT']) == 1 for s in noms): avec_haploide = True; break
    v.close()
    if not avec_haploide: return vcf, 0
    src = pysam.VariantFile(vcf); out = pysam.VariantFile(dest, 'wz', header=src.header)
    for r in src:
        if r.contig in contigs_x:
            for s in noms:
                g = r.samples[s]['GT']
                if g is not None and len(g) == 1 and g[0] is not None:
                    r.samples[s]['GT'] = (g[0], g[0]); r.samples[s].phased = True; n_conv += 1
        out.write(r)
    out.close(); src.close(); pysam.tabix_index(dest, preset='vcf', force=True)
    return dest, n_conv


def appeler_gene(gene, vcf, assemblage, bundle, workdir, echantillon=None, timeout=3600, pgx_python=None):
    """PyPGx run-chip-pipeline pour un gène. Retourne (génotype, phénotype ou None). Lève RuntimeError en cas d'échec."""
    sortie = os.path.join(workdir, 'pgx_' + gene)
    cmd = [pgx_python or sys.executable, '-m', 'pypgx', 'run-chip-pipeline', gene, sortie, vcf, '--assembly', assemblage, '--force']
    if echantillon: cmd += ['--samples', echantillon]
    env = dict(os.environ); env['PYPGX_BUNDLE'] = os.path.abspath(os.path.expanduser(bundle))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1][:300] if (r.stderr or r.stdout).strip() else 'échec PyPGx')
    with zipfile.ZipFile(os.path.join(sortie, 'results.zip')) as z:
        res = pd.read_csv(io.BytesIO(z.read([n for n in z.namelist() if n.endswith('data.tsv')][0])), sep='\t', index_col=0)
    if len(res) != 1 and echantillon is None:
        raise RuntimeError('le VCF contient %d échantillons : un seul patient par fichier' % len(res))
    ligne = res.iloc[0]
    ph = ligne['Phenotype'] if 'Phenotype' in res.columns and not pd.isna(ligne['Phenotype']) else None
    gt = ligne['Genotype'] if 'Genotype' in res.columns and not pd.isna(ligne['Genotype']) else None
    return (None if gt is None else str(gt)), (None if ph is None else str(ph))


def lire_vcf(chemin, bundle, workdir, codage_csv, tables_json, hla=None, assemblage=None, echantillon=None, genes=GENES_VCF, verbose=True, progres=None, pgx_python=None):
    """Retourne {'profil': {gène: float|None}, 'detail': {gène: {...}}, 'assemblage': ...} avec les 22 gènes du modèle (18 VCF + 4 HLA saisis).
    Lève VCFRefuse (fichier refusé) ou PyPGxIndisponible. progres(pourcentage, message) : facultatif (barre de progression)."""
    def _p(pc, msg):
        if progres: progres(int(pc), msg)
    hla_val = lire_hla(hla)   # validé avant tout calcul long
    _p(1, "Vérification de l'installation de PyPGx"); verifier_installation(pgx_python, bundle)
    codage = charger_codage(codage_csv); tables, meta_tables = charger_tables(tables_json)
    _p(2, 'Lecture et contrôle du fichier VCF'); vcf = preparer_vcf(chemin, workdir); regions = regions_genes(pgx_python, genes)
    vcf, n_haploides_x = normaliser_chrX_haploide(vcf, workdir)
    _p(8, "Détection de l'assemblage du génome (GRCh37 / GRCh38)")
    _v = pysam.VariantFile(vcf); _ech = list(_v.header.samples); _v.close()
    if not _ech: raise VCFRefuse("Le VCF ne contient aucun échantillon (colonnes de génotypes absentes) : l'analyse nécessite les génotypes d'un patient.")
    if len(_ech) > 1 and not echantillon: raise VCFRefuse('Le VCF contient %d échantillons : indiquez le nom de celui à analyser (option « échantillon »), un seul patient par analyse.' % len(_ech))
    if echantillon and echantillon not in _ech: raise VCFRefuse("L'échantillon « %s » n'existe pas dans ce VCF (échantillons : %s)." % (echantillon, ', '.join(_ech[:5])))
    ass, det_ass = detecter_assemblage(vcf, regions, assemblage)
    profil, detail = {}, {}
    for i, g in enumerate(genes):
        _p(12 + 86 * i / len(genes), 'Analyse du gène %s (%d/%d)' % (g, i + 1, len(genes)))
        d = dict(valeur=None, statut='non_determine', motif=None, genotype=None, phenotype_pypgx=None, phenotype_utilise=None, methode=METHODE.get(g, 'pypgx_phenotype'))
        if g == 'CYP2D6':
            d['motif'] = coder_gene(g, None, None, tables, codage)[1]
        else:
            n = gene_couvert(vcf, regions[ass], g) if g in regions[ass] else 0; d['enregistrements_dans_le_gene'] = n
            if n == 0:
                d['motif'] = 'Aucun enregistrement du VCF dans la région du gène : gène non couvert.'
            else:
                try:
                    gt, ph = appeler_gene(g, vcf, ass, bundle, workdir, echantillon, pgx_python=pgx_python)
                    d.update(genotype=gt, phenotype_pypgx=ph)
                    val, motif, utilise = coder_gene(g, gt, ph, tables, codage)
                    d.update(valeur=val, motif=motif, phenotype_utilise=utilise, statut='appele' if val is not None else 'non_determine')
                except Exception as e:
                    d['motif'] = 'Échec de PyPGx : %s' % str(e)[:300]
        profil[g] = d['valeur']; detail[g] = d
        if verbose: print('  %-8s %-6s %-26s %-30s %s' % (g, d['valeur'], d['genotype'], d['phenotype_utilise'], d['motif'] or ''), flush=True)
    appeles = [g for g in genes if detail[g]['statut'] == 'appele']
    echecs = [detail[g]['motif'] for g in genes if (detail[g]['motif'] or '').startswith('Échec de PyPGx')]
    if not appeles and echecs: raise PyPGxIndisponible("PyPGx a échoué sur tous les gènes. Première erreur : %s" % echecs[0])
    for g, v in hla_val.items():
        profil[g] = v
        detail[g] = dict(valeur=v, statut='saisi' if v is not None else 'non_determine', methode='saisie_utilisateur',
                         motif=None if v is not None else 'Allèle HLA non renseigné ou « inconnu » (non lisible depuis un VCF de SNV).')
    _p(100, 'Analyse des gènes terminée')
    return dict(profil=profil, detail=detail, assemblage=ass, controle_assemblage=det_ass, pypgx='0.27.0', tables_cpic=meta_tables, genotypes_haploides_chrX_convertis=n_haploides_x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vcf'); ap.add_argument('--bundle', required=True); ap.add_argument('--workdir', required=True)
    ap.add_argument('--codage', required=True); ap.add_argument('--tables', required=True); ap.add_argument('--sortie', default='profil.json')
    ap.add_argument('--hla', default=''); ap.add_argument('--assembly', choices=['GRCh37', 'GRCh38']); ap.add_argument('--echantillon')
    ap.add_argument('--pgx-python', default=None, dest='pgx_python')
    a = ap.parse_args()
    try:
        res = lire_vcf(a.vcf, a.bundle, a.workdir, a.codage, a.tables, a.hla, a.assembly, a.echantillon, pgx_python=a.pgx_python)
    except VCFRefuse as e:
        print('FICHIER REFUSÉ :', e); sys.exit(2)
    except PyPGxIndisponible as e:
        print('PYPGX INDISPONIBLE :', e); sys.exit(3)
    except ValueError as e:
        print('ENTRÉE INVALIDE :', e); sys.exit(4)
    json.dump(res, open(a.sortie, 'w'), indent=1, ensure_ascii=False)
    print('Assemblage :', res['assemblage'], '| profil écrit dans', a.sortie)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
vcf_to_profile.py : lecteur de VCF de l'application PharmaGeno. Transforme un VCF (un patient) en profil à 12 gènes pour moteur_v7.py.

Principe : appel des allèles étoiles et des phénotypes par PyPGx (run-chip-pipeline), puis correspondance phénotype -> valeur 0 / 0,5 / 1 / 1,5 / 2
(codage_pypgx_valeur_v7.csv ; concordance mesurée avec le corpus dans concordance_pypgx_corpus_v7_*). Le résultat pour chaque gène est :
    valeur float  : gène appelé
    None          : gène NON DÉTERMINÉ (jamais remplacé par 1,0). Causes : gène absent du VCF, phénotype « Indeterminate », échec de PyPGx,
                    CYP2D6 (variants structuraux : non analysables depuis un VCF de SNV).
Contrôles avant tout appel (le fichier est refusé avec un message clair si l'un échoue) :
    1. fichier lisible, BGZF + index tabix (si le fichier n'est pas compressé, une copie compressée et indexée est créée dans le dossier de travail) ;
    2. assemblage GRCh37 / GRCh38 : lu dans l'en-tête (longueur de chr1) ET vérifié par la position des enregistrements dans les régions des 11 gènes ;
       s'ils se contredisent, ou si l'assemblage ne peut pas être établi, le fichier est refusé ;
    3. « gène couvert » : au moins un enregistrement du VCF dans la région du gène (sinon : non déterminé, car un VCF de variants ne distingue pas
       « gène normal » de « gène non séquencé » autrement). Heuristique : sur les VCF 1KGP, le minimum observé est de 0 à 3 variants selon les gènes
       (UGT1A1 : 0 pour 1 échantillon sur 1 379, TPMT : 1) ; elle est donc prudente mais pas parfaite pour un gène court.
Limites déclarées : CYP2D6 jamais appelé ; PyPGx ne voit que les positions présentes dans le VCF (un VCF épars peut donner un appel faux, ex. CYP2C19 *2
si une seule des deux positions définissantes est présente : voir P1) ; le codage CYP2B6 / SLCO1B1 / ABCG2 du corpus d'entraînement diffère de PyPGx 0.27.0
pour 7 % / 18 % / 4 % des échantillons 1KGP (concordance_pypgx_corpus_v7_resume.csv).

Usage : python3 vcf_to_profile.py patient.vcf.gz --bundle ~/pypgx-bundle --workdir travail --codage codage_pypgx_valeur_v7.csv --sortie profil.json [--assembly GRCh38]
Prérequis : PyPGx 0.27.0 avec "pandas<3" dans un environnement dédié (option --pgx-python ; voir installer_pypgx_v7.sh), pysam, Java (Beagle), dossier pypgx-bundle 0.27.0.
"""
import argparse, io, json, os, shutil, subprocess, sys, zipfile
import pandas as pd
import pysam

GENES = ['ABCG2', 'CYP2B6', 'CYP2C19', 'CYP2C9', 'CYP2D6', 'CYP3A5', 'DPYD', 'F5', 'NUDT15', 'SLCO1B1', 'TPMT', 'UGT1A1']
LONGUEUR_CHR1 = {248956422: 'GRCh38', 249250621: 'GRCh37'}


class VCFRefuse(Exception):
    """Fichier refusé : le message est destiné à l'utilisateur."""


class PyPGxIndisponible(Exception):
    """PyPGx n'est pas utilisable dans cet environnement (installation, versions, Java, bundle) : le message explique quoi corriger."""


def verifier_installation(pgx_python, bundle):
    """Contrôle avant toute analyse : PyPGx 0.27.0 avec pandas < 3, Java, dossier pypgx-bundle. Lève PyPGxIndisponible avec un message clair."""
    pgx_python = pgx_python or sys.executable
    try:
        r = subprocess.run([pgx_python, '-c', 'import importlib.metadata as m, pypgx, pandas, numpy, fuc; print(m.version("pypgx"), pandas.__version__, numpy.__version__)'],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        raise PyPGxIndisponible("Impossible de lancer l'interpréteur Python de PyPGx (%s) : %s" % (pgx_python, e))
    if r.returncode != 0:
        raise PyPGxIndisponible("PyPGx n'est pas installé dans l'environnement %s (%s). Lancez installer_pypgx_v7.sh puis relancez l'application avec --pgx-python ~/pgxenv/bin/python." % (
            pgx_python, (r.stderr.strip().splitlines() or ['erreur inconnue'])[-1][:200]))
    pgx_v, pd_v, np_v = r.stdout.split()[:3]
    if pgx_v != '0.27.0':
        raise PyPGxIndisponible('PyPGx %s trouvé, la version validée est 0.27.0 (environnement %s).' % (pgx_v, pgx_python))
    if int(pd_v.split('.')[0]) >= 3:
        raise PyPGxIndisponible("pandas %s est incompatible avec PyPGx 0.27.0 (il faut pandas < 3). C'est la cause de l'erreur « setting an array element with a sequence ». "
                                "Lancez installer_pypgx_v7.sh puis relancez l'application avec --pgx-python ~/pgxenv/bin/python." % pd_v)
    if shutil.which('java') is None:
        raise PyPGxIndisponible("Java n'est pas installé : PyPGx en a besoin (phasage Beagle). Sous Ubuntu : sudo apt install default-jre")
    if not os.path.isdir(os.path.join(os.path.abspath(os.path.expanduser(bundle)), '1kgp')):
        raise PyPGxIndisponible("Dossier pypgx-bundle introuvable ou incomplet : %s (il doit contenir le sous-dossier 1kgp). Lancez installer_pypgx_v7.sh." % bundle)
    return dict(pypgx=pgx_v, pandas=pd_v, numpy=np_v)


def _data_pypgx(pgx_python=None):
    r = subprocess.run([pgx_python or sys.executable, '-c', 'import pypgx, os; print(os.path.dirname(pypgx.__file__))'], capture_output=True, text=True, timeout=120)
    return os.path.join(r.stdout.strip().splitlines()[-1], 'api', 'data')


def regions_genes(pgx_python=None):
    """{assemblage: {gene: (chrom sans 'chr', début, fin)}} depuis la table des gènes de PyPGx."""
    t = pd.read_csv(os.path.join(_data_pypgx(pgx_python), 'gene-table.csv')); out = {'GRCh37': {}, 'GRCh38': {}}
    for b in out:
        for _, r in t[t.Gene.isin(GENES)].iterrows():
            reg = r[b + 'Region']
            if isinstance(reg, str) and ':' in reg:
                c, se = reg.split(':'); s, e = se.split('-'); out[b][r.Gene] = (c.replace('chr', ''), int(s), int(e))
    return out


def preparer_vcf(chemin, workdir):
    """Retourne le chemin d'un VCF BGZF indexé (copie compressée créée si nécessaire)."""
    if not os.path.exists(chemin):
        raise VCFRefuse('Fichier introuvable : %s' % chemin)
    os.makedirs(workdir, exist_ok=True)
    try:
        pysam.VariantFile(chemin).close()
    except Exception as e:
        raise VCFRefuse("Fichier illisible : ce n'est pas un VCF valide (texte .vcf ou compressé .vcf.gz).")
    if chemin.endswith('.gz') and os.path.exists(chemin + '.tbi'):
        return chemin
    dest = os.path.join(workdir, 'patient.vcf.gz')
    try:
        src = pysam.VariantFile(chemin); out = pysam.VariantFile(dest, 'wz', header=src.header)
        for r in src: out.write(r)
        out.close(); pysam.tabix_index(dest, preset='vcf', force=True)
    except Exception as e:
        raise VCFRefuse("Impossible de compresser/indexer le VCF (il doit être trié par chromosome et position) : %s" % str(e).splitlines()[0])
    return dest


def detecter_assemblage(vcf, regions, assemblage_demande=None):
    """Assemblage lu dans l'en-tête ET confirmé par les enregistrements dans les régions des gènes. Retourne (assemblage, détail)."""
    v = pysam.VariantFile(vcf); entete = None
    for nom in ('chr1', '1'):
        if nom in v.header.contigs and v.header.contigs[nom].length in LONGUEUR_CHR1:
            entete = LONGUEUR_CHR1[v.header.contigs[nom].length]
    compte = {}
    for b in ('GRCh37', 'GRCh38'):
        n = 0
        for g, (c, s, e) in regions[b].items():
            for nom in (c, 'chr' + c):
                if nom in v.header.contigs:
                    n += sum(1 for _ in v.fetch(nom, s - 1, e)); break
        compte[b] = n
    v.close()
    pos = max(compte, key=compte.get); autre = 'GRCh37' if pos == 'GRCh38' else 'GRCh38'
    if compte[pos] >= 5 and compte[pos] >= 5 * max(compte[autre], 1): par_positions = pos
    else: par_positions = None
    detail = dict(entete=entete, enregistrements_dans_regions=compte, par_positions=par_positions)
    if entete and par_positions and entete != par_positions:
        raise VCFRefuse("Assemblage contradictoire : l'en-tête indique %s mais les positions correspondent à %s (%s). Fichier refusé." % (entete, par_positions, compte))
    ass = par_positions or entete
    if ass is None:
        raise VCFRefuse("Assemblage impossible à établir (en-tête sans longueur de chr1 et trop peu d'enregistrements dans les régions des gènes : %s). Précisez --assembly seulement si vous en êtes certaine." % compte)
    if assemblage_demande and assemblage_demande != ass:
        raise VCFRefuse("Vous avez indiqué %s mais le fichier ressemble à %s (%s). Fichier refusé." % (assemblage_demande, ass, detail))
    return ass, detail


def gene_couvert(vcf, regions_b, gene):
    c, s, e = regions_b[gene]; v = pysam.VariantFile(vcf); n = 0
    for nom in (c, 'chr' + c):
        if nom in v.header.contigs:
            n = sum(1 for _ in v.fetch(nom, s - 1, e)); break
    v.close(); return n


def appeler_gene(gene, vcf, assemblage, bundle, workdir, echantillon=None, timeout=3600, pgx_python=None):
    """Lance PyPGx run-chip-pipeline pour un gène. Retourne (diplotype, phénotype) ou lève RuntimeError."""
    sortie = os.path.join(workdir, 'pgx_' + gene)
    cmd = [pgx_python or sys.executable, '-m', 'pypgx', 'run-chip-pipeline', gene, sortie, vcf, '--assembly', assemblage, '--force']
    if echantillon: cmd += ['--samples', echantillon]
    env = dict(os.environ); env['PYPGX_BUNDLE'] = os.path.abspath(os.path.expanduser(bundle))   # PyPGx lit le panel de référence 1KGP dans ce dossier
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1][:300] if (r.stderr or r.stdout).strip() else 'échec PyPGx')
    with zipfile.ZipFile(os.path.join(sortie, 'results.zip')) as z:   # archive PyPGx = zip contenant data.tsv (lecture sans importer PyPGx)
        res = pd.read_csv(io.BytesIO(z.read([n for n in z.namelist() if n.endswith('data.tsv')][0])), sep='\t', index_col=0)
    if len(res) != 1 and echantillon is None:
        raise RuntimeError('le VCF contient %d échantillons : un seul patient par fichier' % len(res))
    ligne = res.iloc[0]
    return str(ligne.get('Genotype', '')), str(ligne['Phenotype'])


def lire_vcf(chemin, bundle, workdir, codage_csv, assemblage=None, echantillon=None, genes=GENES, verbose=True, progres=None, pgx_python=None):
    """Retourne {'profil': {gène: float|None}, 'detail': {gène: {...}}, 'assemblage': ...}. Lève VCFRefuse si le fichier est refusé.
    progres : fonction facultative progres(pourcentage:int, message:str), appelée à chaque étape (pour la barre de progression de l'interface)."""
    def _p(pc, msg):
        if progres: progres(int(pc), msg)
    _p(1, "Vérification de l'installation de PyPGx")
    verifier_installation(pgx_python, bundle)
    _p(2, 'Lecture et contrôle du fichier VCF')
    codage = {r.phenotype_pypgx: (None if pd.isna(r.valeur) else float(r.valeur)) for r in pd.read_csv(codage_csv).itertuples()}
    vcf = preparer_vcf(chemin, workdir); regions = regions_genes(pgx_python)
    _p(8, "Détection de l'assemblage du génome (GRCh37 / GRCh38)")
    _v = pysam.VariantFile(vcf); _ech = list(_v.header.samples); _v.close()
    if not _ech: raise VCFRefuse("Le VCF ne contient aucun échantillon (colonnes de génotypes absentes) : l'analyse nécessite les génotypes d'un patient.")
    if len(_ech) > 1 and not echantillon: raise VCFRefuse('Le VCF contient %d échantillons : indiquez le nom de celui à analyser (option « échantillon »), un seul patient par analyse.' % len(_ech))
    if echantillon and echantillon not in _ech: raise VCFRefuse("L'échantillon « %s » n'existe pas dans ce VCF (échantillons : %s)." % (echantillon, ', '.join(_ech[:5])))
    ass, det_ass = detecter_assemblage(vcf, regions, assemblage)
    profil, detail = {}, {}
    for i, g in enumerate(genes):
        _p(12 + 86 * i / len(genes), 'Analyse du gène %s (%d/%d)' % (g, i + 1, len(genes)))
        d = dict(valeur=None, phenotype=None, diplotype=None, statut='non_determine', motif=None)
        if g == 'CYP2D6':
            d['motif'] = "CYP2D6 : variants structuraux (délétions, duplications) non analysables depuis un VCF de SNV."
        else:
            n = gene_couvert(vcf, regions[ass], g); d['enregistrements_dans_le_gene'] = n
            if n == 0:
                d['motif'] = 'Aucun enregistrement du VCF dans la région du gène : gène non couvert.'
            else:
                try:
                    dip, ph = appeler_gene(g, vcf, ass, bundle, workdir, echantillon, pgx_python=pgx_python)
                    d.update(diplotype=dip, phenotype=ph)
                    if ph not in codage: d['motif'] = "Phénotype PyPGx non prévu dans le codage : « %s »." % ph
                    elif codage[ph] is None: d['motif'] = 'PyPGx : phénotype indéterminé.'
                    else: d.update(valeur=codage[ph], statut='appele')
                except Exception as e:
                    d['motif'] = 'Échec de PyPGx : %s' % str(e)[:300]
        profil[g] = d['valeur']; detail[g] = d
        if verbose: print('  %-8s %-10s %-34s %s' % (g, d['valeur'], d['phenotype'], d['motif'] or ''), flush=True)
    appeles = [g for g in genes if detail[g]['statut'] == 'appele']
    echecs = [detail[g]['motif'] for g in genes if (detail[g]['motif'] or '').startswith('Échec de PyPGx')]
    if not appeles and echecs:
        raise PyPGxIndisponible("PyPGx a échoué sur tous les gènes. Première erreur : %s" % echecs[0])
    _p(100, 'Analyse des gènes terminée')
    return dict(profil=profil, detail=detail, assemblage=ass, controle_assemblage=det_ass, pypgx='0.27.0')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vcf'); ap.add_argument('--bundle', required=True); ap.add_argument('--workdir', required=True)
    ap.add_argument('--codage', required=True); ap.add_argument('--sortie', default='profil.json')
    ap.add_argument('--assembly', choices=['GRCh37', 'GRCh38']); ap.add_argument('--echantillon'); ap.add_argument('--pgx-python', default=None, dest='pgx_python')
    a = ap.parse_args()
    try:
        res = lire_vcf(a.vcf, a.bundle, a.workdir, a.codage, a.assembly, a.echantillon, pgx_python=a.pgx_python)
    except VCFRefuse as e:
        print('FICHIER REFUSÉ :', e); sys.exit(2)
    except PyPGxIndisponible as e:
        print('PYPGX INDISPONIBLE :', e); sys.exit(3)
    json.dump(res, open(a.sortie, 'w'), indent=1, ensure_ascii=False)
    print('Assemblage :', res['assemblage'], '| profil écrit dans', a.sortie)


if __name__ == '__main__':
    main()

# vcf_parser.py
# Parseur VCF universel — PharmaGeno
import pandas as pd
import gzip
import os

RSID_TO_GENE = {
    "rs4244285":"CYP2C19","rs4986893":"CYP2C19","rs28399504":"CYP2C19",
    "rs56337013":"CYP2C19","rs72552267":"CYP2C19","rs12248560":"CYP2C19",
    "rs12769205":"CYP2C19","rs3758581":"CYP2C19","rs3814637":"CYP2C19",
    "rs3745274":"CYP2B6","rs2279343":"CYP2B6","rs8192719":"CYP2B6",
    "rs34223104":"CYP2B6","rs35303484":"CYP2B6",
    "rs3892097":"CYP2D6","rs5030655":"CYP2D6","rs16947":"CYP2D6",
    "rs1065852":"CYP2D6","rs28371706":"CYP2D6","rs769258":"CYP2D6",
    "rs1799853":"CYP2C9","rs1057910":"CYP2C9","rs28371686":"CYP2C9","rs9332131":"CYP2C9",
    "rs9923231":"VKORC1","rs9934438":"VKORC1","rs2359612":"VKORC1","rs8050894":"VKORC1",
    "rs3918290":"DPYD","rs55886062":"DPYD","rs67376798":"DPYD","rs75017182":"DPYD",
    "rs1800462":"TPMT","rs1800460":"TPMT","rs1142345":"TPMT","rs1800584":"TPMT",
    "rs4149056":"SLCO1B1","rs2306283":"SLCO1B1","rs11045819":"SLCO1B1",
    "rs8175347":"UGT1A1","rs4148323":"UGT1A1",
    "rs776746":"CYP3A5","rs10264272":"CYP3A5","rs41303343":"CYP3A5",
    "rs1050828":"G6PD","rs1050829":"G6PD",
    "rs116855232":"NUDT15","rs186364861":"NUDT15",
}

def _open_vcf(vcf_file):
    if vcf_file.endswith(".gz"):
        return gzip.open(vcf_file, "rt", encoding="utf-8", errors="replace")
    return open(vcf_file, "r", encoding="utf-8", errors="replace")

def _detect_gene(info, rsid):
    for field in info.split(";"):
        if field.startswith("PX="):
            g = field.replace("PX=","").strip()
            if g: return g
        elif field.startswith("GENE="):
            g = field.replace("GENE=","").strip()
            if g: return g
        elif field.startswith("ANN="):
            parts = field.replace("ANN=","").split("|")
            if len(parts) > 3 and parts[3].strip():
                return parts[3].strip()
        elif field.startswith("CSQ="):
            parts = field.replace("CSQ=","").split("|")
            if len(parts) > 3 and parts[3].strip():
                return parts[3].strip()
    if rsid and rsid != "." and rsid in RSID_TO_GENE:
        return RSID_TO_GENE[rsid]
    return None

def _parse_genotype(gt_field):
    if not gt_field: return None
    gt = gt_field.split(":")[0].replace("|","/")
    if gt in ("./.",".","0/0"): return None
    if gt == "1/0": gt = "0/1"
    return gt

def parse_vcf(vcf_file):
    if not os.path.exists(vcf_file):
        raise FileNotFoundError(f"Fichier VCF introuvable : {vcf_file}")
    variants = []
    source = "Standard VCF"
    sample_col = 9
    total = ref_only = no_gene = 0
    with _open_vcf(vcf_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("##"):
                if "PharmCAT" in line or "pharmcat" in line.lower(): source = "PharmCAT"
                elif "SnpEff" in line or "snpeff" in line.lower(): source = "snpEff"
                elif "GATK" in line: source = "GATK"
                elif "VEP" in line: source = "VEP"
                continue
            if line.startswith("#CHROM"):
                continue
            cols = line.split("\t")
            if len(cols) < 8: continue
            total += 1
            chrom,pos,rsid,ref,alt,_,_,info = cols[:8]
            rsid = rsid if rsid != "." else f"chr{chrom}:{pos}"
            gt = _parse_genotype(cols[sample_col]) if len(cols) > sample_col else "1/1"
            if gt is None:
                ref_only += 1
                continue
            gene = _detect_gene(info, rsid)
            if gene is None:
                no_gene += 1
                continue
            gene = gene.split(",")[0].strip()
            variants.append({"chromosome":chrom,"position":pos,"rsid":rsid,
                             "gene":gene,"ref":ref,"alt":alt,"genotype":gt})
    print(f"[VCF Parser] Format detecte   : {source}")
    print(f"[VCF Parser] Variants lus     : {total}")
    print(f"[VCF Parser] Mutations        : {len(variants)}")
    if no_gene:  print(f"[VCF Parser] Sans gene        : {no_gene} (ignores)")
    if ref_only: print(f"[VCF Parser] Reference seule  : {ref_only} (ignores)")
    if not variants:
        return pd.DataFrame(columns=["chromosome","position","rsid","gene","ref","alt","genotype"])
    return pd.DataFrame(variants)

def main():
    import sys
    vcf = sys.argv[1] if len(sys.argv)>1 else "/home/mouna/projet_memoire/data/pharmacat.example2.vcf"
    print(f"Lecture : {vcf}")
    df = parse_vcf(vcf)
    if df.empty:
        print("Aucun variant pharmacogenomique detecte.")
    else:
        print(f"\nVariants detectes ({len(df)}) :")
        print(df.to_string(index=False))
        df.to_csv("/home/mouna/projet_memoire/results/variants_extraits.csv", index=False)

if __name__ == "__main__":
    main()

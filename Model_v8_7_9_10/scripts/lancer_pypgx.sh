#!/bin/bash
# Même commande que l'application (appeler_gene dans vcf_to_profile_v8.py) mais sur le VCF multi-échantillons, sans --samples.
cd /tmp/claude-0/-home-claude/8409b04b-17f7-52aa-bb79-1c3b814505b7/scratchpad/getrm
V=/tmp/claude-0/-home-claude/8409b04b-17f7-52aa-bb79-1c3b814505b7/scratchpad/p1/venv_pgx/bin/python
export PYPGX_BUNDLE=/tmp/claude-0/-home-claude/8409b04b-17f7-52aa-bb79-1c3b814505b7/scratchpad/p1/pypgx-bundle
mkdir -p pypgx104
for g in CYP2C19 CYP2C9 CYP2B6 CYP3A5 CYP3A4 CYP4F2 DPYD NAT2 NUDT15 SLCO1B1 TPMT UGT1A1 VKORC1; do
  s=$(date +%s); $V -m pypgx run-chip-pipeline $g pypgx104/pgx_$g multi104.vcf.gz --assembly GRCh38 --force > pypgx104/log_$g.txt 2>&1; echo "$g rc=$? $(( $(date +%s)-s )) s"
done
echo FIN_PYPGX

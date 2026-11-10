# Génotypes des 11 patients, recopiés du Tableau S3 (mmc1.pdf, PMC12639823). Nomenclature de l'article convertie : *1A->*1, *1B->*37 (hypothèse à confirmer).
# Valeur None = non fourni par l'article ; ('ext', v) = valeur saisie à la main comme le permet l'application (CYP2D6, HLA).
PAT = {
 1:dict(CYP3A5='*3/*3',CYP2C19='*1/*2',CYP2D6=('ext',0.5),SLCO1B1='*1/*1',VKORC1='AA',CYP2C9='*1/*1'),
 2:dict(CYP3A5='*3/*3',CYP2B6='*1/*6',CYP2C9='*1/*2',CYP2C19='*1/*2',CYP4F2='*3/*3',SLCO1B1='*1/*37',VKORC1='GA'),
 3:dict(CYP2B6='*1/*6',CYP3A5='*3/*3',SLCO1B1='*5/*5',VKORC1='GA'),
 4:dict(CYP2D6=('ext',0.5),CYP3A5='*3/*3',CYP4F2='*1/*3',SLCO1B1='*1/*37',UGT1A1='*1/*28'),
 5:dict(HLAB58=('ext','non_porteur'),CYP2C19='*1/*2',CYP3A5='*3/*3',CYP4F2='*1/*3',SLCO1B1='*37/*37',UGT1A1='*1/*28',VKORC1='GA'),
 6:dict(CYP2B6='*1/*1',CYP2C19='*1/*17',CYP3A5='*3/*3',CYP4F2='*3/*3',SLCO1B1='*1/*37',UGT1A1='*1/*28',VKORC1='GG'),
 7:dict(CYP2B6='*1/*6',CYP2C19='*1/*2',CYP3A5='*1/*3',CYP4F2='*1/*3',SLCO1B1='*1/*21',VKORC1='GA'),
 8:dict(CYP2C19='*1/*17',CYP3A5='*3/*3',SLCO1B1='*1/*15',UGT1A1='*28/*28',VKORC1='GA'),
 9:dict(CYP3A5='*3/*3',SLCO1B1='*37/*37',UGT1A1='*1/*28',VKORC1='GA'),
 10:dict(CYP2B6='*1/*6',CYP2C19='*2/*17',HLAA3101=('ext','porteur'),SLCO1B1='*1/*37',VKORC1='GA'),
 11:dict(CYP2C19='*17/*17',CYP2D6=('ext',0.5),CYP3A5='*3/*3',SLCO1B1='*1/*5',UGT1A1='*28/*28',VKORC1='GA'),
}
ART_PHEN = { # phénotype écrit dans l'article (pour contrôle génotype -> phénotype)
 1:dict(CYP3A5='Poor Metabolizer',CYP2C19='Intermediate Metabolizer',SLCO1B1='Normal function',CYP2C9='Normal Metabolizer'),
 2:dict(CYP3A5='Poor Metabolizer',CYP2B6='Intermediate Metabolizer',CYP2C9='Intermediate Metabolizer',CYP2C19='Intermediate Metabolizer',SLCO1B1='Normal function'),
 3:dict(CYP2B6='Intermediate Metabolizer',CYP3A5='Poor Metabolizer',SLCO1B1='Poor Function'),
 4:dict(CYP3A5='Poor Metabolizer',SLCO1B1='Normal function',UGT1A1='Increased risk'),
 5:dict(CYP2C19='Intermediate Metabolizer',CYP3A5='Poor Metabolizer',SLCO1B1='Normal function',UGT1A1='Increased risk'),
 6:dict(CYP2B6='Normal Metabolizer',CYP2C19='Rapid Metabolizer',CYP3A5='Poor Metabolizer',SLCO1B1='Normal function',UGT1A1='Increased risk'),
 7:dict(CYP2B6='Intermediate Metabolizer',CYP2C19='Intermediate Metabolizer',CYP3A5='Intermediate Metabolizer',SLCO1B1='Reduced Function'),
 8:dict(CYP2C19='Rapid metabolizer',CYP3A5='Poor Metabolizer',SLCO1B1='Reduced Function',UGT1A1='High risk'),
 9:dict(CYP3A5='Poor Metabolizer',SLCO1B1='Normal function',UGT1A1='Increased risk'),
 10:dict(CYP2B6='Intermediate Metabolizer',CYP2C19='Intermediate Metabolizer',SLCO1B1='Normal function'),
 11:dict(CYP2C19='Ultrarapid metabolizer',CYP3A5='Poor Metabolizer',SLCO1B1='Decreased function',UGT1A1='High risk'),
}

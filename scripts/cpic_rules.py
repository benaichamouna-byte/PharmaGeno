# cpic_rules.py
# Règles CPIC officielles pour CYP2C19
# Source : https://cpicpgx.org/guidelines/

CPIC_RULES = {
    'CYP2C19': {
        'Poor Metabolizer': {
            'clopidogrel': {
                'recommendation': 'Éviter — inefficace pour ce patient',
                'alternative': 'Prasugrel ou ticagrelor recommandés',
                'level': 'A',
                'reference': 'CPIC guideline for clopidogrel and CYP2C19 (Scott et al., 2013)'
            },
            'omeprazole': {
                'recommendation': 'Dose standard — métabolisme réduit mais effet augmenté',
                'alternative': None,
                'level': 'B',
                'reference': 'CPIC guideline for PPIs and CYP2C19 (Lima et al., 2021)'
            },
            'voriconazole': {
                'recommendation': 'Réduire la dose — risque de toxicité',
                'alternative': None,
                'level': 'A',
                'reference': 'CPIC guideline for voriconazole and CYP2C19 (Moriyama et al., 2017)'
            },
            'citalopram': {
                'recommendation': 'Réduire la dose de 50%',
                'alternative': None,
                'level': 'A',
                'reference': 'CPIC guideline for SSRIs and CYP2C19 (Hicks et al., 2015)'
            },
            'sertraline': {
                'recommendation': 'Considérer une alternative',
                'alternative': None,
                'level': 'B',
                'reference': 'CPIC guideline for SSRIs and CYP2C19 (Hicks et al., 2015)'
            }
        },
        'Intermediate Metabolizer': {
            'clopidogrel': {
                'recommendation': 'Considérer une alternative antiplaquettaire',
                'alternative': 'Prasugrel ou ticagrelor à considérer',
                'level': 'A',
                'reference': 'CPIC guideline for clopidogrel and CYP2C19 (Scott et al., 2013)'
            },
            'omeprazole': {
                'recommendation': 'Dose standard',
                'alternative': None,
                'level': 'B',
                'reference': 'CPIC guideline for PPIs and CYP2C19 (Lima et al., 2021)'
            },
            'voriconazole': {
                'recommendation': 'Dose standard avec surveillance',
                'alternative': None,
                'level': 'B',
                'reference': 'CPIC guideline for voriconazole and CYP2C19 (Moriyama et al., 2017)'
            },
            'citalopram': {
                'recommendation': 'Dose standard',
                'alternative': None,
                'level': 'B',
                'reference': 'CPIC guideline for SSRIs and CYP2C19 (Hicks et al., 2015)'
            },
            'sertraline': {
                'recommendation': 'Dose standard',
                'alternative': None,
                'level': 'B',
                'reference': 'CPIC guideline for SSRIs and CYP2C19 (Hicks et al., 2015)'
            }
        },
        'Normal Metabolizer': {
            'clopidogrel': {
                'recommendation': 'Dose standard recommandée',
                'alternative': None,
                'level': 'A',
                'reference': 'CPIC guideline for clopidogrel and CYP2C19 (Scott et al., 2013)'
            },
            'omeprazole': {
                'recommendation': 'Dose standard',
                'alternative': None,
                'level': 'A',
                'reference': 'CPIC guideline for PPIs and CYP2C19 (Lima et al., 2021)'
            },
            'voriconazole': {
                'recommendation': 'Dose standard',
                'alternative': None,
                'level': 'A',
                'reference': 'CPIC guideline for voriconazole and CYP2C19 (Moriyama et al., 2017)'
            },
            'citalopram': {
                'recommendation': 'Dose standard',
                'alternative': None,
                'level': 'A',
                'reference': 'CPIC guideline for SSRIs and CYP2C19 (Hicks et al., 2015)'
            },
            'sertraline': {
                'recommendation': 'Dose standard',
                'alternative': None,
                'level': 'A',
                'reference': 'CPIC guideline for SSRIs and CYP2C19 (Hicks et al., 2015)'
            }
        },
        'Ultrarapid Metabolizer': {
            'clopidogrel': {
                'recommendation': 'Dose standard ou réduire',
                'alternative': None,
                'level': 'B',
                'reference': 'CPIC guideline for clopidogrel and CYP2C19 (Scott et al., 2013)'
            },
            'omeprazole': {
                'recommendation': 'Augmenter la dose — métabolisme accéléré',
                'alternative': None,
                'level': 'B',
                'reference': 'CPIC guideline for PPIs and CYP2C19 (Lima et al., 2021)'
            },
            'voriconazole': {
                'recommendation': 'Éviter — efficacité réduite',
                'alternative': 'Considérer autre antifongique',
                'level': 'A',
                'reference': 'CPIC guideline for voriconazole and CYP2C19 (Moriyama et al., 2017)'
            },
            'citalopram': {
                'recommendation': 'Dose standard',
                'alternative': None,
                'level': 'B',
                'reference': 'CPIC guideline for SSRIs and CYP2C19 (Hicks et al., 2015)'
            },
            'sertraline': {
                'recommendation': 'Dose standard',
                'alternative': None,
                'level': 'B',
                'reference': 'CPIC guideline for SSRIs and CYP2C19 (Hicks et al., 2015)'
            }
        }
    }
}

# Mapping phénotype ML → phénotype CPIC
PHENOTYPE_MAP = {
    'Efficacy':    'Poor Metabolizer',
    'Dosage':      'Intermediate Metabolizer',
    'Metabolism':  'Normal Metabolizer',
    'Toxicity':    'Poor Metabolizer'
}

def get_recommendations(gene, ml_phenotype):
    cpic_phenotype = PHENOTYPE_MAP.get(ml_phenotype, 'Normal Metabolizer')
    if gene not in CPIC_RULES:
        return cpic_phenotype, []
    drugs = CPIC_RULES[gene].get(cpic_phenotype, {})
    results = []
    for drug, info in drugs.items():
        results.append({
            'drug':           drug,
            'recommendation': info['recommendation'],
            'alternative':    info['alternative'],
            'level':          info['level'],
            'reference':      info['reference'],
            'phenotype':      cpic_phenotype
        })
    # Trier par niveau A puis B
    results.sort(key=lambda x: x['level'])
    return cpic_phenotype, results

if __name__ == '__main__':
    phenotype, recs = get_recommendations('CYP2C19', 'Efficacy')
    print(f"Phénotype CPIC : {phenotype}")
    for r in recs:
        print(f"{r['drug']} → {r['recommendation']} (Niveau {r['level']})")

# Ajout CYP2B6
CPIC_RULES['CYP2B6'] = {
    'Poor Metabolizer': {
        'efavirenz': {
            'recommendation': 'Réduire la dose de 50% — risque de toxicité élevé',
            'alternative': 'Envisager névirapine ou rilpivirine',
            'level': 'A',
            'reference': 'CPIC guideline for efavirenz and CYP2B6 (Desta et al., 2019)'
        },
        'methadone': {
            'recommendation': 'Réduire la dose — accumulation possible',
            'alternative': None,
            'level': 'B',
            'reference': 'CPIC guideline for methadone and CYP2B6 (Crews et al., 2021)'
        },
        'bupropion': {
            'recommendation': 'Dose standard avec surveillance accrue',
            'alternative': None,
            'level': 'B',
            'reference': 'CPIC guideline for bupropion and CYP2B6 (Crews et al., 2021)'
        }
    },
    'Intermediate Metabolizer': {
        'efavirenz': {
            'recommendation': 'Dose standard avec surveillance des effets indésirables',
            'alternative': None,
            'level': 'A',
            'reference': 'CPIC guideline for efavirenz and CYP2B6 (Desta et al., 2019)'
        },
        'methadone': {
            'recommendation': 'Dose standard',
            'alternative': None,
            'level': 'B',
            'reference': 'CPIC guideline for methadone and CYP2B6 (Crews et al., 2021)'
        },
        'bupropion': {
            'recommendation': 'Dose standard',
            'alternative': None,
            'level': 'B',
            'reference': 'CPIC guideline for bupropion and CYP2B6 (Crews et al., 2021)'
        }
    },
    'Normal Metabolizer': {
        'efavirenz': {
            'recommendation': 'Dose standard recommandée',
            'alternative': None,
            'level': 'A',
            'reference': 'CPIC guideline for efavirenz and CYP2B6 (Desta et al., 2019)'
        },
        'methadone': {
            'recommendation': 'Dose standard',
            'alternative': None,
            'level': 'B',
            'reference': 'CPIC guideline for methadone and CYP2B6 (Crews et al., 2021)'
        },
        'bupropion': {
            'recommendation': 'Dose standard',
            'alternative': None,
            'level': 'B',
            'reference': 'CPIC guideline for bupropion and CYP2B6 (Crews et al., 2021)'
        }
    },
    'Ultrarapid Metabolizer': {
        'efavirenz': {
            'recommendation': 'Augmenter la dose — efficacité réduite possible',
            'alternative': None,
            'level': 'B',
            'reference': 'CPIC guideline for efavirenz and CYP2B6 (Desta et al., 2019)'
        },
        'methadone': {
            'recommendation': 'Augmenter la dose — métabolisme accéléré',
            'alternative': None,
            'level': 'B',
            'reference': 'CPIC guideline for methadone and CYP2B6 (Crews et al., 2021)'
        },
        'bupropion': {
            'recommendation': 'Dose standard',
            'alternative': None,
            'level': 'B',
            'reference': 'CPIC guideline for bupropion and CYP2B6 (Crews et al., 2021)'
        }
    }
}

def get_all_covered_drugs():
    """Retourne tous les médicaments couverts avec leur niveau de preuve maximum."""
    drugs = {}
    for gene, phenotypes in CPIC_RULES.items():
        for phenotype, meds in phenotypes.items():
            for drug, info in meds.items():
                if drug not in drugs:
                    drugs[drug] = {'level': info['level'], 'genes': [gene]}
                else:
                    if gene not in drugs[drug]['genes']:
                        drugs[drug]['genes'].append(gene)
                    if info['level'] == 'A':
                        drugs[drug]['level'] = 'A'
    return drugs

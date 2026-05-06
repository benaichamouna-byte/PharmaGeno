import pandas as pd

df = pd.read_csv('/home/mouna/projet_memoire/results/recommandations.csv')

# Supprimer les doublons
df_clean = df.drop_duplicates(subset=['gene', 'rsid', 'drug', 'phenotype'])

# Trier par gène
df_clean = df_clean.sort_values(['gene', 'drug'])

print(f"Avant nettoyage : {len(df)} lignes")
print(f"Après nettoyage : {len(df_clean)} lignes")
print("\nRésultats propres :")
print(df_clean.to_string(index=False))

df_clean.to_csv(
    '/home/mouna/projet_memoire/results/recommandations_clean.csv',
    index=False
)
print("\nSauvegardé dans recommandations_clean.csv")

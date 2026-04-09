import pandas as pd

df = pd.read_excel('data/all.xlsx', usecols=['cntyname', 'quarter', 'year', 'covg4313314','rank4313314'])
filtered_df = df.query("quarter == 'Q4' and year == 2025")

popn = pd.read_excel('data/popn_data.xlsx', usecols=['cntyname','pop19_35'])

merged = filtered_df.merge(popn, on='cntyname', how='inner')

merged = merged[merged['cntyname'] != 'Michigan']

merged.to_csv('data/filtered_output.csv', index=False)



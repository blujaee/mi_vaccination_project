import pandas as pd

df = pd.read_excel('data/all.xlsx', usecols=['cntyname','quarter','year','covg4313314','rank4313314'])

filtered_df = df[(df['quarter']=='Q4') & (df['year'] == '2025')]

filtered_df = df.query("quarter == 'Q4' and year == 2025")

filtered_df.to_csv('data/filtered_output.csv', index=False)

df['covg4313314'].describe()
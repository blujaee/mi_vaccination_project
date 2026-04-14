import pandas as pd

df = pd.read_csv('data/filtered_output.csv')
df['covg4313314'] = pd.to_numeric(df['covg4313314'], errors='coerce')
df['pop19_35'] = pd.to_numeric(df['pop19_35'], errors='coerce')
df['unvacc'] = (df['pop19_35'] * (100 - df['covg4313314']) / 100).round(0)

total_unvacc = int(df['unvacc'].sum())
print(f"Total unvaccinated (19-35 months): {total_unvacc}")

popn = pd.read_excel('data/popn_data.xlsx')
popn = popn[popn['cntyname'] != 'Michigan']
popn['pop19_35'] = pd.to_numeric(popn['pop19_35'], errors='coerce')
popn['covg4313314'] = pd.to_numeric(popn['covg4313314'], errors='coerce')
popn['unvacc'] = (popn['pop19_35'] * (100 - popn['covg4313314']) / 100).round(0)
print(f"Total population (19-35 months):   {int(popn['pop19_35'].sum())}")
print(f"Total unvaccinated (popn_data):    {int(popn['unvacc'].sum())}")

print(df['covg4313314'].describe())
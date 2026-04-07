import pandas as pd

df = pd.read_csv('data/filtered_output.csv')


print(df['covg4313314'].describe())
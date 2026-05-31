import pandas as pd

df = pd.read_csv("data/historical/master_prices.csv")

print(df.isna().sum())
print(df.head())
print(df.columns)
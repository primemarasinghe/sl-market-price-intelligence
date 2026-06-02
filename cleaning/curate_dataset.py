import pandas as pd

INPUT_FILE = "data/historical/master_prices.csv"
OUTPUT_FILE = "data/warehouse/curated_prices.csv"

SELECTED_COMMODITIES = [
    "Beans",
    "Carrot",
    "Cabbage",
    "Tomato",
    "Brinjal",
    "Pumpkin",
    "Snake gourd",
    "Green Chilli",
    "Lime",
    "Red Onion (Local)",
    "Red Onion (Imp)",
    "Big Onion (Local)",
    "Big Onion (Imp)",
    "Potato (Local)",
    "Potato (Imp)",
    "Dried Chilli (Imp)",
    "Coconut (Avg.)",
    "Coconut oil",
    "Red Dhal",
    "Sugar (White)",
    "Egg (White)",
    "Katta (Imp)",
    "Sprat (Imp)",
    "Banana (Sour)",
    "Papaw",
    "Pineapple",
    "Apple (Imp)",
    "Orange (Imp)"
]

df = pd.read_csv(INPUT_FILE)

# Keep only selected commodities
df = df[df["commodity"].isin(SELECTED_COMMODITIES)]

# Drop rows that do not have a valid report date.
df = df.dropna(subset=["report_date"])

# Convert n.a. to NaN
df.replace("n.a.", pd.NA, inplace=True)

# Remove rows with missing current price
df = df.dropna(subset=["retail_pettah_today"])

# Sort
df = df.sort_values(
    ["commodity", "report_date"]
)

# Save
df.to_csv(OUTPUT_FILE, index=False)

print("Curated Dataset Created")
print("Rows:", len(df))
print("Commodities:", df["commodity"].nunique())
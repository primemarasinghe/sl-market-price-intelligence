import pandas as pd
import os

INPUT_FILE = "data/warehouse/curated_prices.csv"

OUTPUT_FOLDER = "data/star_schema"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

# ----------------------------------
# FACT TABLE CREATION
# ----------------------------------

price_columns = {
    "wholesale_pettah_today": ("Pettah", "Wholesale"),
    "wholesale_dambulla_today": ("Dambulla", "Wholesale"),

    "retail_pettah_today": ("Pettah", "Retail"),
    "retail_dambulla_today": ("Dambulla", "Retail"),
    "retail_narahenpita_today": ("Narahenpita", "Retail")
}

fact_rows = []

for _, row in df.iterrows():

    for column, (market, price_type) in price_columns.items():

        value = row[column]

        if pd.isna(value):
            continue

        fact_rows.append({
            "report_date": row["report_date"],
            "commodity": row["commodity"],
            "market": market,
            "price_type": price_type,
            "price": float(value)
        })

fact_df = pd.DataFrame(fact_rows)

print("Fact rows:", len(fact_df))

fact_df.to_csv(
    f"{OUTPUT_FOLDER}/fact_price.csv",
    index=False
)
commodity_dim = (
    fact_df[["commodity"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

commodity_dim["CommodityKey"] = (
    commodity_dim.index + 1
)

commodity_dim = commodity_dim[
    ["CommodityKey", "commodity"]
]

commodity_dim.to_csv(
    f"{OUTPUT_FOLDER}/dim_commodity.csv",
    index=False
)
market_dim = (
    fact_df[["market"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

market_dim["MarketKey"] = (
    market_dim.index + 1
)

market_dim = market_dim[
    ["MarketKey", "market"]
]

market_dim.to_csv(
    f"{OUTPUT_FOLDER}/dim_market.csv",
    index=False
)
price_dim = (
    fact_df[["price_type"]]
    .drop_duplicates()
    .reset_index(drop=True)
)

price_dim["PriceTypeKey"] = (
    price_dim.index + 1
)

price_dim = price_dim[
    ["PriceTypeKey", "price_type"]
]

price_dim.to_csv(
    f"{OUTPUT_FOLDER}/dim_pricetype.csv",
    index=False
)
date_dim = pd.DataFrame({
    "Date": pd.to_datetime(
        fact_df["report_date"]
    ).drop_duplicates()
})

date_dim = date_dim.sort_values("Date")

date_dim["DateKey"] = (
    date_dim["Date"]
    .dt.strftime("%Y%m%d")
)

date_dim["Year"] = date_dim["Date"].dt.year
date_dim["Month"] = date_dim["Date"].dt.month
date_dim["MonthName"] = date_dim["Date"].dt.month_name()
date_dim["Quarter"] = date_dim["Date"].dt.quarter

date_dim.to_csv(
    f"{OUTPUT_FOLDER}/dim_date.csv",
    index=False
)
fact_final = fact_df.copy()

# DateKey
fact_final["DateKey"] = pd.to_datetime(
    fact_final["report_date"]
).dt.strftime("%Y%m%d")

# CommodityKey
fact_final = fact_final.merge(
    commodity_dim,
    on="commodity",
    how="left"
)

# MarketKey
fact_final = fact_final.merge(
    market_dim,
    on="market",
    how="left"
)

# PriceTypeKey
fact_final = fact_final.merge(
    price_dim,
    on="price_type",
    how="left"
)

fact_final = fact_final[
    [
        "DateKey",
        "CommodityKey",
        "MarketKey",
        "PriceTypeKey",
        "price"
    ]
]

fact_final.to_csv(
    f"{OUTPUT_FOLDER}/fact_price_final.csv",
    index=False
)

print("Warehouse Fact Created")
print(len(fact_final))

print("fact_price.csv created")
print("dim_commodity.csv created")
print("dim_market.csv created")
print("dim_pricetype.csv created")
print("dim_date.csv created")
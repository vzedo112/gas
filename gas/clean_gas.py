import pandas as pd
import os
import re
import calendar

input_file = os.path.join(os.path.dirname(__file__), "Gas Investigation.csv")
output_file = os.path.join(os.path.dirname(__file__), "gas.csv")

df = pd.read_csv(input_file, header=None, dtype=str)

cleaned_rows = []

for idx, row in df.iterrows():
    for i, year in enumerate([2023, 2024, 2025]):
        base = i * 4 
        date_str = row[base]
        hdd = row[base + 1]
        gas = row[base + 2]

        if isinstance(date_str, str) and re.match(r"\d{2}/\d{2}/\d{4}", date_str):
            try:
                date = pd.to_datetime(date_str, dayfirst=True)
                cleaned_rows.append({
                    "Year": year,
                    "Month": calendar.month_abbr[date.month],
                    "Date": date.strftime("%d/%m/%Y"),
                    "Hdd": float(hdd) if pd.notna(hdd) else None,
                    "Gas (kWh)": float(str(gas).replace(",", "")) if pd.notna(gas) and gas not in ["", "nan"] else None
                })
            except Exception:
                continue

cleaned_df = pd.DataFrame(cleaned_rows, columns=["Year", "Month", "Date", "Hdd", "Gas (kWh)"])


cleaned_df.to_csv(output_file, index=False)

print(f"Cleaned data saved to {output_file}")
# GDP vs 16 Economies

This repository contains a small analysis script that downloads Maddison/Our World in Data GDP-per-capita data and computes Portugal's GDP per capita as a percentage of the mean GDP per capita for 16 developed economies.

The repository includes:
- gdp_cal.py — script to download the data, compute the comparison, save a CSV and a PNG plot.
- requirements.txt — Python packages required to run the script.

## What the script does

1. Downloads the GDP-per-capita CSV from Our World in Data (Maddison Project).
2. Detects the relevant columns (year, country/entity, ISO code, GDP per capita) even if column headers vary slightly.
3. Filters data to a specified year range (default 1870–2022).
4. Pivots to wide format (years as rows, country ISO codes as columns).
5. Computes the mean GDP per capita across a list of 16 developed economies (default list included in the script).
   - Years with fewer than 12 of these 16 countries present are excluded from the mean to avoid spurious comparisons.
6. Computes Portugal's GDP per capita divided by that mean and expresses it as a percentage.
7. Writes the results to CSV and creates a PNG time-series plot.

## Quickstart

Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
python -m pip install -r requirements.txt
```

Run the script with defaults:

```bash
python gdp_cal.py
```

Customizing (example):

```bash
python gdp_cal.py --start-year 1900 --end-year 2020 --out-csv results/portugal_vs_16.csv --out-png results/portugal_pct.png
```

Outputs:
- portugal_vs_16_developed.csv (by default) — CSV with columns: year, Portugal_gdp_pc, Media_16_gdp_pc, Portugal_pct_da_media_16
- grafico_portugal_pct_media16.png (by default) — time-series plot showing Portugal as % of the 16-economy mean

## Required data sources

- Our World in Data (Maddison Project dataset): https://ourworldindata.org/grapher/gdp-per-capita-maddison-project-database.csv

## Requirements

See requirements.txt. The main packages used are:
- pandas
- requests
- matplotlib

## Notes

- If the source CSV changes structure significantly, column detection may fail; the script prints the available columns to help debugging.
- If you need the script to use a different set of countries or a different threshold for minimum countries to compute the mean, edit the DEVELOPED_16 list and the threshold logic in the script.

## License & Contact

Repository owner: @DiogoTofuMartins

Add a LICENSE file if you want to specify the repository license.

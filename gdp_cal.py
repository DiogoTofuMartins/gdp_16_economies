#!/usr/bin/env python3
"""
gdp_cal.py

Download Maddison/Our World in Data GDP-per-capita data, compute Portugal's GDP per capita
as a percentage of the mean of 16 developed economies, save CSV output and a plot.

Usage:
    python gdp_cal.py
    python gdp_cal.py --start-year 1900 --end-year 2020 --out-csv portugal_vs_16.csv --out-png portugal_pct.png
"""
import io
import argparse
from pathlib import Path
import sys

import requests
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = (11, 6)

# Default constants
OWID_URL = "https://ourworldindata.org/grapher/gdp-per-capita-maddison-project-database.csv"
DEVELOPED_16 = ["GBR", "FRA", "DEU", "DNK", "BEL", "NLD", "ESP", "ITA", "PRT", "SWE", "AUT", "USA", "CAN", "AUS", "NZL", "JPN"]
PORTUGAL = "PRT"

def download_csv(url: str, timeout: int = 60) -> pd.DataFrame:
    """Download CSV from URL and return a DataFrame."""
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))

def detect_columns(df: pd.DataFrame):
    """Return detected (year_col, country_col, code_col, value_col)."""
    cols = [c.lower().strip() for c in df.columns]
    # Find the first match by keywords; raise helpful error if missing
    year_col = next((c for c in df.columns if 'year' in c.lower()), None)
    country_col = next((c for c in df.columns if ('entity' in c.lower() or 'country' in c.lower())), None)
    code_col = next((c for c in df.columns if 'code' in c.lower()), None)
    value_col = next((c for c in df.columns if 'gdp' in c.lower()), None)

    if not all([year_col, country_col, code_col, value_col]):
        missing = [name for name, val in (('year', year_col), ('country/entity', country_col),
                                         ('code', code_col), ('gdp', value_col)) if val is None]
        raise ValueError(f"Could not auto-detect columns: {missing}. Available columns: {df.columns.tolist()}")

    return year_col, country_col, code_col, value_col

def prepare_wide(df: pd.DataFrame, year_col: str, country_col: str, code_col: str, value_col: str,
                 start_year: int, end_year: int) -> pd.DataFrame:
    """Normalize column names, filter by year range, and pivot to wide format."""
    df = df.rename(columns={year_col: 'year', country_col: 'entity', code_col: 'code', value_col: 'gdp_per_capita'})
    df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
    wide = df.pivot_table(index="year", columns="code", values="gdp_per_capita", aggfunc="first")
    return wide

def compute_portugal_vs_mean(wide: pd.DataFrame, developed_16: list, portugal_code: str):
    """Compute Portugal series, mean of developed_16, and percent ratio."""
    missing = [c for c in developed_16 + [portugal_code] if c not in wide.columns]
    if missing:
        print("Aviso: faltam dados para:", missing, file=sys.stderr)

    avg16 = wide[[c for c in developed_16 if c in wide.columns]].copy()
    avg16["count_non_na"] = avg16.count(axis=1)
    avg16_mean = avg16[[c for c in developed_16 if c in avg16.columns]].mean(axis=1)

    # Mask years with insufficient observed countries (less than 12 present)
    avg16_mean[avg16["count_non_na"] < 12] = pd.NA

    prt = wide[portugal_code] if portugal_code in wide.columns else pd.Series(index=wide.index, dtype=float)
    ratio = (prt / avg16_mean) * 100

    out = pd.DataFrame({
        "year": ratio.index,
        "Portugal_gdp_pc": prt.values,
        "Media_16_gdp_pc": avg16_mean.values,
        "Portugal_pct_da_media_16": ratio.values
    })
    return out

def plot_ratio(out: pd.DataFrame, out_png: Path):
    """Plot Portugal % of average and save to PNG."""
    fig, ax = plt.subplots()
    ax.plot(out["year"], out["Portugal_pct_da_media_16"], linewidth=2, color="darkred")
    ax.set_title("PIB per capita de Portugal (% da média de 16 economias desenvolvidas)\nMaddison Project 2023 (PPA 2011$)")
    ax.set_xlabel("Ano")
    ax.set_ylabel("% da média")
    # highlight WWI and WWII (same as original)
    ax.axvspan(1914, 1918, alpha=0.2, color='grey')
    ax.axvspan(1939, 1945, alpha=0.2, color='grey')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=180)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Compute Portugal GDP per capita as % of mean of 16 developed economies.")
    parser.add_argument("--source-url", default=OWID_URL, help="CSV source URL")
    parser.add_argument("--start-year", type=int, default=1870, help="Start year (inclusive)")
    parser.add_argument("--end-year", type=int, default=2022, help="End year (inclusive)")
    parser.add_argument("--out-csv", default="portugal_vs_16_developed.csv", help="Output CSV path")
    parser.add_argument("--out-png", default="grafico_portugal_pct_media16.png", help="Output PNG path")
    args = parser.parse_args()

    print("A descarregar dados...")
    df = download_csv(args.source_url)
    print("Colunas disponíveis:", df.columns.tolist())

    try:
        year_col, country_col, code_col, value_col = detect_columns(df)
    except ValueError as exc:
        print(f"Erro a detetar colunas: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Usando colunas: ano={year_col}, país={country_col}, código={code_col}, valor={value_col}")

    wide = prepare_wide(df, year_col, country_col, code_col, value_col, args.start_year, args.end_year)
    out = compute_portugal_vs_mean(wide, DEVELOPED_16, PORTUGAL)
    out.to_csv(args.out_csv, index=False)
    print(f"CSV guardado em: {args.out_csv}")

    try:
        plot_ratio(out, Path(args.out_png))
        print(f"PNG guardado em: {args.out_png}")
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
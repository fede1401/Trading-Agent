from pathlib import Path

# Trova il percorso assoluto dello script corrente (config.py)
project_root = Path(__file__).resolve()

# Risali finché non trovi 'Trading-Agent'
while project_root.name != 'Trading-Agent':
    if project_root == project_root.parent:  # Se arrivi alla root del file system
        raise RuntimeError("Errore: Impossibile trovare la cartella Trading-Agent!")
    project_root = project_root.parent  # Risali di un livello

# Percorsi principali del progetto
db_path = project_root / "db"
symbols_path = project_root / "symbols"
market_data_path = project_root / "marketData"
work_historical_path = project_root / "workHistorical"
work_live_path = project_root / "workLive"

print(f"project_root: {project_root}\ndb_path: {db_path}")

# Lista dei file di mercato
marketFiles = [
    market_data_path / "csv_files/nasdaq_symbols_sorted.csv",
    market_data_path / "csv_files/nyse_symbols_sorted.csv",
    market_data_path / "csv_files/largest_companies_EU.csv"
]


import sys

def get_project_root() -> Path:
    return project_root

def get_path_specify(which):
    root = get_project_root()
    for w in which:
        sys.path.append(f"{root}/{w}")
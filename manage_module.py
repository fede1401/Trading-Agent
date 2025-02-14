from pathlib import Path

# Trova il percorso assoluto dello script corrente (config.py)
project_root = Path(__file__).resolve()

# Risali finché non trovi 'Trading-Agent'
while project_root.name != 'trading-agent':
    if project_root == project_root.parent:  # Se arrivi alla root del file system
        raise RuntimeError("Errore: Impossibile trovare la cartella Trading-Agent!")
    project_root = project_root.parent  # Risali di un livello

# Percorsi principali del progetto
# relativi al software 
main_project = project_root / "work_historical"
db_path = main_project / "database"
manage_symbols_path = main_project / "symbols"
utils_path = main_project / "utils"

# relativi ai dati
history_market_data_path = project_root / "data" / "dataset" / "historical_market_data"
capitalization_path = project_root / "data" / "dataset" / "capitalization"
symbols_info_path = project_root / "data" / "dataset" / "symbols_info"

# stampa dei percorsi
print(f"""project_root: {project_root}\n
            main_project: {main_project}\n
            db_path: {db_path}\n
            manage_symbols_path: {manage_symbols_path}\n
            utils_path: {utils_path}\n\n
            history_market_data_path: {history_market_data_path}\n
            capitalization_path: {capitalization_path}\n
            symbols_info_path: {symbols_info_path}\n
        """
    )

# Lista dei file di mercato
marketFiles = [
    symbols_info_path / "NASDAQ/nasdaq_symbols_sorted.csv",
    symbols_info_path / "NYSE/nyse_symbols_sorted.csv",
    symbols_info_path / "LARG_COMP_EU/largest_companies_EU.csv"
]


import sys

def get_project_root() -> Path:
    return project_root


# Aggiunge al path di sistema i moduli specificati: questo permette di importare i moduli in ogni file.
def get_path_specify(which):
    #root = get_project_root()
    for w in which:
        sys.path.append(f"{w}")
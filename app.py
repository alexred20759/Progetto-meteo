
# ============================================================
# PROGETTO METEO
# File: app.py
#
# Avvia la dashboard meteorologica realizzata con Streamlit.
# ============================================================

import subprocess
import sys
from pathlib import Path


# Individua la cartella in cui si trova questo file.
CARTELLA_PROGETTO = Path(__file__).resolve().parent

# Individua il file che contiene la dashboard Streamlit.
FILE_DASHBOARD = CARTELLA_PROGETTO / "dashboard.py"


# Avvia Streamlit utilizzando lo stesso interprete Python.
subprocess.run(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(FILE_DASHBOARD),
    ],
    check=False,
)

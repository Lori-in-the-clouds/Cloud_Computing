#!/bin/bash
# --- CONFIGURAZIONE AMBIENTE ---
NED="esame.ned"
INI_MAKO="esame.ini.mako"
INI_FILE="esame.ini"
JSON="esame.json"
DB_FILE="database.db"
RESULTS_DIR="results"
BONUS="bonus.py"
ANALISI="analisi_results.py"
ANALISI_PIU="analisi_piu_configurazioni.py"

read -p "Attenzione: questo script resetterà l'ambiente e cancellerà i dati precedenti. Vuoi procedere? (y/n): " conferma

if [[ ! $conferma =~ ^[yY] ]]; then
    echo "❌ Operazione annullata dall'utente."
    exit 1
fi

echo "=== 1. PULIZIA AMBIENTE (Tabula Rasa) ==="
rm $NED $INI_MAKO $INI_FILE $JSON 
rm -f $DB_FILE $INI_FILE Runfile
rm -rf $RESULTS_DIR/*.sca $RESULTS_DIR/*.vec $RESULTS_DIR/*.vci $RESULTS_DIR/*.data
mkdir -p $RESULTS_DIR
echo "✅Pulizia completata."
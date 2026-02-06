#!/bin/bash

# 1. Recupero dei parametri da riga di comando
STOP_STEP=$1
SCA_PATTERN=$2

# 2. Controllo se il primo parametro (lo step) è presente
if [ -z "$STOP_STEP" ]; then
echo "❌ Errore: Specifica lo step finale (0-4)."
echo "Uso: ./simulate.sh <step> [pattern_sca]_*.sca"
exit 1
fi

# 3. Controllo obbligatorietà del pattern per gli step 3 e 4
if [ "$STOP_STEP" -ge 3 ] && [ -z "$SCA_PATTERN" ]; then
echo "❌ Errore: Per gli step 3 e 4 devi passare il pattern .sca come secondo parametro."
echo "Esempio corretto: ./run_esame.sh $STOP_STEP mu1"
exit 1
fi

# --- STEP 0: Mako ---
echo "--- STEP 0: Compilazione Mako ---"
update_template.py 
if [ "$STOP_STEP" -le 0 ]; then exit 0; fi

# --- STEP 1: Runfile ---
echo "--- STEP 1: Generazione Runfile ---"
make_runfile.py -f esame.ini
if [ "$STOP_STEP" -le 1 ]; then exit 0; fi

# --- STEP 2: Simulazione ---
echo "--- STEP 2: Simulazione in corso (Multicore Mac) ---"
make -j $(sysctl -n hw.ncpu) -B -f Runfile
if [ "$STOP_STEP" -le 2 ]; then exit 0; fi

# --- STEP 3: Parsing ---
echo "--- STEP 3: Parsing con pattern: $SCA_PATTERN ---"
parse_data.py -c esame.json -d database.db -r results/${SCA_PATTERN}
if [ "$STOP_STEP" -le 3 ]; then exit 0; fi

# --- STEP 4: Analisi ---
echo "--- STEP 4: Analisi finale ---"
analyze_data.py -c esame.json -d database.db
echo "--- ✨ Workflow completato con successo! ---"

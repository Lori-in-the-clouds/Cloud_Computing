# OMNet++
## 0. Setup Ambiente
* **Script per avviare l’ambiente OMNeT++:**
    
    ```bash
    nano ~/.zshrc
    ```

    ```
    alias startomnet='cd ~/omnet-install/omnetpp-6.3.0 && source setenv && cd samples/queuenet'
    ```
    
    ```bash
    source ~/.zshrc
    ```
    
    Da questo momento, sarà sufficiente eseguire `startomnet` nel terminale per avere l’ambiente OMNeT++ correttamente configurato.
    
- **Script di esecuzione (run):**
    - Crea un file chiamato run con il seguente contenuto all’interno della directory `/samples/queuenet`:
        
        ```bash
        #!/bin/bash
        ./queuenet $*
        ```
        
    - Rendi lo script eseguibile:
        
        ```bash
        chmod +x run
        ```
        
- **Script di simulazione `simulate.sh`:** lo script centralizza l'intero workflow di simulazione, dalla configurazione iniziale all'analisi finale dei dati. Sintassi:
    ```bash
    ./simulate.sh <step> ["pattern_*.sca"]
    ```
    Dove:
    - **step 0** -> `update_template.py` 
    - **step 1** -> `make_runfile.py -f esame.ini`
    - **step 2** -> `make -j $(sysctl -n hw.ncpu) -B -f Runfile`
    - **step 3** -> `parse_data.py -c esame.json -d database.db -r results/pattern_*.sca`
    - **step 4** -> `analyze_data.py -c nomeconfig.json -d database.db`
    
    **$\color{red}{\text{N.B.}}$** Il `pattern_*.sca` è obbligatorio solo per la fase 3 e 4.

    ```python
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
    ```
---
## 1. Creazione file `.ned`
Questo file viene utilizzato per definire la struttura della rete. I componenti che possono essere utilizzati sono:
* [Source](components_omnet/source.md): corrisponde alla sorgente del traffico che poi verrà distribuito ai vari server.
* [Router](components_omnet/router.md): ha il compito di distribuire il traffico tra i vari server seguendo una particolare politica.
* [Queue](components_omnet/queue.md): viene posta prima del server e viene utilizzata per valutare il tempo in cui le task restano in attesa prima di essere processati.
* [Delay](components_omnet/delay.md): è un tempo fisso che viene applicato ad ogni task per simulare delle operazioni. 
* [Sink](components_omnet/sink.md): corrisponde all'output della network e viene utilizzato per calcolare alcune statistiche di performance.
* [Classifier](components_omnet/classifier.md): modulo di instradamento utilizzato per smistare i pacchetti (job) in arrivo verso diverse uscite sulla base di attributi specifici del pacchetto stesso.

Il **`file.ned`**:
```ned
import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Router;
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Sink;
import org.omnetpp.queueing.Delay;

network esame {

    parameters:
        int K = default(10);
        double rho = default(0.8);
        double mu = default(10);
        double lambda = mu * rho;
        
        srv.capacity = K;
        srv.serviceTime = 1s * exponential(1 / mu);
        src.interArrivalTime = 1s * exponential(1 / lambda);
        //src[*].interArrivalTime = exponential(1s/lambda);
        //srv.serviceTime = 1s * exponential(1 / mu);
        //r.routingAlgorithm="random";
        

    submodules:
		//src: Source;
        //srv: Queue;
        //sink: Sink;
        //r: Router;
        //src[N]: Source;

    connections:
        src.out --> srv.in++;
        srv.out --> sink.in++;

        //for i=0..N-1 { 
		//src[i].out --> delay[i].in++;
        //delay[i].out --> srv[i].in++;
	    //} per fare cicli

        //MAPPA di Ingressi/Uscite
        //source -> out; 
        //queue -> in[]; out;
        //router -> in[]; out[];
        //sink -> in[];
        //delay -> in[], out;

}
```
# 2. Creazione file `ini.mako`:
```ini
[General]
ned-path = .;../queueinglib
network = esame
repeat = 5
cpu-time-limit = 60s
sim-time-limit = 10000s
**.vector-recording = false

%for K in [5, 7, 10, -1]:

%for rho in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85. 0.88, 0.9]:
[Config CONF_rho${"%03d" % int(rho * 100)}_K${K if K > 0 else "inf"}]

**.srv.queueLenght.result-recording-modes = + histogram
**.sink.lifeTime.result-recording-modes = + histogram
**.K = ${K}
**.rho = ${rho}
%endfor
%endfor

[Config CONF_2]
extends = NOME_CONF_DA_ESTENDERE

%for i in [33,34,35,36,37,38,39,40]:
[Config CONF_${i}]

%endfor



#--- PARAMETRI SOURCE ---
# Usiamo il wildcard [*] per prendere tutti i sink
**.src.interArrivalTime = 1s * exponential(1 / **lambda) #intervallo di tempo tra la generazione di un job e il successivo
**.src.jobType = 0 #Un'etichetta numerica che assegni al job
**.src.jobName = "LowTraffic" #Un'etichetta descrittiva per il job

#--- PARAMETRI QUEUE ---
**.srv.serviceTime = 1s * exponential(1 / **mu) #Quanto tempo il server impiega per elaborare un job
**.srv.serviceTime = 1.0s * lognormal(log(1.0 / (mu * sqrt(1 + cv^2))), sqrt(log(1 + cv^2)));
**.srv.capacity = -1  # Coda infinita
**.srv[*].busy.result-recording-modes = +timeavg #Utilizzazione del server (\rho)

#--- PARAMETRI ROUTER ---
#Utilizzato per instradare una percentuale di traffico 
**.router.randomGateIndex=(uniform(0, 10.0) <= 6.0 ? 0 : 1)
		
#--- PARAMETRI DELAY ---
**.delay.delay = uniform(0.1s, 0.2s)
		
#--- PARAMETRI CLASSIFIER (Parte 3) ---
**.classifier.dispatcherField = "jobType" #Indica al modulo quale "etichetta" del job deve leggere per decidere verso quale uscita mandarlo.
#Se scrivi "jobType", lui guarderà il numero che hai assegnato nella sorgente.
		
#--- REGISTRAZIONE STATISTICHE (SINK) ---
**.sink[*].lifeTime.result-recording-modes = +mean, +max #tempo di risposta T_r
```
---
# 3. Creo il file `.ini` dal file `.ini.mako`
* **Compialiamo il file `.ini.mako`:**

    ```bash
    update_template.py 
    ```
    L'output sarà un file `.ini`.
* **Generare il RunFile:**
    ```bash
    make_runfile.py -f file.ini
    ```
    
* **Far Partire la simulazione:**
    
    ```bash
    make -j $(sysctl -n hw.ncpu) -B -f Runfile
    ```
    In particolare nella cartella `/results` ci sono file:
    * `.sca`: contiene i dati scalari.
    * `.vec`: contiene i vettori.
    * `.vci`: indice ai vettori, per migliorare le performance.
    
    A noi interessano i file `.sca`, è qui che si salvano le statistiche che abbiamo specificato nel file `.ini.mako`.
---
# 4. Creazione file `.json`
Per convertire i file di output `.sca` in un database SQLite, si utilizza un file di configurazione JSON che definisce tre tabelle principali:
- **value** -> contiene le metriche delle varie run
- **scenario** -> contiene i parametri di configurazioen delle varie run 
- **histogram**
## 4.1. File `.json`
- `scenario_schema`: specifica i parametri del file `.sca` da mappare nel database.

     **$\color{red}{\text{N.B.}}$**  I parametri devono essere definiti nel file `.ini` (o `.ini.mako`) per essere registrati come scalari nel file `.sca`.
- `metrics`: definisce le metriche da estrarre (es. `ResponseTime`, `WaitingTime`) indicando il modulo OMNeT++ e il nome dello scalare.
- `histograms`: specifica gli istogrammi di interesse (es. `lifeTime:histogram`).
- `aggregation`: determina come gestire campioni multipli per la stessa metrica:
    - `sum` / `avg` / `std`: somma, media o deviazione standard.
    - `none`: estrae il primo valore (utile per parametri univoci o configurazioni costanti).
```json
{
    "scenario_schema": {
        "label": {"pattern": "**.label", "type": "string"},
        "mu1": {"pattern": "**.mu1", "type": "real"},
        "mu2": {"pattern": "**.mu2", "type": "real"},
        "Balance": {"pattern": "**.Balance", "type": "string"},
        "lambda1": {"pattern": "**.lambda1", "type": "real"},
        "lambda2": {"pattern": "**.lambda2", "type": "real"}
    },
    "metrics": {
        "LifeTime": {"module": "**.sink", "scalar_name": "lifeTime:mean" ,"aggr": ["none"]},
        "PQueue": {"module": "**.sink", "scalar_name": "queuesVisited:mean" ,"aggr": ["none"]},
        "ServiceTime": {"module": "**.sink", "scalar_name": "totalServiceTime:mean" ,"aggr": ["none"]},
        "WaitingTime": {"module": "**.sink", "scalar_name": "totalQueueingTime:mean" ,"aggr": ["none"]},
        "BusyTime": {"module": "**.srv[*]", "scalar_name": "busy:timeavg" ,"aggr": ["none"]}
    },
    "histograms": {
        "SinkTime1": {"module": "**.sink1", "histogram_name": "lifeTime:histogram"},
        "SinkTime2": {"module": "**.sink2", "histogram_name": "lifeTime:histogram"}
    },
    "analyses": {
       ...
    }
}
```
---
# 5. Salviamo i file nel database
Sfruttiamo il file di configurazione per salvare i dati in un database sqlite, ovvero in un file `.db`:
```bash
parse_data.py -c nomeconfig.json -d database.db -r results/nome_base*.sca
```
---
# 6. Analizziamo i dati del database
I dati del database `.db` vengono analizzati per generare i file `.data` definiti nel `.json` (sezione `analyses`), ciascuno contenente una tabella strutturata secondo le specifiche del file di configurazione. Ci sono due modalità di analisi dei dati:
1. Analisi di dati scalari
2. Analisi di istogrammi

## 6.1. Focus su Analisi di Dati Scalari
```json
{
    "scenario_schema": {
        ...
    },
    "metrics": {
        ...
    },
    "histograms": {
        ...
    },
    "analyses": {
       "Fase1": {
            "outfile": "results/fase_1.data",
            "scenarios": {
                "fixed": {"label": "fase_1"},
                "range": []
            },
            "metrics": [
                        {"metric": "TotalJobs", "aggr": "none"},
                        {"metric": "DroppedJobs", "aggr": "none"}
                    ]
        },
        "Fase2": {
            "outfile": "results/fase_2.data",
            "scenarios": {
                "fixed": {"label": "fase_2"},
                "range": ["rho"]
            },
            "metrics": [
                {"metric": "TotalJobs", "aggr": "none"},
                {"metric": "DroppedJobs", "aggr": "none"},
                {"metric": "PQueue", "aggr": "none"},
                {"metric": "ServiceTime", "aggr": "none"},
                {"metric": "WaitingTime", "aggr": "none"},
                {"metric": "ResponseTime", "aggr": "none"}
                    ]
        },
    }
}
```
Per ogni configurazione di `analysis` è necessario specificare un **nome** e i seguenti campi:
- `outfile`: percorso del file di output in cui salvare i risultati.
- `scenarios`: insieme dei dati da estrarre dal database. Che a sua volta contiene:

  - `fixed`: insieme di coppie chiave-valore dei parametri mantenuti costanti (equivalente alla clausola WHERE in SQL).
  
  - `range`: lista dei parametri che variano, utilizzati come asse X (equivalente alla clausola ORDER BY).
- `metrics`: metriche da estrarre (asse Y), ciascuna definita da:
	- `metric`: nome della metrica memorizzata nella tabella value;
  
	- `aggr`: tipo di aggregazione applicata (`avg`, `sum`, `std`, `none`), coerente con quelle usate in parse_data.

## 6.2. Focus su Analisi di Istogrammi
L’analisi istogramma produce una stima della Funzione di Densità di Probabilità (PDF) media sulle diverse run, opportunamente normalizzata e interpolata.

Quando si eseguono $N$ run della stessa simulazione (ad esempio con seed diversi), ogni run genera un istogramma proprio. Tuttavia:
- i bin non coincidono tra le run;
- i conteggi assoluti non sono confrontabili, perché ogni run può generare un numero diverso di campioni.

Per questo motivo gli istogrammi non possono essere sommati direttamente.
Lo script risolve il problema riallineando i bin, normalizzando i conteggi e calcolando una PDF media coerente:
```json
{
    "scenario_schema": {
        ...
    },
    "metrics": {
        ...
    },
    "histograms": {
        ...
    },
    "analyses": {
        "analisi_distribuzione_ritardo": {
            "outfile": "data/distribuzione_ritardo.dat",
            "scenario": {
                "num_users": "50",
                "modulazione": "QAM16",
                "carico_traffico": "0.8"
            },
            "histogram": "endToEndDelay:histogram"
        }
    }
}
```
Per ogni configurazione di `analysis` è necessario specificare un nome e i seguenti campi:
- `outfile`: percorso del file di output.
- `scenario` (object, al singolare): dizionario di parametri fissi che identificano univocamente la configurazione da analizzare (tutti i parametri tranne il run number).
- `histogram`: nome dell’istogramma (o del modulo) salvato nella tabella histogram.
---
# 7. Eseguiamo l'analisi dei dati
Una volta popolato il database SQLite tramite il processo di parsing, l'ultimo step consiste nell'estrarre i dati aggregati (medie, intervalli di confidenza, etc.) definiti nel file di configurazione:
```bash
analyze_data.py -c nomeconfig.json -d database.db
```
---
# 8. Calcoliamo Tempo di risposta medio, IC e costo
## 8.1. Caso con una configurazione
```python
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t
from scipy.stats import norm
import math

SIM_TIME_LIMIT = 10000 # seconds
REPETITIONS = 5
N = 45 # Numero di Server

data_mu1 = np.loadtxt("results/fase_1_mu1.data")
data_mu2 = np.loadtxt("results/fase_1_mu2.data")

print("-----UTILIZZO-----")
print(f"N = {N}")
print(f"Ripetizioni per configurazione = {REPETITIONS}")
print("------------------")

# --- COSTO DI NOLEGGIO FISSO ---
def compute_rental_cost_comparison(cost_per_hour1, cost_per_hour2, n = N):
    """Calcola il costo basato solo sul numero di server affittati """
    costo_fisso1 = n * cost_per_hour1
    costo_fisso2 = n * cost_per_hour2
    print(f"Costo Noleggio Fisso Tipo 1 (N={n}) -> {costo_fisso1:.2f}$/hour")
    print(f"Costo Noleggio Fisso Tipo 2 (N={n}) -> {costo_fisso2:.2f}$/hour")
    return costo_fisso1, costo_fisso2

def compute_rental_cost(cost_per_hour, n = N):
    """Calcola il costo basato solo sul numero di server affittati """
    costo_fisso = n * cost_per_hour
    print(f"Costo Noleggio Fisso Tipo  (N={n}) -> {costo_fisso:.2f}$/hour")
    return costo_fisso

# --- COSTO OPERATIVO DURANTE IL TEMPO DI SIMULAZIONE (Basato sull'utilizzo busy_percentage) ---
def compute_cost_comparison(busy_percentage1,busy_percentage2,cost_per_hour1,cost_per_hour2, n = N):
    costo_totale1 = busy_percentage1 * SIM_TIME_LIMIT * (cost_per_hour1 / 3600.0)
    costo_totale2 = busy_percentage2 * SIM_TIME_LIMIT * (cost_per_hour2 / 3600.0)
    print(f"Costo totale 1 -> {(costo_totale1 * n):.2f}")
    print(f"Costo totale 2 -> {(costo_totale2 * n):.2f}") 

def compute_cost(busy_percentage,cost_per_hour, n = N):
    costo_totale = busy_percentage * SIM_TIME_LIMIT * (cost_per_hour / 3600.0)
    print(f"Costo totale -> {costo_totale * n:.2f}")

#---COSTO OPERATIVO IN UN ORA (Basato sull'utilizzo busy_percentage)---
def compute_cost_comparison_hour(busy_percentage1,busy_percentage2,cost_per_hour1,cost_per_hour2, n = N):
    costo_totale1 = busy_percentage1 * SIM_TIME_LIMIT * (cost_per_hour1 / 3600.0)
    costo_totale2 = busy_percentage2 * SIM_TIME_LIMIT * (cost_per_hour2 / 3600.0)
    print(f"Costo totale 1 in un ora -> {((costo_totale1 / SIM_TIME_LIMIT) * 3600 * n):.2f}$/hour")
    print(f"Costo totale 2 in un ora -> {((costo_totale2 / SIM_TIME_LIMIT) * 3600 * n):.2f}$/hour") 

def compute_cost_hour(busy_percentage,cost_per_hour, n = N):
    costo_totale = busy_percentage * SIM_TIME_LIMIT * (cost_per_hour / 3600.0)
    print(f"Costo totale in un ora -> {(costo_totale / SIM_TIME_LIMIT) * 3600 * n:.2f}$/hour")


#---CALCOLO CI---
#n_repeat è il numero di run per configurazione
def compute_CI(std, confidence_percentage,label=""):
    df = REPETITIONS - 1
    alpha = 1 - (confidence_percentage / 100)
    q = 1 - (alpha / 2)
    t_critical = t.ppf(q, df)
    ic = t_critical * (std / math.sqrt(REPETITIONS))
    return print(f"CI_{label} -> +-{(ic):.8f}")

std_1 = data_mu1[1]
busy_1 = data_mu1[2]

std_2 = data_mu2[1]
busy_2 = data_mu2[2]

compute_CI(std=std_1, confidence_percentage=65,label="mu1")
compute_CI(std=std_2, confidence_percentage=65,label="mu2")

compute_cost_comparison(busy_percentage1=busy_1, busy_percentage2=busy_2, cost_per_hour1=1.5, cost_per_hour2=3)
compute_cost_comparison_hour(busy_percentage1=busy_1, busy_percentage2=busy_2, cost_per_hour1=1.5, cost_per_hour2=3)
```
## 8.2. Caso con più configurazioni
```python
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t
import math

SIM_TIME_LIMIT = 10000 # seconds
REPETITIONS = 5
N = 45 # Numero di Server

#---COSTO DEL SISTEMA DURANTE IL PERIODO DI SIMULAZIONE (considerando N server)--
def compute_cost_comparison(busy_percentage1,busy_percentage2,cost_per_hour1,cost_per_hour2, n = N):
    costo_totale1 = busy_percentage1 * SIM_TIME_LIMIT * (cost_per_hour1 / 3600.0)
    costo_totale2 = busy_percentage2 * SIM_TIME_LIMIT * (cost_per_hour2 / 3600.0)
    print(f"Costo totale 1 -> {(costo_totale1 * n):.2f}")
    print(f"Costo totale 2 -> {(costo_totale2 * n):.2f}") 
    return costo_totale1, costo_totale2

def compute_cost(busy_percentage,cost_per_hour, n = N):
    costo_totale = busy_percentage * SIM_TIME_LIMIT * (cost_per_hour / 3600.0)
    print(f"Costo totale -> {costo_totale * n:.2f}")
    return costo_totale

#---COSTO DEL SISTEMA IN UN ORA (considerando N server)---
def compute_cost_comparison_hour(busy_percentage1,busy_percentage2,cost_per_hour1,cost_per_hour2, n = N):
    costo_totale1 = busy_percentage1 * SIM_TIME_LIMIT * (cost_per_hour1 / 3600.0)
    costo_totale2 = busy_percentage2 * SIM_TIME_LIMIT * (cost_per_hour2 / 3600.0)
    print(f"Costo totale 1 in un ora -> {((costo_totale1 / SIM_TIME_LIMIT) * 3600 * n):.2f}$/hour")
    print(f"Costo totale 2 in un ora -> {((costo_totale2 / SIM_TIME_LIMIT) * 3600 * n):.2f}$/hour") 
    return ((costo_totale1 / SIM_TIME_LIMIT) * 3600 * n), ((costo_totale2 / SIM_TIME_LIMIT) * 3600 * n)

def compute_cost_hour(busy_percentage,cost_per_hour, n = N):
    costo_totale = busy_percentage * SIM_TIME_LIMIT * (cost_per_hour / 3600.0)
    print(f"Costo totale in un ora -> {(costo_totale / SIM_TIME_LIMIT) * 3600 * n:.2f}$/hour")
    return ((costo_totale / SIM_TIME_LIMIT) * 3600 * n)

#n_repeat è il numero di run per configurazione
def compute_CI(std, confidence_percentage,label=""):
    df = REPETITIONS - 1
    alpha = 1 - (confidence_percentage / 100)
    q = 1 - (alpha / 2)
    t_critical = t.ppf(q, df)
    ic = t_critical * (std / math.sqrt(REPETITIONS))
    print(f"CI_{label} -> +-{(ic):.8f}")
    return ic

print("server 1".center(50, "="))

data = np.loadtxt("results/fase_2_mu1.data")
list_ic_costo = []

for row in range(data.shape[0]):
    row_data = data[row,:]

    n = row_data[0]
    std = row_data[2]
    busy = row_data[3]

    ic = compute_CI(std,65,label=str(n))
    costo = compute_cost_hour(busy_percentage=busy,cost_per_hour=1.5,n=n)
    
    #Per salvare i valori di N, IC e costo in un file
    #list_ic_costo.append([n,ic,costo])   

#Per salvare i valoir di N, IC e costo in un file    
#np.savetxt("results/ic_mu1_err.data", list_ic_costo, header="N\tIC\tCosto", fmt=['%d', '%.8f', '%.3f'])


print("\n")
print("server 2".center(50, "="))

data = np.loadtxt("results/fase_2_mu2.data")
list_ic_costo = []
for row in range(data.shape[0]):
    row_data = data[row,:]

    n = row_data[0]
    std = row_data[2]
    busy = row_data[3]
   
    ic = compute_CI(std,65,label=str(n))
    costo = compute_cost_hour(busy_percentage=busy,cost_per_hour=3,n=n)

    #Per salvare i valoir di N, IC e costo in un file  
    #list_ic_costo.append([n,ic,costo])   

#Per salvare i valoir di N, IC e costo in un file    
#np.savetxt("results/ic_mu2_err.data", list_ic_costo, header="N\tIC\tCosto", fmt=['%d', '%.8f', '%.3f'])
```
---
# 9. Plottiamo i dati con plotlib 
1. **Creiamo nel progetto il file utils del prof, `plot.py`:**

    ```python
    #!/usr/bin/python3
    import sys
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Patch
    import matplotlib as mpl
    import matplotlib.colors as mc
    #import pathlib

    def set_fonts():
        """ 
        Set LaTeX-friendly fonts. Call this function at the beginning of your code
        """
        mpl.rcParams['font.family'] = 'Nimbus Sans'
        mpl.rcParams["figure.autolayout"] = True
        mpl.rc('text', usetex=True)
        mpl.rcParams.update({'font.size': 10})

    def plot_line(ax, format, fname, label, xcol, ycol, errcol=None):
        """
        Plot a line from data
        
        Parameters
        ----------
        ax : 
            canvas for plotting. Refer to matplotlib.pyplot. Can ge the object returned by matplotlib.pyplot.subplots()
        format: str
            format string. Refer to matplotlib.pyplot
        fname: str or None
            name of a tab-separated column file. Column names are on the first row
        label: str
            label of the curve in the plot
        xcol:
            the x data for the plot 
            can be the name of a column in a dataframe if fname is a file with data
            can be a callable that is invoked on the dataframe
            can be a set list/array with data
        ycol:
            like xcol, but this is the y data of the plot
        errcol:
            like xcol but ti can aslo be none. If set it contains the error values to represent a confidence interval
        """
        if fname is not None:
            data = pd.read_csv(fname, sep='\t')
        use_data=fname is not None and not callable(xcol) and not callable(ycol) and not callable(errcol)
        xcol = xcol(data) if callable(xcol) else xcol
        ycol = ycol(data) if callable(ycol) else ycol
        errcol=errcol(data) if callable(errcol) else errcol
        data=data if use_data else None
        if errcol is not None:
            ax.errorbar(xcol, ycol, yerr=errcol, data=data, fmt=format, label=label, capsize=5)
        else:
            ax.plot(xcol, ycol, format, data=data, label=label)
    ```
2. **Creiamo il file per geneare il plot, `bonus.py`:**

    ```python
    #!/usr/bin/python3
    import sys
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Patch
    import matplotlib as mpl
    import matplotlib.colors as mc
    from plot import plot_line, set_fonts

    lam=200 #MODIFICA
    cv=1.0  #MODIFICA

    """
    cv = 1.0 se il tempo di servizio è esponenziale
    cv = 0.0 determinstico
    """

    #Utilizzata per calcolare il tempo di risposta medio atteso
    def theoretical(N, mu):
        rho=lam/(mu * N)
        if rho >= 1:
            return None
        else:
            return 1/mu * (1 + ((1+cv**2)/2)*rho/(1-rho)) 
        
    data_mu1 = np.loadtxt("results/fase_2_mu1.data") #MODIFICA
    data_mu2 = np.loadtxt("results/fase_2_mu2.data") #MODIFICA

    N_mu1 = data_mu1[:,0] 
    N_mu2 = data_mu2[:,0]

    life_time_mu1 = data_mu1[:,1]
    life_time_mu2 = data_mu2[:,1]

    #Per ricavare il CI
    data_ci_mu1 = np.loadtxt("results/ic_mu1_err.data") #MODIFICA
    data_ci_mu2 = np.loadtxt("results/ic_mu1_err.data") #MODIFICA

    ic_mu1 = data_ci_mu1[:,1]
    ic_mu2 = data_ci_mu2[:,1]


    if __name__ == "__main__":
        print(f"Configurazione con lambda = {lam} e cv = {cv}")
        # plot respone time
        fig, ax = plt.subplots()
        ax.set(xlabel='Number of servers N', ylabel='Time [s]')
        #plot_line(ax, 'o--', 'sample.data', 'Response Time', '#x', 'y', 'sigma(y)')
        
        # Inserisci il range dei possibili valori di N (ricordati che range esclude l'ultimo valore)
        range_N_1 =list(range(30, 56)) #MODIFICA
        range_N_2 =list(range(15, 56)) #MODIFICA
        mu_1 = 8 #MODIFICA
        mu_2 = 16 #MODIFICA

        plot_line(ax, '-', None, f'Theoretical curve $\mu$={mu_1}', range_N_1, [theoretical(x,mu= mu_1) for x in range_N_1])
        plot_line(ax, '-', None, f'Theoretical curve $\mu$={mu_2}', range_N_2, [theoretical(x,mu= mu_2) for x in range_N_2])

        #Inserisci prima asse x e poi asse y (RIMUOVI IC_MU SE NON LO UTILIZZI)
        plot_line(ax, 'o--', None, f'Response time $\mu$={mu_1}', N_mu1, life_time_mu1,ic_mu1 * 2)
        plot_line(ax, 'o--', None, f'Response time $\mu$={mu_2}', N_mu2, life_time_mu2,ic_mu2 * 2)
        #N.B. La funzione ti richide tutto l'intervallo di certezza, quindi l'IC devi moltiplicarlo per 2

        #Per settare il range di valori nell'asse Y
        ax.set_ylim(0, 1)
        #Per settare i valori sull'asse Y
        ax.set_yticks([0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9])

        #Per settare una linea orizzontale rossa 
        ax.axhline(y=0.250, color='red', linestyle='-', linewidth=1) #MODIFICA
        
        plt.legend()
        #plt.savefig('sample.png')
        plt.show()
    ```
---
# 10. Focus su Plot, file iper generico del prof

```python
import matplotlib.pyplot as plt
import numpy as np

# Load curve
data_inf = np.loadtxt("results/loadcurve_inf.data")
data_K10 = np.loadtxt("results/loadcurve_K10.data")
data_K7 = np.loadtxt("results/loadcurve_K7.data")
data_K5 = np.loadtxt("results/loadcurve_K5.data")

x_inf, y_inf, yerr_inf = data_inf[:, 0], data_inf[:, 11], data_inf[:, 12]
x_K10, y_K10, yerr_K10 = data_K10[:, 0], data_K10[:, 11], data_K10[:, 12]
x_K7, y_K7, yerr_K7 = data_K7[:, 0], data_K7[:, 11], data_K7[:, 12]
x_K5, y_K5, yerr_K5 = data_K5[:, 0], data_K5[:, 11], data_K5[:, 12]

# Plot
plt.figure(figsize=(10, 6))
plt.ylim(bottom=0, top=1.2)
plt.errorbar(x_inf, y_inf, yerr=yerr_inf, fmt='o', label=r'$T_{Resp} Qlen=\infty$', color='C1', markersize=6)
plt.errorbar(x_K10, y_K10, yerr=yerr_K10, fmt='o', label=r'$T_{Resp} Qlen=10$', color='C2', markersize=6)
plt.errorbar(x_K7, y_K7, yerr=yerr_K7, fmt='o', label=r'$T_{Resp} Qlen=7$', color='C3', markersize=6)
plt.errorbar(x_K5, y_K5, yerr=yerr_K5, fmt='o', label=r'$T_{Resp} Qlen=5$', color='C4', markersize=6)
plt.plot(x_inf, y_inf, label='_nolegend_', color='C1')
plt.plot(x_K10, y_K10, label='_nolegend_', color='C2')
plt.plot(x_K7, y_K7, label='_nolegend_', color='C3')
plt.plot(x_K5, y_K5, label='_nolegend_', color='C4')

plt.xlabel(r'${\rho}$', fontsize=12)
plt.ylabel('Time [s]', fontsize=12)
plt.legend(loc='upper left')
plt.savefig("TrespMM1.png", dpi=300, bbox_inches='tight')

# Response time breakdown
data_inf = np.loadtxt("results/loadcurve_inf.data")

x_inf, y_resp, yerr_resp = data_inf[:, 0], data_inf[:, 11], data_inf[:, 12]
y_srv, yerr_srv = data_inf[:, 7], data_inf[:, 8]
y_wait, yerr_wait = data_inf[:, 9], data_inf[:, 10]

plt.figure(figsize=(10, 6))
plt.errorbar(x_inf, y_resp, yerr=yerr_resp, fmt='o', label=r'$T_{Resp} Qlen=\infty$', color='C1', markersize=6)
plt.errorbar(x_inf, y_srv, yerr=yerr_srv, fmt='o', label=r'$T_{Srv} Qlen=\infty$', color='C2', markersize=6)
plt.errorbar(x_inf, y_wait, yerr=yerr_wait, fmt='o', label=r'$T_{Wait} Qlen=\infty$', color='C3', markersize=6)

plt.plot(x_inf, y_resp, label='_nolegend_', color='C1')
plt.plot(x_inf, y_srv, label='_nolegend_', color='C2')
plt.plot(x_inf, y_wait, label='_nolegend_', color='C3')

plt.xlim(0, 0.95)
plt.ylim(0, 1.2)
plt.xlabel(r'${\rho}$', fontsize=12)
plt.ylabel('Time [s]', fontsize=12)
plt.legend(loc='upper left')

plt.savefig("TrespMM1BD.png", dpi=300, bbox_inches='tight')

# Validation
data_inf = np.loadtxt("results/loadcurve_inf.data")

x_inf = data_inf[:, 0]
y_resp = data_inf[:, 11]
yerr_resp = data_inf[:, 12]

theoretical_curve = lambda x: 0.1 / (1 - x)

plt.figure(figsize=(10, 6))
plt.fill_between(x_inf, y_resp - yerr_resp, y_resp + yerr_resp, color='C1', alpha=0.4, label=r'$T_{Resp}\pm\sigma$')
plt.plot(x_inf, y_resp, 'o-', label=r'$T_{Resp}$', color='C1', markersize=6)
x = np.linspace(0.1, 0.9, 400)
plt.plot(x, theoretical_curve(x), label='Theoretical curve', color='C2', linewidth=2)

plt.xlim(0.1, 0.9)
plt.ylim(0, 1.2)
plt.xlabel(r'${\rho}$', fontsize=12)
plt.ylabel('Time [s]', fontsize=12)
plt.legend(loc='upper left')

plt.savefig("TrespMM1Validation.png", dpi=300, bbox_inches='tight')

# Drop rate
x_inf, y_inf, yerr_inf = data_inf[:, 0], 100 * data_inf[:, 3] / data_inf[:, 1], 100 * data_inf[:, 4] / data_inf[:, 1]
x_K10, y_K10, yerr_K10 = data_K10[:, 0], 100 * data_K10[:, 3] / data_K10[:, 1], 100 * data_K10[:, 4] / data_K10[:, 1]
x_K7, y_K7, yerr_K7 = data_K7[:, 0], 100 * data_K7[:, 3] / data_K7[:, 1], 100 * data_K7[:, 4] / data_K7[:, 1]
x_K5, y_K5, yerr_K5 = data_K5[:, 0], 100 * data_K5[:, 3] / data_K5[:, 1], 100 * data_K5[:, 4] / data_K5[:, 1]
plt.figure(figsize=(10, 6))
plt.errorbar(x_inf, y_inf, yerr=yerr_inf, fmt='o', label=r'$Qlen=\infty$', color='C1', markersize=6)
plt.errorbar(x_K10, y_K10, yerr=yerr_K10, fmt='o', label=r'$Qlen=10$', color='C2', markersize=6)
plt.errorbar(x_K7, y_K7, yerr=yerr_K7, fmt='o', label=r'$Qlen=7$', color='C3', markersize=6)
plt.errorbar(x_K5, y_K5, yerr=yerr_K5, fmt='o', label=r'$Qlen=5$', color='C4', markersize=6)

plt.plot(x_inf, y_inf, label='_nolegend_', color='C1')
plt.plot(x_K10, y_K10, label='_nolegend_', color='C2')
plt.plot(x_K7, y_K7, label='_nolegend_', color='C3')
plt.plot(x_K5, y_K5, label='_nolegend_', color='C4')

plt.ylabel('Drop rate [%]', fontsize=12)
plt.legend(loc='upper left')
plt.savefig("DropMM1.png", dpi=300, bbox_inches='tight')

# Utilization
x_inf, y_inf, yerr_inf = data_inf[:, 0], 100 * data_inf[:, 5], 100 * data_inf[:, 6]
x_K10, y_K10, yerr_K10 = data_K10[:, 0], 100 * data_K10[:, 5], 100 * data_K10[:, 6]
x_K7, y_K7, yerr_K7 = data_K7[:, 0], 100 * data_K7[:, 5], 100 * data_K7[:, 6]
x_K5, y_K5, yerr_K5 = data_K5[:, 0], 100 * data_K5[:, 5], 100 * data_K5[:, 6]

plt.figure(figsize=(10, 6))
plt.errorbar(x_inf, y_inf, yerr=yerr_inf, fmt='o', label=r'$Qlen=\infty$', color='C1', markersize=6)
plt.errorbar(x_K10, y_K10, yerr=yerr_K10, fmt='o', label=r'$Qlen=10$', color='C2', markersize=6)
plt.errorbar(x_K7, y_K7, yerr=yerr_K7, fmt='o', label=r'$Qlen=7$', color='C3', markersize=6)
plt.errorbar(x_K5, y_K5, yerr=yerr_K5, fmt='o', label=r'$Qlen=5$', color='C4', markersize=6)

plt.plot(x_inf, y_inf, label='_nolegend_', color='C1')
plt.plot(x_K10, y_K10, label='_nolegend_', color='C2')
plt.plot(x_K7, y_K7, label='_nolegend_', color='C3')
plt.plot(x_K5, y_K5, label='_nolegend_', color='C4')

plt.ylabel('Utilization [%]', fontsize=12)
plt.legend(loc='upper left')
plt.savefig("UtilMM1.png", dpi=300, bbox_inches='tight')
```
---
# 11. Formule Utili
* **Formula di Pollaczek-Khinchin (Caso M/G/1):**
    
    $$\displaystyle T_r=\frac{1}{\mu}+ \frac{\rho \cdot \frac{1}{\mu}\cdot (1 + c^2)}{2(1-\rho)}$$
  
  Analisi casi particolari:
  - **Service time M (=Esponenziale):** in questo caso il coefficiente di variazione è $c=1$. La formula P-K si semplifica nel classico modello M/M/1. Se il traffico $\lambda$ è diviso tra $N$ server paralleli:
  
    $$\displaystyle T_r = \frac{1}{\mu -\frac{\lambda}{N}}$$
    
    Formula inversa per trovare $N$:

    $$\displaystyle N=\frac{\lambda}{\mu-\frac{1}{T_r}}$$

  - **Service time G (=Generale):** A differenza di quanto si pensi, la formula P-K scritta sopra è la formula chiusa per il tempo di risposta medio. Tuttavia, non esiste una formula chiusa semplice per la distribuzione completa del tempo di risposta (a meno di non usare le trasformate di Laplace).

  - **Service time D (=Deterministico):** In questo caso il tempo di servizio è costante, quindi non c'è varianza ($c=0$). La formula si riduce a:

    $$T_r=\frac{1}{\mu}+ \frac{\frac{\rho}{\mu}}{(1-\rho)}\cdot 0.5$$

* **Utilizzo del server:**

    $$\displaystyle\rho=\frac{\lambda}{\mu}$$


**$\color{red}{\text{N.B.}}$** Per risolvere le equazione online utiizzare il seguente [link](https://it.symbolab.com/solver/equation-calculator).

---
# 12. Altri comandi utili
* **Per visualizzare il file `.ini` in IDE:**

    ```bash
    ./queuenet file.ini
    ```
* **Per cancellare i file dentro la directory `/results`:**

    ```bash
    rm -rf results/*
    ``` 
* **Script di simulazione:**
    ```bash
    ./simulate.sh <nome_file_senza_estensione> <"Fase_1_mu*-#*”>
    ```  
---
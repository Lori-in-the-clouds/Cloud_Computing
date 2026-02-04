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
        
- **Script di simulazione**
    
    ```bash
    #!/bin/bash
    
    # --- 1. Controllo Input ---
    nome_sim=$1
    path=$2
    
    if [ -z "$nome_sim" ]; then
      echo "Errore: Devi specificare il nome del file (senza estensione)."
      echo "Esempio: ./simulate.sh MM1_base"
      exit 1
    fi
    
    # --- 2. Pulizia (Fondamentale per evitare l'IndexError) ---
    # Rimuoviamo i vecchi risultati per assicurarci che il parse legga solo i nuovi dati
    echo "Pulizia vecchi risultati..."
    rm -f results/${nome_sim}_* 
    rm -f ${nome_sim}.db
    
    update_template.py
    
    # --- 3. Generazione Runfile ---
    echo "Generazione del Runfile da Mako..."
    # Se il tuo file si chiama nome_sim.ini.mako, aggiungi l'estensione qui sotto
    make_runfile.py -f ${nome_sim}.ini.mako 
    
    # --- 4. Esecuzione Simulazioni ---
    echo "Lancio simulazioni"
    make -j $(sysctl -n hw.ncpu) -B -f Runfile
    
    # --- 5. Parsing (Caricamento nel Database) ---
    echo "Parsing dei dati nel database SQLite..."
    # Nota: usiamo -c per il file di configurazione JSON
    parse_data.py -c config${nome_sim}.json -d ${nome_sim}.db -r results/${path}*.sca
    
    # --- 6. Analisi (Generazione tabelle .data) ---
    echo "Estrazione risultati finali..."
    # Attenzione: analyze_data di solito usa il flag -j per il file JSON
    analyze_data.py -c config${nome_sim}.json -d ${nome_sim}.db
    
    echo "--- Processo Completato! ---"
    ```
---
## 1. Creazione file `.ned`
Questo file viene utilizzato per definire la struttura della rete. I componenti che possono essere utilizzati sono:
* [Source](components_omnet/source.md): corrisponde alla sorgente del traffico che poi verrà distribuito ai vari server.
* [Router](components_omnet/router.md): ha il compito di distribuire il traffico tra i vari server seguendo una particolare politica.
* [Queue](components_omnet/queue.md): viene posta prima del server e viene utilizzata per valutare il tempo in cui le task restano in attesa prima di essere processati.
* [Delay](components_omnet/delay.md): è un tempo fisso che viene applicato ad ogni task per simulare delle operazioni. 
* [Sink](components_omnet/sink.md): corrisponde all'output della network e viene utilizzato per calcolare alcune statistiche di performance.

Il **`file.ned`**:
```ned
import org.omnetpp.queueing.Queue;
import org.omnetpp.queueing.Source;
import org.omnetpp.queueing.Sink;

network MM1 {

    parameters:
        int K = default(10);
        double rho = default(0.8);
        double mu = default(10);
        double lambda = mu * rho;
        
        srv.capacity = K;
        srv.serviceTime = 1s * exponential(1 / mu);
        src.interArrivalTime = 1s * exponential(1 / lambda);

    submodules:
        src: Source;
        srv: Queue;
        sink: Sink;
        r: Router;

    connections:
        src.out --> srv.in++;
        srv.out --> sink.in++;
}
```
Focus su array di elementi:
```ned

network MG1
{
	parameters:
		src[*].interArrivalTime = exponential(1s/lambda);
		...

	submodules:
		src[N]: Source;
		... 

	connections:
	    for i=0..N-1 { 
		    src[i].out --> delay[i].in++;
            delay[i].out --> srv[i].in++;
	    }
}
```
# 2. Creazione file `ini.mako`:
```ini
[General]
ned-path = .;../queueinglib
network = NETWORK
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
        "Balance": {"pattern": "**.Balance", "type": "varchar"},
        "lambda1": {"pattern": "**.lambda1", "type": "real"},
        "lambda2": {"pattern": "**.lambda2", "type": "real"},
        "mu1": {"pattern": "**.mu1", "type": "real"},
        "mu2": {"pattern": "**.mu2", "type": "real"}
    },
    "metrics": {
        "PQueue1": {"module": "**.sink1", "scalar_name": "queuesVisited:mean" ,"aggr": ["none"]},
        "ServiceTime1": {"module": "**.sink1", "scalar_name": "totalServiceTime:mean" ,"aggr": ["none"]},
        "WaitingTime1": {"module": "**.sink1", "scalar_name": "totalQueueingTime:mean" ,"aggr": ["none"]},
        "ResponseTime1": {"module": "**.sink1", "scalar_name": "lifeTime:mean" ,"aggr": ["none"]},
        "PQueue2": {"module": "**.sink2", "scalar_name": "queuesVisited:mean" ,"aggr": ["none"]},
        "ServiceTime2": {"module": "**.sink2", "scalar_name": "totalServiceTime:mean" ,"aggr": ["none"]},
        "WaitingTime2": {"module": "**.sink2", "scalar_name": "totalQueueingTime:mean" ,"aggr": ["none"]},
        "ResponseTime2": {"module": "**.sink2", "scalar_name": "lifeTime:mean" ,"aggr": ["none"]}
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
       "SensRho-Kinf": {
            "outfile": "results/loadcurve_inf.data",
            "scenarios": {
                "fixed": {"K": "-1"},
                "range": ["rho"]
            },
            "metrics": [
                {"metric": "TotalJobs", "aggr": "none"},
                {"metric": "DroppedJobs", "aggr": "none"}
                    ]
        },
        "SensRho-K10": {
            "outfile": "results/loadcurve_K10.data",
            "scenarios": {
                "fixed": {"K": "10"},
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

## 6.1. Focus su Analisi di Istogrammi
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
# 7. Calcoliamo Tempo di risposta medio, IC e costo
## 7.1. Caso con una configurazione
```python
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t
import math

data_mu1 = np.loadtxt("results/es1_mu1.data")
data_mu2 = np.loadtxt("results/es1_mu2.data")

def evaluate_price(total_busy_percentage, price_per_hour):
    price_per_second = price_per_hour/3600
    total_simulation_time = 1000
    total_busy_time = total_simulation_time * total_busy_percentage # in seconds

    total_price = total_busy_time * price_per_second
    return total_price

def evaluate_ic(std_dev, confidence_level, n_replicas):
    df = n_replicas - 1
    alpha = 1 - (confidence_level / 100)
    q = 1 - (alpha / 2)
    t_critical = t.ppf(q, df)
    ic = t_critical * (std_dev / math.sqrt(n_replicas))
    return ic

m1=data_mu1[0]
d1=data_mu1[1]
ic1 = evaluate_ic(d1, 65,10)
print(f"d1 = {d1} and ic {ic1}")
busy1=data_mu1[2]
costo1 = evaluate_price(busy1, 1.5)

m2=data_mu2[0]
d2=data_mu2[1]
print(d2)
ic2 = evaluate_ic(d2, 65,10)
busy2=data_mu2[2]
costo2 = evaluate_price(busy2, 1.5)

print(f"40 server in parallelo, tipologia1 --> Tr={m1*1000:.3f}+-{ic1*1000:.3f}ms, costo={costo1:.2f}$")
print(f"40 server in parallelo, tipologia2 --> Tr={m2*1000:.3f}+-{ic2*1000:.3f}ms, costo={costo2:.2f}$")
```
## 7.2. Caso con più configurazioni
```python
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t
import math

data_mu1 = np.loadtxt("results/es3_mu1.data")
data_mu2 = np.loadtxt("results/es3_mu2.data")

def evaluate_ic(std_dev, confidence_level, n_replicas):
    df = n_replicas - 1
    alpha = 1 - (confidence_level / 100)
    q = 1 - (alpha / 2)
    t_critical = t.ppf(q, df)
    ic = t_critical * (std_dev / math.sqrt(n_replicas))
    return ic

def evaluate_price(total_busy_percentage, price_per_hour):
    price_per_second = price_per_hour/3600
    total_simulation_time = 1000
    total_busy_time = total_simulation_time * total_busy_percentage # in seconds

    total_price = total_busy_time * price_per_second
    return total_price

print("server 1".center(50, "="))

data = np.loadtxt("results/es3_mu1.data")
for row in range(data.shape[0]):
    row_data = data[row,:]

    n = row_data[0]
    m=row_data[1]
    d=row_data[2]
    ic = evaluate_ic(d, 65, 10)
    busy=row_data[3]
    costo = evaluate_price(busy, 1.5)
    print(f"{int(n)} tipologia1 --> Tr={m*1000:.3f}+-{ic*1000:.3f}ms, costo={costo:.5f}$")

print("\n\n")
print("server 2".center(50, "="))

data = np.loadtxt("results/es3_mu2.data")
for row in range(data.shape[0]):
    row_data = data[row,:]

    n = row_data[0]
    m=row_data[1]
    d=row_data[2]
    ic = evaluate_ic(d, 65, 10)
    busy=row_data[3]
    costo = evaluate_price(busy, 1.5)
    print(f"{int(n)} tipologia2 --> Tr={m*1000:.3f}+-{ic*1000:.3f}ms, costo={costo:.5f}$")
```
---
# 8. Plottiamo i dati con plotlib 
1. **Creiamo nel progetto il file utils del prof, `plot.py`:
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
    from plots import plot_line, set_fonts

    lam=200
    cv=1.0
    def theoretical(N, mu):
        rho=lam/(mu * N)
        if rho >= 1:
            return None
        else:
            return 1/mu * (1 + ((1+cv**2)/2)*rho/(1-rho)) 
        
    data_mu1 = np.loadtxt("results/es3_mu1.data")
    data_mu2 = np.loadtxt("results/es3_mu2.data")

    tr_mu1 = data_mu1[:,1]
    tr_mu2 = data_mu2[:,1]

    pts_mu1 = data_mu1[:,0]
    pts_mu2 = data_mu2[:,0]

    if __name__ == "__main__":
        # plot respone time
        fig, ax = plt.subplots()
        ax.set(xlabel='Number of servers N', ylabel='Time [s]')
        #plot_line(ax, 'o--', 'sample.data', 'Response Time', '#x', 'y', 'sigma(y)')
        
        pts=list(range(15, 50))
        plot_line(ax, '-', None, 'Theoretical curve mu=10', pts, [theoretical(x, 10) for x in pts])
        plot_line(ax, '-', None, 'Theoretical curve mu=15', pts, [theoretical(x, 15) for x in pts])

        plot_line(ax, 'o--', None, 'Response time mu=10', pts_mu1, tr_mu1)
        plot_line(ax, 'o--', None, 'Response time mu=15', pts_mu2, tr_mu2)
        

        plt.legend()
        # plt.savefig('sample.png')
        plt.show()
   ```
---
# 9. Focus su Plot, file iper generico del prof
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
# 10. Formule Utili
* **Utilizzo del server:**
  $$
    \rho = \frac{\lambda}{\mu}
  $$
* **Tempo di Arrivo:**
  $$
    Avg\_Tr = \frac{1}{\mu -\frac{\lambda}{N}}
  $$
  con $N$, che rappresenta il numero di server in parallelo.
* **Formula inversa del tempo di arrivo** per trovare il numero $N$ di server necessari per soddisfare i requesiti:
$$
N = \frac{\lambda}{\mu-\frac{1}{Avg\_Tr}}
$$
* **Formula di Pollaczek-Chinchne:**
    $$
    T_r = \frac{1}{\mu}+ \frac{\rho \cdot \frac{1}{\mu}\cdot (1 + c^2)}{2(1-\rho)}
    $$
    Se il processo ha service time $M$ (=esponenziale), allora $c=1$


# OMNet++
## 0. Setup Ambiente
* **Script per avviare l’ambiente OMNeT++:**
    
    ```bash
    nano ~/.zshrc
    ```

    ```bash
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

**`file.ned`**
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
    
    A noi interessano i file `.sca`, e' qui che si salvano le statistiche che abbiamo specificato nel file `.ini.mako`.
---
# 4. Creazione file `.json`

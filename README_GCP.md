# Lab RestFUL - Google Cloud Platform

## 1. Setup Iniziale
1. **Controlla quale profilo hai attivo su vsCode**
2. **Crea un ambiente virtuale:**
    ```bash
    python3 -m venv .venv
    ```
3. **Attiva l'ambiente virtuale:**
    ```bash
    source .venv/bin/activate
    ```
4. **Creiamo il file `requirements.txt`:**   
    ```PlainText
    Flask==3.1.2
    flask-cors==6.0.2
    Flask-RESTful==0.3.9
    google-cloud-firestore==2.22.0
    gunicorn==23.0.0
    WTForms==3.0.1
    email-validator==2.3.0
    python-dateutil==2.9.0.post0
    google-cloud-pubsub==2.34.0
    ```
5. **Installiamo i requirements nell’environment:**
   ```bash
    pip install -r ./requirements.txt
    ```
6. **Creiamo il file `.gcloudignore`:**   
    ```PlainText
    .git
    .gitignore

    credentials.json
    __pycache__/

    .venv/
    /setup.gfc
    .pdf
    ```
7. **Creiamo il progetto e l'applicazione Gcloud:**
   ```bash
    export PROJECT_ID=<project_name>
    ```
    ```bash
    gcloud projects create ${PROJECT_ID} --set-as-default
    ```
8. **Linkiamo il billing account:**
   
   ```bash
    gcloud billing accounts list
    ```
    ```bash
    gcloud billing projects link ${PROJECT_ID} --billing-account <billing_account_id>
    ```
    Comandi utili:
    ```bash
    gcloud billing projects describe ${PROJECT_ID}
    gcloud app describe --project=${PROJECT_ID}
    ```
9.  **Creiamo l'applicazione:**
    ```bash
    gcloud services enable appengine.googleapis.com cloudbuild.googleapis.com firestore.googleapis.com pubsub.googleapis.com
    gcloud app create --project=${PROJECT_ID}
    ```
---
# 2. Configurazione Firestone
1. **Creazione di del Database Firestone:**
    ```bash
    export NAME=webuser
    gcloud iam service-accounts create ${NAME}
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:${NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/owner" 
    touch credentials.json 
    gcloud iam service-accounts keys create credentials.json --iam-account ${NAME}@${PROJECT_ID}.iam.gserviceaccount.com 
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
    ```
    N.B. Il nome `NAME` deve essere senza trattini.
2. **Creiamo il file `db.json`:**
    ```json
    [
        {"name": "red", "red": 255, "green": 0, "blue": 0},
        {"name": "green", "red": 0, "green": 255, "blue": 0},
        {"name": "blue", "red": 0, "green": 0, "blue": 255}
    ]
    ```
3. **Creiamo il database Firestone in Gcloud Platform: [link](https://console.cloud.google.com/welcome/new?hl=it).**
4. **Creiamo il file `firestone.py`:** usato per gestire la creazione/modifica/eliminazione dei dati Per creare velocemente i file.

    ```python
    from google.cloud import firestore
    from datetime import datetime
    import json

    DB_NAME = None #MODIFICA

    class FirestoreManager(object):
        
        def __init__(self):
            # Inizializza il client. Se DB_NAME è None, usa il default.
            if DB_NAME:
                self.db = firestore.Client(database=DB_NAME)
            else:
                self.db = firestore.Client()

        def add_element(self, collection_name, document_id, data_dict):
            """
            Salva o sovrascrive un documento.
            collection_name: nome della collezione (es. 'letture' o 'bollette')
            document_id: chiave primaria (es. '01-01-2023' o '01-2023')
            data_dict: dizionario con i dati { 'valore': 100, 'costo': 50 }
            """
            ref = self.db.collection(collection_name).document(str(document_id))
            ref.set(data_dict)

        def get_element(self, collection_name, document_id):
            """Recupera un singolo documento"""
            doc_ref = self.db.collection(collection_name).document(str(document_id))
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None

        def get_all_elements(self, collection_name):
            """Ritorna una lista di dizionari contententi anche l'ID."""
            collection_ref = self.db.collection(collection_name)
            results = []
            for doc in collection_ref.stream():
                data = doc.to_dict()
                data['id'] = doc.id  # Aggiungo l'ID al dizionario dati per comodità
                results.append(data)
            return results

        # --- PULIZIA DATABASE ---

        def clean_db(self):
            """Cancella TUTTE le collezioni nel database"""
            collections = self.db.collections()
            for collection in collections:
                self.clean_collection(collection.id)

        def clean_collection(self, collection_name):
            """Svuota una singola collezione"""
            docs = self.db.collection(collection_name).stream()
            for doc in docs:
                doc.reference.delete()

        # --- POPOLAMENTO INIZIALE ---
        def populate_from_json(self, filename, collection_target):
            try:
                with open(filename, 'r') as f:
                    data_list = json.load(f)
                    for item in data_list:
                        # Assumiamo che nel JSON ci sia un campo 'id' da usare come chiave
                        doc_id = item.pop('id', None) 
                        if doc_id:
                            self.add_element(collection_target, doc_id, item)
            except FileNotFoundError:
                print(f"File {filename} non trovato, salto il popolamento.")


    if __name__ == '__main__':
        db = FirestoreManager()
        db.populate_from_json('db.json',collection_name)
    ```
---        
# 3. RESTful API
Dalla lettura del file **`dettagli_api.yaml`** fornito, estraiamo:
- Le **risorse (endpoints)** disponibili.
- I **metodi HTTP** da implementare per ciascuna risorsa e i relativi **codici di risposta**.
- La **struttura dei dati di input e output**, definita nella sezione **definitions**, ad esempio tramite il riferimento.**`$ref: "#/definitions/Prenotazione"`**, che descrive i campi obbligatori e il loro formato.
- I **parametri richiesti** (nel path, query, header o body) e i relativi tipi.

## 3.1. Steps
1. **File `api.py`:**
   
    ```python
    from flask import Flask, request
    from flask_restful import Resource, Api
    from file_firestone import *
    from flask_cors import CORS
    import re

    app = Flask(__name__)
    CORS(app)
    api=Api(app)
    base_path='/api/v1'

    database_firestone = Classe_firestore() #DA MODIFICARE 

    class FirstResource(Resource):
        
        # Per ottenere una risorsa
        def get(self, colorName): 
            #color = colors_dao.get_method() #questo intercetta le informazioni dentro il json della richiesta
            return None,[200,400]
            
        # Crea una nuova risorsa
        def post(self, colorname): 
            request_info = request.json
            #PARAM = request_info.get("PARAM")
            return None,[200,400]
            
        # Aggiorna una risorsa specifica 
        def put(self, colorname): 
            request_info =request.json
            #PARAM = request_info.get("PARAM")
            return None,[200,400]
            
            
    #Per ciascuna classe eseguiamo il collegamento con il path corretto all'esterno della classe indicando il nome del parametro (se presente nel path).
    api.add_resource(FirstResource, f'{base_path}/colors/<string:colorName>')


    #Ecco un esempio in cui il path possiede solamente un metodo e non è presente alcun parametro:
    class SecondResource(Resource):
        def get(self):
            return colors_dao.get_colors(), 200
            
    api.add_resource(ColorList, f'{base_path}/colors')

    #Per fare debug in locale
    """
    if __name__=='__main__':
        app.run(host="localhost", port=8080, debug=True)
    """
    ```
    **N.B.** Per ogni path definito nel file yaml definisco una classe.
2. **File `api.yaml`:**
    ```yaml
    runtime: python313
    service: default
    entrypoint: gunicorn api:app
    instance_class: F1
    automatic_scaling:
    max_instances: 1

    handlers:
    - url: /static
    static_dir: static
    - url: /.*
    secure: always
    script: auto
    ```
    **N.B.** `gunicorn api:app` → avvia Gunicorn usando l’oggetto `app` che si trova nel file `api.py`.
    
    **N.B.** Se è il **primo file `.yaml`** che crei per il progetto, devi specificare `service: default`. Se invece stai creando un secondo **servizio** (ad esempio per le API), puoi specificare `service: api`.
3. **Debug:** per testare e fare debug dell’API si può usare [SwaggerEditor](https://editor.swagger.io/). È sufficiente **copiare il file OpenAPI (YAML) fornito dal professore** e incollarlo nell’editor per visualizzare la documentazione e testare gli endpoint.
    - **In locale** → usare **`HTTP`** invece di `HTTPS` e impostare `host: "localhost:8080”`.
    - **In cloud** → impostare `host:"api-dot-nomeprogetto.appspot.com"`, `api-dot-` va usato solo se il servizio non è quello di default.
4. **Deploy:**
    
    ```bash
    gcloud app deploy api.yaml
    ```
---

$\color{red}{\text{Questo è testo rosso puro}}$

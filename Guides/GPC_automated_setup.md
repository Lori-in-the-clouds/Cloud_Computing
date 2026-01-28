# Lab RestFUL - Google Cloud Platform
## 1. Setup
1. Per settare rapidamente tutti i file necessari, utilizziamo lo script presnete nel file `init_gcp.py`:
    ```python
    import os

    # ==============================================================================
    # DEFINIZIONE DEI CONTENUTI DEI FILE
    # ==============================================================================

    # 1. requirements.txt (Dal punto 4 del README_GCP.md)
    CONTENT_REQUIREMENTS = """Flask==3.1.2
    flask-cors==6.0.2
    Flask-RESTful==0.3.9
    google-cloud-firestore==2.22.0
    gunicorn==23.0.0
    WTForms==3.0.1
    email-validator==2.3.0
    python-dateutil==2.9.0.post0
    google-cloud-pubsub==2.34.0
    PyYAML==6.0.3
    requests==2.32.5
    """

    # 2. .gcloudignore (Dal punto 6 del README_GCP.md)
    CONTENT_GCLOUDIGNORE = """.git
    .gitignore

    credentials.json
    __pycache__/

    .venv/
    /setup.gfc
    .pdf
    """

    # 3. app.yaml (Standard App Engine Python 3.9)
    CONTENT_APP_YAML = """runtime: python313

    instance_class: F1
    automatic_scaling:
        max_instances: 1

    entrypoint: gunicorn main:app
    service: web

    handlers:
    - url: /static
    static_dir: static
    - url: /.*
    secure: always
    script: auto
    """

    # 4. api.yaml (Placeholder standard)
    CONTENT_API_YAML = """runtime: python313
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
    """

    # 5. db.json (NUOVO: Dati di esempio per test locali o seed)
    CONTENT_DB_JSON = """[
        {"id": "red", "red": 255, "green": 0, "blue": 0},
        {"id": "green", "red": 0, "green": 255, "blue": 0},
        {"id": "blue", "red": 0, "green": 0, "blue": 255}
    ]
    """

    # 6. time_utils.py (Dalla Sezione 5 del README_GCP.md)
    CONTENT_TIME_UTILS = '''from datetime import datetime, time, timedelta
    from dateutil.relativedelta import relativedelta
    import calendar

    # =============================================================================
    # SEZIONE 1: CONVERSIONI BASE (Stringa <-> Oggetto)
    # =============================================================================

    def from_date_to_string(d: datetime) -> str:
        """Converte oggetto datetime in stringa 'gg-mm-YYYY'"""
        return d.strftime("%d-%m-%Y")

    def from_string_to_date(d_str: str) -> datetime | None:
        """Converte stringa 'gg-mm-YYYY' in oggetto datetime"""
        try:
            return datetime.strptime(d_str, "%d-%m-%Y")
        except (ValueError, TypeError):
            return None

    def from_time_to_string(t: time) -> str:
        """Converte oggetto time in stringa 'HH:MM'"""
        return t.strftime("%H:%M")

    def from_string_to_time(t_str: str) -> time | None:
        """Converte stringa 'HH:MM' in oggetto time"""
        try:
            return datetime.strptime(t_str, "%H:%M").time()
        except (ValueError, TypeError):
            return None

    def from_month_to_string(m: datetime) -> str:
        """Converte oggetto datetime in stringa 'MM-YYYY'"""
        return m.strftime("%m-%Y")

    def from_string_to_month(m_str: str) -> datetime | None:
        """Converte stringa 'MM-YYYY' in oggetto datetime"""
        try:
            return datetime.strptime(m_str, "%m-%Y")
        except (ValueError, TypeError):
            return None
        
    # =============================================================================
    # SEZIONE 2: LISTE E RANGE DI DATE
    # =============================================================================

    def get_past_dates(days: int, exclude_today: bool = False) -> list[str]:
        """
        Restituisce una lista di date (stringhe) passate.
        :param days: numero di giorni da recuperare
        :param exclude_today: se True, parte da ieri
        """
        today = datetime.today()
        start = 1 if exclude_today else 0
        return [
            (today - timedelta(days=i)).strftime("%d-%m-%Y")
            for i in range(start, start + days)
        ]

    def giorni_della_settimana(data: datetime = datetime.today()) -> list[str]:
        """Restituisce la lista dei 7 giorni (stringhe) della settimana della data fornita"""
        inizio_settimana = data - timedelta(days=data.weekday()) # Lunedì
        return [
            (inizio_settimana + timedelta(days=i)).strftime("%d-%m-%Y")
            for i in range(7)
        ]

    def giorni_del_mese(data: datetime = datetime.today()) -> list[str]:
        """Restituisce la lista di tutti i giorni (stringhe) del mese della data fornita"""
        num_giorni = calendar.monthrange(data.year, data.month)[1]
        inizio_mese = data.replace(day=1)
        return [
            (inizio_mese + timedelta(days=i)).strftime("%d-%m-%Y")
            for i in range(num_giorni)
        ]

    def primo_e_ultimo_giorno_del_mese(data: datetime = datetime.today()) -> tuple[str, str]:
        """Restituisce una tupla (primo_giorno, ultimo_giorno) come stringhe"""
        giorni = giorni_del_mese(data)
        return giorni[0], giorni[-1]

    # =============================================================================
    # SEZIONE 3: OPERAZIONI MATEMATICHE E LOGICA
    # =============================================================================

    def somma_giorni(data_str: str, giorni: int) -> str:
        """Aggiunge n giorni a una data stringa"""
        d = from_string_to_date(data_str)
        if d:
            return from_date_to_string(d + timedelta(days=giorni))
        return data_str

    def somma_mesi(data_str: str, mesi: int) -> str:
        """Aggiunge n mesi a una data stringa (richiede dateutil)"""
        d = from_string_to_date(data_str)
        if d:
            nuovo = d + relativedelta(months=mesi)
            return from_date_to_string(nuovo)
        return data_str

    def somma_ore_minuti(orario_str: str, ore: int = 0, minuti: int = 0) -> str:
        """Aggiunge ore e minuti a un orario stringa HH:MM"""
        t_obj = datetime.strptime(orario_str, "%H:%M") # Uso datetime fittizio
        nuovo = t_obj + timedelta(hours=ore, minutes=minuti)
        return nuovo.strftime("%H:%M")

    def calculate_end_time(start_time_str: str, duration_minutes: int) -> str | None:
        """
        Calcola l'orario di fine.
        Gestisce automaticamente il cambio di giornata (es. 23:00 + 120min -> 01:00).
        """
        try:
            # Trucco: Creiamo un datetime fittizio con la data di oggi e l'ora data
            dt_start = datetime.strptime(start_time_str, "%H:%M")
            dt_end = dt_start + timedelta(minutes=int(duration_minutes))
            return dt_end.strftime("%H:%M")
        except (ValueError, TypeError):
            return None

    def overlap(t1_str: str, durata_1: int, t2_str: str, durata_2: int) -> bool:
        """Verifica se due intervalli temporali si sovrappongono"""
        def to_minutes(hhmm: str) -> int:
            try:
                h, m = map(int, hhmm.split(":"))
                return h * 60 + m
            except: return 0
        
        start1 = to_minutes(t1_str)
        end1 = start1 + int(durata_1)
        
        start2 = to_minutes(t2_str)
        end2 = start2 + int(durata_2)
        
        # Logica di sovrapposizione standard
        return max(start1, start2) < min(end1, end2)

    # =============================================================================
    # SEZIONE 4: ORDINAMENTO
    # =============================================================================

    def ordina_date(lista_date: list[str], crescente: bool = True) -> list[str]:
        """Ordina lista di date formato 'gg-mm-YYYY'"""
        return sorted(
            lista_date,
            key=lambda d: datetime.strptime(d, "%d-%m-%Y"),
            reverse=not crescente
        )

    def ordina_mesi(lista_mesi: list[str], crescente: bool = True) -> list[str]:
        """Ordina lista di mesi formato 'mm-YYYY'"""
        return sorted(
            lista_mesi,
            key=lambda d: datetime.strptime(d, "%m-%Y"),
            reverse=not crescente
        )

    def ordina_ore_minuti(lista_orari: list[str], crescente: bool = True) -> list[str]:
        """Ordina lista di orari formato 'HH:MM'"""
        return sorted(
            lista_orari,
            key=lambda t: datetime.strptime(t, "%H:%M"),
            reverse=not crescente
        )

    # =============================================================================
    # SEZIONE 5: UTILITY VARIE E FORMATTAZIONE
    # =============================================================================

    def giorno_della_settimana_it(data_str: str) -> str:
        """Restituisce il nome del giorno in italiano (es. 'Lunedì')"""
        data = from_string_to_date(data_str)
        if not data: return ""
        giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        return giorni[data.weekday()]

    def da_ddmmyyyy_a_yyyymmdd(data_str: str) -> str:
        """Converte '10-05-2025' -> '2025-05-10' (Utile per input HTML date)"""
        d = from_string_to_date(data_str)
        return d.strftime("%Y-%m-%d") if d else ""

    def da_yyyymmdd_a_ddmmyyyy(data_str: str) -> str:
        """Converte '2025-05-10' -> '10-05-2025' (Da input HTML a formato interno)"""
        try:
            d = datetime.strptime(data_str, "%Y-%m-%d")
            return d.strftime("%d-%m-%Y")
        except:
            return ""
    '''

    # 7. api.py (Blueprint e Risorse RESTful)
    CONTENT_API_PY = '''from flask import Flask, request
    from flask_restful import Resource, Api
    from file_firestone import *
    from time_utils import *
    from flask_cors import CORS
    import re

    app = Flask(__name__)
    CORS(app)
    api=Api(app)
    base_path='/api/v1'

    db_firestone = FirestoreManager()

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
    """
    class SecondResource(Resource):
        def get(self):
            return colors_dao.get_colors(), 200
            
    api.add_resource(ColorList, f'{base_path}/colors')
    """

    #Per fare debug in locale
    """
    if __name__=='__main__':
        app.run(host="localhost", port=8080, debug=True)
    """
    '''

    # 8. main.py (Entry point + Web App)
    CONTENT_MAIN = '''from flask import Flask, render_template, request, redirect
    from file_firestone import *
    from wtforms import DateField, EmailField, Form, StringField, IntegerField, SubmitField, validators
    from time_utils import *

    #Creiamo applicazione web
    app = Flask(__name__)
    db_firestone = FirestoreManager()

    #Trasformare un dizionario in un oggetto con attributi. Tipo color.red
    class Struct:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    """
    Per utilizzare i WTForm dichiariamo una classe che eredita da Form in cui spefichiamo i nomi e la tipologia di field 
    e validators per i dati che saranno inseriti al loro interno.
    """
    class FirstForm(Form):
        name = StringField('Name', [validators.DataRequired()])
        valore = IntegerField('Valore', [validators.NumberRange(min=0, max=1000)])
        data = DateField('Data', format='%Y-%m-%d') 
        email = EmailField('Email', [validators.Email()])
        submit = SubmitField('Salva Modifiche')
        
    """
    Definiamo quindi le funzioni che gestiscono i metodi dell'applicazione (GET, POST, PUT, DELETE). 
    Ogni funzione dichiara che tipo di metodi può gestire attraverso `methods=[LISTA_METODI]. 
    La funzione dovrà poi eseguire un return sul render del template HTML inserendo come parametri quelli richiesti da quello specifico template.
    """
    @app.route('/path', methods=['GET']) 
    def nome_della_funzione():
        return render_template("FILE.HTML", NOME_PARAMETRO="PARAMETRO")
        
    """
    Il secondo path che dobbiamo gestire risulta essere variabile poiché è presente un parametro dopo una parte che che rimane costante /path/<PARAM>. 
    Questo dovrà essere inserito come parametro della nostra funzione (scritto nello stesso modo) in modo da poterlo utilizzare.
    """
    @app.route('/path/<PARAM>', methods=['GET', 'POST'])
    def nome_della_funzione(PARAM):
        if request.method == 'POST':
            cform = FirstForm(request.form)

            if cform.validate():
                db.add_element("COLLECTION_NAME", cform.name.data, "dati_da_salvare")
                return redirect("/path/" + cform.name.data, code=302)
        
        element = db_firestone.get_element_by_name(PARAM)

        if request.method == 'GET':
            cform=FirstForm(obj=Struct(**element))
            cform.name.data = PARAM
        return render_template("FILE.HTML", NOME_PARAMETRO="PARAMETRO")

    #Per fare debug in locale
    """
    if __name__=='__main__':
        app.run(host="localhost", port=8080, debug=True)
    """
    '''


    CONTENT_FILE_FIRESTONE='''from google.cloud import firestore
    from datetime import datetime
    from time_utils import *
    import json

    DB_NAME = None #MODIFICA

    class FirestoreManager(object):
        
        def __init__(self):
            # Inizializza il client. Se DB_NAME è None, usa il default.
            if DB_NAME:
                self.db = firestore.Client(database=DB_NAME)
            else:
                print("Attenzione: nessun database specificato, uso il default.")

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
            for collection in self.db.collections():
                for doc in collection.stream():
                    doc.reference.delete()

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
        db.populate_from_json('db.json',collection_target="COLLECTION_NAME")
    '''

    # ==============================================================================
    # FUNZIONE DI GENERAZIONE
    # ==============================================================================

    def init_project():
        base_dir = os.getcwd()
        print(f"--- Generazione struttura progetto in: {base_dir} ---")

        # 1. Creazione Cartelle
        folders = ["templates"]
        for folder in folders:
            path = os.path.join(base_dir, folder)
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"[OK] Cartella '{folder}' creata.")
        
        # 2. Creazione File
        files_to_create = {
            "requirements.txt": CONTENT_REQUIREMENTS,
            ".gcloudignore": CONTENT_GCLOUDIGNORE,
            "app.yaml": CONTENT_APP_YAML,
            "api.yaml": CONTENT_API_YAML,
            "db.json": CONTENT_DB_JSON, 
            "time_utils.py": CONTENT_TIME_UTILS,
            "api.py": CONTENT_API_PY,
            "main.py": CONTENT_MAIN,
            "file_firestone.py": CONTENT_FILE_FIRESTONE
        }

        for filename, content in files_to_create.items():
            path = os.path.join(base_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[OK] File '{filename}' creato.")

        print("\n--- SETUP COMPLETATO ---")
        print("File creati correttamente, incluso db.json.")

    if __name__ == "__main__":
        init_project()
    ```
---
2. **Controlla quale profilo hai attivo su vsCode**
3. **Creiamo e settiamo l'ambiente virtuale:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r ./requirements.txt
    ```
4. **Creiamo il progetto e l'applicazione Gcloud:**
   ```bash
    export PROJECT_ID=<project_name>
    ```
    ```bash
    gcloud projects create ${PROJECT_ID} --set-as-default
    ```
5.  **Linkiamo il billing account:**
   
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
6.  **Creiamo l'applicazione:**
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
    **$\color{red}{\text{N.B.}}$** Il nome `NAME` deve essere senza trattini.
2. **Creiamo il file `db.json`:**
    ```json
    [
        {"id": "red", "red": 255, "green": 0, "blue": 0},
        {"id": "green", "red": 0, "green": 255, "blue": 0},
        {"id": "blue", "red": 0, "green": 0, "blue": 255}
    ]
    ```
3. **Creiamo il database Firestone in Gcloud Platform: [link](https://console.cloud.google.com/welcome/new?hl=it).**
4. **Creiamo il file `file_firestone.py`:** usato per gestire la creazione/modifica/eliminazione dei dati Per creare velocemente i file.

    ```python
    from google.cloud import firestore
    from datetime import datetime
    from time_utils import *
    import json

    DB_NAME = None #MODIFICA

    class FirestoreManager(object):
        
        def __init__(self):
            # Inizializza il client. Se DB_NAME è None, usa il default.
            if DB_NAME:
                self.db = firestore.Client(database=DB_NAME)
            else:
                print("Attenzione: nessun database specificato, uso il default.")

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
            for collection in self.db.collections():
                for doc in collection.stream():
                    doc.reference.delete()

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
        db.populate_from_json('db.json',collection_target="COLLECTION_NAME")
    ```
---        
# 3. RESTful API
Dalla lettura del file **`dettagli_api.yaml`** fornito, estraiamo:
- Le **risorse (endpoints)** disponibili.
- I **metodi HTTP** da implementare per ciascuna risorsa e i relativi **codici di risposta**.
- La **struttura dei dati di input e output**, definita nella sezione **definitions**, ad esempio tramite il riferimento.**`$ref:"#/definitions/Prenotazione"`**, che descrive i campi obbligatori e il loro formato.
- I **parametri richiesti** (nel path, query, header o body) e i relativi tipi.

## 3.1. Steps
1. **File `api.py`:**
   
    ```python
    from flask import Flask, request
    from flask_restful import Resource, Api
    from file_firestone import *
    from time_utils import *
    from flask_cors import CORS
    import re

    app = Flask(__name__)
    CORS(app)
    api=Api(app)
    base_path='/api/v1'

    db_firestone = FirestoreManager()

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
    """
    class SecondResource(Resource):
        def get(self):
            return colors_dao.get_colors(), 200
            
    api.add_resource(ColorList, f'{base_path}/colors')
    """

    #Per fare debug in locale
    """
    if __name__=='__main__':
        app.run(host="localhost", port=8080, debug=True)
    """
    ```
    **$\color{red}{\text{N.B.}}$** Per ogni path definito nel file yaml definisco una classe.
    
    Per filtrare la lista di dizionari in base al valore di una key:
    ```python
    l_filtered = [elem for elem in l if elem['id'].split('_')[0] == data]
    ```
    Per creare una lista di dizionari utilizzando solo alcuni campi:
     ```python
    l_ordini = [
        {
            "asilo": item["id"].split("_", 1)[1], 
            "bambini": item["bimbi"]
        } 
        for item in l_filtered 
    ]
    ```   

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
    **$\color{red}{\text{N.B.}}$** `gunicorn api:app` → avvia Gunicorn usando l’oggetto `app` che si trova nel file `api.py`.
    
   **$\color{green}{\text{N.B.}}$** Se è il **primo file `.yaml`** che crei per il progetto, devi specificare `service: default`. Se invece stai creando un secondo **servizio** (ad esempio per le API), puoi specificare `service: api`.
3. **Debug:** per testare e fare debug dell’API si può usare [SwaggerEditor](https://editor.swagger.io/). È sufficiente **copiare il file OpenAPI (YAML) fornito dal professore** e incollarlo nell’editor per visualizzare la documentazione e testare gli endpoint.
    - **In locale** → usare **`HTTP`** invece di `HTTPS` e impostare `host: "localhost:8080”`.
    - **In cloud** → impostare `host:"api-dot-nomeprogetto.appspot.com"`, `api-dot-` va usato solo se il servizio non è quello di default.
4. **Deploy:**
    
    ```bash
    gcloud app deploy api.yaml
    ```
---
# 4. Web Application 
L'obiettivo è quello di creare un'interfaccia web per visualizzare i dati all'interno del database. Per poter eseguire il deployment di questa web app dobbiamo creare i seguenti file: 
* `templates/` → cartella in cui raggruppiamo tutti i template HTML
* `static/` → cartella in cui raggruppiamo tutti i file statici
* `main.py` → usato per gestire tutta l'applicazione
* `app.yaml` → usato per definire il deployment su gcloud
## 4.1. Steps
1. **Creiamo i file html nella directory `templates/`:**
    ```html
    <!DOCTYPE html>
    <html lang="it">
        <head>
            <h1>Titolo</h1>
            <meta charset="UTF-8">
            <link rel="stylesheet" href="/static/color.css">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"> 
        </head>
    
        <body>
                
        
            
        </body>
    </html>
    ```
    **$\color{red}{\text{N.B.}}$** Per utilizzare parametri `{{…}}`.

    **Parti utili html:**
    * Lista non ordinata:
  
        ```html
        <ul>
            <li>Pane</li>
            <li>Latte</li>
            <li>Uova</li>
        </ul>
        ```
    
    * If:
    
        ```html
        <ul>
            {% if c['data'] == giorno_corrente %}
            {% else %}
            {% endif %}
        </ul>
        ```
    * Loop:
        ```html
        <ul>
            {% for c in LIST_PARAM %}
                <li><a href="/PATH/{{c}}">{{c}}</a></li>
            {% endfor %}
        </ul>
        ```
    * Testo linkabile:

        ```html
        <a href="/PATH/0">Link 0</a>
        ```
    * Tabella:
        ```html
        <table class="table">
            <thead>
                <!-- Nomi delle colonne -->
                <tr>
                <th>Nome</th>
                <th>Età</th>
                <th>Città</th>
                </tr>
                
            </thead>

            <tbody>
                <!-- Prima riga -->
                <tr>
                <td>Lorenzo</td>
                <td>25</td>
                <td>Roma</td>
                </tr>
                <!-- Seconda riga -->
                <tr>
                <td>Marco</td>
                <td>30</td>
                <td>Milano</td>
                </tr>
            </tbody>
        </table>
        ```
    * Form:
        ```html
        <form method="POST">
            <table>
            <tr><td>{{cform.name.label}}</td><td>{{cform.name}}</td></tr>
            <tr><td>{{cform.red.label}}</td><td>{{cform.red}}</td></tr>
            <tr><td>{{cform.green.label}}</td><td>{{cform.green}}</td></tr>
            <tr><td>{{cform.blue.label}}</td><td>{{cform.blue}}</td></tr>
            <tr><td></td><td>{{cform.submit}}</td></tr>
        </table>
        </form>
        ```
    * Multi Form:
        ```html
        <form method="POST" name="rform" action="/secretsanta/classeform">
            Inserisci nome, cognome, email per unirti al secret santa:
            <div>{{rform.firstName.label}}: {{rform.firstName}}</div>
            <div>{{rform.lastName.label}}: {{rform.lastName}}</div>
            <div>{{rform.email.label}}: {{rform.email}}</div>
            <button>{{rform.submit}}</button>
        </form>

        <form method="POST" name="fform" action="/secretsanta/registration">
            Per sapere a chi dovrai fare il regalo inserisci la tua email:
            <div>{{fform.email.label}}: {{fform.email}}</div>
            <button>{{fform.submit}}</button>
        </form>
        ```
    * Box Colorata:
        ```html
        <table class="table">
            <tbody>
                <tr><td><div class="colorbox"style="width: 300px; height: 300px; background-color: rgb({{cform.red.data}}, {{cform.green.data}}, {{cform.blue.data}});"></div></td></tr>
            </tbody>
        </table>
        ```
    **$\color{red}{\text{N.B.}}$** Per altre strutture consulatare la documentazione di bootstrap [link](https://getbootstrap.com/docs/5.3/getting-started/introduction/).
   
    
2. **File `main.py`:**
    ```python
    from flask import Flask, render_template, request, redirect
    from file_firestone import *
    from wtforms import DateField, EmailField, Form, StringField, IntegerField, SubmitField, validators
    from time_utils import *

    #Creiamo applicazione web
    app = Flask(__name__)
    db_firestone = FirestoreManager()

    #Trasformare un dizionario in un oggetto con attributi. Tipo color.red
    class Struct:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    '''
    Per utilizzare i WTForm dichiariamo una classe che eredita da Form in cui spefichiamo i nomi e la tipologia di field 
    e validators per i dati che saranno inseriti al loro interno.
    '''
    class FirstForm(Form):
        name = StringField('Name', [validators.DataRequired()])
        valore = IntegerField('Valore', [validators.NumberRange(min=0, max=1000)])
        data = DateField('Data', format='%Y-%m-%d') 
        email = EmailField('Email', [validators.Email()])
        submit = SubmitField('Salva Modifiche')
        
    '''
    Definiamo quindi le funzioni che gestiscono i metodi dell'applicazione (GET, POST, PUT, DELETE). 
    Ogni funzione dichiara che tipo di metodi può gestire attraverso `methods=[LISTA_METODI]. 
    La funzione dovrà poi eseguire un return sul render del template HTML inserendo come parametri quelli richiesti da quello specifico template.
    '''
    @app.route('/path', methods=['GET']) 
    def nome_della_funzione():
        return render_template("FILE.HTML", NOME_PARAMETRO="PARAMETRO")
        
    '''
    Il secondo path che dobbiamo gestire risulta essere variabile poiché è presente un parametro dopo una parte che che rimane costante /path/<PARAM>. 
    Questo dovrà essere inserito come parametro della nostra funzione (scritto nello stesso modo) in modo da poterlo utilizzare.
    '''
    @app.route('/path/<PARAM>', methods=['GET', 'POST'])
    def nome_della_funzione(PARAM):
        if request.method == 'POST':
            cform = FirstForm(request.form)

            if cform.validate():
                db.add_element("COLLECTION_NAME", cform.name.data, "dati_da_salvare")
                return redirect("/path/" + cform.name.data, code=302)
        
        element = db_firestone.get_element_by_name(PARAM)

        if request.method == 'GET':
            cform=FirstForm(obj=Struct(**element))
            cform.name.data = PARAM
        return render_template("FILE.HTML", NOME_PARAMETRO="PARAMETRO")

    #Per fare debug in locale
    """
    if __name__=='__main__':
        app.run(host="localhost", port=8080, debug=True)
    """
   ```
* **File `app.yaml`:**
    ```yaml
    runtime: python313

    instance_class: F1
    automatic_scaling:
        max_instances: 1

    entrypoint: gunicorn main:app
    service: web

    handlers:
    - url: /static
      static_dir: static
    - url: /.*
      secure: always
      script: auto
    ```
* **Deploy:**
  ```bash
  gcloud app deploy app.yaml
    ```
---
# 6. Function
Le function sono delle Action che vengono eseguite in risposta al verificarsi di un determinato Event. Affinché un evento determini esecuzione di una funzione, questo deve essere stato collegato tramite un Trigger. Il nostro obiettivo sarà quello di creare la funzione (action) e collegarla tramite un trigger all'osservazione di uno specifico evento.

Si devono quindi creare i seguenti file all’interno della directory `func_stat/`:
* **`requirements.txt`:**

    ```
    google-cloud-firestore==2.22.0 
    flask==2.3.3
    ```
* **`.gcloudignore`:**
  
    ```
    .git
    .gitignore

    __pycache__/
    .venv/

    /setup.cfg
    credentials.json
    ```
* **`main.py`:** possiamo avere due tipologie:
  * **HTTP Function**: questo tipo di function accetta solamente un oggetto `request` e restituisce un valore (tipicamente `string` o `HTML`). Tutte le informazioni sulla richiesta (metodo, URL, headers, body, query params, ecc.) sono contenute in request.
    ```python
    from flask import Flask, request

    db = firestore.Client(database="NOME_DATABASE")

    def HTTP_FUNCTION(request):
        if request.method == 'GET':
            path = request.path
            pages = path.split('/')
            return 'STRING'
    ```
  * **Event-driven Function (Gen 1):** questo tipo di function accetta due parametri `data` e `context` e sono utilizzate solitamente da eventi come Pub/Sub o Firestore. In particolare il parametro `data` contiene:
    ```json
    {
    "oldValue": {}, 

        "value": {
            "createTime": "2025-01-10T10:00:00.000Z",
            "fields": {
            "bambini": {
                "integerValue": "25" 
            },
            "nome_asilo": {
                "stringValue": "AsiloRossi"
            }
            },
            "name": "projects/mensa-esame/databases/mensa/documents/prenotazioni/AsiloRossi_2025-10-10",
            "updateTime": "2025-01-10T10:00:00.000Z"
    },

    "updateMask": {
        "fieldPaths": [ "bambini" ]
    }
    }
    ```

    ```python
    from flask import Flask, render_template, request, redirect
    from google.cloud import firestore
    from datetime import datetime, timedelta

    def update_db(data, context): 
        db = firestore.Client(database="mensa")

        document_name = context.resource.split("/")[-1]

        new_value = data['value'] if len(data["value"]) != 0 else None
        old_value = data['oldValue'] if len(data["oldValue"]) !=0 else None
        if new_value and not old_value: # document added
            pass
        elif not new_value and old_value: # document removed
            pass
        else: # document updated
            pass
    ```
    **$\color{red}{\text{N.B.}}$** Il metodo .params["KEY"] viene usato per accedere al dizionario creato dall'uso delle wildcard (.../temp/{day} → usiamo 'day' come KEY), mentre grazie .resource.split('/')[-1] possiamo ottenere dal path completo il nome del documento.



## 6.1. Deploy
**Tutti** i seguenti comandi saranno da eseguire mentre ci troviamo all'interno della cartella **`func_stat/`:**

1. **Verifichiamo che le variabili d'ambiente `PROJECT_ID` e `NAME` siano ancora valide** (`NAME` deve essere uguale a quello utilizzato precedentemente):
    
    ```bash
    echo PROJECT_ID = ${PROJECT_ID}
    echo NAME = ${NAME}
    ```
    
2. **Creiamo le credenziali e le salviamo in `credentials.json`:**
    
    ```bash
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:${NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/owner"
    touch credentials.json 
    gcloud iam service-accounts keys create credentials.json --iam-account ${NAME}@${PROJECT_ID}.iam.gserviceaccount.com 
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
    gcloud services enable cloudfunctions.googleapis.com
    ```
 
3. **Il procedimento del deployment da qui in avanti è specifico rispetto al tipo di Function:**
    - **HTTP Function:**
        1. Definiamo il nome della funzione che dovrà essere invocata dalla richiesta HTTP:
            
            ```bash
            export FUNCTION=NOME_FUNZIONE
            ```
            
        2. Definiamo il runtime:
            
            ```bash
            export RUNTIME=python310
            ```
            
        3. Deploy:
            
            ```bash
            gcloud functions deploy ${FUNCTION} \
              --runtime ${RUNTIME} \
              --trigger-http \
              --allow-unauthenticated \
              --docker-registry=artifact-registry \
              --no-gen2
            ```
            
        4. Per eseguire il testing possiamo utilizzare l'indirizzo HTTP della funzione a cui aggiungiamo il path che vogliamo verificare. Usando il seguente comando possiamo ottenere una descrizione della function che contiene anche il suo indirizzo HTTP.
            
            ```bash
            gcloud functions describe $FUNCTION
            ```
            
    - **Event driven Function:**
        1. Definiamo le seguenti variabili globali:
            
            ```bash
            export FUNCTION=NOME_FUNZIONE
            export RUNTIME=python310
            ```
            
            ```bash
            export DATABASE=NOME_DATABASE
            ```
            
            ```bash
            export COLLECTION=COLLECTION_NAME
            ```
            
        2. Controlliamo di aver settato correttamente tutte le variabili globali:
            
            ```bash
            echo $COLLECTION
            echo $DATABASE
            echo $FUNCTION 
            echo $RUNTIME
            ```
            
        3. Deploy della funzione:
            
            ```bash
            gcloud functions deploy "${FUNCTION}" \
              --runtime="${RUNTIME}" \
              --trigger-event="providers/cloud.firestore/eventTypes/document.write" \
              --trigger-resource="projects/${PROJECT_ID}/databases/${DATABASE}/documents/${COLLECTION}/{KEY}" \
              --docker-registry=artifact-registry \
              --no-gen2
            ```
            
            Dove:
            
            - **Con `--trigger-event="...”`  decidiamo che tipi di eventi vogliamo osservare:**
                - `-trigger-event="providers/cloud.firestore/eventTypes/document.create` → quando viene creato un nuovo documento.
                - `-trigger-event="providers/cloud.firestore/eventTypes/document.update` → quando un documento che esiste già viene modificato.
                - `-trigger-event="providers/cloud.firestore/eventTypes/document.delete` → quando viene rimosso un documento.
                - `-trigger-event="providers/cloud.firestore/eventTypes/document.write` → quando un documento viene creato e aggiornato.
            - **Con `projects/[PROJECT_ID]/databases/[DATABASE_ID]/documents/[PATH_AL_DOCUMENTO]` definiamo il path delle risorse da osservare per generare gli eventi.**
                - `PATH_AL_DOCUMENTO` = `.../COLLECTION/NOME_DOC` → andiamo però ad osservare solo quel documento specifico
                - `PATH_AL_DOCUMENTO` = `.../COLLECTION/{NAME}` → per osservare i cambiamenti all'interno di una collection. Dove `NAME` è soltanto un segnaposto e corrisponderà alla **key** del dizionario che verrà usata per ottenere il nome del documento su cui è stato osservato l'evento.
                - `PATH_AL_DOCUMENTO` = `.../{NAME==**}`  → per osservare anche i cambiamenti più in profondità (*utile per le subcollection*)
                
                **$\color{red}{\text{N.B.}}$** Bisogna tenere a mente che l'osservabilità viene comunque sempre fatta sui documenti, ovvero sono sempre loro che determinano lo scatenarsi di un evento.
---
# 7. File `time_utils.py`
```python
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import calendar

# =============================================================================
# SEZIONE 1: CONVERSIONI BASE (Stringa <-> Oggetto)
# =============================================================================

def from_date_to_string(d: datetime) -> str:
    """Converte oggetto datetime in stringa 'gg-mm-YYYY'"""
    return d.strftime("%d-%m-%Y")

def from_string_to_date(d_str: str) -> datetime | None:
    """Converte stringa 'gg-mm-YYYY' in oggetto datetime"""
    try:
        return datetime.strptime(d_str, "%d-%m-%Y")
    except (ValueError, TypeError):
        return None

def from_time_to_string(t: time) -> str:
    """Converte oggetto time in stringa 'HH:MM'"""
    return t.strftime("%H:%M")

def from_string_to_time(t_str: str) -> time | None:
    """Converte stringa 'HH:MM' in oggetto time"""
    try:
        return datetime.strptime(t_str, "%H:%M").time()
    except (ValueError, TypeError):
        return None

def from_month_to_string(m: datetime) -> str:
    """Converte oggetto datetime in stringa 'MM-YYYY'"""
    return m.strftime("%m-%Y")

def from_string_to_month(m_str: str) -> datetime | None:
    """Converte stringa 'MM-YYYY' in oggetto datetime"""
    try:
        return datetime.strptime(m_str, "%m-%Y")
    except (ValueError, TypeError):
        return None
    
# =============================================================================
# SEZIONE 2: LISTE E RANGE DI DATE
# =============================================================================

def get_past_dates(days: int, exclude_today: bool = False) -> list[str]:
    """
    Restituisce una lista di date (stringhe) passate.
    :param days: numero di giorni da recuperare
    :param exclude_today: se True, parte da ieri
    """
    today = datetime.today()
    start = 1 if exclude_today else 0
    return [
        (today - timedelta(days=i)).strftime("%d-%m-%Y")
        for i in range(start, start + days)
    ]

def giorni_della_settimana(data: datetime = datetime.today()) -> list[str]:
    """Restituisce la lista dei 7 giorni (stringhe) della settimana della data fornita"""
    inizio_settimana = data - timedelta(days=data.weekday()) # Lunedì
    return [
        (inizio_settimana + timedelta(days=i)).strftime("%d-%m-%Y")
        for i in range(7)
    ]

def giorni_del_mese(data: datetime = datetime.today()) -> list[str]:
    """Restituisce la lista di tutti i giorni (stringhe) del mese della data fornita"""
    num_giorni = calendar.monthrange(data.year, data.month)[1]
    inizio_mese = data.replace(day=1)
    return [
        (inizio_mese + timedelta(days=i)).strftime("%d-%m-%Y")
        for i in range(num_giorni)
    ]

def primo_e_ultimo_giorno_del_mese(data: datetime = datetime.today()) -> tuple[str, str]:
    """Restituisce una tupla (primo_giorno, ultimo_giorno) come stringhe"""
    giorni = giorni_del_mese(data)
    return giorni[0], giorni[-1]

# =============================================================================
# SEZIONE 3: OPERAZIONI MATEMATICHE E LOGICA
# =============================================================================

def somma_giorni(data_str: str, giorni: int) -> str:
    """Aggiunge n giorni a una data stringa"""
    d = from_string_to_date(data_str)
    if d:
        return from_date_to_string(d + timedelta(days=giorni))
    return data_str

def somma_mesi(data_str: str, mesi: int) -> str:
    """Aggiunge n mesi a una data stringa (richiede dateutil)"""
    d = from_string_to_date(data_str)
    if d:
        nuovo = d + relativedelta(months=mesi)
        return from_date_to_string(nuovo)
    return data_str

def somma_ore_minuti(orario_str: str, ore: int = 0, minuti: int = 0) -> str:
    """Aggiunge ore e minuti a un orario stringa HH:MM"""
    t_obj = datetime.strptime(orario_str, "%H:%M") # Uso datetime fittizio
    nuovo = t_obj + timedelta(hours=ore, minutes=minuti)
    return nuovo.strftime("%H:%M")

def calculate_end_time(start_time_str: str, duration_minutes: int) -> str | None:
    """
    Calcola l'orario di fine.
    Gestisce automaticamente il cambio di giornata (es. 23:00 + 120min -> 01:00).
    """
    try:
        # Trucco: Creiamo un datetime fittizio con la data di oggi e l'ora data
        dt_start = datetime.strptime(start_time_str, "%H:%M")
        dt_end = dt_start + timedelta(minutes=int(duration_minutes))
        return dt_end.strftime("%H:%M")
    except (ValueError, TypeError):
        return None

def overlap(t1_str: str, durata_1: int, t2_str: str, durata_2: int) -> bool:
    """Verifica se due intervalli temporali si sovrappongono"""
    def to_minutes(hhmm: str) -> int:
        try:
            h, m = map(int, hhmm.split(":"))
            return h * 60 + m
        except: return 0
    
    start1 = to_minutes(t1_str)
    end1 = start1 + int(durata_1)
    
    start2 = to_minutes(t2_str)
    end2 = start2 + int(durata_2)
    
    # Logica di sovrapposizione standard
    return max(start1, start2) < min(end1, end2)

# =============================================================================
# SEZIONE 4: ORDINAMENTO
# =============================================================================

def ordina_date(lista_date: list[str], crescente: bool = True) -> list[str]:
    """Ordina lista di date formato 'gg-mm-YYYY'"""
    return sorted(
        lista_date,
        key=lambda d: datetime.strptime(d, "%d-%m-%Y"),
        reverse=not crescente
    )

def ordina_mesi(lista_mesi: list[str], crescente: bool = True) -> list[str]:
    """Ordina lista di mesi formato 'mm-YYYY'"""
    return sorted(
        lista_mesi,
        key=lambda d: datetime.strptime(d, "%m-%Y"),
        reverse=not crescente
    )

def ordina_ore_minuti(lista_orari: list[str], crescente: bool = True) -> list[str]:
    """Ordina lista di orari formato 'HH:MM'"""
    return sorted(
        lista_orari,
        key=lambda t: datetime.strptime(t, "%H:%M"),
        reverse=not crescente
    )

# =============================================================================
# SEZIONE 5: UTILITY VARIE E FORMATTAZIONE
# =============================================================================

def giorno_della_settimana_it(data_str: str) -> str:
    """Restituisce il nome del giorno in italiano (es. 'Lunedì')"""
    data = from_string_to_date(data_str)
    if not data: return ""
    giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    return giorni[data.weekday()]

def da_ddmmyyyy_a_yyyymmdd(data_str: str) -> str:
    """Converte '10-05-2025' -> '2025-05-10' (Utile per input HTML date)"""
    d = from_string_to_date(data_str)
    return d.strftime("%Y-%m-%d") if d else ""

def da_yyyymmdd_a_ddmmyyyy(data_str: str) -> str:
    """Converte '2025-05-10' -> '10-05-2025' (Da input HTML a formato interno)"""
    try:
        d = datetime.strptime(data_str, "%Y-%m-%d")
        return d.strftime("%d-%m-%Y")
    except:
        return ""
```
Per modificare una data partendo da una iniziale utiliziamo: `datetime.replace()`:
```python
data_parziale = data_parziale.replace(year=data_parziale.year + 1,month= 1)
```
---
# 8. Staccare il Billing del Progetto o Eliminarlo
* **Per disattivare il billing:**
    
    ```python
    gcloud billing accounts list
    ```
    
    ```bash
    gcloud billing projects unlink ${PROJECT_ID}
    ```
* **Per eliminare il progetto:**
    
    ```bash
    gcloud projects delete ${PROJECT_ID}
    ```
---
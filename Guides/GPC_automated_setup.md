# Lab RestFUL - Google Cloud Platform
## 1. Setup
1. **Per settare rapidamente tutti i file necessari, utilizziamo lo script presnete nel file `init.py`:**
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
    CONTENT_TIME_UTILS = '''
    
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

    def validate_payload(data, required_fields):
        """
        Controlla se i campi richiesti esistono, se i tipi sono corretti
        e se i valori sono validi.
        """
        for field, expected_type in required_fields.items():
            val = data.get(field)
            
            # 1. Controllo esistenza
            if val is None:
                return False, f"Campo {field} mancante"
            # 2. Controllo tipo (es. int, str, bool)
            if not isinstance(val, expected_type):
                return False, f"Campo {field} deve essere di tipo {expected_type.__name__}"
            # 3. Controlli logici specifici (opzionale)
            if expected_type == int and val < 0:
                return False, f"Campo {field} non può essere negativo"
            # 4. Controllo Email
            if field == "email":
                if not re.match(r"[^@]+@[^@]+\.[^@]+", val):
                    return False, "Email non valida" 
            # 5. Controllo Data
            if field == "date":
                try:
                    datetime.strptime(val, "%d-%m-%Y")
                except ValueError:
                    return False, "Data non valida, formato richiesto gg-mm-YYYY"
                            
                    return True, None   
            # 6. Stringhe non vuote
            if expected_type == str and val.strip() == "":
                return False, f"Campo {field} non può essere vuoto"

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
    def post(self):
        db_firestone.clean_collection("COLLECTION_NAME")
        return None,200
        
    api.add_resource(SecondResource, f'{base_path}/clean')
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
    from wtforms import DateField, EmailField, Form, RadioField, StringField, IntegerField, SubmitField, validators
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
        tipo_scelta = RadioField('Cerca in:', choices=['dumarell', 'cantiere'], default='dumarell')
        submit = SubmitField('Salva Modifiche')
        
    """
    Definiamo quindi le funzioni che gestiscono i metodi dell'applicazione (GET, POST, PUT, DELETE). 
    Ogni funzione dichiara che tipo di metodi può gestire attraverso `methods=[LISTA_METODI]. 
    La funzione dovrà poi eseguire un return sul render del template HTML inserendo come parametri quelli richiesti da quello specifico template.
    """
    @app.route('/path', methods=['GET']) 
    def nome_della_funzione():
        return render_template("FILE.HTML", NOME_PARAMETRO="PARAMETRO")
        
    """Per CERCARE un elemento del database attraverso un FORM HTML"""
    @app.route('/cerca', methods=["GET", "POST"])
    def cerca_elementi():
        # Inizializziamo il form e le variabili di supporto
        cform = FirstForm(request.form)
        risultati = []
        scelta = None

        # AZIONE: L'utente ha premuto il tasto Submit
        if request.method == 'POST' and cform.validate():
            # 1. Recupero parametri dal form
            valore_filtro = cform.cap.data
            collezione = cform.tipo_scelta.data
            scelta = collezione # Per ricordarci cosa stiamo guardando nell'HTML

            # 2. Prendiamo tutto dalla collezione scelta (es. 'umarell' o 'cantiere')
            tutti = db_firestone.get_all_elements(collezione)

            # 3. Filtriamo per il campo 'cap' confrontandolo con quanto inserito dall'utente
            risultati = [item for item in tutti if item.get("cap") == valore_filtro]

        # VISUALIZZAZIONE: Restituiamo sempre lo stesso template
        # In GET: risultati sarà [] e il form sarà vuoto
        # In POST: risultati conterrà i dati filtrati
        return render_template("FILE.html", cform=cform, elements=risultati, tipo=scelta)

    """Per MODIFICARE un elemento preesistente del database attraverso un FORM HTML"""   
    @app.route('/path/<ID_PARAM>', methods=['GET', 'POST'])
    def funzione_modifica(ID_PARAM):
        # 1. Recupero dati dal Database
        # Questa riga serve a caricare i dati attuali per mostrarli nel form
        elemento_esistente = db_firestone.get_element(collection_name="NOME_COLLEZIONE", document_id=ID_PARAM)
        
        # Controllo di sicurezza: se l'ID non esiste, torna alla home o lista
        if not elemento_esistente:
            return redirect("/url_lista_generale")

        # 2. Gestione INVIO DATI (POST)
        if request.method == 'POST':
            cform = FirstForm(request.form)
            if cform.validate():
                # Creiamo il dizionario con i nuovi dati presi dal form
                dati_aggiornati = {
                    "campo1": cform.campo1.data,
                    "campo2": cform.campo2.data,
                    # ... aggiungi tutti i campi necessari ...
                }
                # Sovrascriviamo il documento nel DB usando lo stesso ID
                db_firestone.add_element("NOME_COLLEZIONE", document_id=ID_PARAM, data_dict=dati_aggiornati)
                
                # Redirect dopo il salvataggio per evitare invii doppi (F5)
                return redirect("/path/" + ID_PARAM)

        # 3. Gestione VISUALIZZAZIONE (GET)
        # Pre-compiliamo il form con i dati recuperati dal database al punto 1
        cform = FirstForm(data=elemento_esistente)
        return render_template("FILE.html", cform=cform, id_elemento=ID_PARAM)

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

**➡️ Continua con il Capitolo 2 nella sezione dedicata a Google Cloud Platform: [📂 View Guide](GCP.md#2-configurazione-firestone)**
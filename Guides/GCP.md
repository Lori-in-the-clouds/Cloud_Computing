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
    PyYAML==6.0.3
    requests==2.32.5
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
10. **Generiamo il Service Account e le chiavi IAM per l'autenticazione:**
    ```bash
    export NAME=webuser
    gcloud iam service-accounts create ${NAME}
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member "serviceAccount:${NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role "roles/owner" 
    touch credentials.json 
    gcloud iam service-accounts keys create credentials.json --iam-account ${NAME}@${PROJECT_ID}.iam.gserviceaccount.com 
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
    ```
    **$\color{red}{\text{N.B.}}$** Il nome `NAME` deve essere senza trattini.
---
# 2. Configurazione Firestone
1. **Creiamo il database Firestone in Gcloud Platform: [link](https://console.cloud.google.com/welcome/new?hl=it).**
2. **Creiamo il file `db.json`:**
    ```json
    [
        {"id": "red", "red": 255, "green": 0, "blue": 0},
        {"id": "green", "red": 0, "green": 255, "blue": 0},
        {"id": "blue", "red": 0, "green": 0, "blue": 255}
    ]
    ```
3. **Creiamo il file `file_firestone.py`:** usato per gestire la creazione/modifica/eliminazione dei dati.

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

        def delete_element(self, collection_name, document_id):
            """Elimina un singolo documento dalla collezione specificata. Ritorna True se l'operazione viene inviata correttamente"""
            try:
                doc_ref = self.db.collection(collection_name).document(str(document_id))
                doc_ref.delete()
                return True
            except Exception as e:
                print(f"Errore durante l'eliminazione del documento {document_id}: {e}")
                return False

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

    def validate_payload(data, required_fields):
        """
        Controlla se i campi richiesti esistono, se i tipi sono corretti e se i valori sono validi.
        """
        for field, expected_type in required_fields.items():
            val = data.get(field)
            # 1. Controllo esistenza
            if val is None:
                return False
            # 2. Controllo tipo (es. int, str, bool)
            if not isinstance(val, expected_type):
                return False
            # 3. Controllo Email
            if field == "email":
                if not re.match(r"[^@]+@[^@]+\.[^@]+", val):
                    return False
            return True
    

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
    if __name__=='__main__':
        app.run(host="localhost", port=8080, debug=True)
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
4. **Testing con file `tester_yaml.py`**: avviamo in locale il file `api.py` mentre in un altro terminale avviamo il file `tester_yaml.py`. Assicurati di puntare all’URL corretto della tua API locale nel file `tester_yaml.py`:
     ```python
    if __name__ == "__main__":
    # test = TestEndpoints('https://[YOUR_PROJECT_ID].appspot.com')
    test = TestEndpoints('http://localhost:8080')       
    pprint(test.validate_apis())
    ```
    
5. **Deploy:**
    
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
        {% for c in LIST_PARAM %}
            <li><a href="/PATH/{{c}}">{{c}}</a></li>
        {% endfor %}
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

    * Tabella con `for` innestato:
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
                {% for c in LIST_PARAM %}
                    <tr>
                    <td>{{c.name}}</td>
                    <td>{{c.age}}</td>
                    <td>{{c.city}}</td>
                    </tr>
                {% endfor %}
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
    * Testo Colorato:
        ```html
        <p style="color:red;">{{c.colpevole}}</p>
        ```
    **$\color{red}{\text{N.B.}}$** Per altre strutture consulatare la documentazione di bootstrap [link](https://getbootstrap.com/docs/5.3/getting-started/introduction/).
   
    
2. **File `main.py`:**
    ```python
    from flask import Flask, render_template, request, redirect
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
        return render_template("FILE.html", NOME_PARAMETRO="PARAMETRO")
        
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
    if __name__=='__main__':
        app.run(host="localhost", port=8080, debug=True)
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

*  **`main.py`:** possiamo avere due tipologie:
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
                    },
                    "vittime": {
                        "arrayValue": {
                            "values": [
                                {"stringValue": "Mario"},
                                {"stringValue": "Luigi"},
                                {"stringValue": "Peach"}
                            ]
                        }
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
        **$\color{red}{\text{N.B.}}$** Anche se i valori memorizzati rappresentano numeri interi, nei trigger di Firestore essi vengono forniti come **stringhe**.

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
        Il parametro `context` contiene le informazioni di contesto dell’evento che ha attivato la Cloud Function. In particolare descrive:
        * il path completo della risorsa Firestore coinvolta: `context.resource`.
        * i valori delle wildcard definite nel trigger: `.params["KEY"]`.


## 6.1. Deploy
1. **Verifichiamo che le variabili d'ambiente `PROJECT_ID` e `NAME` siano ancora valide** (`NAME` deve essere uguale a quello utilizzato precedentemente):
    
    ```bash
    echo PROJECT_ID = ${PROJECT_ID}
    echo NAME = ${NAME}
    ```
2. **Il procedimento del deployment da qui in avanti è specifico rispetto al tipo di Function:**
    - **HTTP Function:**
        1. Definiamo il nome della funzione che dovrà essere invocata dalla richiesta HTTP:
            
            ```bash
            export FUNCTION=NOME_FUNZIONE
            ```
            
        2. Definiamo il runtime:
            
            ```bash
            export RUNTIME=python310
            ```
            
        3. **Deploy:**
            
            ```bash
            gcloud functions deploy ${FUNCTION} \
              --runtime ${RUNTIME} \
              --trigger-http \
              --allow-unauthenticated \
              --docker-registry=artifact-registry \
              --no-gen2
            ```
            
        4. **Testing**: utiliziamo l'URL assegnato da Google Cloud durante il deploy. Per ottnere l'indirizzo HTTP eseguiamo:           
            ```bash
            gcloud functions describe $FUNCTION
            ```
        
        5. **Testing in locale:** 
            ```python
            @app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
            @app.route("/<path:path>", methods=["GET", "POST"])
            def local_test(path):
                return HTTP_FUNCTION(request)
            ```
            In seguito utilizzamo un qualsiasi path per testare la nostra funzione (funziona solo con il `GET`), per esempio:
            ```bash
            http://localhost:8080/test
            ```
            

            
    - **Event driven Function:**
        1. Definiamo le seguenti variabili globali:
            
            ```bash
            export FUNCTION=NOME_FUNZIONE
            export RUNTIME=python310
            export DATABASE=NOME_DATABASE
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
       4. **Testing in locale:**
          * Togliamo dalla funzione il parametro `context`
          * Utilizziamo nel main un `fake_event`:
 
            ```python
            fake_event = {
                "value": {
                    "name": "projects/test/databases/(default)/documents/letture/12-05-2026",
                    "fields": {
                        "value": {
                            "integerValue": "100"
                        }
                    }
                },
                "oldValue": {}
            }
            ```  
        * Chiamiamo la funzione inseredno il `fake_event`:
       
            ```bash
            python3 update_db(fake_event)
            ```
---
# 7. PubSub
## 7.1. Caso in cui i nomi del Topic e della Subscription sono noti a priori
1. **Settiamo le variabili di ambiente (devono essere settate in tutti i terminali che utilizziamo):**
   
    ```bash
    export PROJECT_ID="PROJECT_NAME"
    export TOPIC_NAME="TOPIC_NAME"
    export SUBSCRIPTION_NAME="SUBSCRIPTION_NAME"
    ````
    Per controllare tutte le variabili:
    ```bash
    echo $PROJECT_ID
    echo $TOPIC_NAME
    echo $SUBSCRIPTION_NAME
    ````
    Verificare in ogni ciascun terminale che utilizziamo di aver esportato le credenziali:
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
    ```
2. **Creiamo il topic e la subscription su gcloud:**
    ```bash
    gcloud pubsub topics create $TOPIC_NAME
    gcloud pubsub subscriptions create $SUBSCRIPTION_NAME --topic=$TOPIC_NAME
    ````

3. **Scriviamo il codice del pub e del sub:**

    * **Codice `publisher`:** il Publisher non è quasi mai un file a sé stante che lanci separatamente. È una funzione integrata nel tuo codice principale.
    
        ```python
        import os
        import json
        from google.cloud import firestore
        from google.cloud import pubsub_v1

        #Inizializziamo il publisher
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(os.environ['PROJECT_ID'], os.environ['TOPIC_NAME']) 

        data={'key1': 'value1', 'key2': 'value2'}
        future = publisher.publish(topic_path, json.dumps(data).encode('utf-8'))
        
        try:
            message_id = future.result()
            print(f"✅ Messaggio inviato con ID: {message_id}")
        except Exception as e:
            print(f"❌ Errore durante l'invio: {e}")

        time.sleep(0.5)
        ```
    * **`subscriber.py`:**
        ```python
        import os
        import sys
        import json
        from google.cloud import pubsub_v1
        from google.cloud import firestore

        project_id = os.environ['PROJECT_ID']
        sub_name = os.environ['SUBSCRIPTION_NAME']

        subscriber = pubsub_v1.SubscriberClient()
        sub_path = subscriber.subscription_path(project_id, sub_name)

        # Se vuoi legger qualcosa passata per linea di comando
        cap_interessati = sys.argv[1:] 

        #Funzione che scatta automaticamente quando arriva un mesaggio
        def callback(message):

            dati = json.loads(message.data.decode('utf-8'))
            value1 = dati.get('key1')
            value2 = dati.get('key2')
            message.ack() #Conferma la ricezione

            #if not cap_interessati or str(cap_messaggio) in cap_interessati:
            print("Abbiamo ricevuto....")

        if __name__ == '__main__':
            print("Tentativo di avvio del Subscriber...")
            pull = subscriber.subscribe(sub_path, callback=callback)
            try:
                print(f"In ascolto su {sub_path}...")
                pull.result()
            except Exception as e:
                # Se c'è un errore (es. permessi, nomi sbagliati), ora lo vedrai scritto!
                print(f"❌ Il subscriber si è fermato per un errore: {e}")
                pull.cancel()
            except KeyboardInterrupt:
                # Questo serve per quando premi Ctrl+C
                pull.cancel()
                print("\n🛑 Subscriber fermato manualmente.")
        ```

3. **In un terminale far partire il pub (va bene anche in locale)**
4. **In un altro terminale fai partire il sub**

## 7.2. Caso in cui dobbbiamo definire dinamicamente i nomi dei Topic e delle Subscription

1. **Template `publisher`:** questo codice va inserito dove nascono i dati (es. `api.py`). La funzione chiave è `publish_message`: gestisce da sola la creazione del topic se non esiste e l'invio del messaggio.
    ```python
    import os
    from google.cloud import pubsub_v1

    # Configurazione Globale
    PROJECT_ID = os.environ.get('PROJECT_ID')
    publisher = pubsub_v1.PublisherClient()

    def publish_message(topic_name, message_string):
        """
        1. Crea il topic se non esiste.
        2. Invia il messaggio.
        """
        # Costruzione percorso completo: projects/{id}/topics/{nome}
        topic_path = publisher.topic_path(PROJECT_ID, topic_name)
        
        # 2. Logica "Get or Create" (Idempotenza)
        try:
            publisher.get_topic(request={"topic": topic_path})
        except Exception:
            print(f"Creating topic {topic_name}...")
            publisher.create_topic(name=topic_path)

        # 3. Pubblicazione (Importante: encode in bytes!)
        future = publisher.publish(topic_path, data=message_string.encode("utf-8"))
        
        return future.result() # Restituisce l'ID del messaggio pubblicato

    # --- ESEMPIO DI UTILIZZO ---
    # publish_message("cartolina", "id-12345")
    ```
2. **Template `subscriber`:**

    ```python
    import os
    import sys
    import uuid
    from google.cloud import pubsub_v1

    # --- CONFIGURAZIONE ---
    PROJECT_ID = os.environ.get('PROJECT_ID')

    # Argomenti da riga di comando (es: python3 worker.py nome_topic)
    if len(sys.argv) < 2:
        print("Errore: specifica il topic da ascoltare.")
        sys.exit(1)

    topic_name = sys.argv[1]

    # 1. Setup Percorsi
    topic_path = f"projects/{PROJECT_ID}/topics/{topic_name}"

    # Generiamo un nome sottoscrizione casuale (es. sub-cartolina-xf32s)
    sub_name = f"sub-{topic_name}-{str(uuid.uuid4())[:8]}"
    subscription_path = f"projects/{PROJECT_ID}/subscriptions/{sub_name}"

    # 2. Inizializzazione Client
    subscriber = pubsub_v1.SubscriberClient()

    # Creazione Sottoscrizione Effimera
    print(f"Creazione sottoscrizione: {sub_name} su topic: {topic_path}")
    try:
        subscriber.create_subscription(request={"name": subscription_path, "topic": topic_path})
    except Exception as e:
        print(f"Errore creazione subscription (forse il topic non esiste?): {e}")
        sys.exit(1)

    # 3. La Callback (Cosa fare quando arriva un messaggio)
    def callback(message_obj):
        # IMPORTANTE: Decodifica i dati
        content = message_obj.data.decode("utf-8")
        print(f"📩 Ricevuto: {content}")
        
        # --- SPAZIO PER LA TUA LOGICA ---
        # Esempio: db.get_element("collection", content)
        # --------------------------------
        
        # Conferma ricezione (altrimenti PubSub lo rimanda all'infinito)
        message_obj.ack()

    # 4. Loop di Ascolto e Pulizia
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"In ascolto... (Ctrl+C per chiudere)")

    with subscriber:
        try:
            # Mantiene lo script vivo
            streaming_pull_future.result()
        except KeyboardInterrupt:
            print("\nChiusura richiesta dall'utente...")
            streaming_pull_future.cancel()
        finally:
            # PULIZIA FINALE: Cancella la sottoscrizione
            print("Eliminazione sottoscrizione temporanea...")
            subscriber.delete_subscription(request={"subscription": subscription_path})
            print("Fatto. Ciao!")
    ```
3. **In un terminale far partire il pub (va bene anche in locale).**
4. **In un altro terminale fai partire il sub.**
---
# 8. File `time_utils.py`
```python
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import calendar

# =============================================================================
# SEZIONE 1: CONVERSIONI BASE (Stringa <-> Oggetto)
# =============================================================================

def from_string_do_date(d_str: str, pattern = "%d-%m-%Y") -> datetime:
    """
    Converte una stringa in un oggetto datetime o time basandosi sul pattern.
    Esempi pattern: "%d-%m-%Y", "%H:%M", "%Y-%m-%d %H:%M:%S"
    """
    if not d_str:
        return None
    try:
        dt = datetime.strptime(d_str, pattern)
        # Se il pattern contiene solo ore e minuti, restituiamo un oggetto .time()
        if "%H" in pattern and "%d" not in pattern:
            return dt.time()
        return dt
    except (ValueError, TypeError):
        return None

def from_date_to_string(d: datetime, pattern = "%d-%m-%Y") -> str:
    """
    Converte un oggetto (datetime o time) in stringa basandosi sul pattern.
    """
    if d is None:
        return None
    return d.strftime(pattern)
  
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

def calculate_end_time(start_time_str: str, duration_minutes: int) -> str:
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

from datetime import datetime
from dateutil.relativedelta import relativedelta

def aggiungi_un_mese(data_input) -> str:
    # Se la data è una stringa, la convertiamo prima in oggetto datetime
    if isinstance(data_input, str):
        data_obj = datetime.strptime(data_input, "%Y-%m-%d")
    else:
        data_obj = data_input

    # Aggiunge esattamente un mese solare
    nuova_data = data_obj + relativedelta(months=1)
    
    return from_date_to_string(nuova_data)

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

def ordina_lista_di_dizionari_per_data(l, campo_con_data, formato_data="%Y-%m-%d %H:%M:%S",reverse=False):
    """Ordina una lista di dizionari in base a una data (stringa o oggetto datetime)."""
    # Usiamo sorted con una chiave (key) personalizzata
    lista_sorted = sorted(
        l, 
        key=lambda x: datetime.strptime(x[campo_con_data], formato_data),
        reverse=reverse
    )
    return lista_sorted

# =============================================================================
# SEZIONE 5: UTILITY VARIE E FORMATTAZIONE
# =============================================================================

def giorno_della_settimana_it(data_str: str) -> str:
    """Restituisce il nome del giorno in italiano (es. 'Lunedì')"""
    data = from_string_to_date(data_str)
    if not data: return ""
    giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    return giorni[data.weekday()]

def mese_it_month(month_str: str) -> str:
    """Restituisce il nome del mese in italiano (es. 'Gennaio')"""
    data = from_string_to_month(month_str)
    if not data:
        return ""

    mesi = [
        "Gennaio", "Febbraio", "Marzo", "Aprile",
        "Maggio", "Giugno", "Luglio", "Agosto",
        "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]
    return mesi[data.month - 1]

def mese_it_date(date_str: str) -> str:
    """Restituisce il nome del mese in italiano (es. 'Gennaio')"""
    data = from_string_to_date(date_str)
    if not data:
        return ""

    mesi = [
        "Gennaio", "Febbraio", "Marzo", "Aprile",
        "Maggio", "Giugno", "Luglio", "Agosto",
        "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]

    return mesi[data.month - 1]

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
# 9. Staccare il Billing del Progetto o Eliminarlo
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
# 10. Cose utiili
* **Controllo Email:**

    ```python
    import email_validator

    def validazione_email(email):
        try:
            email_validator.validate_email(email)
            return True
        except email_validator.EmailNotValidError:
            return False
    ```
* **Generazione e Controllo UID:**
  
     ```python
    import uuid

    def is_valid_uuid(uuid_to_test, version=4):
        """
        Verifica se una stringa è un UUID valido.
        """
        try:
            # Tenta di creare un oggetto UUID; se fallisce, solleva ValueError
            uuid_obj = uuid.UUID(uuid_to_test, version=version)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_to_test
    
    #nuovo_id = uuid.uuid4()
    ```   
* **Generazione e Controllo IPaddress:**
     ```python
    import ipaddress

    def is_valid_ip(ip_str):
        try:
            ipaddress.IPv4Address(ip_str)
            return True
        except ValueError:
            return False

    # Esempio:
    # is_valid_ip("192.168.1.1") -> True
    # is_valid_ip("192.168.1.300") -> False

    """Controlliamo che il NetworkID inviato sia reale risettetto alla maschera"""
    def check_netid(ip, cidr):
        try:
            # strict=True lancia errore se ci sono bit host impostati (es. .5/24)
            ipaddress.IPv4Network(f"{ip}/{cidr}", strict=True)
            return True
        except ValueError:
            return False

    """Serve a capire se un pacchetto (IP) può passare attraverso una determinata regola (Rete)."""
    def find_matching_rules(target_ip_str, rules_from_db):
        """
        target_ip_str: l'IP da testare (es. "192.168.1.10")
        rules_from_db: lista di dizionari dal database
        """
        addr = ipaddress.IPv4Address(target_ip_str)
        matches = []

        for rule in rules_from_db:
            # Costruisco la rete della regola
            # strict=False corregge eventuali errori nel DB (es. 192.168.1.1/24 diventa .0/24)
            net = ipaddress.IPv4Network(f"{rule['ip']}/{rule['netmaskCIDR']}", strict=False)
            
            # Controllo magico: l'IP è contenuto nella rete?
            if addr in net:
                matches.append(rule)
                
        return matches
    ```  
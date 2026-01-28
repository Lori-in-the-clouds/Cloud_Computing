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